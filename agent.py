"""Gemini/LangGraph research workflow; credentials come from environment."""

import os
from typing import Literal, TypedDict

import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph


load_dotenv()


class AgentState(TypedDict):
    query: str
    repo_link: str
    response_language: str
    domain: str
    fetched_markdown: str
    plan: str


def _make_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY in the environment before using /api/research.")
    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
        temperature=0,
        google_api_key=api_key,
    )


def invoke_llm(prompt: str) -> str:
    response = _make_llm().invoke([HumanMessage(content=prompt)])
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
        "Classify the user's request as 'software' (applied codebase / implementation) "
        "or 'theoretical' (research synthesis). Reply with exactly one word: software "
        "or theoretical. Keep classification in English.\n\n"
        f"User request: {state.get('query', '')}\n"
        f"Repository: {state.get('repo_link', '') or 'not provided'}\n"
        f"Requested response language: {language}"
    )
    domain = invoke_llm(prompt).strip().lower()
    return {"domain": domain if domain in ("software", "theoretical") else "software"}


def fetch_with_tinyfish(state: AgentState):
    repo_link = (state.get("repo_link") or "").strip()
    if not repo_link:
        return {"fetched_markdown": "No repository URL provided."}

    tinyfish_key = os.getenv("TINYFISH_API_KEY")
    if not tinyfish_key:
        return {"fetched_markdown": "Repository context was not fetched: TINYFISH_API_KEY is not configured."}

    try:
        response = requests.post(
            os.getenv("TINYFISH_API_URL", "https://api.fetch.tinyfish.ai"),
            json={"urls": [repo_link]},
            headers={"X-API-Key": tinyfish_key, "Content-Type": "application/json"},
            timeout=20,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        markdown = results[0].get("text", "No text returned.") if results else "No content returned."
    except requests.RequestException as exc:
        markdown = f"Repository context could not be fetched ({type(exc).__name__})."
    except (ValueError, KeyError, TypeError):
        markdown = "Repository context response could not be parsed."
    return {"fetched_markdown": markdown}


def route_domain(state: AgentState) -> Literal["codebase_action_node", "literature_synthesis_node"]:
    return "codebase_action_node" if state["domain"] == "software" else "literature_synthesis_node"


def codebase_action_node(state: AgentState):
    language = state.get("response_language", "English")
    prompt = (
        f"User's goal/request: {state['query']}\n"
        f"Target repository: {state['repo_link']}\n"
        f"Repository context: {state['fetched_markdown']}\n\n"
        "Provide concrete implementation guidance and exact code changes where possible. "
        f"Write the response in {language}."
    )
    return {"plan": invoke_llm(prompt)}


def literature_synthesis_node(state: AgentState):
    language = state.get("response_language", "English")
    prompt = (
        f"User's research goal: {state['query']}\n"
        f"Retrieved context: {state['fetched_markdown']}\n\n"
        f"Synthesize the relevant theoretical concepts in {language}."
    )
    return {"plan": invoke_llm(prompt)}


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
