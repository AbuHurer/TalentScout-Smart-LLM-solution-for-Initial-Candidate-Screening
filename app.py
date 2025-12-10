import streamlit as st
import google.generativeai as genai
import json
import os
import time

# --- Configuration & Setup ---
st.set_page_config(
    page_title="TalentScout | AI Hiring Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "interview_active" not in st.session_state:
    st.session_state.interview_active = True

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "models/gemini-pro" # Fallback default

# --- System Prompt Design ---
SYSTEM_PROMPT = """
You are 'TalentScout', a professional, friendly, and efficient AI recruitment assistant for a tech agency.

YOUR GOAL:
Conduct a preliminary screening interview with a candidate.

PHASE 1: INFORMATION GATHERING
You must collect the following information. Do not ask for everything at once. Ask for 1-2 items at a time naturally.
1. Full Name
2. Email Address
3. Phone Number
4. Years of Experience
5. Desired Position(s)
6. Current Location
7. Tech Stack (Languages, Frameworks, Tools)

PHASE 2: TECHNICAL SCREENING
Once you have ALL the information above:
1. Acknowledge the tech stack.
2. Ask exactly 3 technical conceptual questions based specifically on the user's declared tech stack.
3. Ask these questions ONE BY ONE. Wait for the user's answer before asking the next.
4. After the user answers, give a very brief (1 sentence) feedback or acknowledgment, then ask the next question.

PHASE 3: CONCLUSION
After 3 technical questions:
1. Thank the candidate.
2. Inform them that a human recruiter will review their profile and reach out via email.
3. Type exactly "End of Interview." to signal the conversation is over.

CONSTRAINTS:
- Maintain a professional but conversational tone.
- If the user deviates, politely bring them back to the topic.
- If the user wants to stop, say "Goodbye".
- Keep responses concise.
"""

# --- Helper Functions ---

def get_available_models(api_key):
    """Fetches available models that support content generation."""
    try:
        genai.configure(api_key=api_key)
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return models
    except Exception as e:
        st.sidebar.error(f"Error fetching models: {e}")
        return ["models/gemini-pro"] # Safe fallback

def init_chat():
    """Initialize the chat with a greeting if history is empty."""
    if not st.session_state.messages:
        greeting = "Hello! I am TalentScout, your virtual recruitment assistant. I'm here to gather some basic information and discuss your technical background. To get started, could you please tell me your full name?"
        st.session_state.messages.append({"role": "model", "parts": [greeting]})

def get_gemini_response(user_input, api_key, model_name):
    """Interacts with the Gemini API to get the next response."""
    if not api_key:
        return "Please enter your API Key in the sidebar to proceed."

    try:
        genai.configure(api_key=api_key)
        # Clean up model name if needed (remove 'models/' prefix if user selects it, though SDK usually handles it)
        active_model = genai.GenerativeModel(model_name)
        
        # Construct chat history for the API
        chat_history = []
        # Add system prompt as the first piece of context (Developer instruction)
        chat_history.append({"role": "user", "parts": [SYSTEM_PROMPT]}) 
        chat_history.append({"role": "model", "parts": ["Understood. I am ready to act as TalentScout."]})
        
        # Append actual conversation
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["parts"][0]]})
            
        # Add current user input
        chat_history.append({"role": "user", "parts": [user_input]})

        # Add Safety Settings to prevent aggressive blocking of technical terms
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]

        response = active_model.generate_content(chat_history, safety_settings=safety_settings)
        
        # Robustly handle the response text
        try:
            return response.text
        except ValueError:
            # This occurs if the response was blocked by safety filters
            return "I apologize, but I couldn't generate a response to that. Could you please rephrase?"
            
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI Layout ---

# Sidebar for Settings
with st.sidebar:
    st.title("🔧 Configuration")
    api_key = st.text_input("Enter Google Gemini API Key", type="password")
    
    st.divider()
    
    # Model Selection Logic
    st.subheader("Model Selection")
    if api_key:
        # Check if we need to fetch models (only once or on button press)
        if st.button("Fetch Available Models"):
            with st.spinner("Checking your available models..."):
                available_models = get_available_models(api_key)
                st.session_state.available_models = available_models
        
        if "available_models" in st.session_state:
            st.session_state.selected_model = st.selectbox(
                "Select Model", 
                st.session_state.available_models,
                index=0
            )
        else:
            st.warning("Click 'Fetch' to see models available to your key.")
            # Default fallback input if fetch fails or hasn't run
            st.session_state.selected_model = st.text_input("Or type model name manually:", "models/gemini-1.5-flash")
    else:
        st.info("Enter API Key to configure model.")

    st.divider()
    st.caption("Common Models: gemini-1.5-flash, gemini-pro, gemini-1.5-pro-latest")
    
    st.divider()
    
    st.subheader("Debug / Admin View")
    if st.checkbox("Show Conversation State"):
        if "messages" in st.session_state:
            st.json(st.session_state.messages)

# Main Chat Interface
st.title("🤖 TalentScout")
st.markdown("### AI-Powered Technical Recruitment Screen")
st.markdown("---")

init_chat()

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["parts"][0])

# Chat Input
if st.session_state.interview_active:
    if user_input := st.chat_input("Type your answer here..."):
        # 1. Display User Message
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "parts": [user_input]})

        # 2. Generate AI Response
        with st.chat_message("model"):
            if not api_key:
                st.error("Please enter your API Key in the sidebar.")
            else:
                with st.spinner("TalentScout is thinking..."):
                    response_text = get_gemini_response(user_input, api_key, st.session_state.selected_model)
                    st.write(response_text)
                
                # 3. Update History
                st.session_state.messages.append({"role": "model", "parts": [response_text]})
                
                # 4. Check for Conversation End
                if "End of Interview" in response_text or "Goodbye" in response_text:
                    st.session_state.interview_active = False
                    st.success("Interview Completed. Data safely stored (simulated).")
                    
                    # Simulate Data Saving
                    with st.expander("📄 View Transcript (Simulated Backend)"):
                        transcript = [f"{m['role'].upper()}: {m['parts'][0]}" for m in st.session_state.messages]
                        st.text_area("Transcript", value="\n\n".join(transcript), height=300)

else:
    st.info("This session has ended. Refresh the page to start a new interview.")

# --- Footer ---
st.markdown("---")
st.caption("TalentScout AI v1.0 | Powered by Google Gemini & Streamlit | Privacy Notice: No data is permanently stored in this demo.")