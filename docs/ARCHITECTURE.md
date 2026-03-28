# Architecture

## System style

ProcureBrain should be a supervised, modular agent platform centered on chat.

The system should separate:

- API transport
- domain logic
- application use cases
- agent workflows
- ingestion and retrieval
- persistence and vector storage
- long-running workers

## Primary stack

- `FastAPI` for the backend API
- `LangGraph` for orchestration and agent state
- `LangChain` integrations for model providers and tools
- `MongoDB` for chats, messages, runs, sources, and documents
- `Qdrant` for embeddings and retrieval

## Model routing

Use a model router abstraction so the application can switch providers without changing business logic.

Supported providers:

- `OpenAI`
- `Google Gemini`
- `Groq`

## Retrieval model

The assistant should support public knowledge gathering from:

- direct URLs
- public site pages
- multi-page website crawling within safe limits
- uploaded and stored PDFs

Recommended ingestion flow:

1. fetch source
2. extract readable content
3. normalize metadata
4. chunk text
5. embed and store in Qdrant
6. retrieve relevant chunks for analysis

## Agent model

Start with a supervised graph:

1. user chat request
2. planner node
3. retrieval node
4. analyst node
5. writer node

Later versions can add:

- supervisor loops
- topic monitoring
- scheduled intelligence jobs
- persistent research threads

## Skill architecture

Skills should be scalable beyond the initial planner and analyst roles.

Each skill package should have:

- `skill.json` for identity and metadata
- `SYSTEM.md` for the core instructions
- optional `INPUTS.md`
- optional `OUTPUTS.md`
- optional `EXAMPLES.md`

This lets the platform:

- discover all installed skills dynamically
- filter skills by tags or compatible agents
- compose multiple skills into one agent context
- add new skills without changing the folder layout

Integration path:

1. discover skill packages from the `skills/` root
2. parse metadata
3. load markdown instruction fragments
4. compose a final runtime prompt for the requested agent or workflow
