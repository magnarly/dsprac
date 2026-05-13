"""
AI Agent Worker - Background task processor
Processes test generation requests asynchronously
"""
import asyncio
import redis
import json
import os
import httpx

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def get_redis_client():
    return redis.from_url(REDIS_URL)

async def process_test_generation(task_data: dict):
    """Process a test generation task"""
    topics = task_data.get("topics", [])
    difficulty = task_data.get("difficulty", "medium")
    num_questions = task_data.get("num_questions", 10)
    num_mcqs = task_data.get("num_mcqs", 5)
    
    # Call AI agent API to generate test
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8003/generate-test",
                json={
                    "topics": topics,
                    "difficulty": difficulty,
                    "num_questions": num_questions,
                    "num_mcqs": num_mcqs
                },
                timeout=120.0
            )
            
            if response.status_code == 200:
                result = response.json()
                # Store result in Redis
                r = get_redis_client()
                r.setex(f"test:{result['test_id']}", 3600, json.dumps(result))
                return result
            else:
                return {"error": f"Generation failed: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}

async def process_problem_generation(task_data: dict):
    """Process a single problem generation task"""
    topic = task_data.get("topic")
    difficulty = task_data.get("difficulty", "medium")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8003/generate-problem",
                json={"topic": topic, "difficulty": difficulty},
                timeout=60.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Generation failed: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}

async def worker_loop():
    """Main worker loop - processes tasks from Redis queue"""
    print("AI Agent Worker started...")
    r = get_redis_client()
    
    while True:
        try:
            # Get task from queue
            task = r.blpop("task_queue", timeout=5)
            
            if task:
                _, task_json = task
                task_data = json.loads(task_json)
                
                task_type = task_data.get("type")
                
                if task_type == "generate_test":
                    result = await process_test_generation(task_data)
                elif task_type == "generate_problem":
                    result = await process_problem_generation(task_data)
                else:
                    result = {"error": f"Unknown task type: {task_type}"}
                
                # Store result
                task_id = task_data.get("id")
                if task_id:
                    r.setex(f"task_result:{task_id}", 3600, json.dumps(result))
                    
        except Exception as e:
            print(f"Worker error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(worker_loop())
