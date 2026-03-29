# ProcureBrain

ProcureBrain is a chat-first procurement, market-intelligence, and AI research backend designed to grow into a long-term assistant across your learning and product journey.

The goal is to build one system that can help with:

- procurement research
- supplier and market intelligence
- technology trend tracking
- AI and business news analysis
- public website and PDF retrieval
- structured chat-based analysis
- long-running monitoring and recurring research workflows

This repository is intentionally structured early for scale so we can keep the same root architecture as the project grows through multiple versions.

## Vision

ProcureBrain should not be just a simple chatbot.

It should become a modular intelligence assistant that can:

- accept user questions in chat
- convert vague questions into better research tasks
- read public pages, documents, and PDFs
- retrieve relevant knowledge from a vector database
- analyze evidence through a procurement and business lens
- produce grounded responses with sources
- support long-running topic monitoring over time

This project also has a second purpose:

- help build strong engineering skills in `AI`, `agent systems`, `retrieval`, `orchestration`, and `production backend design`

## Product direction

The product direction is centered on one main interaction model:

`chat -> planning -> retrieval -> analysis -> response`

In later versions, this expands to:

`chat -> planning -> retrieval -> analysis -> validation -> response -> monitoring`

The system should stay supervised and modular. We do not want uncontrolled autonomy too early. We want reliable building blocks that can evolve into stronger multi-agent workflows.

## Main use cases

ProcureBrain is being designed to support use cases such as:

- researching an AI vendor or technology category
- understanding procurement market trends
- tracking supplier or category risks
- analyzing public sites and articles for intelligence signals
- retrieving knowledge from uploaded PDF reports and documents
- generating structured briefs from mixed sources
- monitoring a topic over time and producing recurring updates

## Core architecture

The backend follows a layered architecture so we can add features without reorganizing the project root later.

### Core stack

- `FastAPI` for the backend API
- `LangGraph` for stateful agent orchestration
- `LangChain` integrations for model providers and tools
- `MongoDB` as the primary application database
- `Qdrant` as the vector database
- `Trafilatura`, `BeautifulSoup`, and `httpx` for public web retrieval
- `PyPDF` for PDF extraction

### Why these choices

#### FastAPI

FastAPI gives us a clean backend foundation for chat APIs, source ingestion, session handling, and future worker coordination.

#### LangGraph

LangGraph is a strong fit because this system needs structured, stateful, inspectable multi-step workflows rather than a single prompt call.

#### MongoDB

MongoDB is a better fit than a relational-first setup for this product because chat sessions, messages, agent runs, sources, and document metadata are naturally document-oriented.

#### Qdrant

Qdrant is a strong dedicated vector database for retrieval, source matching, and knowledge reuse as we scale ingestion.

#### Multi-model support

This project is designed to support:

- `OpenAI`
- `Google Gemini`
- `Groq`

That allows a future model router to choose providers based on task type, cost, latency, and quality.

## System design principles

The whole project is shaped around these principles:

- stable root structure from the beginning
- modular backend boundaries
- chat-first product thinking
- source-grounded outputs
- clean separation of domain logic from provider integrations
- scalable skill-based agent composition
- long-running workflows added in stages, not rushed

## Project structure

This is the current repository layout:

```text
ProcureBrainv1/
  .env.example
  .gitignore
  pyproject.toml
  README.md

  docker/
    docker-compose.yml
    Dockerfile.api
    Dockerfile.worker

  docs/
    API.md
    ARCHITECTURE.md
    DOMAIN.md
    ROADMAP.md
    SKILLS.md

  scripts/
    dev.ps1
    seed_demo_data.py

  prompts/
    shared/
      citation_rules.md
      report_style.md

  skills/
    _shared/
      README.md
      skill.template.json
      SYSTEM.template.md
    planner/
      skill.json
      SYSTEM.md
      INPUTS.md
      OUTPUTS.md
    researcher/
      skill.json
      SYSTEM.md
      INPUTS.md
      OUTPUTS.md
    analyst/
      skill.json
      SYSTEM.md
      INPUTS.md
      OUTPUTS.md
    writer/
      skill.json
      SYSTEM.md
      OUTPUTS.md
    supervisor/
      skill.json
      SYSTEM.md
    procurement_guard/
      skill.json
      SYSTEM.md

  src/
    procurebrain/
      main.py

      api/
        deps.py
        router.py
        routes/

      config/
        settings.py
        logging.py

      core/
        constants.py
        exceptions.py
        security.py

      domain/
        chat/
        agents/
        sources/
        documents/
        intelligence/

      application/
        orchestrators/
        use_cases/

      agents/
        registry.py
        state.py
        supervisor.py
        nodes/
        tools/

      ingestion/
        pdf/
        web/

      persistence/
        mongodb/
        repositories/

      vectorstore/
        qdrant/

      skills/
        composer.py
        loader.py
        models.py
        registry.py
        service.py

      workers/
        queue.py
        tasks/

      observability/
        metrics.py
        tracing.py

  tests/
    conftest.py
    unit/
    integration/
    e2e/
```

## Folder responsibilities

### `docs/`

Contains architectural and product documentation that explains the system shape before and during implementation.

### `skills/`

Contains top-level agent skill packages. These are treated as reusable capability packages, not just random prompt files.

### `src/procurebrain/api/`

Contains FastAPI transport-level code, route registration, and request dependencies.

### `src/procurebrain/domain/`

Contains business domain logic and core domain concepts for chat, documents, sources, agents, and intelligence.

### `src/procurebrain/application/`

Contains use cases and orchestration logic that coordinate domain actions and agent workflows.

### `src/procurebrain/agents/`

Contains runtime agent pieces such as shared state, nodes, supervisor logic, and tools used by workflows.

### `src/procurebrain/ingestion/`

Contains ingestion and extraction logic for web pages and PDFs.

### `src/procurebrain/persistence/`

Contains MongoDB clients, collections, indexes, and repository implementations.

### `src/procurebrain/vectorstore/`

Contains Qdrant integrations for embeddings and retrieval.

### `src/procurebrain/workers/`

Contains long-running or scheduled job entry points and background tasks.

### `src/procurebrain/skills/`

Contains backend code for discovering, loading, filtering, and composing top-level skills into runtime prompts.

## Skill system

One of the important design decisions in this project is that agent skills are treated as first-class modular packages.

Each skill can define:

- metadata
- compatible agents
- allowed tools
- system instructions
- expected inputs
- expected outputs
- optional examples

### Skill package contract

Each skill folder should contain:

- `skill.json`
- `SYSTEM.md`

Optional files:

- `INPUTS.md`
- `OUTPUTS.md`
- `EXAMPLES.md`

### Why this matters

This makes the project scalable because future skills can be added without changing the application structure.

Examples of future skills:

- site crawler skill
- supplier risk skill
- procurement negotiation skill
- category intelligence skill
- competitor analysis skill
- trend summarizer skill
- monitoring alert skill

### Backend integration

The backend already includes a basic skill integration layer:

- [loader.py](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\src\procurebrain\skills\loader.py)
- [models.py](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\src\procurebrain\skills\models.py)
- [registry.py](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\src\procurebrain\skills\registry.py)
- [composer.py](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\src\procurebrain\skills\composer.py)
- [service.py](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\src\procurebrain\skills\service.py)

This allows the application to:

- discover installed skills
- load their metadata and instruction fragments
- filter skills by agent compatibility
- compose final prompts for runtime agent use

## Data model direction

The exact schema is not implemented yet, but the intended MongoDB collections include:

- `users`
- `chat_sessions`
- `messages`
- `agent_runs`
- `sources`
- `documents`
- `briefs`
- `tracked_topics`

These collections are a strong fit for a chat-centric intelligence product and give us room to support monitoring later.

## Retrieval direction

The retrieval system should support:

- direct public URLs
- public web pages
- selected multi-page site retrieval
- uploaded PDFs
- stored chunks in Qdrant
- filtered retrieval for agent analysis

The intended flow is:

1. fetch or ingest source
2. extract readable content
3. normalize metadata
4. chunk content
5. embed content
6. store vectors in Qdrant
7. retrieve relevant chunks for analysis

## Chat direction

The chat experience is the center of the product.

Users should be able to:

- create or continue sessions
- ask procurement or AI market questions
- provide URLs or documents
- trigger research and analysis
- receive grounded structured answers

The initial API surface is documented in [docs/API.md](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\docs\API.md).

## Long-running assistant direction

This project is also designed to become a long-running assistant through your journey.

That means future versions should support:

- tracked topics
- recurring research runs
- scheduled monitoring jobs
- supplier or technology watchlists
- daily or weekly intelligence outputs

We are not implementing the full 24/7 system immediately, but the structure already leaves room for it in `workers/`, `observability/`, and `tracked_topics`.

## Version roadmap

### Version 1: Chat Research Core

Goal:
Build the first useful end-to-end research assistant inside chat.

Scope:

- create chat sessions and messages
- build a model router
- ingest URLs and PDFs
- retrieve evidence from Qdrant
- run a supervised analysis flow
- return structured responses in chat

### Version 2: Retrieval Strength

Goal:
Make retrieval more reliable and more useful.

Scope:

- better public site reading
- site crawling rules
- metadata-aware retrieval
- improved source ranking
- stronger citation behavior

### Version 3: Multi-agent supervision

Goal:
Introduce stronger coordination between specialized agents.

Scope:

- planner
- researcher
- analyst
- writer
- supervisor
- guardrails and validation

### Version 4: Long-running intelligence assistant

Goal:
Support continuous or recurring intelligence work.

Scope:

- tracked topics
- recurring jobs
- monitoring workflows
- alerts and periodic updates

## Environment configuration

The example environment file is:

- [.env.example](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\.env.example)

Current configuration includes support for:

- OpenAI API key
- Google API key
- Groq API key
- default model provider selection
- MongoDB connection
- Qdrant connection

## Development setup

This repository is still in scaffold stage, but the intended local setup is:

1. Create a Python `3.11` environment
2. Install dependencies
3. Copy `.env.example` to `.env`
4. Set your API keys and database values
5. Start MongoDB and Qdrant
6. Run the API server

### Recommended `uv` workflow

Use `uv` as the default environment manager for this project.

```powershell
uv python install 3.11
uv venv --python 3.11
.venv\Scripts\activate
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
```

If you want to run directly with `uv`, you can also use:

```powershell
uv run uvicorn procurebrain.main:app --reload
```

Example development command:

```powershell
python -m uvicorn procurebrain.main:app --reload
```

There is also a helper script at:

- [scripts/dev.ps1](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\scripts\dev.ps1)

### Requirements files

If you prefer simple requirements over editable installs, use:

- [requirements.txt](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\requirements.txt)
- [requirements-dev.txt](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\requirements-dev.txt)

## Docker

The repository includes starter Docker files for the API and worker plus a compose file for local services:

- [docker/docker-compose.yml](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\docker\docker-compose.yml)
- [docker/Dockerfile.api](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\docker\Dockerfile.api)
- [docker/Dockerfile.worker](C:\Users\DABC\Desktop\Learning\python\ProcureBrainv1\docker\Dockerfile.worker)

These are scaffold-level files and will need refinement as implementation continues.

## Current status

What is already done:

- stable project root established
- backend architecture documented
- MongoDB and Qdrant selected as main data layers
- multi-model support planned in configuration
- API route structure scaffolded
- skills system designed as a scalable plugin-style contract
- top-level skill manifests and templates added

What is not implemented yet:

- real chat models and schemas
- MongoDB repositories
- model router
- Qdrant indexing logic
- actual ingestion logic
- actual LangGraph workflow
- background job execution

## Recommended next implementation order

To move from scaffold to working Version 1, the best next order is:

1. implement MongoDB client and repositories
2. implement chat session and message schemas
3. implement model router for OpenAI, Gemini, and Groq
4. implement web and PDF ingestion pipeline
5. implement Qdrant storage and retrieval
6. connect the first LangGraph workflow
7. connect runtime skill composition into agent prompts
8. expose the first working chat research endpoint

## Repository creation note

This README is written to serve as the initial project description for your Git repository.

Before creating the repository, you may want to:

- rename the root from `ProcureBrainv1` to `ProcureBrain`
- add a license
- add contribution notes later if you want collaborators

## Summary

ProcureBrain is being built as a serious, scalable backend for a procurement and AI intelligence assistant.

The project is designed to stay modular, chat-first, source-aware, skill-driven, and ready for long-term growth without repeated folder reorganization.
