"""Local document analysis for PDF, TXT, and PPTX uploads using Ollama."""

from pathlib import Path
from typing import Sequence

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pptx import Presentation

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".pptx"}


def load_documents(file_paths: Sequence[str]) -> list[Document]:
    """Extract supported local files into LangChain documents."""
    documents: list[Document] = []
    for file_path in file_paths:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if not path.is_file() or suffix not in ALLOWED_EXTENSIONS:
            continue

        if suffix == ".pdf":
            documents.extend(PyPDFLoader(str(path)).load())
        elif suffix == ".txt":
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if text:
                documents.append(Document(page_content=text, metadata={"source": path.name}))
        elif suffix == ".pptx":
            presentation = Presentation(str(path))
            for slide_number, slide in enumerate(presentation.slides, start=1):
                parts: list[str] = []
                for shape in slide.shapes:
                    if getattr(shape, "has_text_frame", False):
                        text = shape.text.strip()
                        if text:
                            parts.append(text)
                    if getattr(shape, "has_table", False):
                        for row in shape.table.rows:
                            parts.append(" | ".join(cell.text.strip() for cell in row.cells))
                if parts:
                    documents.append(Document(
                        page_content="\n".join(parts),
                        metadata={"source": path.name, "slide": slide_number},
                    ))
    return documents


def format_docs(docs: Sequence[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def process_documents_and_run_chain(
    query: str,
    repo_url: str | None = None,
    pdf_paths: Sequence[str] | None = None,
    response_language: str = "English",
    documents: Sequence[Document] | None = None,
) -> str:
    """Answer a literature question using uploaded documents and optional URL context."""
    full_query = query.strip()
    if repo_url:
        full_query += f"\n\nReference document URL (provided by the user): {repo_url}"

    documents = list(documents) if documents is not None else load_documents(pdf_paths or [])
    llm = ChatOllama(model="llama3.1", temperature=0.2)
    if not documents:
        return str(llm.invoke(
            f"Answer the user's research question in {response_language}.\n\n{full_query[:12000]}"
        ).content)

    splits = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120).split_documents(documents)
    # Use an in-memory vector store per request so one user's upload cannot affect a later query.
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=OllamaEmbeddings(model="all-minilm"),
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    prompt = ChatPromptTemplate.from_template(
        "You answer questions about supplied research documents. Use the context below, "
        "and say when it does not contain enough information. Respond in {language}.\n\n"
        "Context:\n{context}\n\nQuestion:\n{question}"
    )
    chain = (
        {"context": retriever | format_docs,
         "question": RunnablePassthrough(),
         "language": lambda _: response_language}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain.invoke(full_query[:12000])
