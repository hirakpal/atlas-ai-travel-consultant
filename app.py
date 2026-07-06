import streamlit as st
from streamlit_echarts import st_echarts

# 1. Custom CSS for "Premium Glass & Glow"
st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: #e0e6ed; }
    .css-1r6slp0 { background-color: #161b22; border-radius: 15px; border: 1px solid #30363d; }
    .status-pill { padding: 5px 15px; border-radius: 20px; background: #21262d; margin-right: 10px; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

# 2. Split Screen Architecture
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### 🤖 Atlas - AI Travel Consultant")
    # Agent Status Pillbox (as seen in image_c0f57f.jpg)
    st.markdown("""
        <div style="display:flex;">
            <span class="status-pill">● Researcher</span>
            <span class="status-pill">● Generator</span>
            <span class="status-pill">● Critic</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Chat Container
    chat_container = st.container(height=500)
    with chat_container:
        st.chat_message("assistant").write("Hi Hirak! Where are you thinking of travelling this time?")
        st.chat_message("user").write("Bali in October, mid-range budget, love food and nature")
        st.chat_message("assistant").write("Cross referencing your travel DNA against 40+ destinations—Bali, Lisbon and Kyoto are your strongest matches...")

    user_input = st.chat_input("Tell Atlas where you want to go...")

with col2:
    # Right Panel: DNA & Shortlist
    st.subheader("Travel DNA Profile")
    st.caption("Auto-updated as you chat with Atlas")
    
    # Radar Chart Placeholder (Use streamlit-echarts here)
    st.info("Radar Chart Visualization") 
    
    st.subheader("Destinations shortlist")
    st.caption("Hover a pin for details - click to lock in")
    
    # Map Container (The dark gradient background from image_c0f57f.jpg)
    st.container(height=300).markdown("""
        <div style="background: linear-gradient(180deg, #161b22 0%, #0d1117 100%); height: 100%; border-radius: 10px;">
        <!-- Map visualization would go here -->
        </div>
    """, unsafe_allow_html=True)
