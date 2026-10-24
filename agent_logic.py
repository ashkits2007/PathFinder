from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from google import genai

# Initialize the Gemini client (Replace with actual API key or use environment variables)
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

class AgentState(TypedDict):
    user_query: str
    domain: Optional[str]
    fetched_markdown: Optional[str]
    final_plan: Optional[str]

def analyze_intent(state: AgentState):
    """Uses Gemini to intelligently classify if the query is code-based or theoretical."""
    query = state["user_query"]
    
    prompt = f"""
    Classify the following user query into one of two categories: 'software' (if it mentions a GitHub repo, code, or engineering architecture) or 'theoretical' (if it asks about pure math, physics, chemistry, or general paper synthesis).
    Query: {query}
    Output ONLY the exact word: software or theoretical.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        domain = response.text.strip().lower()
        if "software" in domain:
            domain = "software"
        else:
            domain = "theoretical"
    except Exception:
        domain = "software" # Fallback
        
    return {"domain": domain}

def fetch_with_tinyfish(state: AgentState):
    """Placeholder for Utkarsh's TinyFish Web Fetch integration."""
    simulated_markdown = "# arXiv Paper: Lightweight Chunking for RAG\n\nAbstract: This paper introduces an optimized token-window allocation strategy to reduce latency..."
    return {"fetched_markdown": simulated_markdown}

def codebase_action_node(state: AgentState):
    """Uses Gemini to translate academic methods into codebase-specific steps."""
    query = state["user_query"]
    markdown = state["fetched_markdown"]
    
    prompt = f"""
    You are PATHFINDER, an AI engineering co-pilot. 
    User Target/Repo: {query}
    Retrieved Research Content: {markdown}
    
    Provide 3 concise, highly actionable implementation steps detailing how the developer can apply this research method to their codebase.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        plan = response.text
    except Exception as e:
        plan = f"Error generating plan: {e}"
        
    return {"final_plan": plan}

def literature_synthesis_node(state: AgentState):
    """Synthesizes theoretical overlaps across academic fields."""
    return {"final_plan": "Theoretical literature cross-reference and mathematical bridge analysis completed."}

def route_domain(state: AgentState):
    if state["domain"] == "software":
        return "codebase_action"
    return "literature_synthesis"

# Assemble the Graph
workflow = StateGraph(AgentState)
workflow.add_node("analyze_intent", analyze_intent)
workflow.add_node("fetch_with_tinyfish", fetch_with_tinyfish)
workflow.add_node("codebase_action", codebase_action_node)
workflow.add_node("literature_synthesis", literature_synthesis_node)

workflow.set_entry_point("analyze_intent")
workflow.add_edge("analyze_intent", "fetch_with_tinyfish")
workflow.add_conditional_edges(
    "fetch_with_tinyfish",
    route_domain,
    {
        "codebase_action": "codebase_action",
        "literature_synthesis": "literature_synthesis"
    }
)
workflow.add_edge("codebase_action", END)
workflow.add_edge("literature_synthesis", END)

pathfinder_app = workflow.compile()
