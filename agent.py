import os
import requests
from typing import Literal, TypedDict
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

# Hardcoded key for testing
GEMINI_API_KEY = "your-gemini-api-key"

class AgentState(TypedDict):
    query: str
    repo_link: str
    response_language: str
    domain: str
    fetched_markdown: str
    plan: str

# Initialize the Gemini client directly with the key
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GEMINI_API_KEY,
)

def invoke_llm(prompt: str) -> str:
    """Invoke Gemini and normalize its response to plain text."""
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content

    if isinstance(content, list):
        return "\n".join(
            str(part.get("text", part)) if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content)

def analyze_intent(state: AgentState):
    language = state.get("response_language", "English")
    prompt = (
        "Classify the user's request as 'software' (applied codebase / "
        "implementation) or 'theoretical' (research synthesis). "
        "Reply with exactly one word: software or theoretical. "
        "The requested response language is only for the final answer; "
        "keep this classification in English.\n\n"
        f"User request: {state.get('query', '')}\n"
        f"Repository: {state.get('repo_link', '') or 'not provided'}\n"
        f"Requested response language: {language}"
    )
    domain = invoke_llm(prompt).strip().lower()

    if domain not in ("software", "theoretical"):
        domain = "software"

    return {"domain": domain}

def fetch_with_tinyfish(state: AgentState):
    repo_link = (state.get("repo_link") or "").strip()
    if not repo_link:
        return {"fetched_markdown": "No repository URL provided."}
    
    tinyfish_key = os.getenv("TINYFISH_API_KEY", "you-tinyfish-api-key")
    TINYFISH_URL = "https://api.fetch.tinyfish.ai"
    HEADERS = {"X-API-Key": tinyfish_key, "Content-Type": "application/json"}
    
    try:
        response = requests.post(
            TINYFISH_URL, 
            json={"urls": [repo_link]},
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        
        results = response.json().get("results", [])
        if results:
            fetched_markdown = results[0].get("text", "No text returned.")
        else:
            fetched_markdown = f"# TinyFish Notice\nConnected successfully, but no content text was returned for {repo_link}."
            
    except Exception as e:
        fetched_markdown = f"# Simulated Repository Context (Fallback)\nTinyFish API response took too long or failed: {str(e)}\nProceeding with AI code generation for {repo_link}."
        
    return {"fetched_markdown": fetched_markdown}

def route_domain(state: AgentState) -> Literal["codebase_action_node", "literature_synthesis_node"]:
    if state["domain"] == "software":
        return "codebase_action_node"
    return "literature_synthesis_node"

def codebase_action_node(state: AgentState):
    language = state.get("response_language", "English")
    prompt = (
        f"User's goal/request: {state['query']}\n"
        f"Target repository: {state['repo_link']}\n"
        f"Scraped repository context (from TinyFish): {state['fetched_markdown']}\n\n"
        f"Do not just provide a plan or high-level suggestions. Write the actual, production-ready code edits, complete functions, or full file contents required to fully implement the user's request. "
        f"Provide clean markdown code blocks containing the exact code changes. "
        f"Please write your response in {language}."
    )
    plan = invoke_llm(prompt)
    return {"plan": plan}

def literature_synthesis_node(state: AgentState):
    language = state.get("response_language", "English")
    prompt = (
        f"User's research goal: {state['query']}\n"
        f"Scraped context: {state['fetched_markdown']}\n\n"
        f"Synthesize the core theoretical concepts regarding the user's goal. "
        f"Please write the synthesis in {language}."
    )
    plan = invoke_llm(prompt)
    return {"plan": plan}

# Graph Construction
workflow = StateGraph(AgentState)
workflow.add_node("analyze_intent", analyze_intent)
workflow.add_node("fetch_with_tinyfish", fetch_with_tinyfish)
workflow.add_node("codebase_action_node", codebase_action_node)
workflow.add_node("literature_synthesis_node", literature_synthesis_node)

workflow.set_entry_point("analyze_intent")
workflow.add_edge("analyze_intent", "fetch_with_tinyfish")
workflow.add_conditional_edges("fetch_with_tinyfish", route_domain)
workflow.add_edge("codebase_action_node", END)
workflow.add_edge("literature_synthesis_node", END)

agent_app = workflow.compile()
