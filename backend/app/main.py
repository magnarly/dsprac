"""
FastAPI Backend for DSA Learning Platform
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx

app = FastAPI(
    title="DSA Learning Platform API",
    description="API for AI-powered DSA practice test generation and code execution",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SyllabusInput(BaseModel):
    topics: List[str]
    difficulty: str = "medium"
    num_questions: int = 10
    num_mcqs: int = 5

class CodeSubmission(BaseModel):
    language: str  # python, cpp, java, bash
    code: str
    problem_id: str

class TestQuestion(BaseModel):
    id: str
    type: str  # coding or mcq
    title: str
    description: str
    difficulty: str
    tags: List[str]
    test_cases: Optional[List[Dict[str, str]]] = None
    options: Optional[List[str]] = None  # For MCQs
    correct_answer: Optional[str] = None

class GeneratedTest(BaseModel):
    test_id: str
    title: str
    description: str
    questions: List[TestQuestion]

# Mock database
tests_db: Dict[str, GeneratedTest] = {}
problems_db: List[Dict[str, Any]] = []

@app.get("/")
async def root():
    return {"message": "DSA Learning Platform API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/tests/create", response_model=GeneratedTest)
async def create_test(syllabus: SyllabusInput):
    """
    Create a new DSA practice test based on syllabus.
    Triggers AI agent to generate questions by scraping web resources.
    """
    import uuid
    
    test_id = str(uuid.uuid4())
    
    # Call AI agent service to generate test
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://ai-agent:8003/generate-test",
                json=syllabus.model_dump(),
                timeout=60.0
            )
            if response.status_code == 200:
                questions_data = response.json()["questions"]
            else:
                # Fallback to mock generation
                questions_data = await _mock_generate_questions(syllabus)
        except Exception:
            # Fallback to mock generation
            questions_data = await _mock_generate_questions(syllabus)
    
    test = GeneratedTest(
        test_id=test_id,
        title=f"DSA Practice Test: {', '.join(syllabus.topics[:3])}",
        description=f"Custom test covering {len(syllabus.topics)} topics",
        questions=[TestQuestion(**q) for q in questions_data]
    )
    
    tests_db[test_id] = test
    return test

async def _mock_generate_questions(syllabus: SyllabusInput) -> List[Dict]:
    """Mock question generation for demo purposes"""
    questions = []
    
    # Generate coding questions
    for i in range(syllabus.num_questions):
        questions.append({
            "id": f"q_coding_{i}",
            "type": "coding",
            "title": f"{syllabus.topics[i % len(syllabus.topics)]} Problem {i+1}",
            "description": f"Solve this {syllabus.difficulty} difficulty problem on {syllabus.topics[i % len(syllabus.topics)]}.",
            "difficulty": syllabus.difficulty,
            "tags": syllabus.topics,
            "test_cases": [
                {"input": "1 2 3", "output": "6"},
                {"input": "5 10 15", "output": "30"}
            ]
        })
    
    # Generate MCQs
    for i in range(syllabus.num_mcqs):
        questions.append({
            "id": f"q_mcq_{i}",
            "type": "mcq",
            "title": f"Concept Check: {syllabus.topics[i % len(syllabus.topics)]}",
            "description": f"What is the time complexity of the optimal solution?",
            "difficulty": syllabus.difficulty,
            "tags": syllabus.topics,
            "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "correct_answer": "O(n log n)"
        })
    
    return questions

@app.get("/api/tests/{test_id}", response_model=GeneratedTest)
async def get_test(test_id: str):
    """Get test details by ID"""
    if test_id not in tests_db:
        raise HTTPException(status_code=404, detail="Test not found")
    return tests_db[test_id]

@app.post("/api/tests/{test_id}/submit")
async def submit_test(test_id: str, submissions: List[CodeSubmission]):
    """Submit test solutions for evaluation"""
    if test_id not in tests_db:
        raise HTTPException(status_code=404, detail="Test not found")
    
    results = []
    for submission in submissions:
        # Call code executor service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "http://code-executor:8002/execute",
                    json=submission.model_dump(),
                    timeout=30.0
                )
                result = response.json()
            except Exception as e:
                result = {"status": "error", "error": str(e)}
        
        results.append({
            "problem_id": submission.problem_id,
            **result
        })
    
    return {"test_id": test_id, "results": results}

@app.get("/api/problems")
async def list_problems(
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 50
):
    """List available problems with optional filters"""
    filtered = problems_db
    
    if topic:
        filtered = [p for p in filtered if topic.lower() in [t.lower() for t in p.get("tags", [])]]
    
    if difficulty:
        filtered = [p for p in filtered if p.get("difficulty", "").lower() == difficulty.lower()]
    
    return {"problems": filtered[:limit], "total": len(filtered)}

@app.post("/api/problems/generate")
async def generate_problem(topic: str, difficulty: str = "medium"):
    """Generate a new problem using AI agent"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://ai-agent:8003/generate-problem",
                json={"topic": topic, "difficulty": difficulty},
                timeout=30.0
            )
            problem = response.json()
            problems_db.append(problem)
            return problem
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to generate problem")

@app.post("/api/execute")
async def execute_code(submission: CodeSubmission):
    """Execute code in sandboxed environment"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://code-executor:8002/execute",
                json=submission.model_dump(),
                timeout=30.0
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@app.post("/api/scrape")
async def scrape_resources(topics: List[str]):
    """Scrape web resources for given topics"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://scraper:8001/scrape",
                json={"topics": topics},
                timeout=120.0
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
