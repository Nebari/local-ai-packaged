from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import uuid
from datetime import datetime

app = FastAPI(title='Simple Mem0 API', version='1.0.0')

DATA_DIR = '/app/data'
os.makedirs(DATA_DIR, exist_ok=True)

class Message(BaseModel):
    role: str
    content: str

class MemoryCreate(BaseModel):
    messages: List[Message]
    user_id: Optional[str] = 'default'
    agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class SearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = 'default'
    limit: Optional[int] = 10

def load_memories(user_id: str):
    file_path = os.path.join(DATA_DIR, f'{user_id}_memories.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def save_memories(user_id: str, memories: list):
    file_path = os.path.join(DATA_DIR, f'{user_id}_memories.json')
    with open(file_path, 'w') as f:
        json.dump(memories, f, indent=2)

@app.post('/memories/')
def create_memory(mem: MemoryCreate):
    try:
        memories = load_memories(mem.user_id)
        
        # Extract content from messages
        content = ' '.join([msg.content for msg in mem.messages])
        
        # Create memory entry
        memory_entry = {
            'id': str(uuid.uuid4()),
            'content': content,
            'messages': [msg.dict() for msg in mem.messages],
            'user_id': mem.user_id,
            'agent_id': mem.agent_id,
            'metadata': mem.metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        memories.append(memory_entry)
        save_memories(mem.user_id, memories)
        
        return {'status': 'success', 'results': [memory_entry]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/memories/')
def get_memories(user_id: str = 'default'):
    try:
        memories = load_memories(user_id)
        return {'status': 'success', 'results': memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/memories/search')
def search_memories(request: SearchRequest):
    try:
        memories = load_memories(request.user_id)
        
        # Simple text search
        results = []
        for memory in memories:
            if request.query.lower() in memory['content'].lower():
                results.append(memory)
                
        return {'status': 'success', 'results': results[:request.limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete('/memories/')
def delete_memories(user_id: str = 'default'):
    try:
        file_path = os.path.join(DATA_DIR, f'{user_id}_memories.json')
        if os.path.exists(file_path):
            os.remove(file_path)
        return {'status': 'success', 'message': 'Memories deleted'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/')
def home():
    return {
        'message': 'Simple Mem0 REST API', 
        'docs': '/docs',
        'endpoints': ['/memories/', '/memories/search']
    }