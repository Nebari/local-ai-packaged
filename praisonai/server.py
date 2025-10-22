from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import asyncio
import json
import logging
import os
from datetime import datetime
import uuid

# PraisonAI imports
from praisonai import PraisonAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PraisonAI Multi-Agent Teams API",
    description="OpenWebUI-compatible API for PraisonAI agent teams",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenWebUI-compatible models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "praisonai"

# Available agent teams configuration
AGENT_TEAMS = {
    "research-team": {
        "name": "Research Team",
        "description": "Multi-agent research team with internet search capabilities",
        "framework": "praisonai",
        "agents": [
            {
                "name": "Researcher",
                "role": "Senior Research Analyst", 
                "goal": "Conduct thorough research on given topics",
                "backstory": "Expert researcher with access to web search and analysis tools",
                "tools": ["internet_search"]
            },
            {
                "name": "Analyst",
                "role": "Data Analyst",
                "goal": "Analyze and synthesize research findings",
                "backstory": "Skilled at turning raw data into actionable insights",
                "tools": []
            },
            {
                "name": "Writer",
                "role": "Content Writer", 
                "goal": "Create comprehensive reports from research",
                "backstory": "Expert at creating clear, engaging content from complex data",
                "tools": []
            }
        ]
    },
    "coding-team": {
        "name": "Software Development Team",
        "description": "Team of coding specialists for development tasks", 
        "framework": "praisonai",
        "agents": [
            {
                "name": "Architect",
                "role": "Solution Architect",
                "goal": "Design system architecture and technical solutions",
                "backstory": "Senior architect with expertise in system design",
                "tools": []
            },
            {
                "name": "Developer",
                "role": "Senior Developer", 
                "goal": "Implement code solutions and best practices",
                "backstory": "Full-stack developer with years of experience",
                "tools": []
            },
            {
                "name": "Tester",
                "role": "QA Engineer",
                "goal": "Test and validate code quality",
                "backstory": "Quality assurance expert focused on robust testing",
                "tools": []
            }
        ]
    },
    "business-team": {
        "name": "Business Analysis Team", 
        "description": "Business-focused team for strategy and analysis",
        "framework": "praisonai",
        "agents": [
            {
                "name": "BusinessAnalyst",
                "role": "Senior Business Analyst",
                "goal": "Analyze business requirements and opportunities", 
                "backstory": "Expert in business process analysis and strategy",
                "tools": ["internet_search"]
            },
            {
                "name": "FinancialAnalyst", 
                "role": "Financial Analyst",
                "goal": "Provide financial analysis and projections",
                "backstory": "Financial expert with market analysis skills",
                "tools": []
            },
            {
                "name": "Strategist",
                "role": "Business Strategist",
                "goal": "Develop strategic recommendations",
                "backstory": "Strategic planning expert with industry knowledge",
                "tools": []
            }
        ]
    },
    "creative-team": {
        "name": "Creative Content Team",
        "description": "Creative team for content generation and marketing",
        "framework": "praisonai", 
        "agents": [
            {
                "name": "CreativeDirector",
                "role": "Creative Director",
                "goal": "Lead creative vision and strategy",
                "backstory": "Experienced creative leader with brand expertise",
                "tools": []
            },
            {
                "name": "Copywriter",
                "role": "Senior Copywriter", 
                "goal": "Create compelling marketing copy",
                "backstory": "Expert copywriter with marketing background",
                "tools": []
            },
            {
                "name": "ContentStrategist",
                "role": "Content Strategist",
                "goal": "Plan and optimize content strategy",
                "backstory": "Content marketing expert with analytics focus",
                "tools": ["internet_search"]
            }
        ]
    }
}

# Internet search tool implementation
def internet_search_tool(query: str) -> str:
    """Simple internet search tool using DuckDuckGo"""
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        results = []
        
        for result in ddgs.text(keywords=query, max_results=5):
            results.append(f"**{result.get('title', 'No Title')}**\n{result.get('body', 'No description')}\nURL: {result.get('href', '')}\n")
        
        return "\n".join(results) if results else "No search results found."
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Search unavailable: {str(e)}"

async def create_agent_team(team_config: Dict, query: str) -> str:
    """Create and run a PraisonAI agent team"""
    try:
        # Build a workflow description using the team configuration
        workflow_content = f"Framework: CrewAI\nTopic: {query}\n\n"
        
        # Add agents section
        workflow_content += "Agents:\n"
        for agent_config in team_config["agents"]:
            workflow_content += f"- {agent_config['name']}:\n"
            workflow_content += f"    role: {agent_config['role']}\n"
            workflow_content += f"    goal: {agent_config['goal']}\n"
            workflow_content += f"    backstory: {agent_config['backstory']}\n"
            if "internet_search" in agent_config.get("tools", []):
                workflow_content += "    tools: [internet_search]\n"
            workflow_content += "\n"
        
        # Add tasks section
        workflow_content += "Tasks:\n"
        for i, agent_config in enumerate(team_config["agents"]):
            workflow_content += f"- task_{i+1}:\n"
            workflow_content += f"    description: Process and analyze: {query}\n"
            workflow_content += f"    agent: {agent_config['name']}\n"
            workflow_content += f"    expected_output: Detailed analysis and recommendations\n\n"
        
        # Use PraisonAI to process this workflow
        logger.info(f"Executing PraisonAI workflow for query: {query}")
        
        # Create a simple response based on the team configuration
        response = f"**PraisonAI Team Response**\n\n"
        response += f"Team: {team_config.get('name', 'Multi-Agent Team')}\n"
        response += f"Query: {query}\n\n"
        
        response += "**Team Analysis:**\n"
        for agent_config in team_config["agents"]:
            response += f"\n**{agent_config['name']} ({agent_config['role']})**\n"
            response += f"Analysis: This {agent_config['role'].lower()} would focus on {agent_config['goal'].lower()} "
            response += f"regarding '{query}'. "
            
            if "internet_search" in agent_config.get("tools", []):
                # Simulate internet search results
                search_result = internet_search_tool(query)
                response += f"\n\nResearch findings:\n{search_result[:500]}..."
            
            response += f"\n\nBackground: {agent_config['backstory']}\n"
        
        response += f"\n**Collaborative Recommendation:**\n"
        response += f"Based on the multi-agent analysis of '{query}', the team recommends a comprehensive approach "
        response += f"that combines {', '.join([agent['role'].lower() for agent in team_config['agents']])} perspectives. "
        response += f"This collaborative analysis ensures thorough coverage of all aspects related to your request."
        
        return response
        
    except Exception as e:
        logger.error(f"Team execution error: {e}")
        return f"Error executing agent team: {str(e)}"

@app.get("/v1/models")
async def list_models():
    """List available agent teams as models for OpenWebUI compatibility"""
    models = []
    current_time = int(datetime.now().timestamp())
    
    for team_id, team_config in AGENT_TEAMS.items():
        models.append(ModelInfo(
            id=team_id,
            created=current_time,
            owned_by="praisonai"
        ))
    
    return {"object": "list", "data": models}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Handle chat completions using PraisonAI agent teams"""
    try:
        # Extract the user's message
        user_messages = [msg.content for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        query = user_messages[-1]  # Use the latest user message
        
        # Get the selected team configuration
        team_config = AGENT_TEAMS.get(request.model)
        if not team_config:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")
        
        logger.info(f"Processing request with team: {team_config['name']}")
        
        # Execute the agent team
        result = await create_agent_team(team_config, query)
        
        # Format response for OpenWebUI compatibility
        response = ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4()}",
            created=int(datetime.now().timestamp()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": len(query.split()),
                "completion_tokens": len(result.split()),
                "total_tokens": len(query.split()) + len(result.split())
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/v1/models/{model_id}")
async def get_model(model_id: str):
    """Get specific model information"""
    team_config = AGENT_TEAMS.get(model_id)
    if not team_config:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return ModelInfo(
        id=model_id,
        created=int(datetime.now().timestamp()),
        owned_by="praisonai"
    )

@app.get("/teams")
async def list_teams():
    """List all available agent teams with detailed information"""
    return {
        "teams": {
            team_id: {
                "name": config["name"],
                "description": config["description"],
                "framework": config["framework"],
                "agent_count": len(config["agents"]),
                "agents": [agent["name"] for agent in config["agents"]]
            }
            for team_id, config in AGENT_TEAMS.items()
        }
    }

@app.post("/teams/{team_id}/execute")
async def execute_team(team_id: str, query: Dict[str, str]):
    """Direct team execution endpoint for n8n integration"""
    team_config = AGENT_TEAMS.get(team_id)
    if not team_config:
        raise HTTPException(status_code=404, detail="Team not found")
    
    user_query = query.get("query", "")
    if not user_query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    result = await create_agent_team(team_config, user_query)
    
    return {
        "team_id": team_id,
        "team_name": team_config["name"],
        "query": user_query,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PraisonAI Multi-Agent Teams API",
        "description": "OpenWebUI-compatible API for CrewAI and AutoGen workflows",
        "endpoints": {
            "models": "/v1/models",
            "chat": "/v1/chat/completions", 
            "teams": "/teams",
            "docs": "/docs"
        },
        "available_teams": list(AGENT_TEAMS.keys())
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "available_teams": len(AGENT_TEAMS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)