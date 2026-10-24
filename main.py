from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent import agent_app

app = FastAPI(title="PATHFINDER API", version="1.0")

class ResearchRequest(BaseModel):
    query: str
    repo_link: Optional[str] = ""

class ResearchResponse(BaseModel):
    status: str
    domain: str
    plan: str
    raw_markdown: str

@app.post("/api/research", response_model=ResearchResponse)
async def run_research_agent(request: ResearchRequest):
    """POST /api/research handling user prompt and repo link."""
    initial_state = {
        "query": request.query,
        "repo_link": request.repo_link,
        "domain": "",
        "fetched_markdown": "",
        "plan": ""
    }
    
    try:
        # Execute the LangGraph workflow
        final_state = agent_app.invoke(initial_state)
        
        return ResearchResponse(
            status="success",
            domain=final_state.get("domain", ""),
            plan=final_state.get("plan", ""),
            raw_markdown=final_state.get("fetched_markdown", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)