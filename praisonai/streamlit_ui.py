import streamlit as st
import requests
import json
import re
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Keiken Agent Portal", page_icon="⬜", layout="wide")

# --- THEME / CSS ---
st.markdown("""
<style>
/* Basic container cleanup */
.block-container {padding-top: 1rem; padding-bottom: 2rem;}

/* Chat bubbles */
.chat-bubble {
    padding: 0.8rem 1rem;
    border-radius: 12px;
    margin-bottom: 0.6rem;
    max-width: 80%;
    line-height: 1.5;
}
.user {background-color: rgba(255,255,255,0.08); align-self: flex-end;}
.assistant {background-color: rgba(255,122,0,0.10); border: 1px solid rgba(255,122,0,0.25);}
.chat-row {display: flex; margin-bottom: 0.4rem;}
.user-row {justify-content: flex-end;}
.assistant-row {justify-content: flex-start;}

/* Input bar */
textarea {
    border-radius: 8px !important;
    background: rgba(255,255,255,0.05);
}

/* Averro branding */
.main-header {
    background: linear-gradient(135deg, #FF7A00 0%, #E85B00 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    text-align: center;
}
.main-header h1 {
    color: white;
    margin: 0;
    font-size: 1.8rem;
}

/* Thinking section styles */
.thinking-content {
    font-style: italic;
    color: rgba(255,122,0,0.8);
    background-color: rgba(255,122,0,0.05);
    padding: 0.5rem;
    border-radius: 8px;
    border-left: 3px solid rgba(255,122,0,0.4);
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>Keiken Agent Portal</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">Powered by Nebari Software - Multi-Agent Team Selection & Chat</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    
    # Team selection
    team_options = {
        "Research": "Research Team",
        "CreativeStudio": "Creative Studio", 
        "SalesOps": "Sales Operations"
    }
    
    selected_team = st.selectbox(
        "AI Team:",
        options=list(team_options.keys()),
        format_func=lambda x: team_options[x]
    )
    
    # Controls
    memory_enabled = st.checkbox("Conversation Memory", value=True)
    
    # Clear button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- HELPER FUNCTIONS ---
def parse_thinking_content(content):
    """Parse content to extract thinking sections and main answer."""
    # Look for <thinking>...</thinking> tags
    thinking_pattern = r'<thinking>(.*?)</thinking>'
    thinking_matches = re.findall(thinking_pattern, content, re.DOTALL)
    
    # Remove thinking tags from main content
    main_content = re.sub(thinking_pattern, '', content, flags=re.DOTALL)
    main_content = main_content.strip()
    
    return thinking_matches, main_content

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DISPLAY CHAT ---
for i, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    css_class = "assistant" if role == "assistant" else "user"
    row_class = f"{css_class}-row chat-row"
    content = msg["content"]
    
    if role == "assistant":
        # Parse thinking content for assistant messages
        thinking_sections, main_content = parse_thinking_content(content)
        
        # Display main content in chat bubble
        st.markdown(
            f'<div class="{row_class}"><div class="chat-bubble {css_class}">{main_content}</div></div>',
            unsafe_allow_html=True,
        )
        
        # If there are thinking sections, show them in expandable sections
        if thinking_sections:
            for j, thinking in enumerate(thinking_sections):
                thinking_clean = thinking.strip()
                if thinking_clean:
                    with st.expander(
                        "View AI Reasoning", 
                        expanded=False,
                        # Use a unique key for each expander
                        key=f"thinking_{i}_{j}"
                    ):
                        st.markdown(
                            f'<div class="thinking-content">{thinking_clean}</div>',
                            unsafe_allow_html=True
                        )
    else:
        # Display user messages normally
        st.markdown(
            f'<div class="{row_class}"><div class="chat-bubble {css_class}">{content}</div></div>',
            unsafe_allow_html=True,
        )

# --- INPUT AREA ---
prompt = st.chat_input("Ask your Averro AI team...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call AI API
    try:
        # Prepare messages for API
        api_messages = []
        if memory_enabled:
            # Send conversation history
            for msg in st.session_state.messages:
                api_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        else:
            # Send only current message
            api_messages = [{"role": "user", "content": prompt}]
        
        # Make API call
        with st.spinner("AI is thinking..."):
            response = requests.post(
                f"http://keiken-teams-api:8000/teams/{selected_team}/execute",
                json={"messages": api_messages},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('result', 'No response received')
                
                # Clean up response - remove HTML tags except thinking tags
                # Remove HTML tags but keep <thinking> tags
                clean_response = re.sub(r'<(?!/?thinking\b)[^>]+>', '', ai_response)
                clean_response = clean_response.strip()
                
                # Add AI response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": clean_response
                })
            else:
                # Error response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Sorry, I encountered an error: {response.status_code}"
                })
                
    except Exception as e:
        # Exception handling
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Sorry, I couldn't process your request: {str(e)}"
        })

    # Refresh UI
    st.rerun()