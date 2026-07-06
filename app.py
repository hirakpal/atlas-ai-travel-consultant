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

# --- 2. VIRTUAL COUNCIL (Agentic Orchestration) ---
def run_agent_council(user_input):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # The Council Prompt defines the multi-step persona
    prompt = f"""
    You are the Atlas Council (Researcher, Generator, Critic).
    Current State: {json.dumps(st.session_state.dna_vector)}
    User Request: {user_input}
    
    Task: 
    1. Researcher: Find coordinates/location data for the user request.
    2. Generator: Create a travel plan and suggest relevant POIs (Hotels/Cafes).
    3. Critic: Review the plan for luxury and feasibility.
    
    Return ONLY JSON:
    {{
        "response_text": "text",
        "map_center": [lat, lon],
        "zoom": 12,
        "poi_markers": [{{"name": "Hotel A", "coords": [lat, lon], "type_color": "blue"}}],
        "dna_updates": {{"Adventure": 5}}
    }}
    """
    
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)

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
        with st.chat_message("assistant"):
            with st.status("Council is deliberating...", expanded=True) as status:
                ai_data = run_agent_council(user_input)
                
                # Update State
                st.session_state.map_center = ai_data["map_center"]
                st.session_state.map_zoom = ai_data["zoom"]
                st.session_state.poi_markers = ai_data["poi_markers"]
                for k, v in ai_data.get("dna_updates", {}).items():
                    st.session_state.dna_vector[k] += v
                
                status.update(label="Council Decision Complete", state="complete")
            st.write(ai_data["response_text"])
        st.session_state.messages.append({"role": "assistant", "content": ai_data["response_text"]})
        st.rerun()

with col2:
    st.subheader("📍 Interactive Map")
    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom, tiles="CartoDB positron")
    for poi in st.session_state.poi_markers:
        folium.Marker(location=poi["coords"], popup=poi["name"], icon=folium.Icon(color=poi["type_color"])).add_to(m)
    st_folium(m, height=500, use_container_width=True)
