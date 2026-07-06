import google.generativeai as genai
import json
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generator_node(state):
    # Initialize the model
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Format the prompt
    prompt = GENERATOR_SYSTEM_PROMPT.format(
        profile=state["profile"].model_dump_json(),
        critique=state.get("critique", "None")
    )
    
    # Call Gemini
    response = model.generate_content(prompt)
    
    # Parse the JSON response
    # We use json.loads to clean the output
    result = json.loads(response.text.replace("```json", "").replace("```", ""))
    
    # Update State
    return {
        "messages": [result["response_text"]],
        "is_finalized": not result["needs_more_info"]
    }
