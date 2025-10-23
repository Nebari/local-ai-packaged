import streamlit as st
import requests
import json
import re
import time
from datetime import datetime

def clean_html_content(content):
    """Remove HTML tags and clean up content for display"""
    if not content:
        return content
    
    # Remove common HTML patterns
    html_patterns = [
        r'<div[^>]*>.*?</div>',  # Remove div tags and content
        r'<[^>]+>',             # Remove any remaining HTML tags
        r'\*\*([^*]+)\*\*',     # Convert **text** to text
    ]
    
    cleaned_content = content
    for pattern in html_patterns:
        if pattern == r'\*\*([^*]+)\*\*':
            cleaned_content = re.sub(pattern, r'\1', cleaned_content)
        else:
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL)
    
    return cleaned_content.strip()

def parse_thinking_and_response(content):
    """Parse response to separate thinking from main content"""
    # Look for patterns like <thinking>...</thinking> or similar
    thinking_patterns = [
        r'<thinking>(.*?)</thinking>',
        r'<think>(.*?)</think>', 
        r'\*\*Thinking:\*\*(.*?)\*\*Response:\*\*',
        r'Internal thoughts:(.*?)(?:\n\n|\*\*)',
    ]
    
    thinking = ""
    main_content = content
    
    for pattern in thinking_patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            thinking = match.group(1).strip()
            main_content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE).strip()
            break
    
    # Clean HTML from both thinking and main content
    thinking = clean_html_content(thinking)
    main_content = clean_html_content(main_content)
    
    return thinking, main_content

# Modern Averro-branded page configuration
st.set_page_config(
    page_title="Averro AI — Intelligent Solutions",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern Averro branding
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        background: #1C1C1C;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .averro-header {
        background: linear-gradient(135deg, #FF7A00 0%, #E85B00 50%, #FFB547 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(255, 122, 0, 0.2);
    }
    
    .averro-header h1 {
        color: white;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .averro-header .subtitle {
        color: rgba(255,255,255,0.9);
        font-weight: 500;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1C1C1C 0%, #151821 100%);
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        font-size: 16px;
        line-height: 1.55;
    }
    
    .chat-message.user {
        background: rgba(255,255,255,0.06);
        margin-left: 20%;
        border-left: 3px solid #FF7A00;
    }
    
    .chat-message.assistant {
        background: rgba(255,122,0,0.10);
        margin-right: 20%;
        border-left: 3px solid #FFB547;
    }
    
    .chat-message .avatar {
        font-size: 1.5rem;
        margin-right: 0.75rem;
        vertical-align: middle;
    }
    
    .chat-message .thinking {
        font-style: italic;
        color: rgba(255,255,255,0.7);
        border-left: 2px solid #FF7A00;
        padding-left: 1rem;
        margin-bottom: 1rem;
        background: rgba(255,122,0,0.05);
        border-radius: 8px;
        padding: 0.75rem 1rem;
    }
    
    /* Input styling */
    .stChatInputContainer {
        background: #151821;
        border-radius: 12px;
        border: 1px solid rgba(255,122,0,0.3);
        box-shadow: 0 2px 8px rgba(255,122,0,0.1);
    }
    
    /* Buttons and controls */
    .stButton > button {
        background: linear-gradient(135deg, #FF7A00 0%, #E85B00 100%);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255,122,0,0.3);
    }
    
    /* Sidebar elements */
    .sidebar-section {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,122,0,0.2);
    }
    
    .sidebar-header {
        color: #FF7A00;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Toggle switches */
    .stCheckbox > label {
        font-weight: 500;
        color: #F7F7F7;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: #151821;
        border: 1px solid rgba(255,122,0,0.3);
        border-radius: 8px;
    }
    
    /* Typography improvements */
    h1, h2, h3 {
        color: #F7F7F7;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-card {
        background: rgba(255,122,0,0.08);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255,122,0,0.2);
        text-align: center;
    }
    
    /* Animation classes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Timestamp styling */
    .timestamp {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.5);
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Custom branded header
st.markdown("""
<div class="averro-header">
    <h1>🚀 Averro AI — Intelligent Solutions</h1>
    <div class="subtitle">Advanced Multi-Agent Collaboration Platform</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state with better structure
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_team" not in st.session_state:
    st.session_state.selected_team = "research-team"

if "show_thinking" not in st.session_state:
    st.session_state.show_thinking = True

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True

if "streaming_enabled" not in st.session_state:
    st.session_state.streaming_enabled = True

# Add message processing tracking
if "last_processed_message_id" not in st.session_state:
    st.session_state.last_processed_message_id = None

# Modern Averro-branded sidebar
with st.sidebar:
    # Header section
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-header">🚀 Averro AI Platform</div>
        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
            Intelligent Solutions for Modern Business
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Team selection section
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-header">🎯 AI Team Selection</div>
    </div>
    """, unsafe_allow_html=True)
    
    team_options = {
        "research-team": "🔬 Research Team",
        "creative-team": "🎨 Creative Studio", 
        "sales-team": "💼 Sales Operations"
    }
    
    selected_team = st.selectbox(
        "Choose your specialized AI team:",
        options=list(team_options.keys()),
        format_func=lambda x: team_options[x],
        key="team_selector",
        label_visibility="collapsed"
    )
    
    st.session_state.selected_team = selected_team
    
    # Feature toggles section
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-header">⚙️ Feature Controls</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.memory_enabled = st.checkbox(
            "💾 Memory", 
            value=st.session_state.memory_enabled,
            help="Remember conversation context"
        )
        
        st.session_state.show_thinking = st.checkbox(
            "💭 Thinking", 
            value=st.session_state.show_thinking,
            help="Show AI reasoning process"
        )
    
    with col2:
        st.session_state.streaming_enabled = st.checkbox(
            "⚡ Streaming", 
            value=st.session_state.streaming_enabled,
            help="Real-time response streaming"
        )
    
    # Controls section
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-header">💬 Chat Controls</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("📤 Export", use_container_width=True):
            chat_export = {
                "client": "Averro",
                "team": selected_team,
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.messages,
                "features": {
                    "memory_enabled": st.session_state.memory_enabled,
                    "show_thinking": st.session_state.show_thinking,
                    "streaming_enabled": st.session_state.streaming_enabled
                }
            }
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(chat_export, indent=2),
                file_name=f"averro_ai_chat_{selected_team}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# Main chat interface with custom styling
st.markdown("---")

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history with modern bubbles
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            # User message bubble
            timestamp = message.get('timestamp', datetime.now().strftime('%H:%M'))
            safe_user_content = message["content"].replace('<', '&lt;').replace('>', '&gt;') if message["content"] else ''
            st.markdown(f"""
            <div class="chat-message user fade-in">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span class="avatar">👤</span>
                    <strong style="color: #FF7A00;">You</strong>
                    <span class="timestamp" style="margin-left: auto;">{timestamp}</span>
                </div>
                <div>{safe_user_content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Assistant message bubble  
            team_name = team_options.get(message.get('team', selected_team), 'Averro AI')
            timestamp = message.get('timestamp', datetime.now().strftime('%H:%M'))
            
            # Check if message has pre-processed thinking/content structure
            if isinstance(message.get('content'), dict):
                # New structure with separated thinking and content
                thinking_content = message['content'].get('thinking', '')
                main_content = message['content'].get('response', '')
            else:
                # Legacy structure - message content is a string, don't re-parse
                thinking_content = message.get('thinking', '')
                main_content = message.get('content', '')
            
            # Build message content
            message_html = f"""
            <div class="chat-message assistant fade-in">
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <span class="avatar">🤖</span>
                    <strong style="color: #FFB547;">{team_name}</strong>
                    <span class="timestamp" style="margin-left: auto;">{timestamp}</span>
                </div>
            """
            
            # Add thinking if enabled and exists
            if st.session_state.show_thinking and thinking_content:
                message_html += f"""
                <div class="thinking">
                    💭 <em>Thinking: {thinking_content}</em>
                </div>
                """
            
            # Add main response (escape HTML for safety)
            safe_content = main_content.replace('<', '&lt;').replace('>', '&gt;') if main_content else ''
            message_html += f"""
                <div>{safe_content}</div>
            </div>
            """
            
            st.markdown(message_html, unsafe_allow_html=True)

# Modern chat input with Averro styling
st.markdown("---")
st.markdown("### 💬 Chat with Your Averro AI Team")

# Custom input styling
if prompt := st.chat_input("Ask your Averro AI team anything...", key="main_chat_input"):
    # Generate unique message ID
    message_id = f"user_{datetime.now().timestamp()}_{len(st.session_state.messages)}"
    
    # Add user message with timestamp and ID
    user_message = {
        "role": "user", 
        "content": prompt,
        "timestamp": datetime.now().strftime('%H:%M'),
        "message_id": message_id
    }
    st.session_state.messages.append(user_message)
    
    # Rerun to show user message immediately
    st.rerun()

# Handle AI response generation (only if there's a new unprocessed user message)
if (st.session_state.messages and 
    st.session_state.messages[-1]["role"] == "user" and
    st.session_state.messages[-1].get("message_id") != st.session_state.last_processed_message_id and
    not hasattr(st.session_state, 'processing_response')):
    
    # Set flag to prevent duplicate processing and track current message
    st.session_state.processing_response = True
    current_user_message = st.session_state.messages[-1]
    st.session_state.last_processed_message_id = current_user_message.get("message_id")
    
    # Show loading indicator
    with st.spinner(f"{team_options[selected_team]} is analyzing your request..."):
        try:
            # Prepare conversation context
            api_messages = []
            if st.session_state.memory_enabled:
                # Send full conversation history
                for msg in st.session_state.messages:
                    # Extract content properly for API
                    content = msg["content"]
                    if isinstance(content, dict):
                        content = content.get('response', str(content))
                    
                    api_messages.append({
                        "role": msg["role"],
                        "content": content
                    })
            else:
                # Send only the latest user message
                latest_msg = st.session_state.messages[-1]
                api_messages = [{
                    "role": latest_msg["role"],
                    "content": latest_msg["content"]
                }]
            
            # Call PraisonAI API
            response = requests.post(
                f"http://praisonai-teams:8000/teams/{selected_team}/execute",
                json={"messages": api_messages},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                full_response = result.get('result', 'No response available')
                
                # Parse thinking and main content
                thinking_content, main_content = parse_thinking_and_response(full_response)
                
                # Store structured message data to prevent duplication
                assistant_message = {
                    "role": "assistant",
                    "content": main_content,  # Store clean main content
                    "thinking": thinking_content,  # Store thinking separately  
                    "team": selected_team,
                    "timestamp": datetime.now().strftime('%H:%M'),
                    "message_id": f"assistant_{datetime.now().timestamp()}_{len(st.session_state.messages)}"
                }
                
                st.session_state.messages.append(assistant_message)
                
            else:
                # Handle API errors
                error_message = {
                    "role": "assistant",
                    "content": f"❌ Service Error {response.status_code}: {response.text}",
                    "thinking": "",
                    "team": selected_team,
                    "timestamp": datetime.now().strftime('%H:%M'),
                    "message_id": f"error_{datetime.now().timestamp()}"
                }
                st.session_state.messages.append(error_message)
                
        except requests.exceptions.Timeout:
            timeout_message = {
                "role": "assistant", 
                "content": "⏱️ Request timed out. The AI team is working on complex analysis. Please try again.",
                "thinking": "",
                "team": selected_team,
                "timestamp": datetime.now().strftime('%H:%M'),
                "message_id": f"timeout_{datetime.now().timestamp()}"
            }
            st.session_state.messages.append(timeout_message)
            
        except requests.exceptions.RequestException as e:
            connection_message = {
                "role": "assistant",
                "content": f"🔗 Connection error: Please check your network and try again.",
                "thinking": "",
                "team": selected_team,
                "timestamp": datetime.now().strftime('%H:%M'),
                "message_id": f"connection_error_{datetime.now().timestamp()}"
            }
            st.session_state.messages.append(connection_message)
            
        except Exception as e:
            error_message = {
                "role": "assistant",
                "content": f"❌ Unexpected error occurred. Please try again.",
                "thinking": "",
                "team": selected_team,
                "timestamp": datetime.now().strftime('%H:%M'),
                "message_id": f"general_error_{datetime.now().timestamp()}"
            }
            st.session_state.messages.append(error_message)
        
        finally:
            # Clear processing flag and rerun to show response
            if hasattr(st.session_state, 'processing_response'):
                del st.session_state.processing_response
            st.rerun()

# Add team capabilities info to sidebar
with st.sidebar:
    # Current team info
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-header">🎯 Active Team</div>
    </div>
    """, unsafe_allow_html=True)
    
    if selected_team == "research-team":
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #FF7A00; margin: 0;">🔬 Research Team</h4>
            <p style="font-size: 0.9rem; margin: 0.5rem 0;">
                • Data Analysis & Insights<br>
                • Market Research<br>
                • Real-time Web Search<br>
                • Comprehensive Reports
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif selected_team == "creative-team":
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #FF7A00; margin: 0;">🎨 Creative Studio</h4>
            <p style="font-size: 0.9rem; margin: 0.5rem 0;">
                • Brand Development<br>
                • Content Creation<br>
                • Marketing Strategy<br>
                • Visual Concepts
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif selected_team == "sales-team":
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #FF7A00; margin: 0;">💼 Sales Operations</h4>
            <p style="font-size: 0.9rem; margin: 0.5rem 0;">
                • Sales Strategy<br>
                • Lead Generation<br>
                • Performance Analysis<br>
                • Revenue Optimization
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat statistics
    if st.session_state.messages:
        user_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        ai_count = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-header">📊 Session Stats</div>
            <div style="display: flex; gap: 1rem;">
                <div class="metric-card" style="flex: 1; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #FF7A00;">{}</div>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">Questions</div>
                </div>
                <div class="metric-card" style="flex: 1; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #FFB547;">{}</div>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">Responses</div>
                </div>
            </div>
        </div>
        """.format(user_count, ai_count), unsafe_allow_html=True)

# Modern Averro footer
st.markdown("---")
st.markdown("""
<div style="
    text-align: center; 
    padding: 2rem 1rem; 
    background: rgba(255,122,0,0.05);
    border-radius: 12px;
    border: 1px solid rgba(255,122,0,0.2);
    margin-top: 2rem;
">
    <div style="
        background: linear-gradient(135deg, #FF7A00, #FFB547);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    ">
        🚀 Averro AI — Intelligent Solutions
    </div>
    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">
        Powered by Advanced Multi-Agent AI Technology
    </div>
</div>
""", unsafe_allow_html=True)