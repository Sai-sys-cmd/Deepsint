from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import subprocess
import json
import os
from pathlib import Path

app = FastAPI(title="OSINT API", description="API for OSINT data collection using Blackbird")

# Configure CORS to allow requests from localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRequest(BaseModel):
    username: str
    email: Optional[str] = None
    name: Optional[str] = None

class BlackbirdResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    output_file: Optional[str] = None

@app.post("/api/search", response_model=BlackbirdResponse)
async def search_user(request: UserRequest):
    """
    Search for user information using Blackbird tool
    """
    try:
        # Ensure tmp directory exists
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)
        
        # Ensure data directory exists for Blackbird
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Construct the Blackbird command
        blackbird_dir = os.path.expanduser("~/dev/tools/blackbird")
        blackbird_path = os.path.join(blackbird_dir, "blackbird.py")
        
        cmd = [
            "python", 
            "blackbird.py",  # Use relative path since we're in the blackbird directory
            "-u", request.username,
            "--json",
            "--no-update"
        ]
        
        print(f"Executing command: {' '.join(cmd)}")
        print(f"Working directory: {blackbird_dir}")
        print(f"Blackbird path exists: {os.path.exists(blackbird_path)}")
        
        # Create output file path in our backend tmp directory
        backend_dir = os.getcwd()
        output_file = tmp_dir / f"{request.username}_blackbird_results.json"
        
        # Execute Blackbird command and redirect output to file
        with open(output_file, 'w') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=blackbird_dir  # Run from Blackbird's directory
            )
        
        print(f"Command exit code: {result.returncode}")
        print(f"Command stderr: {result.stderr}")
        print(f"Output file created: {output_file.exists()}")
        if output_file.exists():
            print(f"Output file size: {output_file.stat().st_size} bytes")
        
        if result.returncode != 0:
            return BlackbirdResponse(
                success=False,
                message=f"Blackbird execution failed: {result.stderr}",
                data=None
            )
        
        # Try to read the output file
        response_data = None
        
        if output_file.exists() and output_file.stat().st_size > 0:
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    response_data = json.load(f)
                print("Successfully parsed JSON output")
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw output
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        response_data = {"raw_output": f.read()}
                    print("JSON parsing failed, returning raw output")
                except Exception as e:
                    print(f"Error reading output file: {e}")
                    response_data = {"error": "Could not read output file"}
        else:
            print("Output file does not exist or is empty")
        
        return BlackbirdResponse(
            success=True,
            message="Search completed successfully",
            data=response_data,
            output_file=str(output_file) if output_file.exists() else None
        )
        
    except subprocess.TimeoutExpired:
        return BlackbirdResponse(
            success=False,
            message="Search timed out after 5 minutes",
            data=None
        )
    except Exception as e:
        return BlackbirdResponse(
            success=False,
            message=f"An error occurred: {str(e)}",
            data=None
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "OSINT API is running"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "OSINT API",
        "version": "1.0.0",
        "endpoints": {
            "/api/search": "POST - Search for user information",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)