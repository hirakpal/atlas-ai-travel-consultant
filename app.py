import streamlit as st
import os
import json
import google.generativeai as genai
from streamlit_echarts import st_echarts
from streamlit_folium import st_folium
import folium

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Atlas AI Travel Consultant",
    page_icon="🌍",
    layout="wide"
)

# ======================================================
# GEMINI CONFIG
# ======================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY is missing")
    st.stop()

genai.configure(api_key=api_key)

# ======================================================
# DATA
# ======================================================

DNA_KEYS = [
    "Adventure",
    "Relaxation",
    "Photography",
    "Luxury",
    "Budget Conscious",
    "Sustainability",
    "Culture",
    "Food Explorer",
    "Shopping",
    "Nightlife",
    "Family Focus",
    "Nature"
]

CITY_COORDINATES = {
    "Bali": [-8.3405, 115.0920],
    "Lisbon": [38.7223, -9.1393],
    "Kyoto": [35.0116, 135.7681],
    "Delhi": [28.6139, 77.2090],
    "Tokyo": [35.6762, 139.6503],
    "Paris": [48.8566, 2.3522],
    "London": [51.5074, -0.1278],
    "Rome": [41.9028, 12.4964]
}

# ======================================================
# SESSION STATE
# ======================================================

if "dna_vector" not in st.session_state:
    st.session_state.dna_vector = {k: 50 for k in DNA_KEYS}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "shortlist" not in st.session_state:
    st.session_state.shortlist = []

# ======================================================
# HELPERS
# ======================================================

def clamp(value):
    return max(0, min(100, value))

def update_dna(dna_updates):
    for key, value in dna_updates.items():
        if key in st.session_state.dna_vector:
            st.session_state.dna_vector[key] = clamp(
                st.session_state.dna_vector[key] + int(value)
            )

# ======================================================
# AI
# ======================================================

def run_agent_council(user_input):

    model = genai.GenerativeModel("gemini-3.5-flash")

    prompt = f"""
You are Atlas, a premium travel consultant.

Current Travel DNA:
{json.dumps(st.session_state.dna_vector)}

User Request:
{user_input}

Return ONLY JSON:

{{
    "response_text": "recommended trip",
    "dna_updates": {{
        "Adventure": 5
    }},
    "shortlist": ["Bali", "Kyoto"]
}}
"""

    try:

        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json"
            }
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "")
            text = text.replace("```", "").strip()

        return json.loads(text)

    except Exception:
        return {
            "response_text": "Unable to generate recommendation.",
            "dna_updates": {},
            "shortlist": []
        }

# ======================================================
# UI
# ======================================================

left, right = st.columns([1, 1])

# ======================================================
# LEFT PANEL
# ======================================================

with left:

    st.title("🌍 Atlas AI Travel Consultant")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input(
        "Tell Atlas where you want to travel...",
        key="atlas_chat"
    )

    if user_input:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        with st.status("Atlas is planning...", expanded=True):

            ai_data = run_agent_council(user_input)

            update_dna(
                ai_data.get("dna_updates", {})
            )

            st.session_state.shortlist = ai_data.get(
                "shortlist",
                []
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": ai_data["response_text"]
            }
        )

        st.rerun()

# ======================================================
# RIGHT PANEL
# ======================================================

with right:

    st.subheader("🧬 Travel DNA")

    radar_options = {
        "radar": {
            "indicator": [
                {
                    "name": key,
                    "max": 100
                }
                for key in st.session_state.dna_vector.keys()
            ]
        },
        "series": [
            {
                "type": "radar",
                "data": [
                    {
                        "value": list(
                            st.session_state.dna_vector.values()
                        )
                    }
                ]
            }
        ]
    }

    st_echarts(
        options=radar_options,
        height="350px"
    )

    st.subheader("📍 Shortlisted Destinations")

    travel_map = folium.Map(
        location=[20, 0],
        zoom_start=2
    )

    for city in st.session_state.shortlist:

        if city in CITY_COORDINATES:

            folium.Marker(
                location=CITY_COORDINATES[city],
                tooltip=city
            ).add_to(travel_map)

    st_folium(
        travel_map,
        height=350,
        use_container_width=True
    )

    if st.session_state.shortlist:

        st.subheader("⭐ Recommendations")

        for city in st.session_state.shortlist:
            st.success(city)
