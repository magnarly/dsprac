# Code Executor Dockerfile - Secure Code Execution
FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies for multiple languages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    openjdk-17-jdk-headless \
    python3 \
    python3-pip \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Set up Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Copy requirements and install Python dependencies
COPY code-executor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy executor code
COPY code-executor/ ./code-executor/

# Expose port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "code-executor.main:app", "--host", "0.0.0.0", "--port", "8002"]
