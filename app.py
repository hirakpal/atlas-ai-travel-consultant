import streamlit as st
import os
import json
import re
import google.generativeai as genai
from streamlit_echarts import st_echarts
from streamlit_folium import st_folium
import folium

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Atlas AI Travel Consultant",
    page_icon="🌍",
    layout="wide"
)

# ============================================================
# API CONFIG
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY is missing. Add it in Streamlit secrets.")
    st.stop()

genai.configure(api_key=api_key)

# ============================================================
# DATA
# ============================================================

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
    "Rome": [41.9028, 12.4964],
    "Barcelona": [41.3874, 2.1686],
    "Singapore": [1.3521, 103.8198],
    "Dubai": [25.2048, 55.2708],
    "Bangkok": [13.7563, 100.5018],
    "New York": [40.7128, -74.0060],
    "Amsterdam": [52.3676, 4.9041],
    "Istanbul": [41.0082, 28.9784],
    "Maldives": [3.2028, 73.2207],
    "Sydney": [-33.8688, 151.2093],
    "Cape Town": [-33.9249, 18.4241],
    "Santorini": [36.3932, 25.4615],
    "Prague": [50.0755, 14.4378]
}

# ============================================================
# SESSION STATE
# ============================================================

if "dna_vector" not in st.session_state:
    st.session_state.dna_vector = {k: 50 for k in DNA_KEYS}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "shortlist" not in st.session_state:
    st.session_state.shortlist = []

if "last_plan" not in st.session_state:
    st.session_state.last_plan = {
        "response_text": "",
        "trip_theme": "",
        "shortlist": [],
        "itinerary": [],
        "travel_tips": [],
        "dna_updates": {}
    }

# ============================================================
# HELPERS
# ============================================================

def clamp_score(value):
    return max(0, min(100, int(value)))


def safe_json_parse(text):
    """
    Handles clean JSON and markdown-wrapped JSON.
    """

    if not text:
        return None

    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    # Fallback: extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if matc*:
        try:
            return *son.loads(match.group(0))
        *xcept Exception:
            retur* None

    return None


def apply*dna_updates(dna_updates):
    for *, v in dna_updates.items():
      * if k in st.session_state.dna_vect*r:
            st.session_state.dn*_vector[k] = clamp_score(
        *       st.session_state.dna_vector[k] + int(v)
            )


def re*et_app():
    st.session_state.mes*ages = []
    st.session_state.sho*tlist = []
    st.session_state.la*t_plan = {
        "response_text"* "",
        "trip_theme": "",
   *    "shortlist": [],
        "itin*rary": [],
        "travel_tips": *],
        "dna_updates": {}
    }*    st.session_state.dna_vector = *k: 50 for k in DNA_KEYS}


# =====*==================================*===================
# AI COUNCIL L*GIC
# ============================*===============================

d*f run_agent_council(user_input):
 *  model = genai.GenerativeModel("g*mini-3.5-flash")

    prompt = f""*
You are Atlas, a premium AI trave* consultant.

Current Travel DNA:
*json.dumps(st.session_state.dna_ve*tor, indent=2)}

User request:
{us*r_input}

Act as a council of 3 ag*nts:
1. Researcher: identify suita*le destination styles.
2. Planner:*build a practical travel plan.
3. *ritic: check if the plan matches t*e Travel DNA.

Return JSON only in*this exact shape:

{{
  "response_*ext": "A polished human-readable t*avel recommendation.",
  "trip_the*e": "Short theme name",
  "dna_upd*tes": {{
    "Adventure": 0,
    "*elaxation": 0,
    "Photography": *,
    "Luxury": 0,
    "Budget Con*cious": 0,
    "Sustainability": 0*
    "Culture": 0,
    "Food Explo*er": 0,
    "Shopping": 0,
    "Ni*htlife": 0,
    "Family Focus": 0,*    "Nature": 0
  }},
  "shortlist*: ["Bali", "Kyoto", "Lisbon"],
  "*tinerary": [
    {{
      "day": "Day 1",
      "title": "Arrival and orientation",
      "details": "Short practical plan"
    }},
    {{
      "day": "Day 2",
      "title": "Main experience",
      "details": "Short practical plan"
    }},
    {{
      "day": "Day 3",
      "title": "Relaxed exploration",
      "details": "Short practical plan"
    }}
  ],
  "travel_tips": [
    "Tip 1",
    "Tip 2",
    "Tip 3"
  ]
}}

Rules:
- Use only city name* that are likely travel destinatio*s.
- Prefer cities from this known*coordinate list where possible:
{l*st(CITY_COORDINATES.keys())}
- Kee* JSON valid.
- Do not include mark*own.
"""

    try:
        respons* = model.generate_content(
       *    prompt,
            generation*config={"response_mime_type": "app*ication/json"},
            reques*_options={"timeout": 20}
        )*
        parsed = safe_json_parse(*esponse.text)

        if not pars*d:
            raise ValueError("I*valid JSON returned by model")

  *     parsed.setdefault("response_t*xt", "Here is a travel recommendat*on.")
        parsed.setdefault("t*ip_theme", "Personalised Escape")
*       parsed.setdefault("dna_upda*es", {})
        parsed.setdefault*"shortlist", [])
        parsed.se*default("itinerary", [])
        p*rsed.setdefault("travel_tips", [])*
        return parsed

    except*Exception as e:
        return {
 *          "response_text": "I had *rouble generating the travel plan.*Please try again with a simpler re*uest.",
            "trip_theme": *Planning issue",
            "dna_*pdates": {},
            "shortlis*": [],
            "itinerary": []*
            "travel_tips": [
                "Check that GEMINI_API_KEY is configured.",
                "Try a shorter travel request.",
                "Confirm the model name is enabled for your API key."
            ]
        }


# =======*==================================*=================
# SIDEBAR CONTRO* PANEL
# =========================*==================================*
with st.sidebar:
    st.markdown(*## 🧭 Atlas Control Panel")

    s*.markdown("### Travel DNA Tuning")*
    for key in DNA_KEYS:
        *t.session_state.dna_vector[key] = *t.slider(
            key,
       *    min_value=0,
            max_v*lue=100,
            value=st.sess*on_state.dna_vector[key],
        *   step=5
        )

    st.divide*()

    st.markdown("### Quick Pro*pts")

    quick_prompt = None

  * if st.button("🏝️ Planner: Bali R*laxation"):
        quick_prompt =*"Plan a relaxing luxury Bali trip *ith nature, food and photography."*
    if st.button("🏯 Planner: Kyo*o Culture"):
        quick_prompt * "Plan a cultural Kyoto trip with *emples, food, photography and calm*experiences."

    if st.button("�* Planner: Lisbon Budget Trip"):
  *     quick_prompt = "Plan a budget*conscious Lisbon trip with culture* food and scenic photography."

  * if st.button("👨‍👩‍👧 Planner: F*mily Holiday"):
        quick_prom*t = "Plan a safe family-friendly h*liday with relaxation, nature and *ight adventure."

    st.divider()*
    if st.button("🔄 Reset Atlas"*:
        reset_app()
        st.r*run()


# ========================*==================================*
# MAIN HEADER
# =================*==================================*=======

st.markdown("""
<style>
.*ain-title {
    font-size: 34px;
 *  font-weight: 800;
    margin-bot*om: 0px;
}
.subtitle {
    color: *9ca3af;
    font-size: 15px;
    m*rgin-bottom: 20px;
}
.agent-pill {*    display: inline-block;
    pad*ing: 6px 12px;
    border-radius: *99px;
    background: #111827;
   *border: 1px solid #374151;
    fon*-size: 12px;
    margin-right: 8px*
}
.destination-card {
    padding* 12px;
    border-radius: 14px;
  * border: 1px solid #374151;
    ba*kground: #111827;
    margin-botto*: 10px;
}
</style>
""", unsafe_all*w_html=True)

st.markdown('<div cl*ss="main-title">🌍 Atlas AI Travel*Consultant</div>', unsafe_allow_ht*l=True)
st.markdown('<div class="s*btitle">Interactive travel plannin* cockpit powered by Travel DNA, AI*council reasoning, maps and itiner*ry cards.</div>', unsafe_allow_htm*=True)

st.markdown("""
<span clas*="agent-pill">🔎 Researcher</span>*<span class="agent-pill">🧠 Planne*</span>
<span class="agent-pill">�*️ Critic</span>
<span class="agent*pill">🗺️ Mapper</span>
""", unsaf*_allow_html=True)

st.divider()

#*==================================*=========================
# MAIN L*YOUT
# ===========================*================================

*eft, right = st.columns([1.1, 1])
*# ================================*===========================
# LEFT* CHAT + ITINERARY
# ==============*==================================*==========

with left:
    st.mark*own("### 💬 Travel Conversation")
*    chat_container = st.container(*eight=360)

    with chat_containe*:
        for msg in st.session_st*te.messages:
            with st.c*at_message(msg["role"]):
         *      st.write(msg["content"])

  * user_input = st.chat_input(
     *  "Tell Atlas your travel goal..."*
        key="atlas_single_chat_in*ut"
    )

    final_input = user_*nput or quick_prompt

    if final*input:
        st.session_state.me*sages.append({
            "role":*"user",
            "content": fin*l_input
        })

        with s*.status("Atlas Council is analysin* your travel DNA...", expanded=Tru*) as status:
            st.write(*🔎 Researcher scanning destination*fit...")
            st.write("🧠 *lanner preparing itinerary...")
  *         st.write("🛡️ Critic chec*ing alignment with DNA...")

     *      ai_data = run_agent_council(*inal_input)

            apply_dna*updates(ai_data.get("dna_updates",*{}))

            st.session_state.shortlist = ai_data.get("shortlist", [])
            st.session_state.last_plan = ai_data

            status.update(
                label="Atlas plan ready",
                state="complete"
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_data.get("response_text", "")
        })

        st.rerun()

    st.markdown("### 🗓️ Suggested Itinerary")

    itinerary = st.session_state.last_plan.get("itinerary", [])

    if itinerary:
        tabs = st.tabs([item.get("day", f"Day {i+1}") for i, item in enumerate(itinerary)])

        for tab, item in zip(tabs, itinerary):
            with tab:
                st.markdown(f"#### {item.get('title', 'Travel Plan')}")
                st.write(item.get("details", "No details available."))
    else:
        st.info("Ask Atlas for a trip plan to generate an itinerary.")


# ============================================================
# RIGHT: DNA + MAP + SHORTLIST
# ============================================================

with right:
    st.markdown("### 🧬 Travel DNA Profile")

    radar_options = {
        "tooltip": {},
        "radar": {
            "indicator": [
                {"name": k, "max": 100}
                for k in st.session_state.dna_vector.keys()
            ],
            "radius": "65%"
        },
        "series": [
            {
                "name": "Travel DNA",
                "type": "radar",
                "areaStyle": {"opacity": 0.25},
                "data": [
                    {
                        "value": list(st.session_state.dna_vector.values()),
                        "name": "Current Profile",
                        "itemStyle": {"color": "#00f2ff"}
                    }
                ]
            }
        ]
    }

    st_echarts(
        options=radar_options,
        height="330px"
    )

    st.markdown("### 📍 Destination Map")

    m = folium.Map(
        location=[20, 20],
        zoom_start=2,
        tiles="CartoDB dark_matter"
    )

    mapped_cities = []

    for city in st.session_state.shortlist:
        if city in CITY_COORDINATES:
            mapped_cities.append(city)

            folium.Marker(
                location=CITY_COORDINATES[city],
                tooltip=city,
                popup=f"Atlas shortlisted: {city}",
                icon=folium.Icon(color="blue", icon="star")
            ).add_to(m)

    st_folium(
        m,
        height=330,
        use_container_width=True
    )

    st.markdown("### ⭐ Destination Shortlist")

    if st.session_state.shortlist:
        for city in st.session_state.shortlist:
            if city in CITY_COORDINATES:
                st.markdown(
                    f"""
                    <div class="destination-card">
                        <b>{city}</b><br/>
                        <span style="color:#9ca3af;">Mapped and ready for planning.</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="destination-card">
                        <b>{city}</b><br/>
                        <span style="color:#fbbf24;">No map coordinate configured yet.</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No destinations shortlisted yet.")

    st.markdown("### 💡 Travel Tips")

    tips = st.session_state.last_plan.get("travel_tips", [])

    if tips:
        for tip in tips:
            st.write(f"• {tip}")
    else:
        st.write("Travel tips will appear after Atlas creates a plan.")
