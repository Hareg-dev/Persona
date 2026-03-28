# Advanced Capabilities

## Direction

ProcureBrain is evolving beyond simple chat into a context-engineered research copilot.

Target advanced layers:

- context window management
- short-term and long-term memory
- knowledge graph extraction
- mindmap generation
- markdown and visual exports
- speech-ready outputs
- delegated deep-agent orchestration

## Recommended open-source building blocks

- `LangGraph` for graph orchestration: [langgraph](https://github.com/langchain-ai/langgraph)
- `Qdrant` for vector memory: [qdrant/qdrant](https://github.com/qdrant/qdrant)
- `Mem0` for richer long-term agent memory ideas: [mem0ai/mem0](https://github.com/mem0ai/mem0)
- `Graphiti` for real-time knowledge graph memory: [getzep/graphiti](https://github.com/getzep/graphiti)
- `Mermaid` for diagram generation: [mermaid-js/mermaid](https://github.com/mermaid-js/mermaid)
- `markmap` for markdown mindmaps: [markmap/markmap](https://github.com/markmap/markmap)
- `Plotly` for graph exports: [plotly/plotly.py](https://github.com/plotly/plotly.py)
- `Coqui TTS` for open speech generation: [coqui-ai/TTS](https://github.com/coqui-ai/TTS)

## Agent depth

Normal agent:

- one orchestrated workflow
- one main reasoning path
- limited task decomposition

Deep or sub-agent orchestration:

- one supervisor breaks work into sub-tasks
- multiple specialized agents work on distinct parts
- outputs are merged back into one response

For this project, start with normal graph agents and only add deep-agent delegation for very broad long-running research tasks.
