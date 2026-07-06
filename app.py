import streamlit as st
import os
import json
import google.generativeai as genai
from streamlit_echarts import st_echarts
from streamlit_folium import st_folium
import folium

# --- 1. CONFIG & STATE ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
if "dna_vector" not in st.session_state:
    st.session_state.dna_vector = {k: 50 for k in ["Adventure", "Relaxation", "Photography", "Luxury", "Budget Conscious", "Sustainability", "Culture", "Food Explorer", "Shopping", "Nightlife", "Family Focus", "Nature"]}
if "messages" not in st.session_state: st.session_state.messages = []
if "shortlist" not in st.session_state: st.session_state.shortlist = []

# --- 2. THE COUNCIL LOGIC (Multi-Agent Loop) ---
def run_agent_council(user_input):
    model = genai.GenerativeModel('gemini-1.5-flash')
    config = {"response_mime_type": "application/json"}
    
    # STEP 1: Generator Node
    prompt_gen = f"Current DNA: {st.session_state.dna_vector}. User: {user_input}. Return JSON: {{'response_text': '...', 'dna_updates': {{'Adventure': 5}}, 'shortlist': ['City1', 'City2']}}"
    res_gen = model.generate_content(prompt_gen, generation_config=config)
    plan = json.loads(res_gen.text)
    
    # STEP 2: Critic Node (The missing logic)
    prompt_crit = f"Critique this travel plan: {plan}. Is it aligned with DNA: {st.session_state.dna_vector}? Return JSON: {{'is_approved': true/false, 'feedback': '...'}}"
    res_crit = model.generate_content(prompt_crit, generation_config=config)
    critique = json.loads(res_crit.text)
    
    # STEP 3: Fallback if Critic rejects
    if not critique['is_approved']:
        plan['response_text'] += f"\n\n*Atlas Note: {critique['feedback']}*"
        
    return plan

# --- 3. UI LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    chat_container = st.container(height=500)
    for msg in st.session_state.messages:
        with chat_container: st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input("Tell Atlas where you want to go..."):
        with chat_container:
            st.chat_message("user").write(user_input)
            with st.status("Agent Council working...", expanded=True) as status:
                ai_data = run_agent_council(user_input)
                # Update State
                for k, v in ai_data.get("dna_updates", {}).items(): st.session_state.dna_vector[k] += v
                st.session_state.shortlist = ai_data.get("shortlist", [])
                status.update(label="Council approved plan!", state="complete")
            
            st.chat_message("assistant").write(ai_data["response_text"])
            st.session_state.messages.extend([{"role": "user", "content": user_input}, {"role": "assistant", "content": ai_data["response_text"]}])
            st.rerun()

with col2:
    # Radar
    st_echarts(options={"radar": {"indicator": [{"name": k, "max": 100} for k in st.session_state.dna_vector.keys()]}, "series": [{"type": "radar", "data": [{"value": list(st.session_state.dna_vector.values()), "itemStyle": {"color": "#00f2ff"}}]}]}, height="400px")
    
    # Interactive Map
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")
    for city in st.session_state.shortlist:
        folium.Marker(location=[0, 0], popup=city).add_to(m) # Note: You'd use a geocoding API here to get real coordinates
    st_folium(m, height=300)
