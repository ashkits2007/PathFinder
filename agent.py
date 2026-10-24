'''
agent.py
This file constructs the LangGraph Agent Brain containing the AgentState and the conditional routing logic between the codebase_action_node and literature_synthesis_node using Google Gemini.
'''

import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"  # Replace with your actual Google API key
# LLM Initialization
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

class AgentState(TypedDict):
    query: str
    repo_link: str
    domain: str
    fetched_markdown: str
    plan: str

def analyze_intent(state: AgentState):
    """Node 1: Classify Intent into 'software' or 'theoretical'."""
    prompt = f"Analyze this query and repository: {state['query']}, {state['repo_link']}. Is the intent 'software' (applied codebase) or 'theoretical' (research synthesis)? Reply with only one word: software or theoretical."
    response = llm.invoke([HumanMessage(content=prompt)])
    domain = response.content.strip().lower()
    if domain not in ["software", "theoretical"]:
        domain = "software" # Default fallback
    return {"domain": domain}

def fetch_with_tinyfish(state: AgentState):
    """Node 2: Scrape Paper / Repo using TinyFish Web Agent Scraper."""
    # Placeholder for actual TinyFish API integration
    # In production, this replaces clunky PDF parsers and grabs clean Markdown
    mock_markdown = f"# Scraped Content for {state['query']}\nFound repository and paper details."
    return {"fetched_markdown": mock_markdown}

def route_domain(state: AgentState) -> Literal["codebase_action_node", "literature_synthesis_node"]:
    """Conditional Edge routing based on domain."""
    if state["domain"] == "software":
        return "codebase_action_node"
    return "literature_synthesis_node"

def codebase_action_node(state: AgentState):
    """Node 3A: Generate 3-Step Implementation Plan for software."""
    prompt = f"Based on this markdown: {state['fetched_markdown']}, generate a 3-step implementation plan for applying this to the repo {state['repo_link']}."
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"plan": response.content}

def literature_synthesis_node(state: AgentState):
    """Node 3B: Cross-Field Synthesis for theoretical queries."""
    prompt = f"Based on this markdown: {state['fetched_markdown']}, synthesize the core theoretical concepts."
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"plan": response.content}

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