import streamlit as st
import google.generativeai as genai

st.title("Connection Audit")

# 1. Check if key exists
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Error: GEMINI_API_KEY is not defined in Streamlit secrets.")
    st.stop()

def run_agent_council(user_input):
    # Using the model that we just confirmed works!
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # We remove the "response_mime_type" config to ensure compatibility
    prompt = f"""
    You are the Atlas Council. Current DNA: {json.dumps(st.session_state.dna_vector)}.
    User Request: {user_input}.
    Return a clean JSON object (and nothing else) with these keys:
    "response_text", "map_center", "zoom", "poi_markers", "dna_updates".
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's valid JSON
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text), None
    except Exception as e:
        return None, str(e)
