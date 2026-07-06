from typing import TypedDict, List, Optional, Dict
from pydantic import BaseModel

# 1. This is your "Source of Truth" JSON model
class TravellerIntentProfile(BaseModel):
    destination: Optional[str] = None
    trip_purpose: Optional[str] = None
    dna_vector: Dict[str, float] = {
        "Adventure": 50.0, "Culture": 50.0, "Nature": 50.0, 
        "Luxury": 50.0, "Budget Conscious": 50.0, "Relaxation": 50.0
    }
    shortlist: List[str] = []

# 2. This is the State passed between Agents in the Graph
class AgentState(TypedDict):
    user_input: str
    messages: List[str] # Conversation history
    profile: TravellerIntentProfile # The JSON being mutated
    critique: Optional[str] # Feedback from the Critic
    is_finalized: bool

# Node 1: Generator
def generator_node(state: AgentState):
    # Call Gemini to create/update the plan based on state.profile
    return {"messages": ["Plan generated..."]}

# Node 2: Critic
def critic_node(state: AgentState):
    # Logic: Does the plan match the dna_vector? 
    # If not, return critique string
    return {"critique": "Plan is too expensive for a 'Budget Conscious' profile."}

# Node 3: Researcher (The Map/Places API Agent)
def researcher_node(state: AgentState):
    # Logic: Use Google Places API to verify destinations
    return {"profile": updated_profile}
