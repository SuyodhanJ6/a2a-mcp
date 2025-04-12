# Stage 1: Build stage
FROM python:3.13-slim AS builder

# Set work directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy dependencies and requirements files first
COPY pyproject.toml .
COPY uv.lock .

# Install system dependencies required by spaCy and build tools
RUN apt-get update && apt-get install --no-install-recommends -y \
    wget build-essential python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install uv \
    && touch README.md \
    && uv pip install -v --system --no-cache-dir .

# Stage 2: Final stage
FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy application from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Expose the default port
EXPOSE 10000

# Run the application
CMD ["python", "__main__.py", "--host", "0.0.0.0", "--port", "10000"]