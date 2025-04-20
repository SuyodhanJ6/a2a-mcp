import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional, AsyncIterable, Union
import logging

from common.types import (
    SendTaskRequest, 
    SendTaskResponse, 
    Task, 
    TaskState, 
    TaskStatus, 
    Artifact,
    TaskSendParams,
    Message,
    TextPart,
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
    TaskStatusUpdateEvent,
    JSONRPCResponse,
    TaskIdParams,
    TaskArtifactUpdateEvent,
    InvalidParamsError,
    InternalError,
    PushNotificationConfig
)
from common.server.task_manager import InMemoryTaskManager
from common.utils.push_notification_auth import PushNotificationSenderAuth
import common.server.utils as utils

logger = logging.getLogger(__name__)

class AgentTaskManager(InMemoryTaskManager):
    """Manages tasks for the A2E agent."""

    def __init__(self, agent, notification_sender_auth: Optional[PushNotificationSenderAuth] = None):
        super().__init__()
        self.agent = agent
        self.notification_sender_auth = notification_sender_auth

    def _get_user_query(self, task_send_params: TaskSendParams) -> str:
        """Extract the user query from the task parameters."""
        part = task_send_params.message.parts[0]
        if not isinstance(part, TextPart):
            raise ValueError("Only text parts are supported")
        return part.text

    def _validate_request(
        self, request: Union[SendTaskRequest, SendTaskStreamingRequest]
    ) -> JSONRPCResponse | None:
        """Validate the incoming request."""
        task_send_params: TaskSendParams = request.params
        if not utils.are_modalities_compatible(
            task_send_params.acceptedOutputModes, self.agent.SUPPORTED_CONTENT_TYPES
        ):
            logger.warning(
                "Unsupported output mode. Received %s, Support %s",
                task_send_params.acceptedOutputModes,
                self.agent.SUPPORTED_CONTENT_TYPES,
            )
            return utils.new_incompatible_types_error(request.id)
        
        if task_send_params.pushNotification and not task_send_params.pushNotification.url:
            logger.warning("Push notification URL is missing")
            return JSONRPCResponse(id=request.id, error=InvalidParamsError(message="Push notification URL is missing"))
        
        return None

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Process a new task request."""
        validation_error = self._validate_request(request)
        if validation_error:
            return SendTaskResponse(id=request.id, error=validation_error.error)
        
        if request.params.pushNotification:
            if not await self.set_push_notification_info(request.params.id, request.params.pushNotification):
                return SendTaskResponse(id=request.id, error=InvalidParamsError(message="Push notification URL is invalid"))

        await self.upsert_task(request.params)
        task = await self.update_store(
            request.params.id, TaskStatus(state=TaskState.WORKING), None
        )
        await self.send_task_notification(task)

        task_send_params: TaskSendParams = request.params
        query = self._get_user_query(task_send_params)
        try:
            agent_response = self.agent.invoke(query, task_send_params.sessionId)
            return await self._process_agent_response(request, agent_response)
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            return SendTaskResponse(
                id=request.id,
                error=InternalError(message=f"Error invoking agent: {e}")
            )

    async def on_send_task_subscribe(
        self, request: SendTaskStreamingRequest
    ) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        """Handle streaming task requests."""
        try:
            error = self._validate_request(request)
            if error:
                return error

            await self.upsert_task(request.params)

            if request.params.pushNotification:
                if not await self.set_push_notification_info(request.params.id, request.params.pushNotification):
                    return JSONRPCResponse(id=request.id, error=InvalidParamsError(message="Push notification URL is invalid"))

            task_send_params: TaskSendParams = request.params
            sse_event_queue = await self.setup_sse_consumer(task_send_params.id, False)            

            asyncio.create_task(self._run_streaming_agent(request))

            return self.dequeue_events_for_sse(
                request.id, task_send_params.id, sse_event_queue
            )
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            return JSONRPCResponse(
                id=request.id,
                error=InternalError(
                    message=f"An error occurred while streaming the response: {e}"
                ),
            )

    async def _run_streaming_agent(self, request: SendTaskStreamingRequest):
        """Process a streaming task."""
        task_send_params: TaskSendParams = request.params
        query = self._get_user_query(task_send_params)

        try:
            async for item in self.agent.stream(query, task_send_params.sessionId):
                is_task_complete = item["is_task_complete"]
                require_user_input = item.get("require_user_input", False)
                parts = [{"type": "text", "text": item["content"]}]
                artifact = None
                message = None
                end_stream = False

                if not is_task_complete and not require_user_input:
                    task_state = TaskState.WORKING
                    message = Message(role="agent", parts=parts)
                elif require_user_input:
                    task_state = TaskState.INPUT_REQUIRED
                    message = Message(role="agent", parts=parts)
                    end_stream = True
                else:
                    task_state = TaskState.COMPLETED
                    artifact = Artifact(role="assistant", parts=parts)
                    end_stream = True

                task_status = TaskStatus(state=task_state, message=message)
                latest_task = await self.update_store(
                    task_send_params.id,
                    task_status,
                    None if artifact is None else [artifact],
                )
                await self.send_task_notification(latest_task)

                if artifact:
                    task_artifact_update_event = TaskArtifactUpdateEvent(
                        taskId=task_send_params.id, artifact=artifact
                    )
                    await self.enqueue_events_for_sse(
                        task_send_params.id, task_artifact_update_event
                    )

                task_update_event = TaskStatusUpdateEvent(
                    taskId=task_send_params.id, status=task_status, final=end_stream
                )
                await self.enqueue_events_for_sse(
                    task_send_params.id, task_update_event
                )

        except Exception as e:
            logger.error(f"An error occurred while streaming the response: {e}")
            await self.enqueue_events_for_sse(
                task_send_params.id,
                InternalError(message=f"An error occurred while streaming the response: {e}")                
            )

    async def _process_agent_response(
        self, request: SendTaskRequest, agent_response: dict
    ) -> SendTaskResponse:
        """Process the agent's response and update the task status."""
        task_send_params: TaskSendParams = request.params
        task_id = task_send_params.id
        history_length = task_send_params.historyLength
        task_status = None

        parts = [{"type": "text", "text": agent_response["content"]}]
        artifact = None
        if agent_response.get("require_user_input", False):
            task_status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message=Message(role="agent", parts=parts),
            )
        else:
            task_status = TaskStatus(state=TaskState.COMPLETED)
            artifact = Artifact(role="assistant", parts=parts)
        
        task = await self.update_store(
            task_id, task_status, None if artifact is None else [artifact]
        )
        task_result = self.append_task_history(task, history_length)
        await self.send_task_notification(task)
        return SendTaskResponse(id=request.id, result=task_result)

    async def send_task_notification(self, task: Task):
        """Send a push notification for a task update."""
        if not await self.has_push_notification_info(task.id):
            logger.info(f"No push notification info found for task {task.id}")
            return
            
        push_info = await self.get_push_notification_info(task.id)
        if not push_info or not self.notification_sender_auth:
            return

        logger.info(f"Notifying for task {task.id} => {task.status.state}")
        await self.notification_sender_auth.send_push_notification(
            push_info.url,
            data=task.model_dump(exclude_none=True)
        )

    async def set_push_notification_info(self, task_id: str, push_notification_config: PushNotificationConfig):
        """Set push notification info with verification."""
        # Verify the ownership of notification URL by issuing a challenge request.
        if self.notification_sender_auth:
            is_verified = await self.notification_sender_auth.verify_push_notification_url(push_notification_config.url)
            if not is_verified:
                return False
        
        await super().set_push_notification_info(task_id, push_notification_config)
        return True 