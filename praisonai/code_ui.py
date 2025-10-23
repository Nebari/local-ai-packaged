import streamlit as st
import requests
import json
import os
import re
from datetime import datetime
from pathlib import Path
import zipfile
import tempfile

# --- PAGE CONFIG ---
st.set_page_config(page_title="Keiken Code Portal", page_icon="⬜", layout="wide")

# --- THEME / CSS ---
st.markdown("""
<style>
/* Basic container cleanup */
.block-container {padding-top: 1rem; padding-bottom: 2rem;}

/* Chat bubbles for code interface */
.chat-bubble {
    padding: 0.8rem 1rem;
    border-radius: 12px;
    margin-bottom: 0.6rem;
    max-width: 90%;
    line-height: 1.5;
}
.user {background-color: rgba(255,255,255,0.08); align-self: flex-end;}
.assistant {background-color: rgba(255,122,0,0.10); border: 1px solid rgba(255,122,0,0.25);}
.chat-row {display: flex; margin-bottom: 0.4rem;}
.user-row {justify-content: flex-end;}
.assistant-row {justify-content: flex-start;}

/* Code blocks */
pre {
    background-color: rgba(40,44,52,0.95) !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    overflow-x: auto !important;
}

/* Input areas */
textarea {
    border-radius: 8px !important;
    background: rgba(255,255,255,0.05);
}

/* File upload area */
.uploadedFile {
    border: 2px dashed rgba(255,122,0,0.3);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    background: rgba(255,122,0,0.05);
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

/* File tree styling */
.file-tree {
    background-color: rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 1rem;
    max-height: 300px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 0.9rem;
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
    <h1>Keiken Code Interface</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">Powered by Nebari Software - Chat with Entire Codebase using AI</p>
</div>
""", unsafe_allow_html=True)# --- HELPER FUNCTIONS ---
def parse_thinking_content(content):
    """Parse content to extract thinking sections and main answer."""
    # Look for <thinking>...</thinking> tags
    thinking_pattern = r'<thinking>(.*?)</thinking>'
    thinking_matches = re.findall(thinking_pattern, content, re.DOTALL)
    
    # Remove thinking tags from main content
    main_content = re.sub(thinking_pattern, '', content, flags=re.DOTALL)
    main_content = main_content.strip()
    
    return thinking_matches, main_content

def extract_files_from_zip(uploaded_file):
    """Extract files from uploaded zip and return file structure."""
    files_content = {}
    file_tree = []
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Save uploaded file
        zip_path = os.path.join(tmp_dir, uploaded_file.name)
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract and read files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            for file_path in file_list:
                if not file_path.endswith('/'):  # Skip directories
                    # Check if it's a text file
                    if any(file_path.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.css', '.html', '.xml', '.json', '.yml', '.yaml', '.md', '.txt', '.sql', '.sh', '.bat']):
                        try:
                            with zip_ref.open(file_path) as f:
                                content = f.read().decode('utf-8')
                                files_content[file_path] = content
                                file_tree.append(file_path)
                        except Exception as e:
                            st.warning(f"Could not read {file_path}: {str(e)}")
                    else:
                        file_tree.append(f"{file_path} (binary file - skipped)")
    
    return files_content, file_tree

def create_context_summary(files_content):
    """Create a context summary from uploaded files."""
    if not files_content:
        return "No code files provided."
    
    context = "=== CODEBASE ANALYSIS CONTEXT ===\n\n"
    
    # Add file overview
    context += f"Files analyzed: {len(files_content)} files\n"
    context += "File list:\n"
    for file_path in sorted(files_content.keys()):
        lines = len(files_content[file_path].split('\n'))
        context += f"- {file_path} ({lines} lines)\n"
    
    context += "\n=== FILE CONTENTS ===\n\n"
    
    # Add file contents (truncated if too long)
    for file_path, content in files_content.items():
        context += f"--- {file_path} ---\n"
        if len(content) > 5000:  # Truncate very long files
            context += content[:2500] + "\n\n... [FILE TRUNCATED] ...\n\n" + content[-2500:]
        else:
            context += content
        context += "\n\n"
    
    return context

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "codebase_context" not in st.session_state:
    st.session_state.codebase_context = ""
if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = False

# --- SIDEBAR ---
with st.sidebar:
    st.header("Code Analysis Settings")
    
    # Team selection
    team_options = {
        "Research": "Research Team - Code Analysis & Documentation",
        "CreativeStudio": "Creative Studio - Code Generation & Refactoring", 
        "SalesOps": "Sales Operations - Technical Proposals & Architecture"
    }
    
    selected_team = st.selectbox(
        "Analysis Team:",
        options=list(team_options.keys()),
        format_func=lambda x: team_options[x]
    )
    
    st.divider()
    
    # File upload section
    st.subheader("📁 Upload Codebase")
    uploaded_file = st.file_uploader(
        "Upload ZIP file containing your codebase",
        type=['zip'],
        help="Upload a ZIP file containing your source code files"
    )
    
    if uploaded_file and not st.session_state.files_uploaded:
        with st.spinner("Processing codebase..."):
            try:
                files_content, file_tree = extract_files_from_zip(uploaded_file)
                st.session_state.codebase_context = create_context_summary(files_content)
                st.session_state.files_uploaded = True
                st.session_state.file_tree = file_tree
                st.success(f"Processed {len(files_content)} code files")
            except Exception as e:
                st.error(f"Error processing codebase: {str(e)}")
    
    # Show file tree if files are uploaded
    if st.session_state.files_uploaded and 'file_tree' in st.session_state:
        st.subheader("📋 File Structure")
        with st.expander("View Files", expanded=True):
            st.markdown(
                f'<div class="file-tree">{"<br>".join(st.session_state.file_tree)}</div>',
                unsafe_allow_html=True
            )
    
    # Controls
    memory_enabled = st.checkbox("Conversation Memory", value=True)
    include_context = st.checkbox("Include Codebase Context", value=True, disabled=not st.session_state.files_uploaded)
    
    # Clear buttons
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("Clear Codebase"):
        st.session_state.codebase_context = ""
        st.session_state.files_uploaded = False
        if 'file_tree' in st.session_state:
            del st.session_state.file_tree
        st.rerun()

# --- MAIN CONTENT ---

# Show codebase status
if st.session_state.files_uploaded:
    st.info(f"🗂️ Codebase loaded - Ready for analysis with {selected_team}")
else:
    st.warning("📤 Upload a ZIP file of your codebase to get started with AI-powered code analysis")

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
prompt = st.chat_input("Ask questions about your codebase, request code analysis, or generate new code...")

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
        
        # Add codebase context if enabled and available
        enhanced_prompt = prompt
        if include_context and st.session_state.codebase_context:
            enhanced_prompt = f"""CODEBASE CONTEXT:
{st.session_state.codebase_context}

USER QUERY: {prompt}

Please analyze the provided codebase and answer the user's question with specific references to the code files when relevant."""
            
            # Update the last message with enhanced prompt
            api_messages[-1]["content"] = enhanced_prompt
        
        # Make API call
        with st.spinner("Analyzing code..."):
            response = requests.post(
                f"http://keiken-teams-api:8000/teams/{selected_team}/execute",
                json={"messages": api_messages},
                timeout=120  # Longer timeout for code analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('result', 'No response received')
                
                # Clean up response - remove HTML tags except thinking tags
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

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.6); font-size: 0.9rem;">
    <p>💡 <strong>Tips:</strong> Upload your codebase as a ZIP file, then ask questions about architecture, request code reviews, or generate new features.</p>
    <p>Powered by <strong>Keiken Agent Portal</strong> - Nebari Software</p>
</div>
""", unsafe_allow_html=True)