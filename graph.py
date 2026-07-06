from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("generator", generator_node)
workflow.add_node("critic", critic_node)
workflow.add_node("researcher", researcher_node)

# Add Edges (The "Council" Flow)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "generator")
workflow.add_edge("generator", "critic")

# Conditional Edge: If Critic says "No", go back to Generator
workflow.add_conditional_edges("critic", should_continue) 

app = workflow.compile()
