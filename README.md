# AI-Powered DSA Learning Platform

## Overview
This repository contains a complete agentic workflow for creating an advanced learning environment for students powered by AI. The platform focuses on custom DSA practice tests similar to LeetCode or Codeforces, with support for C/C++, Java, Python, and Bash.

## Architecture

### Microservices Architecture (Docker-based)

1. **Frontend Service** - Next.js UI for student interaction
2. **Backend API** - FastAPI service handling business logic
3. **Code Executor** - Secure sandboxed code execution for multiple languages
4. **Web Scraper** - Scrapes educational resources from the web
5. **AI Agent** - Orchestrates test generation and content creation

### Key Features

- **Syllabus Input**: Students provide their syllabus
- **Web Scraping**: Automatically scrapes relevant DSA resources
- **Test Generation**: Creates custom MCQs and coding problems
- **Multi-language Support**: C/C++, Java, Python, Bash
- **Secure Execution**: Sandboxed code execution environment
- **Interoperability**: Works with NotebookLM and other tools

## Services

### 1. Frontend (Next.js)
- Modern React-based UI
- Real-time code editor
- Test dashboard
- Progress tracking

### 2. Backend API (FastAPI)
- RESTful API endpoints
- User management
- Test management
- Integration with AI agents

### 3. Code Executor
- Docker-in-Docker isolation
- Support for C/C++, Java, Python, Bash
- Time and memory limits
- Security sandboxing

### 4. Web Scraper
- Scrapes GeeksforGeeks, LeetCode, Codeforces patterns
- Extracts problem statements, solutions, explanations
- Respects robots.txt and rate limits

### 5. AI Agent
- LLM-powered test generation
- Question difficulty calibration
- Solution validation
- Personalized learning paths

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.10+

### Quick Start

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Project Structure

```
/workspace
├── app/                    # Next.js frontend
├── backend/                # FastAPI backend
│   ├── app/
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── utils/
├── code-executor/          # Code execution service
│   ├── executors/
│   └── sandbox/
├── scraper/                # Web scraping service
│   ├── scrapers/
│   └── parsers/
├── ai-agent/               # AI orchestration
│   ├── agents/
│   └── workflows/
├── docker/                 # Docker configurations
└── docs/                   # Documentation
```

## API Endpoints

### Tests
- `POST /api/tests/create` - Create a new test from syllabus
- `GET /api/tests/:id` - Get test details
- `POST /api/tests/:id/submit` - Submit test solution

### Problems
- `GET /api/problems` - List available problems
- `POST /api/problems/generate` - Generate new problems via AI

### Execution
- `POST /api/execute` - Execute code in sandbox

## Technology Stack

- **Frontend**: Next.js 16, React 19, TypeScript, TailwindCSS
- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL (via Docker)
- **Cache**: Redis (via Docker)
- **Code Execution**: Docker containers with language-specific images
- **AI**: LangChain, OpenAI/Anthropic APIs
- **Scraping**: BeautifulSoup, Scrapy, Playwright

## Security Considerations

- All code execution happens in isolated Docker containers
- Resource limits (CPU, memory, time) enforced
- Network access restricted during execution
- Input validation on all endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
