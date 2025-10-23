import chainlit as cl
import os
import asyncio
import requests
import json
from typing import Dict, Any

# Keiken branding configuration
KEIKEN_ORANGE = "#FF7A00"

@cl.on_chat_start
async def start():
    """Initialize the Keiken UI interface"""
    
    # Set custom branding
    await cl.Message(
        content="""# 🏢 Keiken Multi-Agent UI
        
**Powered by Nebari Software**

Welcome to Keiken's advanced multi-agent orchestration platform. This interface allows you to:

- **Auto Mode**: Automatically generate and deploy agent teams for your tasks
- **Manual Mode**: Customize agent configurations and workflows  
- **Agent Orchestration**: Coordinate multiple AI agents working together
- **Workflow Management**: Design complex multi-step processes

Select a mode below to get started:""",
        author="Keiken System"
    ).send()
    
    # Create action buttons for mode selection
    actions = [
        cl.Action(name="auto_mode", value="auto", label="🤖 Auto Mode", description="Automatically generate agents"),
        cl.Action(name="manual_mode", value="manual", label="⚙️ Manual Mode", description="Customize agent setup"),
        cl.Action(name="settings", value="settings", label="🛠️ Settings", description="Configure preferences")
    ]
    
    await cl.Message(
        content="Choose your preferred mode:",
        actions=actions,
        author="Keiken System"
    ).send()
    
    # Initialize session state
    cl.user_session.set("mode", None)
    cl.user_session.set("agents", [])
    cl.user_session.set("current_task", None)

@cl.action_callback("auto_mode")
async def on_auto_mode(action):
    """Handle auto mode selection"""
    cl.user_session.set("mode", "auto")
    
    await cl.Message(
        content="""## 🤖 Auto Mode Selected

In Auto Mode, Keiken will:
1. Analyze your task description
2. Automatically generate appropriate agent teams
3. Configure tools and workflows
4. Execute the multi-agent process

**Please describe your task:**""",
        author="Keiken Auto Mode"
    ).send()

@cl.action_callback("manual_mode") 
async def on_manual_mode(action):
    """Handle manual mode selection"""
    cl.user_session.set("mode", "manual")
    
    await cl.Message(
        content="""## ⚙️ Manual Mode Selected

In Manual Mode, you have full control over:
- Agent roles and capabilities
- Tool configurations  
- Workflow design
- Inter-agent communication

**Available Agent Teams:**
- 🔍 Research Team (Data gathering & analysis)
- 🎨 Creative Studio (Content creation & design)
- 💼 Sales Operations (Proposals & strategies)

Which team would you like to customize?""",
        author="Keiken Manual Mode"
    ).send()
    
    # Create team selection actions
    team_actions = [
        cl.Action(name="select_research", value="Research", label="🔍 Research Team"),
        cl.Action(name="select_creative", value="CreativeStudio", label="🎨 Creative Studio"),
        cl.Action(name="select_sales", value="SalesOps", label="💼 Sales Operations")
    ]
    
    await cl.Message(
        content="Select a team to customize:",
        actions=team_actions,
        author="Keiken Manual Mode"
    ).send()

@cl.action_callback("settings")
async def on_settings(action):
    """Handle settings configuration"""
    await cl.Message(
        content="""## 🛠️ Keiken Settings

**Current Configuration:**
- Platform: Keiken Multi-Agent Platform
- Version: 1.0.0
- Provider: Nebari Software
- Backend: http://keiken-teams-api:8000

**Available Models:**
- Local Ollama models via backend
- Research Team with internet search
- Creative Studio with workflow automation  
- Sales Operations with routing logic

**Memory & Context:**
- Conversation memory: Enabled
- Multi-agent context sharing: Enabled
- Thinking transparency: Enabled

Settings are automatically configured for optimal performance.""",
        author="Keiken Settings"
    ).send()

@cl.action_callback("select_research")
async def on_select_research(action):
    """Configure Research Team"""
    cl.user_session.set("selected_team", "Research")
    
    await cl.Message(
        content="""## 🔍 Research Team Configuration

**Team Composition:**
- **Researcher**: Senior Research Analyst with web search capabilities
- **Analyst**: Data analysis and synthesis expert
- **Writer**: Report generation and documentation specialist

**Workflow**: Parallel research execution for comprehensive coverage

**Tools Available:**
- Internet search via SearxNG
- Data analysis capabilities
- Report generation

**Current Settings:**
- Search depth: Comprehensive
- Source validation: Enabled  
- Thinking transparency: Enabled

Ready to receive research tasks! Describe what you'd like to investigate.""",
        author="Research Team"
    ).send()

@cl.action_callback("select_creative")
async def on_select_creative(action):
    """Configure Creative Studio"""
    cl.user_session.set("selected_team", "CreativeStudio")
    
    await cl.Message(
        content="""## 🎨 Creative Studio Configuration  

**Team Composition:**
- **Creative Director**: Vision and strategy leadership
- **Designer**: Visual and content creation
- **Marketer**: Brand consistency and audience focus

**Workflow**: Sequential creative process (Ideation → Drafting → Review)

**Capabilities:**
- Creative campaign development
- Content strategy and creation
- Brand consistency validation

**Current Settings:**
- Creative depth: Professional level
- Brand alignment: Keiken standards
- Quality control: Enabled

Ready for creative projects! What would you like to create?""",
        author="Creative Studio"
    ).send()

@cl.action_callback("select_sales")
async def on_select_sales(action):
    """Configure Sales Operations"""  
    cl.user_session.set("selected_team", "SalesOps")
    
    await cl.Message(
        content="""## 💼 Sales Operations Configuration

**Team Composition:**
- **Sales Router**: Scenario analysis and team routing
- **New Business Specialist**: Proposals and growth opportunities  
- **Renewal Specialist**: Customer retention and renewals

**Workflow**: Smart routing (New Business vs Renewal scenarios)

**Capabilities:**
- Proposal generation
- Strategic sales support
- Customer retention strategies
- Technical sales assistance

**Current Settings:**  
- Routing intelligence: Advanced
- Proposal quality: Professional
- CRM integration: Available

Ready for sales scenarios! Describe your sales challenge or opportunity.""",
        author="Sales Operations"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages and route to appropriate team"""
    
    mode = cl.user_session.get("mode")
    selected_team = cl.user_session.get("selected_team")
    
    if not mode:
        await cl.Message(
            content="Please select a mode first using the buttons above.",
            author="Keiken System"
        ).send()
        return
    
    # Show thinking process
    thinking_msg = cl.Message(content="", author="Keiken AI")
    await thinking_msg.send()
    
    try:
        # Determine which team to use
        if mode == "auto":
            # In auto mode, intelligently select the best team
            team_name = await auto_select_team(message.content)
        else:
            # In manual mode, use selected team or default
            team_name = selected_team or "Research"
        
        # Update thinking message
        thinking_msg.content = f"🧠 **Keiken AI Thinking**\n\nRouting to {team_name} team for processing...\n\n"
        await thinking_msg.update()
        
        # Call the backend API
        response = await call_keiken_backend(team_name, message.content)
        
        # Update thinking message with reasoning if available
        thinking_sections, main_content = parse_thinking_content(response)
        
        if thinking_sections:
            thinking_content = "\n\n".join(thinking_sections)
            thinking_msg.content = f"🧠 **Keiken AI Thinking**\n\n{thinking_content}\n\n"
            await thinking_msg.update()
        
        # Send the main response
        await cl.Message(
            content=f"**{team_name} Team Response:**\n\n{main_content}",
            author=f"Keiken {team_name}"
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ **Error**: {str(e)}\n\nPlease try again or contact support.",
            author="Keiken System"
        ).send()

async def auto_select_team(user_input: str) -> str:
    """Automatically select the best team based on user input"""
    user_lower = user_input.lower()
    
    # Simple keyword-based routing (can be enhanced with ML)
    if any(word in user_lower for word in ['research', 'analyze', 'study', 'investigate', 'data', 'report']):
        return "Research"
    elif any(word in user_lower for word in ['create', 'design', 'campaign', 'content', 'marketing', 'brand']):
        return "CreativeStudio"  
    elif any(word in user_lower for word in ['sales', 'proposal', 'client', 'revenue', 'deal', 'renewal']):
        return "SalesOps"
    else:
        # Default to Research for general queries
        return "Research"

async def call_keiken_backend(team_name: str, user_message: str) -> str:
    """Call the Keiken backend API"""
    try:
        url = f"http://keiken-teams-api:8000/teams/{team_name}/execute"
        payload = {
            "messages": [
                {"role": "user", "content": user_message}
            ]
        }
        
        # Use synchronous request in async context
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.post(url, json=payload, timeout=60)
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('result', 'No response received from Keiken backend.')
        else:
            return f"Backend error: HTTP {response.status_code}"
            
    except Exception as e:
        return f"Connection error: {str(e)}"

def parse_thinking_content(content: str):
    """Parse content to extract thinking sections"""
    import re
    thinking_pattern = r'<thinking>(.*?)</thinking>'
    thinking_matches = re.findall(thinking_pattern, content, re.DOTALL)
    main_content = re.sub(thinking_pattern, '', content, flags=re.DOTALL).strip()
    return thinking_matches, main_content

if __name__ == "__main__":
    cl.run()