from fastapi import FastAPI
from pydantic import BaseModel
from agent_logic import pathfinder_app # Importing the brain we just built

# 1. Initialize the FastAPI server
app = FastAPI(
    title="PATHFINDER API",
    description="Backend for the GitHub-to-Research AI Agent",
    version="1.0.0"
)

# 2. Define the data structure we expect from the frontend
class QueryRequest(BaseModel):
    user_query: str

# 3. Create the endpoint that the frontend will call
@app.post("/api/research")
async def run_research_agent(request: QueryRequest):
    """
    Receives a query, runs the LangGraph workflow, and returns the final state.
    """
    # Create the initial state dictionary for LangGraph
    initial_state = {"user_query": request.user_query}
    
    # Run the graph
    result = pathfinder_app.invoke(initial_state)
    
    # Send the results back to the frontend as JSON
    return {
        "status": "success",
        "domain": result.get("domain"),
        "plan": result.get("final_plan"),
        "raw_markdown": result.get("fetched_markdown")
    }

# Health check endpoint just to make sure the server is alive
@app.get("/health")
async def health_check():
    return {"status": "PATHFINDER server is running!"}