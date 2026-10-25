"""Combined Pathfinder FastAPI backend.

Routes:
- GET / and /health
- POST /api/research (JSON, Gemini/LangGraph)
- POST /api/literature (multipart form with optional PDF/TXT/PPTX files)
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from agent import agent_app
from agent1 import format_docs, load_documents, process_documents_and_run_chain

app = FastAPI(title="PATHFINDER API", version="2.1")
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".pptx"}


class ResearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10_000)
    repo_link: Optional[str] = ""
    response_language: str = "English"


class ResearchResponse(BaseModel):
    status: str
    domain: str
    plan: str
    raw_markdown: str


@app.get("/")
async def root():
    return {"status": "online", "message": "Pathfinder API is active"}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "PATHFINDER API"}


@app.post("/api/research", response_model=ResearchResponse)
async def run_research_agent(request: ResearchRequest):
    """Run the LangGraph software/theoretical research workflow."""
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
            domain=final_state.get("domain", "theoretical"),
            plan=final_state.get("plan", ""),
            raw_markdown=final_state.get("fetched_markdown", ""),
        )
    except Exception as exc:
        # Keep server-side credentials and provider details out of API responses.
        raise HTTPException(status_code=500, detail="Research agent execution failed.") from exc


@app.post("/api/literature")
async def run_literature_agent(
    query: str = Form(...),
    response_language: str = Form("English"),
    doc_link: Optional[str] = Form(None),
    files: Optional[list[UploadFile]] = File(default=None),
):
    """Accept the multipart contract sent by the Streamlit literature UI."""
    saved_paths: list[str] = []
    parsed_files: list[str] = []
    total_bytes = 0
    try:
        with tempfile.TemporaryDirectory(prefix="pathfinder_uploads_") as temp_dir:
            for uploaded in files or []:
                filename = Path(uploaded.filename or "upload").name
                suffix = Path(filename).suffix.lower()
                if suffix not in ALLOWED_EXTENSIONS:
                    raise HTTPException(
                        status_code=415,
                        detail=f"Unsupported file type for {filename}. Upload PDF, TXT, or PPTX files.",
                    )

                content = await uploaded.read()
                total_bytes += len(content)
                if total_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Uploaded files exceed the 20 MB limit.")

                destination = Path(temp_dir) / f"{len(saved_paths)}_{Path(filename).name}"
                destination.write_bytes(content)
                saved_paths.append(str(destination))
                parsed_files.append(filename)
                await uploaded.close()

            try:
                documents = load_documents(saved_paths)
                raw_markdown = format_docs(documents)
                answer = process_documents_and_run_chain(
                    query=query.strip(),
                    repo_url=(doc_link or "").strip() or None,
                    pdf_paths=saved_paths,
                    response_language=response_language,
                    documents=documents,
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=503,
                    detail="Literature analysis failed. Check that Ollama is running and the configured model is available.",
                ) from exc

        return {
            "status": "success",
            "domain": "theoretical",
            "plan": answer,
            "raw_markdown": raw_markdown if raw_markdown else "No extracted file text; answered from the question and reference URL.",
        }
    finally:
        for uploaded in files or []:
            await uploaded.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
