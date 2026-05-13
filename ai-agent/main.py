"""
AI Agent Service - LLM-powered test and problem generation
Orchestrates content creation using scraped data
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import httpx
import os

app = FastAPI(
    title="AI Agent API",
    description="LLM-powered DSA test and problem generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SyllabusInput(BaseModel):
    topics: List[str]
    difficulty: str = "medium"
    num_questions: int = 10
    num_mcqs: int = 5

class ProblemGenerationRequest(BaseModel):
    topic: str
    difficulty: str = "medium"

class GeneratedQuestion(BaseModel):
    id: str
    type: str  # coding or mcq
    title: str
    description: str
    difficulty: str
    tags: List[str]
    test_cases: Optional[List[Dict[str, str]]] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

class GeneratedTest(BaseModel):
    test_id: str
    title: str
    description: str
    questions: List[GeneratedQuestion]

# LLM configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai or anthropic
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

@app.get("/")
async def root():
    return {"message": "AI Agent Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/generate-test", response_model=GeneratedTest)
async def generate_test(syllabus: SyllabusInput):
    """
    Generate a complete DSA practice test based on syllabus
    Uses LLM to create questions from scraped educational content
    """
    import uuid
    
    # First, scrape relevant content
    async with httpx.AsyncClient() as client:
        try:
            scrape_response = await client.post(
                "http://scraper:8001/scrape",
                json={"topics": syllabus.topics},
                timeout=60.0
            )
            scraped_content = scrape_response.json()
        except Exception:
            scraped_content = []
    
    # Generate questions using LLM
    questions = await llm_generate_questions(syllabus, scraped_content)
    
    test = GeneratedTest(
        test_id=str(uuid.uuid4()),
        title=f"DSA Practice Test: {', '.join(syllabus.topics[:3])}",
        description=f"Custom test covering {len(syllabus.topics)} topics",
        questions=questions
    )
    
    return test

@app.post("/generate-problem")
async def generate_problem(request: ProblemGenerationRequest):
    """Generate a single DSA problem"""
    # Scrape content for the topic
    async with httpx.AsyncClient() as client:
        try:
            scrape_response = await client.post(
                "http://scraper:8001/scrape",
                json={"topics": [request.topic]},
                timeout=30.0
            )
            scraped_content = scrape_response.json()
        except Exception:
            scraped_content = []
    
    # Generate problem using LLM
    question = await llm_generate_single_problem(request.topic, request.difficulty, scraped_content)
    
    return question

@app.post("/generate-mcq")
async def generate_mcq(topic: str, difficulty: str = "medium"):
    """Generate an MCQ question"""
    question = await llm_generate_mcq(topic, difficulty)
    return question

async def llm_generate_questions(syllabus: SyllabusInput, scraped_content: List) -> List[GeneratedQuestion]:
    """Generate questions using LLM (mock implementation)"""
    questions = []
    
    # In production, this would call OpenAI/Anthropic API
    # For now, we'll generate mock questions
    
    # Generate coding questions
    for i in range(syllabus.num_questions):
        topic = syllabus.topics[i % len(syllabus.topics)]
        questions.append(GeneratedQuestion(
            id=f"q_coding_{i}",
            type="coding",
            title=f"{topic} Challenge #{i+1}",
            description=f"""
Given an input array, implement an efficient solution using {topic}.

**Problem Statement:**
You are given an array of integers. Your task is to implement a {topic}-based algorithm to solve the following:

**Input Format:**
- First line contains n (size of array)
- Second line contains n space-separated integers

**Output Format:**
- Print the result on a single line

**Constraints:**
- 1 ≤ n ≤ 10^5
- Array elements fit in standard integer types

**Example:**
Input:
5
1 2 3 4 5

Output:
[result based on {topic}]
""",
            difficulty=syllabus.difficulty,
            tags=[topic],
            test_cases=[
                {"input": "5\n1 2 3 4 5", "output": "15"},
                {"input": "3\n10 20 30", "output": "60"},
                {"input": "1\n42", "output": "42"}
            ],
            explanation=f"This problem tests your understanding of {topic} concepts."
        ))
    
    # Generate MCQs
    for i in range(syllabus.num_mcqs):
        topic = syllabus.topics[i % len(syllabus.topics)]
        questions.append(GeneratedQuestion(
            id=f"q_mcq_{i}",
            type="mcq",
            title=f"Concept Check: {topic}",
            description=f"What is the average time complexity of the optimal {topic} algorithm?",
            difficulty=syllabus.difficulty,
            tags=[topic],
            options=["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n²)"],
            correct_answer="O(n log n)",
            explanation=f"The optimal {topic} algorithm has O(n log n) average time complexity."
        ))
    
    return questions

async def llm_generate_single_problem(topic: str, difficulty: str, scraped_content: List) -> Dict:
    """Generate a single problem using LLM"""
    # Mock implementation
    return {
        "id": f"problem_{topic.lower().replace(' ', '_')}",
        "type": "coding",
        "title": f"{topic} Problem",
        "description": f"Solve this {difficulty} difficulty problem on {topic}.",
        "difficulty": difficulty,
        "tags": [topic],
        "test_cases": [
            {"input": "test input 1", "output": "expected output 1"}
        ]
    }

async def llm_generate_mcq(topic: str, difficulty: str) -> Dict:
    """Generate an MCQ using LLM"""
    return {
        "id": f"mcq_{topic.lower().replace(' ', '_')}",
        "type": "mcq",
        "title": f"{topic} Concept Question",
        "description": f"Select the correct statement about {topic}.",
        "difficulty": difficulty,
        "tags": [topic],
        "options": [
            "Option A: Incorrect statement",
            "Option B: Correct statement",
            "Option C: Partially correct",
            "Option D: Completely wrong"
        ],
        "correct_answer": "Option B: Correct statement",
        "explanation": f"Detailed explanation about {topic}."
    }

async def call_openai(prompt: str) -> str:
    """Call OpenAI API for text generation"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4-turbo-preview",
                "messages": [
                    {"role": "system", "content": "You are an expert DSA instructor and problem setter."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

async def call_anthropic(prompt: str) -> str:
    """Call Anthropic API for text generation"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 2000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]

# Background worker for async task processing
@app.on_event("startup")
async def startup_event():
    """Initialize background worker"""
    print("AI Agent service started")
