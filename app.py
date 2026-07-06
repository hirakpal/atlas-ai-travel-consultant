import streamlit as st
import os
import json
import google.generativeai as genai
from streamlit_echarts import st_echarts
from streamlit_folium import st_folium
import folium

# --- 1. CONFIG & STATE ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Add missing coordinates dictionary
CITY_COORDINATES = {
    "Bali": [-8.3405, 115.0920], 
    "Lisbon": [38.7223, -9.1393], 
    "Kyoto": [35.0116, 135.7681],
    "Delhi": [28.6139, 77.2090]
}

if "dna_vector" not in st.session_state:
    st.session_state.dna_vector = {k: 50 for k in ["Adventure", "Relaxation", "Photography", "Luxury", "Budget Conscious", "Sustainability", "Culture", "Food Explorer", "Shopping", "Nightlife", "Family Focus", "Nature"]}
if "messages" not in st.session_state: st.session_state.messages = []
if "shortlist" not in st.session_state: st.session_state.shortlist = []

# --- 2. THE COUNCIL LOGIC (Multi-Agent Loop) ---
# --- ATOMIC COUNCIL LOGIC ---
def run_agent_council(user_input):
    model = genai.GenerativeModel('gemini-3.5-flash')
    config = {"response_mime_type": "application/json"}
    
    # Combined Prompt: Generator & Critic in ONE call for speed
    prompt = f"""
    You are Atlas, a luxury travel consultant. 
    Current DNA: {st.session_state.dna_vector}. 
    User: {user_input}. 
    Act as a Council: First, generate a plan. Second, critique your own plan.
    Return JSON: {{
        "response_text": "text", 
        "dna_updates": {{"Adventure": 5}}, 
        "shortlist": ["City1"]
    }}
    """
    
    # Set a timeout for the API call
    try:
        response = model.generate_content(prompt, generation_config=config, request_options={"timeout": 10})
        return json.loads(response.text)
    except Exception as e:
        return {"response_text": "I had trouble connecting. Let's try again?", "dna_updates": {}, "shortlist": []}
# --- ATOMIC UI EXECUTION ---
if user_input := st.chat_input("Tell Atlas where you want to go..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display status
    with st.status("Agent Council working...", expanded=True) as status:
        ai_data = run_agent_council(user_input)
        
        # Immediate state update
        for k, v in ai_data.get("dna_updates", {}).items():
            st.session_state.dna_vector[k] += v
        st.session_state.shortlist = ai_data.get("shortlist", [])
        
        status.update(label="Planning Complete!", state="complete")
        
    st.session_state.messages.append({"role": "assistant", "content": ai_data["response_text"]})
    st.rerun() # Force UI refresh
# --- 3. UI LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🤖 Atlas - AI Travel Consultant")
    # --- ADD THE PILLBOX HERE ---
    st.markdown("""
        <div style="display:flex; gap: 10px; margin-bottom: 20px;">
            <span style="padding: 5px 12px; border-radius: 15px; background: #1f2937; color: #60a5fa; font-size: 11px; border: 1px solid #374151;">● Researcher</span>
            <span style="padding: 5px 12px; border-radius: 15px; background: #1f2937; color: #34d399; font-size: 11px; border: 1px solid #374151;">● Generator</span>
            <span style="padding: 5px 12px; border-radius: 15px; background: #1f2937; color: #f87171; font-size: 11px; border: 1px solid #374151;">● Critic</span>
        </div>
    """, unsafe_allow_html=True)
    chat_container = st.container(height=500)
    for msg in st.session_state.messages:
        with chat_container: st.chat_message(msg["role"]).write(msg["content"])



with col2:
    # Radar
    st.subheader("Travel DNA Profile")
    st_echarts(options={"radar": {"indicator": [{"name": k, "max": 100} for k in st.session_state.dna_vector.keys()]}, "series": [{"type": "radar", "data": [{"value": list(st.session_state.dna_vector.values()), "itemStyle": {"color": "#00f2ff"}}]}]}, height="280px")
    
    # Interactive Map
    st.subheader("Destinations shortlist")
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")
    for city in st.session_state.shortlist:
        folium.Marker(location=CITY_COORDINATES.get(city, [0, 0]), tooltip=city).add_to(m)
    st_folium(m, height=300, use_container_width=True)
