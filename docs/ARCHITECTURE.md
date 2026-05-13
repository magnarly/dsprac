# AI-Powered DSA Learning Platform - Architecture Documentation

## System Overview

This document describes the complete architecture of the AI-powered DSA learning platform that generates custom practice tests based on student syllabi.

## Agentic Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Student       │────▶│   Frontend      │────▶│   Backend API   │
│   (Syllabus)    │     │   (Next.js)     │     │   (FastAPI)     │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                    ┌────────────────────────────────────┼────────────────────────────────────┐
                    │                                    │                                    │
                    ▼                                    ▼                                    ▼
           ┌─────────────────┐                 ┌─────────────────┐                 ┌─────────────────┐
           │   Web Scraper   │                 │    AI Agent     │                 │  Code Executor  │
           │   Service       │◀───────────────▶│   Service       │                 │   Service       │
           │                 │                 │                 │                 │                 │
           │ - GeeksforGeeks │                 │ - OpenAI        │                 │ - Python        │
           │ - LeetCode      │                 │ - Anthropic     │                 │ - C/C++         │
           │ - Codeforces    │                 │ - LangChain     │                 │ - Java          │
           └─────────────────┘                 └─────────────────┘                 │ - Bash          │
                                                                                   └─────────────────┘
```

## Data Flow

1. **Syllabus Input**: Student enters topics via the frontend UI
2. **Test Generation Request**: Frontend sends request to backend API
3. **Content Scraping**: Backend triggers scraper service to gather educational content
4. **AI Processing**: AI agent uses LLMs to generate questions from scraped content
5. **Test Assembly**: Backend compiles generated questions into a structured test
6. **Code Execution**: When students submit solutions, code executor runs them in sandboxes

## Service Details

### 1. Frontend Service (Port 3000)
- **Technology**: Next.js 16, React 19, TypeScript, TailwindCSS
- **Responsibilities**:
  - Syllabus input form
  - Test display with questions
  - Code editor interface
  - Real-time execution feedback

### 2. Backend API Service (Port 8000)
- **Technology**: FastAPI, Python 3.11
- **Responsibilities**:
  - RESTful API endpoints
  - Orchestration between services
  - Test management
  - User session handling

**Key Endpoints**:
- `POST /api/tests/create` - Generate new test from syllabus
- `GET /api/tests/{id}` - Retrieve test details
- `POST /api/tests/{id}/submit` - Submit solutions
- `POST /api/execute` - Execute code

### 3. Web Scraper Service (Port 8001)
- **Technology**: FastAPI, BeautifulSoup, Scrapy, Playwright
- **Responsibilities**:
  - Scrape educational websites
  - Extract problem statements and solutions
  - Format content for AI processing
  - NotebookLM integration

**Supported Sources**:
- GeeksforGeeks
- LeetCode (via API patterns)
- Codeforces

### 4. Code Executor Service (Port 8002)
- **Technology**: FastAPI, Docker SDK
- **Responsibilities**:
  - Secure code execution in isolated containers
  - Multi-language support
  - Resource limit enforcement
  - Timeout handling

**Language Support**:
- Python 3.11
- C++ (GCC 12)
- Java (OpenJDK 17)
- Bash 5

**Security Features**:
- Network isolation
- Memory limits
- CPU time limits
- Read-only file system

### 5. AI Agent Service
- **Technology**: LangChain, OpenAI/Anthropic APIs
- **Responsibilities**:
  - Process scraped content
  - Generate coding problems
  - Create MCQs
  - Calibrate difficulty levels
  - Provide explanations

**LLM Integration**:
- OpenAI GPT-4 Turbo
- Anthropic Claude 3

### 6. Database (PostgreSQL - Port 5432)
- Stores user data
- Test definitions
- Submission history
- Problem bank

### 7. Cache (Redis - Port 6379)
- Session management
- Task queue for async processing
- Result caching
- Rate limiting

## Docker Configuration

The application uses Docker Compose to orchestrate all services:

```yaml
services:
  - frontend (Next.js)
  - backend (FastAPI)
  - scraper (FastAPI + scraping tools)
  - code-executor (FastAPI + Docker)
  - ai-agent (LangChain worker)
  - db (PostgreSQL)
  - redis (Redis)
```

## Security Considerations

1. **Code Execution Security**:
   - All user code runs in isolated Docker containers
   - No network access during execution
   - Strict resource limits (CPU, memory, time)
   - Read-only file system

2. **API Security**:
   - CORS configuration
   - Rate limiting via Redis
   - Input validation
   - SQL injection prevention (SQLAlchemy ORM)

3. **Data Privacy**:
   - No personal data stored without consent
   - Encrypted connections (HTTPS in production)
   - Secure credential management

## Scalability

### Horizontal Scaling
- Stateless services can be scaled independently
- Redis for distributed session management
- PostgreSQL connection pooling

### Load Balancing
- Nginx reverse proxy (production)
- Docker Swarm or Kubernetes for orchestration

## Monitoring & Logging

- Health check endpoints on all services
- Structured logging (JSON format)
- Prometheus metrics (planned)
- Grafana dashboards (planned)

## Development Workflow

1. **Local Development**:
   ```bash
   docker-compose up -d
   npm run dev  # Frontend hot reload
   ```

2. **Testing**:
   - Unit tests for each service
   - Integration tests for API endpoints
   - End-to-end tests with Playwright

3. **Deployment**:
   - Docker images pushed to registry
   - Kubernetes manifests for production
   - CI/CD pipeline (GitHub Actions)

## Future Enhancements

1. **Advanced AI Features**:
   - Personalized difficulty adjustment
   - Learning path recommendations
   - Automated solution hints

2. **Collaboration**:
   - Multi-user practice sessions
   - Leaderboards
   - Discussion forums

3. **Analytics**:
   - Performance tracking
   - Weakness identification
   - Progress visualization

4. **Additional Languages**:
   - JavaScript/TypeScript
   - Go
   - Rust
