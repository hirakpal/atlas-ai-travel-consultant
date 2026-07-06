import streamlit as st
import google.generativeai as genai

st.title("Connection Audit")

# 1. Check if key exists
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Error: GEMINI_API_KEY is not defined in Streamlit secrets.")
    st.stop()

# 2. Attempt a basic connection
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # We use 'gemini-1.5-flash' as the primary test
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, are you working?")
    st.success("Connection Successful!")
    st.write("Model Response:", response.text)
except Exception as e:
    st.error(f"Critical Connection Error: {e}")
