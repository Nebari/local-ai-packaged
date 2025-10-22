from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import os

app = FastAPI(title="Simple MCP Memory Server", version="1.0.0")

DATA_DIR = "/app/data"
DATA_FILE = os.path.join(DATA_DIR, "memories.json")
os.makedirs(DATA_DIR, exist_ok=True)

class MCPMessage(BaseModel):
    content: str
    user_id: Optional[str] = "default"

class MCPSearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = "default"
    limit: Optional[int] = 5

def load_memories():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_memories(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.post("/mcp/add_memory")
def add_memory(message: MCPMessage):
    try:
        memories = load_memories()
        
        if message.user_id not in memories:
            memories[message.user_id] = []
        
        memories[message.user_id].append({
            'content': message.content,
            'timestamp': str(len(memories[message.user_id]) + 1)
        })
        
        save_memories(memories)
        
        return {
            "status": "success", 
            "message": "Memory added successfully",
            "user_id": message.user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/search_memory")
def search_memory(request: MCPSearchRequest):
    try:
        memories = load_memories()
        user_memories = memories.get(request.user_id, [])
        
        # Simple text search
        results = []
        for memory in user_memories:
            if request.query.lower() in memory['content'].lower():
                results.append(memory)
        
        return {
            "status": "success",
            "results": results[:request.limit],
            "user_id": request.user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/memories/{user_id}")
def get_memories(user_id: str = "default"):
    try:
        memories = load_memories()
        user_memories = memories.get(user_id, [])
        
        return {
            "status": "success",
            "memories": user_memories,
            "user_id": user_id,
            "count": len(user_memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mcp/memories/{user_id}")
def delete_memories(user_id: str = "default"):
    try:
        memories = load_memories()
        
        if user_id in memories:
            del memories[user_id]
            save_memories(memories)
            message = f"All memories deleted for user {user_id}"
        else:
            message = f"No memories found for user {user_id}"
        
        return {
            "status": "success",
            "message": message,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {
        "message": "Simple MCP Memory Server - Ready for Model Context Protocol",
        "docs": "/docs",
        "endpoints": ["/mcp/add_memory", "/mcp/search_memory", "/mcp/memories/{user_id}"]
    }