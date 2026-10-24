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
    
def fetch_with_tinyfish(state: AgentState):
    """Grabs arXiv HTML/PDF pages and converts them to clean Markdown."""
    # TODO: Insert actual TinyFish Web Fetch API call here
    simulated_markdown = "# Academic Paper\n\nAbstract: This paper introduces lightweight chunking..."
    return {"fetched_markdown": simulated_markdown}

def codebase_action_node(state: AgentState):
    """Translates academic methods into actionable, codebase-specific implementation steps."""
    # TODO: Pass state["fetched_markdown"] and repo data to Claude/Gemini
    return {"final_plan": "Actionable implementation steps for the GitHub repo."}

# 3. Assemble the Graph
workflow = StateGraph(AgentState)
