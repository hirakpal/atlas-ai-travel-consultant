import streamlit as st
import os
import json
import google.generativeai as genai
from streamlit_echarts import st_echarts
from streamlit_folium import st_folium
import folium

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Atlas AI Travel Consultant", page_icon="🌍", layout="wide")

# --- 2. GEMINI CONFIG ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("GEMINI_API_KEY is missing from Streamlit secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- 3. DATA & STATE ---
DNA_KEYS = ["Adventure", "Relaxation", "Photography", "Luxury", "Budget Conscious", "Sustainability", "Culture", "Food Explorer", "Shopping", "Nightlife", "Family Focus", "Nature"]
CITY_COORDINATES = {"Bali": [-8.3405, 115.0920], "Lisbon": [38.7223, -9.1393], "Kyoto": [35.0116, 135.7681], "Delhi": [28.6139, 77.2090], "Tokyo": [35.6762, 139.6503], "Paris": [48.8566, 2.3522], "London": [51.5074, -0.1278], "Rome": [41.9028, 12.4964]}

if "dna_vector" not in st.session_state: st.session_state.dna_vector = {k: 50 for k in DNA_KEYS}
if "messages" not in st.session_state: st.session_state.messages = []
if "shortlist" not in st.session_state: st.session_state.shortlist = []

# --- 4. HELPERS ---
def update_dna(dna_updates):
    for key, value in dna_updates.items():
        if key in st.session_state.dna_vector:
            st.session_state.dna_vector[key] = max(0, min(100, st.session_state.dna_vector[key] + int(value)))

def run_agent_council(user_input):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"""You are Atlas, a travel consultant. 
    Current DNA: {json.dumps(st.session_state.dna_vector)}. 
    Request: {user_input}. 
    Return ONLY JSON: {{"response_text": "...", "dna_updates": {{"Adventure": 5}}, "shortlist": ["Bali"]}}"""

    try:
        response = model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        # RETURN THE ACTUAL ERROR TO THE CHAT
        return {
            "response_text": f"DEBUG ERROR: {str(e)}", 
            "dna_updates": {}, 
            "shortlist": []
        }

# --- 5. UI ---
left, right = st.columns([1, 1])

with left:
    st.title("🌍 Atlas AI Travel Consultant")
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Tell Atlas where you want to travel..."):
        # Display User Input
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # AI Processing
        with st.chat_message("assistant"):
            with st.status("Atlas is planning...", expanded=True) as status:
                ai_data = run_agent_council(user_input)
                update_dna(ai_data.get("dna_updates", {}))
                st.session_state.shortlist = ai_data.get("shortlist", [])
                status.update(label="Planning Complete!", state="complete")
            
            st.write(ai_data["response_text"])
        
        st.session_state.messages.append({"role": "assistant", "content": ai_data["response_text"]})
        st.rerun()

with right:
    st.subheader("🧬 Travel DNA")
    st_echarts(options={"radar": {"indicator": [{"name": k, "max": 100} for k in st.session_state.dna_vector.keys()]}, "series": [{"type": "radar", "data": [{"value": list(st.session_state.dna_vector.values())}]}]}, height="350px")

    st.subheader("📍 Shortlisted Destinations")
    travel_map = folium.Map(location=[20, 0], zoom_start=2)
    for city in st.session_state.shortlist:
        if city in CITY_COORDINATES:
            folium.Marker(location=CITY_COORDINATES[city], tooltip=city).add_to(travel_map)
    st_folium(travel_map, height=350, use_container_width=True)
