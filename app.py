import streamlit as st
import json
import google.generativeai as genai
from streamlit_echarts import st_echarts
from streamlit_folium import st_folium
import folium

# --- 1. CONFIG ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

if "dna_vector" not in st.session_state:
    st.session_state.dna_vector = {k: 50 for k in ["Adventure", "Relaxation", "Photography", "Luxury", "Budget Conscious", "Sustainability", "Culture", "Food Explorer", "Shopping", "Nightlife", "Family Focus", "Nature"]}
if "map_center" not in st.session_state: st.session_state.map_center = [20, 0]
if "map_zoom" not in st.session_state: st.session_state.map_zoom = 2
if "poi_markers" not in st.session_state: st.session_state.poi_markers = []
if "messages" not in st.session_state: st.session_state.messages = []

# --- AUDIT & TRANSLATION HELPER ---
def translate_error(error_msg):
    # Translates raw API errors into human-friendly explanations
    if "404" in error_msg: return "I'm having trouble connecting to my specialized planning module. Please check my model access."
    if "401" in error_msg or "403" in error_msg: return "I don't have permission to access the planning tools. Please check my API configuration."
    if "JSON" in error_msg: return "I had a moment of confusion and couldn't format the travel plan correctly. Let me try again."
    return f"I encountered an unexpected hiccup: {error_msg}"

# --- 2. VIRTUAL COUNCIL (Agentic Orchestration) ---
def run_agent_council(user_input):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Current DNA: {json.dumps(st.session_state.dna_vector)}. Request: {user_input}. Return ONLY JSON: {{\"response_text\": \"...\", \"map_center\": [0,0], \"zoom\": 2, \"poi_markers\": [], \"dna_updates\": {{}}}}"
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        # Audit: Log the raw response to the terminal for debugging
        print(f"AUDIT LOG - Raw Response: {response.text}")
        return json.loads(response.text.strip()), None
    except Exception as e:
        return None, str(e)

# --- 3. UI LAYOUT ---
st.set_page_config(layout="wide")
col1, col2 = st.columns([1, 1])

with col1:
    st.title("🌍 Atlas Agentic Council")
    chat_container = st.container(height=500)
    for msg in st.session_state.messages:
        with chat_container: st.chat_message(msg["role"]).write(msg["content"])

if user_input := st.chat_input("Where do you want to explore?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with chat_container: st.chat_message("user").write(user_input)
    
    with chat_container:
        with st.status("Atlas is planning...", expanded=True) as status:
            ai_data, error = run_agent_council(user_input)
            
            if error:
                friendly_msg = translate_error(error)
                st.error(f"Atlas Log: {friendly_msg}")
                status.update(label="Planning Failed", state="error")
            else:
                # Update State only if success
                st.session_state.map_center = ai_data.get("map_center", [20, 0])
                st.session_state.map_zoom = ai_data.get("zoom", 2)
                st.session_state.poi_markers = ai_data.get("poi_markers", [])
                
                st.chat_message("assistant").write(ai_data.get("response_text", "Ready!"))
                st.session_state.messages.append({"role": "assistant", "content": ai_data["response_text"]})
                status.update(label="Planning Complete!", state="complete")
        st.rerun()
with col2:
    st.subheader("📍 Interactive Map")
    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom, tiles="CartoDB positron")
    for poi in st.session_state.poi_markers:
        folium.Marker(location=poi["coords"], popup=poi["name"], icon=folium.Icon(color=poi["type_color"])).add_to(m)
    st_folium(m, height=500, use_container_width=True)
