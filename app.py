import streamlit as st
import json
import google.generativeai as genai
from streamlit_echarts import st_echarts
from streamlit_folium import st_folium
import folium

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Atlas Agentic Council", layout="wide")

# --- 2. GEMINI CONFIG ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("GEMINI_API_KEY is missing from secrets.")
    st.stop()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- 3. SESSION STATE ---
if "dna_vector" not in st.session_state:
    st.session_state.dna_vector = {k: 50 for k in ["Adventure", "Relaxation", "Photography", "Luxury", "Budget Conscious", "Sustainability", "Culture", "Food Explorer", "Shopping", "Nightlife", "Family Focus", "Nature"]}
if "map_center" not in st.session_state: st.session_state.map_center = [20, 0]
if "map_zoom" not in st.session_state: st.session_state.map_zoom = 2
if "poi_markers" not in st.session_state: st.session_state.poi_markers = []
if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. COUNCIL LOGIC ---
def run_agent_council(user_input):
    model = genai.GenerativeModel("gemini-3.5-flash")
    prompt = f"""
    You are a travel planning agent. 
    Current DNA: {json.dumps(st.session_state.dna_vector)}.
    Current Location: {st.session_state.map_center}.
    User Request: {user_input}.
    Task: Return valid JSON (no markdown) with these keys:
    "response_text", "map_center" (list: [lat, lon]), "zoom" (int), 
    "poi_markers" (list of dicts: name, coords, type_color), "dna_updates" (dict).
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text), None
    except Exception as e:
        return None, str(e)

# --- 5. UI LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.title("🌍 Atlas Agentic Council")
    chat_container = st.container(height=500)
    
    for msg in st.session_state.messages:
        with chat_container:
            st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input("Where do you want to explore?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with chat_container:
            st.chat_message("user").write(user_input)
            with st.spinner("Atlas is planning..."):
                ai_data, error = run_agent_council(user_input)
                
                if error:
                    st.error(f"Planning Failed: {error}")
                else:
                    st.session_state.map_center = ai_data.get("map_center", [20, 0])
                    st.session_state.map_zoom = ai_data.get("zoom", 2)
                    st.session_state.poi_markers = ai_data.get("poi_markers", [])
                    
                    for k, v in ai_data.get("dna_updates", {}).items():
                        if k in st.session_state.dna_vector:
                            st.session_state.dna_vector[k] = min(100, st.session_state.dna_vector[k] + v)
                    
                    st.chat_message("assistant").write(ai_data["response_text"])
                    st.session_state.messages.append({"role": "assistant", "content": ai_data["response_text"]})
        st.rerun()

with col2:
    st.subheader("🧬 Travel DNA")
    st_echarts(options={"radar": {"indicator": [{"name": k, "max": 100} for k in st.session_state.dna_vector.keys()]}, 
                        "series": [{"type": "radar", "data": [{"value": list(st.session_state.dna_vector.values())}]}]}, height="300px")

    st.subheader("📍 Interactive Map")
    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom, tiles="CartoDB positron")
    for poi in st.session_state.poi_markers:
        folium.Marker(location=poi["coords"], popup=poi["name"], icon=folium.Icon(color=poi.get("type_color", "blue"))).add_to(m)
    st_folium(m, height=400, use_container_width=True)
