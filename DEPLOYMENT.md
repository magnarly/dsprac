# DSA Practice Platform - Deployment Guide

## Overview
This is an AI-powered DSA learning platform with microservices architecture. Due to environment constraints (limited disk space ~500MB), the full Docker deployment may not work in all environments.

## Architecture
- **Frontend**: Next.js (Port 3000)
- **Backend API**: FastAPI (Port 8000)
- **Web Scraper**: Python/FastAPI (Port 8001)
- **Code Executor**: Python/FastAPI (Port 8002)
- **AI Agent**: LangChain + OpenAI/Anthropic
- **Database**: PostgreSQL (Port 5432)
- **Cache**: Redis (Port 6379)

## Prerequisites
- Docker & Docker Compose OR Podman
- Minimum 2GB free disk space
- 2GB RAM
- Node.js 18+ (for local development)
- Python 3.11+ (for backend services)

## Option 1: Full Docker Deployment (Recommended for Production)

### Using Docker
```bash
docker-compose up -d --build
```

### Using Podman
```bash
# Configure registries
echo 'unqualified-search-registries = ["docker.io"]' | sudo tee /etc/containers/registries.conf

# Start podman socket service
podman system service --time=0 unix:///tmp/podman.sock &

# Run docker-compose with podman socket
export DOCKER_HOST=unix:///tmp/podman.sock
docker-compose -H unix:///tmp/podman.sock up -d --build
```

Access the application at: http://localhost:3000

## Option 2: Local Development Mode (Lightweight)

If you have limited disk space or just want to develop/test:

### 1. Install Dependencies
```bash
# Backend dependencies
cd /workspace/backend
pip install -r requirements.txt

# Frontend dependencies
cd /workspace/app
npm install

# Scraper dependencies
cd /workspace/scraper
pip install -r requirements.txt

# Code executor dependencies
cd /workspace/code-executor
pip install -r requirements.txt

# AI Agent dependencies
cd /workspace/ai-agent
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the root directory:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dsaprac
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Run Services Individually

**Start PostgreSQL and Redis (using minimal containers):**
```bash
podman run -d --name dsaprac_db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=dsaprac -p 5432:5432 postgres:15-alpine
podman run -d --name dsaprac_redis -p 6379:6379 redis:7-alpine
```

**Start Backend:**
```bash
cd /workspace/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Start Frontend:**
```bash
cd /workspace
npm run dev
```

**Start Scraper:**
```bash
cd /workspace/scraper
python main.py
```

**Start Code Executor:**
```bash
cd /workspace/code-executor
python main.py
```

**Start AI Agent:**
```bash
cd /workspace/ai-agent
python main.py
```

## Option 3: Simplified Single-Container Development

For testing with minimal resources, use the simplified setup:

```bash
# Run only essential services
podman run -d --name dsaprac_redis -p 6379:6379 redis:7-alpine

# Run backend and frontend locally without containers
cd /workspace/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
cd /workspace && npm run dev
```

## Troubleshooting

### Disk Space Issues
The VFS storage driver used by Podman in nested environments requires significant disk space. If you encounter "no space left on device" errors:

1. Clean up unused images and containers:
```bash
podman system prune -a --force
rm -rf /var/lib/containers/storage/*
```

2. Use overlay driver if supported:
```bash
# Edit /etc/containers/storage.conf
[storage]
driver = "overlay"
```

### Registry Pull Issues
If you get "short-name did not resolve" errors:
```bash
# Update registries.conf
echo 'unqualified-search-registries = ["docker.io", "quay.io"]' | sudo tee /etc/containers/registries.conf
```

### Port Conflicts
Check which ports are in use:
```bash
netstat -tlnp | grep -E '3000|8000|8001|8002|5432|6379'
```

Change ports in `docker-compose.yml` if needed.

## API Endpoints

Once running, the following endpoints are available:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
  - `GET /api/problems` - List all problems
  - `POST /api/problems/generate` - Generate problems from syllabus
  - `POST /api/code/execute` - Execute code
  - `GET /api/mcq` - Get MCQs
- **Scraper**: http://localhost:8001
- **Code Executor**: http://localhost:8002

## Features

### Syllabus-Based Test Generation
1. Enter your DSA syllabus topics
2. AI scrapes web resources (GeeksforGeeks, Codeforces, etc.)
3. Generates custom coding problems and MCQs
4. Creates tests similar to LeetCode/Codeforces

### Multi-Language Code Execution
Supports:
- Python 3.11
- C/C++ (GCC)
- Java (OpenJDK)
- Bash

### Secure Sandboxing
Code execution happens in isolated containers with:
- Memory limits
- CPU limits
- Network isolation
- Timeout enforcement

## NotebookLM Integration

The platform can import/export study materials compatible with Google's NotebookLM:
- Export problem sets as markdown
- Import research notes
- Link external resources

## Support

For issues or questions:
1. Check docs/ARCHITECTURE.md for system design
2. Review AGENTS.md for AI agent configuration
3. Check container logs: `podman logs <container_name>`
