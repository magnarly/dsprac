# AI Agent Dockerfile - LLM Orchestration
FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY ai-agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY ai-agent/ ./ai-agent/

# No port exposed - this service runs tasks asynchronously

# Run the agent worker
CMD ["python", "ai-agent/worker.py"]
