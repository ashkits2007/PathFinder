"""Combined PATHFINDER agent module.

Provides both ``agent_app`` for Gemini/TinyFish repository research and
``process_documents_and_run_chain`` for local PDF, TXT, and PPTX analysis.
This is a copy candidate; it does not modify either source module.
"""

import os
from pathlib import Path
from typing import Literal, Sequence, TypedDict

import requests
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, StateGraph
from pptx import Presentation

load_dotenv()

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".pptx"}


class AgentState(TypedDict):
    query: str
    repo_link: str
    response_language: str
    domain: str
    fetched_markdown: str
    plan: str


def _make_llm() -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY in the environment before using /api/research.")
    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
        temperature=0,
        google_api_key=api_key,
    )


def invoke_llm(prompt: str) -> str:
    """Call Gemini and consistently return plain text from either response shape."""
    content = _make_llm().invoke([HumanMessage(content=prompt)]).content
    if isinstance(content, list):
        return "\n".join(
            str(part.get("text", part)) if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content)


def analyze_intent(state: AgentState):
    prompt = (
        "Classify the user's request as 'software' (applied codebase / implementation) "
        "or 'theoretical' (research synthesis). Reply with exactly one word: software "
        "or theoretical. Keep classification in English.\n\n"
        f"User request: {state.get('query', '')}\n"
        f"Repository: {state.get('repo_link', '') or 'not provided'}"
    )
    domain = invoke_llm(prompt).strip().lower()
    return {"domain": domain if domain in {"software", "theoretical"} else "software"}


def fetch_with_tinyfish(state: AgentState):
    repo_link = (state.get("repo_link") or "").strip()
    if not repo_link:
        return {"fetched_markdown": "No repository URL provided."}
    api_key = os.getenv("TINYFISH_API_KEY")
    if not api_key:
        return {"fetched_markdown": "Repository context was not fetched: TINYFISH_API_KEY is not configured."}
    try:
        response = requests.post(
            os.getenv("TINYFISH_API_URL", "https://api.fetch.tinyfish.ai"),
            json={"urls": [repo_link], "format": "markdown"},
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            timeout=20,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return {"fetched_markdown": results[0].get("text", "No text returned.") if results else "No content returned."}
    except requests.RequestException as exc:
        return {"fetched_markdown": f"Repository context could not be fetched ({type(exc).__name__})."}
    except (ValueError, KeyError, TypeError):
        return {"fetched_markdown": "Repository context response could not be parsed."}


def route_domain(state: AgentState) -> Literal["codebase_action_node", "literature_synthesis_node"]:
    return "codebase_action_node" if state["domain"] == "software" else "literature_synthesis_node"


def codebase_action_node(state: AgentState):
    language = state.get("response_language", "English")
    return {"plan": invoke_llm(
        f"User's goal/request: {state['query']}\nTarget repository: {state['repo_link']}\n"
        f"Repository context: {state['fetched_markdown']}\n\n"
        "Provide concrete implementation guidance and exact code changes where possible. "
        f"Write the response in {language}."
    )}


def literature_synthesis_node(state: AgentState):
    language = state.get("response_language", "English")
    return {"plan": invoke_llm(
        f"User's research goal: {state['query']}\nRetrieved context: {state['fetched_markdown']}\n\n"
        f"Synthesize the relevant theoretical concepts in {language}."
    )}
