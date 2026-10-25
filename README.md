# PathFinder

### From Research to Action

PathFinder is an AI-powered research-to-solution agent that transforms complex problems into **evidence-backed, actionable deliverables**.

It follows two specialised workflows under one platform: software problems receive codebase-specific implementation plans, while literature-based problems receive structured research reports that can be downloaded as PDFs.

##  The Problem

Finding information is only the first step in solving a complex problem.

- **Software developers** need to identify relevant research, understand existing codebases, evaluate possible approaches, and decide what to implement.
- **Researchers and students** need to discover relevant literature, evaluate sources, synthesise findings, and organise their research into a usable document.

Generic AI-generated answers may not provide enough project-specific context, traceable evidence, or a structured path from research to action.

PathFinder aims to bridge this gap by connecting research discovery with practical, problem-specific outputs.

##  Our Solution

PathFinder uses a shared research and evidence-gathering foundation to support two distinct workflows.

### 1. Software Track — Plan the Solution

For software engineering problems, PathFinder aims to:

- Accept a GitHub repository URL or a technical problem description.
- Profile the repository's structure, dependencies, and relevant implementation constraints.
- Discover research papers, technical resources, and related implementation repositories.
- Investigate relevant implementation details and available community feedback.
- Compare possible approaches against the target project's requirements.
- Generate a structured, actionable implementation plan with supporting evidence.

**Output:** A codebase-specific technical roadmap with recommendations, relevant files or components, potential risks, and suggested tests.

### 2. Literature Track — Produce the Research

For literature-based questions, PathFinder aims to:

- Discover relevant academic papers and web sources.
- Retrieve accessible source material and extract useful information.
- Evaluate and organise evidence relevant to the research question.
- Synthesise findings into a structured report.
- Include source references to support key claims.
- Generate a downloadable PDF research report.

**Output:** A structured, citation-backed research document.

## ⚙️ How It Works

The proposed workflow consists of the following stages:

1. **Problem Intake:** Receive the user's problem, requirements, and optional repository URL.
2. **Task Routing:** Determine whether the problem requires the software workflow or the literature workflow.
3. **Research Discovery:** Search for relevant papers, technical documentation, implementation repositories, and other useful sources.
4. **Evidence Retrieval:** Retrieve accessible content and extract information relevant to the problem.
5. **Context Analysis:** Analyse the collected evidence alongside the user's requirements and, for software tasks, the target codebase.
6. **Synthesis and Planning:** Compare approaches, identify constraints, and formulate recommendations.
7. **Deliverable Generation:** Produce an actionable software implementation plan or a downloadable literature report.
8. **Evidence Presentation:** Present relevant sources and explain how they support the resulting recommendations.

The workflow is designed to be modular, allowing individual stages to be improved or extended independently.

##  Technology Stack

The following technologies are proposed for the system architecture. The final stack may evolve during implementation.

| Component | Technology | Purpose |
|---|---|---|
| Frontend | Next.js, React, JavaScript, Tailwind CSS | User interface and analysis dashboard |
| Backend API | Python, FastAPI | Input validation, workflow execution, and result delivery |
| Agent orchestration | LangGraph | Coordinating multi-stage research workflows |
| LLM | Gemini API or another supported LLM | Evidence synthesis, reasoning, and structured output generation |
| Web research | TinyFish | Web search, content retrieval, and browser-based research workflows |
| Repository analysis | GitHub API and Git | Inspecting public repository metadata and source structure |
| Research storage | ChromaDB or FAISS (optional) | Semantic retrieval and reusable research context |
| Report generation | PDF generation library (to be selected) | Producing downloadable literature reports |

##  The Role of TinyFish

TinyFish is intended to serve as PathFinder's web research and evidence-gathering layer.

Depending on the capabilities of the configured tools, it can support workflows such as:

- Discovering relevant online resources.
- Retrieving accessible web content for analysis.
- Investigating implementation details on relevant websites.
- Gathering information that can be passed to the reasoning and synthesis stages.

The retrieved material is then processed by the rest of the system to generate task-specific results.

**TinyFish gathers evidence; PathFinder coordinates the workflow and turns that evidence into a useful deliverable.**

Source availability and reliability must be checked, and recommendations should retain links to their supporting evidence wherever possible.



##  Reliability and Safety

PathFinder is being designed with the following principles in mind:

- **Evidence traceability:** Preserve source URLs and distinguish sourced facts from generated recommendations.
- **Context-aware planning:** Tailor software recommendations to the target repository and its constraints.
- **Responsible synthesis:** Avoid presenting unsupported claims or invented citations as verified evidence.
- **Safe repository handling:** Do not execute arbitrary repository code during analysis.
- **Secure configuration:** Keep API keys and secrets in backend environment variables.
- **Failure handling:** Account for inaccessible sources, API failures, timeouts, and incomplete research.
- **Transparent execution:** Present workflow stages and operational status without exposing private model chain-of-thought.

##  Development Roadmap

- [ ] Complete the PathFinder frontend and input flows.
- [ ] Build the FastAPI backend and workflow interface.
- [ ] Implement software-versus-literature task routing.
- [ ] Integrate GitHub repository profiling for supported repositories.
- [ ] Integrate TinyFish-based research discovery and content retrieval.
- [ ] Implement evidence-grounded synthesis and source attribution.
- [ ] Generate actionable software implementation plans.
- [ ] Generate downloadable literature PDFs with references.
- [ ] Add live workflow progress and clear error states.
- [ ] Evaluate results using representative software and literature problems.
- [ ] Explore research caching and semantic retrieval.

##  Vision

PathFinder aims to make research more actionable by connecting what can be discovered online with what a particular problem actually requires.

Rather than treating research as the final destination, PathFinder uses it as the foundation for a practical next step.

**PathFinder — Investigate the evidence. Find the path forward.**

---

> **Project status:** In development. Features and integrations listed as planned or proposed should not be assumed to be implemented until verified in the repository.
