import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from agent import agent_app

app = FastAPI(title="PATHFINDER API", version="2.0")


class ResearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10000)
    repo_link: Optional[str] = ""
    response_language: str = "English"


class ResearchResponse(BaseModel):
    status: str
    domain: str
    plan: str
    raw_markdown: str


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "PATHFINDER API"}


@app.post("/api/research", response_model=ResearchResponse)
async def run_research_agent(request: ResearchRequest):
    """Run the LangGraph workflow and return its result."""
    initial_state = {
        "query": request.query.strip(),
        "repo_link": (request.repo_link or "").strip(),
        "response_language": request.response_language,
        "domain": "",
        "fetched_markdown": "",
        "plan": "",
    }
    try:
        final_state = agent_app.invoke(initial_state)
        return ResearchResponse(
            status="success",
            domain=final_state.get("domain", ""),
            plan=final_state.get("plan", ""),
            raw_markdown=final_state.get("fetched_markdown", ""),
        )
    except Exception as exc:
        # Keep a useful message for local development; avoid exposing secrets in logs.
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
