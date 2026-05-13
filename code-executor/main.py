"""
Code Executor Service - Secure sandboxed code execution
Supports: Python, C/C++, Java, Bash
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import subprocess
import tempfile
import os
import docker
import uuid
import time

app = FastAPI(
    title="Code Executor API",
    description="Secure sandboxed code execution for multiple languages",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeSubmission(BaseModel):
    language: str  # python, cpp, java, bash
    code: str
    problem_id: str
    test_cases: Optional[List[Dict[str, str]]] = None
    timeout: int = 5  # seconds
    memory_limit: int = 256  # MB

class ExecutionResult(BaseModel):
    status: str  # success, error, timeout, runtime_error
    output: str
    execution_time: float
    memory_used: int
    test_results: Optional[List[Dict]] = None

# Language configurations
LANGUAGE_CONFIG = {
    "python": {
        "extension": ".py",
        "compile_cmd": None,
        "run_cmd": "python3 {file}",
        "docker_image": "python:3.11-slim"
    },
    "cpp": {
        "extension": ".cpp",
        "compile_cmd": "g++ -o {output} {file}",
        "run_cmd": "./{output}",
        "docker_image": "gcc:12"
    },
    "java": {
        "extension": ".java",
        "compile_cmd": "javac {file}",
        "run_cmd": "java {classname}",
        "docker_image": "openjdk:17-slim"
    },
    "bash": {
        "extension": ".sh",
        "compile_cmd": None,
        "run_cmd": "bash {file}",
        "docker_image": "bash:5"
    }
}

@app.get("/")
async def root():
    return {"message": "Code Executor Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/execute", response_model=ExecutionResult)
async def execute_code(submission: CodeSubmission):
    """
    Execute code in a secure Docker container
    """
    if submission.language not in LANGUAGE_CONFIG:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {submission.language}. Supported: {list(LANGUAGE_CONFIG.keys())}"
        )
    
    config = LANGUAGE_CONFIG[submission.language]
    
    try:
        # Execute with Docker isolation
        result = await execute_in_docker(submission, config)
        return result
    except Exception as e:
        return ExecutionResult(
            status="error",
            output=str(e),
            execution_time=0,
            memory_used=0
        )

async def execute_in_docker(submission: CodeSubmission, config: Dict) -> ExecutionResult:
    """Execute code in a Docker container for isolation"""
    client = docker.from_env()
    
    # Create temporary directory for code
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write code to file
        filename = f"code{config['extension']}"
        filepath = os.path.join(tmpdir, filename)
        
        with open(filepath, 'w') as f:
            f.write(submission.code)
        
        # Prepare Docker run command
        volumes = {tmpdir: {'bind': '/workspace', 'mode': 'ro'}}
        working_dir = "/workspace"
        
        # Build compile command if needed
        compile_cmd = None
        if config['compile_cmd']:
            output_name = "program"
            compile_cmd = config['compile_cmd'].format(
                file=filename,
                output=output_name
            )
        
        # Build run command
        classname = os.path.splitext(filename)[0].capitalize()
        run_cmd = config['run_cmd'].format(
            file=filename,
            classname=classname
        )
        
        # Create full command
        if compile_cmd:
            full_command = f"{compile_cmd} && timeout {submission.timeout}s {run_cmd}"
        else:
            full_command = f"timeout {submission.timeout}s {run_cmd}"
        
        start_time = time.time()
        
        try:
            # Run container
            container = client.containers.run(
                config['docker_image'],
                command=['/bin/sh', '-c', full_command],
                volumes=volumes,
                working_dir=working_dir,
                mem_limit=f"{submission.memory_limit}m",
                network_disabled=True,
                remove=True,
                detach=False,
                stdout=True,
                stderr=True
            )
            
            execution_time = time.time() - start_time
            
            # Decode output
            output = container.decode('utf-8') if isinstance(container, bytes) else str(container)
            
            return ExecutionResult(
                status="success",
                output=output.strip(),
                execution_time=execution_time,
                memory_used=0,  # Would need cgroup info for accurate measurement
                test_results=None
            )
            
        except docker.errors.ContainerError as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                status="runtime_error",
                output=e.stderr.decode('utf-8') if e.stderr else str(e),
                execution_time=execution_time,
                memory_used=0
            )
        except Exception as e:
            return ExecutionResult(
                status="error",
                output=str(e),
                execution_time=0,
                memory_used=0
            )

@app.post("/execute/batch")
async def execute_batch(submissions: List[CodeSubmission]):
    """Execute multiple code submissions"""
    results = []
    for submission in submissions:
        result = await execute_code(submission)
        results.append({
            "problem_id": submission.problem_id,
            **result.model_dump()
        })
    
    return {"results": results}

@app.get("/languages")
async def list_languages():
    """List supported programming languages"""
    return {
        "languages": list(LANGUAGE_CONFIG.keys()),
        "details": LANGUAGE_CONFIG
    }

# Fallback execution without Docker (for development)
async def execute_local(submission: CodeSubmission, config: Dict) -> ExecutionResult:
    """Execute code locally without Docker (development only)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = f"code{config['extension']}"
        filepath = os.path.join(tmpdir, filename)
        
        with open(filepath, 'w') as f:
            f.write(submission.code)
        
        start_time = time.time()
        
        try:
            # Compile if needed
            if config['compile_cmd']:
                compile_result = subprocess.run(
                    config['compile_cmd'].format(file=filepath, output="program"),
                    shell=True,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=submission.timeout
                )
                if compile_result.returncode != 0:
                    return ExecutionResult(
                        status="compile_error",
                        output=compile_result.stderr,
                        execution_time=time.time() - start_time,
                        memory_used=0
                    )
            
            # Run the code
            classname = os.path.splitext(filename)[0].capitalize()
            run_cmd = config['run_cmd'].format(file=filepath, classname=classname)
            
            result = subprocess.run(
                run_cmd,
                shell=True,
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=submission.timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                return ExecutionResult(
                    status="success",
                    output=result.stdout,
                    execution_time=execution_time,
                    memory_used=0
                )
            else:
                return ExecutionResult(
                    status="runtime_error",
                    output=result.stderr,
                    execution_time=execution_time,
                    memory_used=0
                )
                
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status="timeout",
                output="Time limit exceeded",
                execution_time=submission.timeout,
                memory_used=0
            )
        except Exception as e:
            return ExecutionResult(
                status="error",
                output=str(e),
                execution_time=0,
                memory_used=0
            )
