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

# --- 3. SESSION STATE CONFIG ---
if "dna_vector" not in st.session_state:
    st.session_state.dna_vector = {k: 50 for k in ["Adventure", "Relaxation", "Photography", "Luxury", "Budget Conscious", "Sustainability", "Culture", "Food Explorer", "Shopping", "Nightlife", "Family Focus", "Nature"]}

# Core Profiling State Machinery
if "profile" not in st.session_state:
    st.session_state.profile = {
        "essential_trip_info": {
            "destination": None,
            "travel_dates": None,
            "budget_range": None,
            "traveler_count": None
        },
        "inferred_preferences": [],
        "long_term_traits": []
    }

if "map_center" not in st.session_state: st.session_state.map_center = [20, 0]
if "map_zoom" not in st.session_state: st.session_state.map_zoom = 2
if "poi_markers" not in st.session_state: st.session_state.poi_markers = []
if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. ENGINE LOGIC ---
def run_agent_council(user_input):
    model = genai.GenerativeModel("gemini-3.5-flash")
    
    prompt = f"""
    You are the Atlas Agentic Council. Your objective is to build a rich conversational profile for a traveler while simultaneously satisfying a state-driven travel plan.

    CURRENT PROFILE STATE:
    {json.dumps(st.session_state.profile, indent=2)}
    
    CURRENT TRAVEL DNA MATRIX:
    {json.dumps(st.session_state.dna_vector, indent=2)}

    USER REQUEST/RESPONSE:
    "{user_input}"

    TASK PROTOCOL:
    1. EXTRACT: Read the user's input. Parse out destinations, explicit trip information, or implicit style indicators.
    2. CONTEXT CHECK: 
       - Look closely at "essential_trip_info". If any keys ('destination', 'travel_dates', 'budget_range', 'traveler_count') are null, look for them in the user input and populate them.
       - If some essential keys are still missing, your "response_text" MUST focus primarily on asking a context-aware follow-up question to discover those variables.
       - If all essential keys are filled, pivot entirely to recommending contextual POIs and customized insights.
    3. INFER TRAITS: Dynamically deduce long term traits or short term preferences based on user wording (e.g. "I love walking around historical sites" means adding 'History Buff' to long_term_traits and incrementing 'Culture' in DNA).

    OUTPUT SPECS: Return a clean, valid raw JSON object string. Do not include markdown wraps (like ```json). Use these exact keys:
    {{
        "response_text": "Your direct message or progressive profiling question to the user",
        "essential_trip_info": {{ "destination": "string or null", "travel_dates": "string or null", "budget_range": "string or null", "traveler_count": "string or null" }},
        "inferred_preferences": ["list of strings"],
        "long_term_traits": ["list of strings"],
        "dna_updates": {{ "DNA_Key": integer_delta_to_add_or_subtract }},
        "map_center": [lat, lon],
        "zoom": int,
        "poi_markers": [ {{ "name": "POI Name", "coords": [lat, lon], "type_color": "blue/red/green/orange" }} ]
    }}
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
    
    # Static Chat Box Container
    chat_box = st.container(height=450)
    with chat_box:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input("Where do you want to explore?"):
        with chat_box:
            st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Council is building your profiling architecture..."):
            ai_data, error = run_agent_council(user_input)
            
            if error:
                st.error(f"Council Deliberation Error: {error}")
            else:
                # Atomically Update Profile Variables
                for key in st.session_state.profile["essential_trip_info"].keys():
                    if ai_data.get("essential_trip_info", {}).get(key):
                        st.session_state.profile["essential_trip_info"][key] = ai_data["essential_trip_info"][key]
                
                # Append traits without duplicating
                st.session_state.profile["inferred_preferences"] = list(set(st.session_state.profile["inferred_preferences"] + ai_data.get("inferred_preferences", [])))
                st.session_state.profile["long_term_traits"] = list(set(st.session_state.profile["long_term_traits"] + ai_data.get("long_term_traits", [])))
                
                # Update Map State
                st.session_state.map_center = ai_data.get("map_center", st.session_state.map_center)
                st.session_state.map_zoom = ai_data.get("zoom", st.session_state.map_zoom)
                st.session_state.poi_markers = ai_data.get("poi_markers", st.session_state.poi_markers)
                
                # Mutate DNA Matrix Vector
                for k, v in ai_data.get("dna_updates", {}).items():
                    if k in st.session_state.dna_vector:
                        st.session_state.dna_vector[k] = max(0, min(100, st.session_state.dna_vector[k] + v))
                
                # Write Assistant Output & Save
                with chat_box:
                    st.chat_message("assistant").write(ai_data["response_text"])
                st.session_state.messages.append({"role": "assistant", "content": ai_data["response_text"]})
        st.rerun()

    # Profiling Verification Pane
    with st.expander("🔍 Real-time Profile JSON Schema Tracker", expanded=True):
        st.json(st.session_state.profile)

with col2:
    st.subheader("🧬 Evolving Travel DNA")
    st_echarts(options={
        "radar": {"indicator": [{"name": k, "max": 100} for k in st.session_state.dna_vector.keys()]}, 
        "series": [{"type": "radar", "data": [{"value": list(st.session_state.dna_vector.values())}]}]
    }, height="280px")

    st.subheader("📍 Interactive Map Engine")
    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom, tiles="CartoDB positron")
    for poi in st.session_state.poi_markers:
        folium.Marker(
            location=poi["coords"], 
            popup=poi["name"], 
            icon=folium.Icon(color=poi.get("type_color", "blue"))
        ).add_to(m)
    st_folium(m, height=350, use_container_width=True)
