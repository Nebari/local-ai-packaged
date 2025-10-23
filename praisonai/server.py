from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, AsyncGenerator
import asyncio
import json
import logging
import os
from datetime import datetime
import uuid
import requests

# PraisonAI imports
from praisonai import PraisonAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Keiken Multi-Agent Teams API",
    description="OpenWebUI-compatible API for Keiken intelligent agent teams - Powered by Nebari Software",
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
    "Research": {
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
    "CreativeStudio": {
        "name": "Creative Studio", 
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
    },
    "SalesOps": {
        "name": "Sales Operations",
        "description": "Sales operations team for proposals, renewals, and strategic sales support",
        "framework": "praisonai",
        "agents": [
            {
                "name": "SalesRouter",
                "role": "Sales Operations Router",
                "goal": "Route sales scenarios to appropriate specialists",
                "backstory": "Expert at analyzing sales scenarios and directing to the right team member",
                "tools": []
            },
            {
                "name": "NewBusinessSpecialist", 
                "role": "New Business Specialist",
                "goal": "Handle new business development and upsell opportunities",
                "backstory": "Experienced in crafting compelling proposals and identifying growth opportunities",
                "tools": ["internet_search"]
            },
            {
                "name": "RenewalSpecialist",
                "role": "Renewal and Retention Specialist", 
                "goal": "Manage renewals and customer retention strategies",
                "backstory": "Expert at customer relationship management and renewal optimization",
                "tools": []
            }
        ]
    }
}

# Team-specific workflow instructions
def get_team_specific_instructions(team_name: str) -> str:
    """Get team-specific workflow instructions based on the plan"""
    instructions = {
        "Research": """
You are a Research Team Agent whose job is to efficiently gather, analyse and summarise high-impact insights for business decisions.
Begin by breaking down the user's query into separate research sub-tasks, then execute those tasks in parallel (e.g., data gathering, competitor benchmarking, trend identification).
For each sub-task produce a short reasoning trace that shows your thought process.
Then aggregate the results into a concise, actionable summary, emphasising what a generic zero-shot model would miss (for example: source gaps, contradictory evidence, recommendation risks).
        """,
        "CreativeStudio": """
You are a Creative Studio Agent operating in a structured chain of work.
Step 1: Ideation – generate at least 5 distinct creative directions based on the user query.
Step 2: Drafting – select the most promising direction and build a detailed draft.
Step 3: Review and polish – refine the draft for clarity, style, and brand consistency.
        """,
        "SalesOps": """
You are a Sales Operations Agent tasked with routing the user's scenario to the appropriate sub-team and then producing the output.
First: analyse the user's query to decide whether it fits "New Business / Upsell" or "Renewal / Retention".
Then hand off to the chosen sub-team workflow and generate the final deliverable (proposal, strategy, etc.).
        """
    }
    return instructions.get(team_name, "Follow standard workflow procedures for your team.")

# Internet search tool implementation
def internet_search_tool(query: str) -> str:
    """Internet search tool using SearxNG service"""
    try:
        # Use SearxNG service for web search
        response = requests.get(
            "http://searxng:8080/search",
            params={"q": query, "format": "json", "categories": "general"},
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"SearxNG returned status {response.status_code}")
            return f"Search service error: HTTP {response.status_code}"
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return "No search results found."
        
        # Format top 5 results
        formatted_results = []
        for result in results[:5]:
            title = result.get('title', 'No Title')
            content = result.get('content', 'No description')
            url = result.get('url', '')
            formatted_results.append(f"**{title}**\n{content}\nURL: {url}\n")
        
        return "\n".join(formatted_results)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"SearxNG connection error: {e}")
        return f"Search service unavailable: {str(e)}"
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Search failed: {str(e)}"

async def create_agent_team(team_name: str, team_config: Dict, messages: List[ChatMessage], stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
    """Create and run a PraisonAI agent team with real AI responses and conversation context"""
    try:
        import requests
        
        # Use Ollama for actual AI responses
        ollama_url = "http://ollama:11434/api/generate"
        
        # Build conversation context from message history
        conversation_context = ""
        current_query = ""
        
        for msg in messages:
            if msg.role == "user":
                current_query = msg.content
                conversation_context += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                conversation_context += f"Assistant: {msg.content}\n"
        
        logger.info(f"Executing PraisonAI workflow for query: {current_query}")
        
        if stream:
            return create_streaming_response(team_config, conversation_context, current_query)
        
        # Remove complex response headers that were causing HTML display issues
        
        # Use only the primary agent (first in the team) to avoid duplicate responses
        primary_agent = team_config["agents"][0]
        agent_name = primary_agent['name']
        agent_role = primary_agent['role']
        agent_goal = primary_agent['goal']
        agent_backstory = primary_agent['backstory']
        
        # Create team-specific prompt with conversation context and thinking tags
        team_specific_instructions = get_team_specific_instructions(team_name)
        
        agent_prompt = f"""You are {agent_name}, a {agent_role} representing the {team_config['name']}.
        
Your goal: {agent_goal}
Your background: {agent_backstory}

TEAM WORKFLOW INSTRUCTIONS:
{team_specific_instructions}

You are working with a team of experts including other specialists, but you should provide a comprehensive response that represents the collective expertise of the entire team following your team's specific workflow.

Conversation history:
{conversation_context}

Current question: {current_query}

IMPORTANT: Structure your response with your reasoning process wrapped in <thinking> tags, followed by your final answer:

<thinking>
[Your analysis process here - follow your team's workflow instructions, break down the question, consider different perspectives from your team expertise, evaluate options, research findings if applicable]
</thinking>

[Your final comprehensive response here]

Please provide a detailed, professional response to the current question, taking into account the conversation history. Show your reasoning process in the thinking section, then provide a clear final answer following your team's specific workflow approach."""

        # Get search results if agent has internet search tool
        search_context = ""
        if "internet_search" in primary_agent.get("tools", []):
            search_results = internet_search_tool(current_query)
            search_context = f"\n\nAvailable research data:\n{search_results[:1000]}\n\nUse this research to inform your response."
            agent_prompt += search_context

        try:
            # Get AI response from Ollama
            ollama_response = requests.post(ollama_url, json={
                "model": "llama3.1:8b",
                "prompt": agent_prompt,
                "stream": False
            }, timeout=30)
            
            if ollama_response.status_code == 200:
                ai_response = ollama_response.json().get('response', 'No response generated')
                # Clean the response to remove any internal formatting
                import re
                ai_response = re.sub(r'<[^>]+>', '', ai_response)  # Remove HTML tags
                ai_response = re.sub(r'\*\*.*?\*\*:', '', ai_response)  # Remove bold headers like "**Research Team Response:**"
                ai_response = ai_response.strip()
            else:
                ai_response = f"AI model unavailable. Using fallback analysis for {agent_role}."
                
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            ai_response = f"As a {agent_role}, I would focus on {agent_goal.lower()} regarding '{current_query}'. However, the AI model is currently unavailable for detailed analysis."
        
        # Return clean response without multiple agent headers
        response = ai_response
        
        return response
        
    except Exception as e:
        logger.error(f"Team execution error: {e}")
        return f"Error executing agent team: {str(e)}"

async def create_streaming_response(team_config: Dict, conversation_context: str, current_query: str) -> AsyncGenerator[str, None]:
    """Create streaming response for agent team execution"""
    try:
        ollama_url = "http://ollama:11434/api/generate"
        
        # Skip complex initial headers to avoid HTML formatting issues
        
        # Use only the primary agent for streaming to avoid duplicates
        primary_agent = team_config["agents"][0]
        agent_name = primary_agent['name']
        agent_role = primary_agent['role']
        agent_goal = primary_agent['goal']
        agent_backstory = primary_agent['backstory']
        
        # Create agent-specific prompt with conversation context and thinking tags
        agent_prompt = f"""You are {agent_name}, a {agent_role} representing the {team_config['name']}.
        
Your goal: {agent_goal}
Your background: {agent_backstory}

You are working with a team of experts, but you should provide a comprehensive response that represents the collective expertise of the entire team.

Conversation history:
{conversation_context}

Current question: {current_query}

IMPORTANT: Structure your response with your reasoning process wrapped in <thinking> tags, followed by your final answer:

<thinking>
[Your analysis process here - break down the question, consider different perspectives from your team expertise, evaluate options, research findings if applicable]
</thinking>

[Your final comprehensive response here]

Please provide a detailed, professional response to the current question, taking into account the conversation history. Show your reasoning process in the thinking section, then provide a clear final answer."""

        # Get search results if agent has internet search tool
        if "internet_search" in primary_agent.get("tools", []):
            search_results = internet_search_tool(current_query)
            agent_prompt += f"\n\nAvailable research data:\n{search_results[:1000]}\n\nUse this research to inform your response."

        try:
            # Stream AI response from Ollama
            ollama_stream_response = requests.post(ollama_url, json={
                "model": "llama3.1:8b",
                "prompt": agent_prompt,
                "stream": True
            }, timeout=60, stream=True)
            
            if ollama_stream_response.status_code == 200:
                for line in ollama_stream_response.iter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line.decode('utf-8'))
                            if 'response' in chunk_data:
                                # Clean the response content
                                content = chunk_data['response']
                                # Remove any HTML tags or formatting markers
                                import re
                                content = re.sub(r'<[^>]+>', '', content)
                                content = re.sub(r'\*\*.*?\*\*:', '', content)
                                
                                content_chunk = {
                                    "id": f"chatcmpl-{uuid.uuid4()}",
                                    "object": "chat.completion.chunk",
                                    "created": int(datetime.now().timestamp()),
                                    "model": "multi-agent-team",
                                    "choices": [{
                                        "index": 0,
                                        "delta": {
                                            "content": content
                                        },
                                        "finish_reason": None
                                    }]
                                }
                                yield f"data: {json.dumps(content_chunk)}\n\n"
                                
                            if chunk_data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                error_chunk = {
                    "id": f"chatcmpl-{uuid.uuid4()}",
                    "object": "chat.completion.chunk",
                    "created": int(datetime.now().timestamp()),
                    "model": "multi-agent-team",
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "content": f"AI model unavailable for {agent_role}.\n"
                        },
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
                
        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            error_chunk = {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion.chunk",
                "created": int(datetime.now().timestamp()),
                "model": "multi-agent-team",
                "choices": [{
                    "index": 0,
                    "delta": {
                        "content": f"Error getting response from {agent_role}: {str(e)}\n"
                    },
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
        
        # Send final chunk
        final_chunk = {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion.chunk",
            "created": int(datetime.now().timestamp()),
            "model": "multi-agent-team",
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        error_chunk = {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion.chunk",
            "created": int(datetime.now().timestamp()),
            "model": "multi-agent-team",
            "choices": [{
                "index": 0,
                "delta": {
                    "content": f"Error in streaming response: {str(e)}"
                },
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"
        yield "data: [DONE]\n\n"

@app.get("/v1/models")
async def list_models():
    """List available agent teams as models for OpenWebUI compatibility"""
    models = []
    current_time = int(datetime.now().timestamp())
    
    for team_id, team_config in AGENT_TEAMS.items():
        models.append(ModelInfo(
            id=team_id,
            created=current_time,
            owned_by="keiken-nebari-software"
        ))
    
    return {"object": "list", "data": models}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Handle chat completions using PraisonAI agent teams with conversation context and streaming support"""
    try:
        # Validate messages
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Get the selected team configuration
        team_config = AGENT_TEAMS.get(request.model)
        if not team_config:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")
        
        logger.info(f"Processing request with team: {team_config['name']}, streaming: {request.stream}")
        
        # Execute the agent team with full conversation context
        if request.stream:
            # Return streaming response
            async def stream_generator():
                async for chunk in await create_agent_team(request.model, team_config, request.messages, stream=True):
                    yield chunk
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        else:
            # Non-streaming response
            result = await create_agent_team(request.model, team_config, request.messages, stream=False)
            
            # Calculate token usage based on full conversation
            full_conversation = " ".join([msg.content for msg in request.messages])
            prompt_tokens = len(full_conversation.split())
            completion_tokens = len(str(result).split())
            
            # Format response for OpenWebUI compatibility
            response = ChatCompletionResponse(
                id=f"chatcmpl-{uuid.uuid4()}",
                created=int(datetime.now().timestamp()),
                model=request.model,
                choices=[{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": str(result)
                    },
                    "finish_reason": "stop"
                }],
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
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
        owned_by="keiken-nebari-software"
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
async def execute_team(team_id: str, request_data: Dict[str, Any]):
    """Direct team execution endpoint for n8n integration with conversation context support"""
    team_config = AGENT_TEAMS.get(team_id)
    if not team_config:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Support both simple query and conversation format
    if "query" in request_data:
        # Simple query format (backward compatibility)
        user_query = request_data.get("query", "")
        if not user_query:
            raise HTTPException(status_code=400, detail="Query is required")
        messages = [ChatMessage(role="user", content=user_query)]
    elif "messages" in request_data:
        # Conversation format
        messages = [ChatMessage(**msg) for msg in request_data["messages"]]
        if not messages:
            raise HTTPException(status_code=400, detail="Messages are required")
        user_query = messages[-1].content
    else:
        raise HTTPException(status_code=400, detail="Either 'query' or 'messages' is required")
    
    stream = request_data.get("stream", False)
    
    if stream:
        # Return streaming response for n8n
        async def stream_generator():
            full_response = ""
            async for chunk in await create_agent_team(team_id, team_config, messages, stream=True):
                if chunk.startswith("data: ") and not chunk.startswith("data: [DONE]"):
                    try:
                        chunk_data = json.loads(chunk[6:])  # Remove "data: " prefix
                        if chunk_data.get("choices") and chunk_data["choices"][0].get("delta", {}).get("content"):
                            content = chunk_data["choices"][0]["delta"]["content"]
                            full_response += content
                            yield json.dumps({"partial_result": content, "full_result": full_response}) + "\n"
                    except json.JSONDecodeError:
                        continue
        
        return StreamingResponse(
            stream_generator(),
            media_type="application/x-ndjson",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    else:
        # Non-streaming response
        result = await create_agent_team(team_id, team_config, messages, stream=False)
        
        return {
            "team_id": team_id,
            "team_name": team_config["name"],
            "query": user_query,
            "result": str(result),
            "conversation_length": len(messages),
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