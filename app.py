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

if "profile" not in st.session_state:
    st.session_state.profile = {
        "essential_trip_info": {"destination": None, "travel_dates": None, "budget_range": None, "traveler_count": None},
        "inferred_preferences": [],
        "long_term_traits": []
    }

if "map_center" not in st.session_state: st.session_state.map_center = [20, 0]
if "map_zoom" not in st.session_state: st.session_state.map_zoom = 2
if "poi_markers" not in st.session_state: st.session_state.poi_markers = []
if "messages" not in st.session_state: st.session_state.messages = []

# Audit log initialization
if "audit_trail" not in st.session_state:
    st.session_state.audit_trail = []

def log_audit(status, event_type, details):
    """Appends an operational record to our system log."""
    st.session_state.audit_trail.insert(0, {
        "status": status,
        "type": event_type,
        "details": details
    })

# --- 4. ENGINE LOGIC ---
def run_agent_council(user_input):
    model = genai.GenerativeModel("gemini-3.5-flash")
    
    prompt = f"""
    You are the Atlas Agentic Council. Your objective is to build a rich conversational profile for a traveler while simultaneously satisfying a state-driven travel plan.

    CURRENT PROFILE STATE:
    {json.dumps(st.session_state.profile)}
    
    CURRENT TRAVEL DNA MATRIX:
    {json.dumps(st.session_state.dna_vector)}

    USER REQUEST/RESPONSE:
    "{user_input}"

    TASK PROTOCOL:
    1. EXTRACT variables for 'destination', 'travel_dates', 'budget_range', 'traveler_count'.
    2. If fields are missing, ask an organic follow-up question. 
    3. Deduce long term traits and update DNA matrix properties using deltas.

    OUTPUT SPECS: Return a clean, valid raw JSON object string ONLY. Do not include markdown wraps (like ```json). Use these exact keys:
    {{
        "response_text": "text",
        "essential_trip_info": {{ "destination": val, "travel_dates": val, "budget_range": val, "traveler_count": val }},
        "inferred_preferences": [],
        "long_term_traits": [],
        "dna_updates": {{}},
        "map_center": [lat, lon],
        "zoom": int,
        "poi_markers": [ {{ "name": "string", "coords": [lat, lon], "type_color": "string" }} ]
    }}
    """
    try:
        log_audit("INFO", "API Request Outbound", f"Prompt text prepared for input: '{user_input}'")
        response = model.generate_content(prompt)
        raw_text = response.text
        log_audit("INFO", "API Response Inbound", f"Raw text returned from LLM: {raw_text[:200]}...")
        
        # Clean potential markdown string responses safely
        clean_text = raw_text.replace('```json', '').replace('```', '').strip()
        parsed_json = json.loads(clean_text)
        
        log_audit("SUCCESS", "JSON Parse Complete", "Successfully converted text engine to local dictionary schema.")
        return parsed_json, None
    except Exception as e:
        error_msg = str(e)
        log_audit("CRITICAL", "Engine Call Failed", f"Exception dropped during generation/parsing: {error_msg}")
        return None, error_msg

# --- 5. AUDIT TRAIL SIDEBAR (The 3rd Column/Panel) ---
with st.sidebar:
    st.title("🛡️ System Audit Trail")
    st.caption("Live pipeline execution state updates & error reporting.")
    
    if st.button("Clear Audit Log"):
        st.session_state.audit_trail = []
        st.rerun()
        
    st.write("---")
    
    if not st.session_state.audit_trail:
        st.info("No system transactions captured yet.")
    else:
        for log in st.session_state.audit_trail:
            if log["status"] == "CRITICAL":
                st.error(f"**[{log['status']}] {log['type']}**\n\n{log['details']}")
            elif log["status"] == "SUCCESS":
                st.success(f"**[{log['status']}] {log['type']}**\n\n{log['details']}")
            else:
                st.info(f"**[{log['status']}] {log['type']}**\n\n{log['details']}")

# --- 6. MAIN UI LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.title("🌍 Atlas Agentic Council")
    
    chat_box = st.container(height=450)
    with chat_box:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input("Where do you want to explore?"):
        with chat_box:
            st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Council is deliberating..."):
            ai_data, error = run_agent_council(user_input)
            
            if error:
                # Error is no longer hidden! It's explicitly logged to the screen
                st.error(f"Execution Halted. Review the System Audit Trail in the sidebar.")
            else:
                # Apply data properties safely
                for key in st.session_state.profile["essential_trip_info"].keys():
                    if ai_data.get("essential_trip_info", {}).get(key):
                        st.session_state.profile["essential_trip_info"][key] = ai_data["essential_trip_info"][key]
                
                st.session_state.profile["inferred_preferences"] = list(set(st.session_state.profile["inferred_preferences"] + ai_data.get("inferred_preferences", [])))
                st.session_state.profile["long_term_traits"] = list(set(st.session_state.profile["long_term_traits"] + ai_data.get("long_term_traits", [])))
                
                st.session_state.map_center = ai_data.get("map_center", st.session_state.map_center)
                st.session_state.map_zoom = ai_data.get("zoom", st.session_state.map_zoom)
                st.session_state.poi_markers = ai_data.get("poi_markers", st.session_state.poi_markers)
                
                for k, v in ai_data.get("dna_updates", {}).items():
                    if k in st.session_state.dna_vector:
                        st.session_state.dna_vector[k] = max(0, min(100, st.session_state.dna_vector[k] + v))
                
                with chat_box:
                    st.chat_message("assistant").write(ai_data["response_text"])
                st.session_state.messages.append({"role": "assistant", "content": ai_data["response_text"]})
        st.rerun()

    with st.expander("🔍 Real-time Profile JSON Schema Tracker", expanded=False):
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
