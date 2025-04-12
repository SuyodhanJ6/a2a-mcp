### Simple Request

```bash
curl -X POST https://a2a.enso.sh \
-H "Content-Type: application/json" \
-d '{
	"jsonrpc": "2.0",
	"id": 11,
	"method": "tasks/send",
	"params": {
		"id": "129",
		"sessionId": "8f01f3d172cd4396a0e535ae8aec6687",
		"acceptedOutputModes": [
			"text"
		],
		"message": {
			"role": "user",
			"parts": [
				{
					"type": "text",
					"text": "How much is the exchange rate for 1 USD to INR?"
				}
			]
		}
	}
}' | jq
```

### Multiple Messages
```bash
curl -X POST http://localhost:10000 \
-H "Content-Type: application/json" \
-d '{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tasks/send",
  "params": {
    "id": "130",
    "sessionId": "a9bb617f2cd94bd585da0f88ce2ddba2",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "How much is the exchange rate for 1 USD?"
        }
      ]
    }
  }
}' | jq
```

```bash
curl -X POST http://localhost:10000 \
-H "Content-Type: application/json" \
-d '{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tasks/send",
  "params": {
    "id": "130",
    "sessionId": "a9bb617f2cd94bd585da0f88ce2ddba2",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "CAD"
        }
      ]
    }
  }
}' | jq
```


### Streaming Response
```bash
curl -X POST https://a2a.enso.sh \
-H "Content-Type: application/json" \
-d '{
  "jsonrpc": "2.0",
  "id": 12,
  "method": "tasks/sendSubscribe",
  "params": {
    "id": "131",
    "sessionId": "cebd704d0ddd4e8aa646aeb123d60614",
    "acceptedOutputModes": [
      "text"
    ],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "How much is 100 USD in GBP?"
        }
      ]
    }
  }
}'
```