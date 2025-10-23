import streamlit as st
import requests
import json
import os
import re
from datetime import datetime
import sqlite3
from pathlib import Path

# --- PAGE CONFIG ---
st.set_page_config(page_title="Keiken Chat", page_icon="⬜", layout="wide")

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

/* Keiken branding */
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

/* Model selection styling */
.model-card {
    background: rgba(255,122,0,0.1);
    border: 1px solid rgba(255,122,0,0.3);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
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

/* Vision upload area */
.vision-upload {
    border: 2px dashed rgba(255,122,0,0.3);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    background: rgba(255,122,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>Keiken Chat</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">Powered by Nebari Software - Single Agent Chat with 100+ LLMs</p>
</div>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def parse_thinking_content(content):
    """Parse content to extract thinking sections and main answer."""
    thinking_pattern = r'<thinking>(.*?)</thinking>'
    thinking_matches = re.findall(thinking_pattern, content, re.DOTALL)
    main_content = re.sub(thinking_pattern, '', content, flags=re.DOTALL)
    main_content = main_content.strip()
    return thinking_matches, main_content

def init_database():
    """Initialize SQLite database for chat history"""
    db_path = Path.home() / ".keiken" / "chat_database.sqlite"
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            model_used TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return str(db_path)

def get_conversations():
    """Get all conversations from database"""
    db_path = st.session_state.get("db_path")
    if not db_path:
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, created_at, updated_at 
        FROM conversations 
        ORDER BY updated_at DESC
    ''')
    
    conversations = cursor.fetchall()
    conn.close()
    
    return conversations

def create_conversation(title):
    """Create new conversation"""
    db_path = st.session_state.get("db_path")
    if not db_path:
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (title) VALUES (?)
    ''', (title,))
    
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return conversation_id

def save_message(conversation_id, role, content, model_used=None):
    """Save message to database"""
    db_path = st.session_state.get("db_path")
    if not db_path or not conversation_id:
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages (conversation_id, role, content, model_used) 
        VALUES (?, ?, ?, ?)
    ''', (conversation_id, role, content, model_used))
    
    # Update conversation timestamp
    cursor.execute('''
        UPDATE conversations 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (conversation_id,))
    
    conn.commit()
    conn.close()

def load_conversation_messages(conversation_id):
    """Load messages for a conversation"""
    db_path = st.session_state.get("db_path")
    if not db_path:
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT role, content, model_used, timestamp 
        FROM messages 
        WHERE conversation_id = ? 
        ORDER BY timestamp ASC
    ''', (conversation_id,))
    
    messages = cursor.fetchall()
    conn.close()
    
    return [{"role": msg[0], "content": msg[1], "model": msg[2], "timestamp": msg[3]} for msg in messages]

# --- SESSION STATE ---
if "db_path" not in st.session_state:
    st.session_state.db_path = init_database()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "available_models" not in st.session_state:
    # Initialize with Keiken models
    st.session_state.available_models = ["Research", "CreativeStudio", "SalesOps"]

# --- SIDEBAR ---
with st.sidebar:
    st.header("Chat Settings")
    
    # Model selection
    st.subheader("🤖 AI Model")
    selected_model = st.selectbox(
        "Choose AI Model:",
        options=st.session_state.available_models,
        format_func=lambda x: {
            "Research": "🔍 Research Team - Internet search & analysis",
            "CreativeStudio": "🎨 Creative Studio - Content & design",
            "SalesOps": "💼 Sales Operations - Proposals & strategy"
        }.get(x, x)
    )
    
    st.markdown(f"""
    <div class="model-card">
        <strong>Selected:</strong> {selected_model}<br>
        <small>Powered by Keiken Agent Platform</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Features
    st.subheader("🚀 Features")
    internet_search = st.checkbox("Internet Search", value=True, help="Enable web search capabilities")
    vision_support = st.checkbox("Vision Support", value=True, help="Upload images for analysis")
    thinking_display = st.checkbox("Show AI Reasoning", value=True, help="Display thinking process")
    
    st.divider()
    
    # Conversations
    st.subheader("💬 Conversations")
    
    if st.button("➕ New Chat"):
        st.session_state.current_conversation_id = None
        st.session_state.messages = []
        st.rerun()
    
    # List conversations
    conversations = get_conversations()
    for conv in conversations[:10]:  # Show last 10 conversations
        conv_id, title, created_at, updated_at = conv
        if st.button(f"📝 {title[:20]}...", key=f"conv_{conv_id}"):
            st.session_state.current_conversation_id = conv_id
            st.session_state.messages = load_conversation_messages(conv_id)
            st.rerun()
    
    st.divider()
    
    # Database info
    st.subheader("💾 Storage")
    st.caption(f"Database: {Path(st.session_state.db_path).name}")
    st.caption(f"Conversations: {len(conversations)}")

# --- MAIN CONTENT ---

# Vision upload section
if vision_support:
    st.subheader("📷 Vision Input")
    uploaded_image = st.file_uploader(
        "Upload an image for analysis",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
        help="Upload images to ask questions about visual content"
    )
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded image", width=300)
        st.info("💡 You can now ask questions about this image!")

# --- DISPLAY CHAT ---
for i, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    css_class = "assistant" if role == "assistant" else "user"
    row_class = f"{css_class}-row chat-row"
    content = msg["content"]
    
    if role == "assistant":
        # Parse thinking content for assistant messages
        if thinking_display:
            thinking_sections, main_content = parse_thinking_content(content)
        else:
            thinking_sections, main_content = [], content
        
        # Display main content in chat bubble
        display_content = main_content
        if "model" in msg and msg["model"]:
            display_content = f"**{msg['model']} Response:**\n\n{main_content}"
            
        st.markdown(
            f'<div class="{row_class}"><div class="chat-bubble {css_class}">{display_content}</div></div>',
            unsafe_allow_html=True,
        )
        
        # If there are thinking sections, show them in expandable sections
        if thinking_sections and thinking_display:
            for j, thinking in enumerate(thinking_sections):
                thinking_clean = thinking.strip()
                if thinking_clean:
                    with st.expander(
                        "View AI Reasoning", 
                        expanded=False,
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
prompt = st.chat_input("Chat with Keiken AI...")

if prompt:
    # Create new conversation if needed
    if not st.session_state.current_conversation_id:
        # Generate title from first message
        title = prompt[:50] + "..." if len(prompt) > 50 else prompt
        st.session_state.current_conversation_id = create_conversation(title)
    
    # Add user message
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    
    # Save to database
    save_message(
        st.session_state.current_conversation_id,
        "user", 
        prompt
    )

    # Call AI API
    try:
        # Prepare messages for API
        api_messages = []
        for msg in st.session_state.messages:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add image context if uploaded
        enhanced_prompt = prompt
        if uploaded_image and vision_support:
            enhanced_prompt = f"[Image uploaded: {uploaded_image.name}]\n\n{prompt}\n\nPlease analyze the uploaded image and respond to the user's question about it."
            api_messages[-1]["content"] = enhanced_prompt
        
        # Make API call
        with st.spinner(f"Keiken {selected_model} is thinking..."):
            response = requests.post(
                f"http://keiken-teams-api:8000/teams/{selected_model}/execute",
                json={"messages": api_messages},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('result', 'No response received')
                
                # Clean up response - remove HTML tags except thinking tags
                clean_response = re.sub(r'<(?!/?thinking\b)[^>]+>', '', ai_response)
                clean_response = clean_response.strip()
                
                # Add AI response
                assistant_message = {
                    "role": "assistant", 
                    "content": clean_response,
                    "model": selected_model
                }
                st.session_state.messages.append(assistant_message)
                
                # Save to database
                save_message(
                    st.session_state.current_conversation_id,
                    "assistant", 
                    clean_response,
                    selected_model
                )
            else:
                # Error response
                error_message = {
                    "role": "assistant", 
                    "content": f"Sorry, I encountered an error: {response.status_code}",
                    "model": "System"
                }
                st.session_state.messages.append(error_message)
                
    except Exception as e:
        # Exception handling
        error_message = {
            "role": "assistant", 
            "content": f"Sorry, I couldn't process your request: {str(e)}",
            "model": "System"
        }
        st.session_state.messages.append(error_message)

    # Refresh UI
    st.rerun()

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.6); font-size: 0.9rem;">
    <p>💬 <strong>Keiken Chat Features:</strong> Single-agent conversations • Internet search • Vision support • Persistent chat history</p>
    <p>Powered by <strong>Keiken Agent Platform</strong> - Nebari Software</p>
</div>
""", unsafe_allow_html=True)