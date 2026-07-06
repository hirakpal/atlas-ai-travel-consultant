import streamlit as st
import google.generativeai as genai

st.title("Debug Mode")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    user_input = st.text_input("Ask something:")
    if user_input:
        try:
            response = model.generate_content(user_input)
            st.write("Full Raw Response:", response.text)
        except Exception as e:
            st.error(f"Execution Error: {e}")
else:
    st.error("API Key missing.")
