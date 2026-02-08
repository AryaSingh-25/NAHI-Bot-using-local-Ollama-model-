import streamlit as st
import requests
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="NHAI AI Assistant",
    page_icon="🛣️",
    layout="wide"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
    h1 {
        color: #1e3a8a;
        font-weight: 700;
    }
    .stButton > button {
        background-color: #1e3a8a;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton > button:hover {
        background-color: #2563eb;
    }
    .success-box {
        background-color: #dcfce7;
        border-left: 4px solid #16a34a;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("# 🛣️")
with col2:
    st.title("NHAI AI Assistant")
    st.markdown("*Ask anything about National Highways Authority of India*")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📊 System Status")
    
    # Check Ollama connection
    try:
        test_response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if test_response.status_code == 200:
            models = test_response.json().get('models', [])
            model_names = [m['name'] for m in models]
            status_html = f"""
            <div class='success-box'>
                <strong>✅ Ollama Connected</strong><br>
                Status: Online<br>
                Available Models: {len(models)}
            </div>
            """
        else:
            status_html = """
            <div style='background-color: #fee; border-left: 4px solid #f00; padding: 1rem;'>
                <strong>❌ Ollama Not Found</strong><br>
                Please start Ollama
            </div>
            """
            model_names = []
    except:
        status_html = """
        <div style='background-color: #fee; border-left: 4px solid #f00; padding: 1rem;'>
            <strong>❌ Ollama Not Running</strong><br>
            Run: ollama serve
        </div>
        """
        model_names = []
    
    st.markdown(status_html, unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("⚙️ Configuration")
    
    # Model selection
    default_models = ['llama3:latest', 'gemma3:4b']
    available_models = model_names if model_names else default_models
    
    selected_model = st.selectbox(
        "Select AI Model",
        options=available_models,
        index=0,
        help="Choose your Ollama model"
    )
    
    data_folder = st.text_input("Data Folder Path", value="data", help="Folder containing your .txt files")
    
    st.markdown("---")
    st.markdown("### 🎯 Features")
    st.markdown("""
    - ✅ 100% Local & Private
    - ✅ No API Limits
    - ✅ 83+ Topics Covered
    - ✅ Source Citations
    - ✅ Chat Memory
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Sample Questions")
    st.markdown("""
    - What does NHAI stand for?
    - Green Highways Policy?
    - Bharatmala Pariyojana?
    - FASTag information?
    - Road safety initiatives?
    """)
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Load knowledge base
@st.cache_data
def load_knowledge_base(folder_path):
    """Load all text files from the data folder"""
    knowledge = {}
    folder = Path(folder_path)
    
    if not folder.exists():
        return None
    
    for txt_file in folder.glob("*.txt"):
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if len(content) > 100:
                    topic_name = txt_file.stem.replace('_', ' / ').replace('-', ' ').title()
                    knowledge[topic_name] = content
        except Exception as e:
            continue
    
    return knowledge

# Create context from knowledge base
def create_context(knowledge_base, query, max_topics=10):
    """Create a relevant context string from knowledge base based on query"""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    # Score each topic by relevance
    scored_topics = []
    for topic, content in knowledge_base.items():
        content_lower = content.lower()
        topic_lower = topic.lower()
        
        # Calculate relevance score
        score = 0
        for word in query_words:
            if len(word) > 2:
                if word in topic_lower:
                    score += 5
                if word in content_lower:
                    score += content_lower.count(word)
        
        if score > 0:
            scored_topics.append((topic, content, score))
    
    # If no matches, include all topics
    if not scored_topics:
        scored_topics = [(topic, content, 1) for topic, content in knowledge_base.items()]
    
    # Sort by relevance and take top topics
    scored_topics.sort(key=lambda x: x[2], reverse=True)
    top_topics = scored_topics[:max_topics]
    
    # Build context
    context = "NHAI Knowledge Base:\n\n"
    for topic, content, _ in top_topics:
        content_preview = content[:500] if len(content) > 500 else content
        context += f"### {topic}\n{content_preview}\n\n"
    
    return context

# Generate response using Ollama
def generate_response_ollama(context, user_question, chat_history, model_name):
    """Generate response using local Ollama"""
    
    OLLAMA_API = "http://localhost:11434/api/chat"
    
    # Build system prompt
    system_message = f"""You are an expert AI assistant for the National Highways Authority of India (NHAI).

Your knowledge base:
{context}

Instructions:
- Answer questions using the knowledge base provided above
- Be professional, clear, and concise
- If the question is simple (like "what does NHAI stand for"), answer directly and briefly
- For complex questions, provide detailed answers from the knowledge base
- Always mention which topic/source your answer comes from when using the knowledge base
- Be helpful and friendly
- If information is not in the knowledge base, use your general knowledge about NHAI"""

    # Build messages
    messages = [
        {"role": "system", "content": system_message}
    ]
    
    # Add recent chat history (last 4 messages)
    for msg in chat_history[-4:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current question
    messages.append({
        "role": "user",
        "content": user_question
    })
    
    try:
        # Call Ollama API
        response = requests.post(
            OLLAMA_API,
            json={
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 512
                }
            },
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['message']['content']
            return answer.strip()
        else:
            return f"❌ Ollama error: {response.status_code}. Please check if Ollama is running."
            
    except requests.exceptions.ConnectionError:
        return "❌ **Cannot connect to Ollama!**\n\nPlease make sure Ollama is running:\n```\nollama serve\n```\n\nOr install Ollama from: https://ollama.ai"
    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. The model might be loading. Please try again."
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nMake sure Ollama is running with: `ollama serve`"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "initialized" not in st.session_state:
    st.session_state.initialized = False

# Main chat interface
knowledge_base = load_knowledge_base(data_folder)

if knowledge_base is None:
    st.error(f"❌ Could not find data folder: '{data_folder}'")
    st.info("📁 Please ensure the 'data' folder exists in the same directory as this script")
elif len(knowledge_base) == 0:
    st.error(f"❌ No valid text files found in '{data_folder}'")
    st.info("📝 Make sure your .txt files contain meaningful content (more than 100 characters)")
else:
    # Show welcome message
    if not st.session_state.initialized:
        st.success(f"🎉 **System Initialized!** Loaded {len(knowledge_base)} topics from NHAI knowledge base")
        st.session_state.initialized = True
    
    # Show metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Topics Loaded", len(knowledge_base))
    with col2:
        st.metric("💬 Chat Messages", len(st.session_state.messages))
    with col3:
        st.metric("🤖 AI Model", selected_model)
    
    with st.expander("📖 View All Available Topics"):
        cols = st.columns(3)
        for idx, topic in enumerate(sorted(knowledge_base.keys())):
            cols[idx % 3].markdown(f"• {topic}")
    
    st.markdown("---")
    
    # Display chat history
    if len(st.session_state.messages) == 0:
        st.info("👋 **Welcome!** Ask me anything about NHAI - policies, projects, safety initiatives, and more!")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question here... (e.g., What does NHAI stand for?)"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner(f"🤔 Thinking with {selected_model}..."):
                context = create_context(knowledge_base, prompt)
                response = generate_response_ollama(context, prompt, st.session_state.messages, selected_model)
                st.markdown(response)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: #64748b; padding: 1rem;'>
        <p><strong>NHAI AI Assistant v3.0</strong> | Powered by Ollama ({selected_model}) | Built with Streamlit</p>
        <p style='font-size: 0.8rem;'>National Highways Authority of India - 100% Local & Private AI</p>
        <p style='font-size: 0.75rem; color: #94a3b8;'>🔒 Completely Private | 🚀 No Limits | 💻 Runs Locally</p>
    </div>
""", unsafe_allow_html=True)