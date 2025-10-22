import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="PraisonAI Multi-Agent Teams",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 PraisonAI Multi-Agent Teams")
st.markdown("**Simple UI for PraisonAI Multi-Agent Collaboration**")

# Sidebar for team selection
with st.sidebar:
    st.header("⚙️ Team Selection")
    
    # Team options
    team_options = {
        "research-team": "🔍 Research Team - Web search, analysis, and reporting",
        "coding-team": "💻 Coding Team - Architecture, development, and testing", 
        "business-team": "💼 Business Team - Analysis, financial planning, strategy",
        "creative-team": "🎨 Creative Team - Design, copywriting, content strategy"
    }
    
    selected_team = st.selectbox(
        "Choose Agent Team:",
        options=list(team_options.keys()),
        format_func=lambda x: team_options[x]
    )
    
    st.info(f"Selected: **{team_options[selected_team]}**")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    # User input
    user_query = st.text_area(
        "💭 What would you like the team to work on?",
        placeholder="Enter your task or question here...\n\nExample: 'Analyze the latest AI trends and create a market report'",
        height=150
    )
    
    # Execute button
    if st.button("🚀 Execute Team Task", type="primary", use_container_width=True):
        if user_query.strip():
            with st.spinner(f"🔄 {team_options[selected_team].split(' - ')[0]} is working on your task..."):
                try:
                    # Call the PraisonAI teams API
                    response = requests.post(
                        f"http://praisonai-teams:8000/teams/{selected_team}/execute",
                        json={"query": user_query},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display results
                        st.success("✅ Task completed successfully!")
                        
                        # Team info
                        st.subheader(f"📊 {result.get('team_name', 'Team')} Results")
                        
                        # Timestamp
                        st.caption(f"⏰ Completed at: {result.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
                        
                        # Main result
                        with st.container():
                            st.markdown("### 📋 Team Analysis & Recommendations")
                            st.markdown(result.get('result', 'No result available'))
                        
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The team might still be working on complex tasks.")
                except requests.exceptions.RequestException as e:
                    st.error(f"🔗 Connection error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a task or question for the team to work on.")

with col2:
    st.markdown("### 🎯 Team Capabilities")
    
    if selected_team == "research-team":
        st.markdown("""
        **🔍 Research Team**
        - 📊 Senior Research Analyst
        - 📈 Data Analyst  
        - ✍️ Content Writer
        - 🌐 Internet search tools
        - 📚 Comprehensive research & reporting
        """)
    elif selected_team == "coding-team":
        st.markdown("""
        **💻 Coding Team**
        - 🏗️ Software Architect
        - 👨‍💻 Developer
        - 🧪 QA Engineer
        - 🔧 Full development lifecycle
        - 📋 Technical documentation
        """)
    elif selected_team == "business-team":
        st.markdown("""
        **💼 Business Team**
        - 📊 Business Analyst
        - 💰 Financial Analyst
        - 📈 Strategy Consultant
        - 💹 Market analysis
        - 📋 Strategic planning
        """)
    elif selected_team == "creative-team":
        st.markdown("""
        **🎨 Creative Team**
        - 🎭 Creative Director
        - ✍️ Copywriter
        - 📝 Content Strategist
        - 🎨 Creative direction
        - 📢 Marketing content
        """)
    
    st.markdown("### 🔗 API Integration")
    st.code(f"""
# Direct API call
POST /teams/{selected_team}/execute
{{
    "query": "Your task description"
}}
    """)

# Footer
st.markdown("---")
st.markdown("**🤖 Powered by PraisonAI Multi-Agent Framework** | Built with Streamlit")

# Add some CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: bold;
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)