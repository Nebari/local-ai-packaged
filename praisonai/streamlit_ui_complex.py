import streamlit as st
import requests
import json
import re
import time
from datetime import datetime

def clean_response_content(content):
    """Clean and sanitize AI response content"""
    if not content:
        return ""
    
    # Remove HTML tags completely
    content = re.sub(r'<[^>]+>', '', content)
    
    # Remove markdown bold formatting
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    
    # Clean up multiple newlines
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    return content.strip()

def extract_thinking(content):
    """Extract thinking content from response"""
    thinking_patterns = [
        r'<thinking>(.*?)</thinking>',
        r'<think>(.*?)</think>',
        r'Thinking:(.*?)(?:\n\n|\*\*|$)'
    ]
    
    for pattern in thinking_patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            thinking = match.group(1).strip()
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE).strip()
            return clean_response_content(thinking), clean_response_content(content)
    
    return "", clean_response_content(content)

# Page configuration
st.set_page_config(
    page_title="Averro AI Platform",
    page_icon="▲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS without emoticons
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: #1A1A1A;
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main-header {
        background: linear-gradient(135deg, #FF7A00 0%, #E85B00 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(255, 122, 0, 0.2);
    }
    
    .main-header h1 {
        color: white;
        font-weight: 700;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header .subtitle {
        color: rgba(255,255,255,0.9);
        font-weight: 500;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .message-bubble {
        margin: 1rem 0;
        padding: 1.25rem;
        border-radius: 12px;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .user-message {
        background: rgba(255,255,255,0.08);
        border-left: 3px solid #FF7A00;
        margin-left: 15%;
    }
    
    .ai-message {
        background: rgba(255,122,0,0.06);
        border-left: 3px solid #FFB547;
        margin-right: 15%;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        font-weight: 600;
    }
    
    .message-role {
        color: #FF7A00;
        font-size: 0.9rem;
    }
    
    .message-time {
        color: rgba(255,255,255,0.5);
        font-size: 0.8rem;
        font-weight: 400;
    }
    
    .thinking-section {
        background: rgba(255,122,0,0.1);
        border: 1px solid rgba(255,122,0,0.3);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        font-style: italic;
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
    }
    
    .sidebar-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,122,0,0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-title {
        color: #FF7A00;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .modern-button {
        background: linear-gradient(135deg, #FF7A00, #E85B00);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.8rem;
    }
    
    .modern-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(255,122,0,0.3);
    }
    
    .stSelectbox > div > div {
        background: #2A2A2A;
        border: 1px solid rgba(255,122,0,0.3);
        border-radius: 8px;
    }
    
    .stCheckbox > label {
        font-weight: 500;
        color: #F0F0F0;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    
    .stat-card {
        background: rgba(255,122,0,0.1);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FF7A00;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.7);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_team" not in st.session_state:
    st.session_state.selected_team = "research-team"

if "show_thinking" not in st.session_state:
    st.session_state.show_thinking = True

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True

# Header
st.markdown("""
<div class="main-header">
    <h1>▲ Averro AI Platform</h1>
    <div class="subtitle">Advanced Multi-Agent Intelligence Solutions</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Team Selection
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">AI Team Selection</div>
    </div>
    """, unsafe_allow_html=True)
    
    team_options = {
        "research-team": "Research Analysts",
        "creative-team": "Creative Studio", 
        "sales-team": "Sales Operations"
    }
    
    selected_team = st.selectbox(
        "Active Team:",
        options=list(team_options.keys()),
        format_func=lambda x: team_options[x],
        key="team_selector"
    )
    st.session_state.selected_team = selected_team
    
    # Controls
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">Controls</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.memory_enabled = st.checkbox("Memory", value=st.session_state.memory_enabled)
        
    with col2:
        st.session_state.show_thinking = st.checkbox("Thinking", value=st.session_state.show_thinking)
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("Export", use_container_width=True):
            chat_data = {
                "messages": st.session_state.messages,
                "team": selected_team,
                "timestamp": datetime.now().isoformat()
            }
            st.download_button(
                "Download JSON",
                data=json.dumps(chat_data, indent=2),
                file_name=f"averro_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    # Stats
    if st.session_state.messages:
        user_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        ai_count = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        
        st.markdown("""
        <div class="sidebar-card">
            <div class="sidebar-title">Session Stats</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{}</div>
                    <div class="stat-label">Questions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{}</div>
                    <div class="stat-label">Responses</div>
                </div>
            </div>
        </div>
        """.format(user_count, ai_count), unsafe_allow_html=True)

# Chat Display
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":
        timestamp = message.get('timestamp', datetime.now().strftime('%H:%M'))
        st.markdown(f"""
        <div class="message-bubble user-message">
            <div class="message-header">
                <span class="message-role">You</span>
                <span class="message-time">{timestamp}</span>
            </div>
            <div>{message["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        team_name = team_options.get(message.get('team', selected_team), 'AI Assistant')
        timestamp = message.get('timestamp', datetime.now().strftime('%H:%M'))
        thinking = message.get('thinking', '')
        content = message.get('content', '')
        
        message_html = f"""
        <div class="message-bubble ai-message">
            <div class="message-header">
                <span class="message-role">{team_name}</span>
                <span class="message-time">{timestamp}</span>
            </div>
        """
        
        if st.session_state.show_thinking and thinking:
            message_html += f"""
            <div class="thinking-section">
                <strong>Analysis:</strong> {thinking}
            </div>
            """
        
        message_html += f"""
            <div>{content}</div>
        </div>
        """
        
        st.markdown(message_html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat Input - Single processing approach
if prompt := st.chat_input("Type your message here..."):
    # Add user message immediately
    user_message = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().strftime('%H:%M')
    }
    st.session_state.messages.append(user_message)
    
    # Process AI response immediately in the same execution
    try:
        # Prepare API messages
        api_messages = []
        if st.session_state.memory_enabled:
            for msg in st.session_state.messages:
                api_messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", "")
                })
        else:
            api_messages = [{"role": "user", "content": prompt}]
        
        # Call API
        with st.spinner(f"{team_options[selected_team]} is processing..."):
            response = requests.post(
                f"http://praisonai-teams:8000/teams/{selected_team}/execute",
                json={"messages": api_messages},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                full_response = result.get('result', 'No response available')
                
                # Extract thinking and clean content
                thinking, clean_content = extract_thinking(full_response)
                
                # Add AI response
                ai_message = {
                    "role": "assistant",
                    "content": clean_content,
                    "thinking": thinking,
                    "team": selected_team,
                    "timestamp": datetime.now().strftime('%H:%M')
                }
                st.session_state.messages.append(ai_message)
                
            else:
                # Add error message
                error_message = {
                    "role": "assistant",
                    "content": f"Error: Service returned status {response.status_code}",
                    "thinking": "",
                    "team": selected_team,
                    "timestamp": datetime.now().strftime('%H:%M')
                }
                st.session_state.messages.append(error_message)
    
    except Exception as e:
        # Add error message
        error_message = {
            "role": "assistant",
            "content": f"Error: {str(e)}",
            "thinking": "",
            "team": selected_team,
            "timestamp": datetime.now().strftime('%H:%M')
        }
        st.session_state.messages.append(error_message)
    
    # Rerun to display new messages
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="
    text-align: center;
    padding: 2rem;
    background: rgba(255,122,0,0.05);
    border-radius: 12px;
    border: 1px solid rgba(255,122,0,0.2);
">
    <div style="
        font-size: 1.1rem;
        font-weight: 700;
        color: #FF7A00;
        margin-bottom: 0.5rem;
    ">
        Averro AI Platform
    </div>
    <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">
        Powered by Advanced Multi-Agent Technology
    </div>
</div>
""", unsafe_allow_html=True)