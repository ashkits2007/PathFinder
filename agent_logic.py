from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

# 1. Define the State (The agent's memory that passes between nodes)
class AgentState(TypedDict):
    user_query: str
    domain: Optional[str] # Will be 'software' or 'theoretical'
    fetched_markdown: Optional[str]
    final_plan: Optional[str]

# 2. Define the Nodes (The "Doers")
def analyze_intent(state: AgentState):
    """Uses Claude/Gemini to determine if the query is code-based or theoretical."""
    query = state["user_query"].lower()
    
    # Simple heuristic for the hackathon MVP, can be replaced with an LLM call
    if "github.com" in query or "repo" in query:
        domain = "software"
    else:
        domain = "theoretical"
        
    return {"domain": domain}

# 3. Assemble the Graph
workflow = StateGraph(AgentState)
