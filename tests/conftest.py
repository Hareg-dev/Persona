from pathlib import Path
import sys
import types

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


if "fastapi" not in sys.modules:
    fastapi_module = types.ModuleType("fastapi")

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class _Status:
        HTTP_404_NOT_FOUND = 404

    fastapi_module.HTTPException = HTTPException
    fastapi_module.status = _Status()
    sys.modules["fastapi"] = fastapi_module


if "trafilatura" not in sys.modules:
    trafilatura_module = types.ModuleType("trafilatura")
    trafilatura_module.extract = lambda html, url=None, include_comments=False, include_links=False: html
    sys.modules["trafilatura"] = trafilatura_module


if "langgraph.graph" not in sys.modules:
    langgraph_module = types.ModuleType("langgraph")
    graph_module = types.ModuleType("langgraph.graph")
    START = "__start__"
    END = "__end__"

    class _CompiledGraph:
        def __init__(self, nodes, edges):
            self.nodes = nodes
            self.edges = edges

        async def ainvoke(self, state):
            current = self.edges.get(START)
            while current and current != END:
                state = await self.nodes[current](state)
                current = self.edges.get(current)
            return state

    class StateGraph:
        def __init__(self, _state_type):
            self.nodes = {}
            self.edges = {}

        def add_node(self, name, fn):
            self.nodes[name] = fn

        def add_edge(self, source, target):
            self.edges[source] = target

        def compile(self):
            return _CompiledGraph(self.nodes, self.edges)

    graph_module.START = START
    graph_module.END = END
    graph_module.StateGraph = StateGraph
    langgraph_module.graph = graph_module
    sys.modules["langgraph"] = langgraph_module
    sys.modules["langgraph.graph"] = graph_module


if "langchain_core.messages" not in sys.modules:
    lc_module = types.ModuleType("langchain_core")
    lc_messages = types.ModuleType("langchain_core.messages")

    class _BaseMessage:
        def __init__(self, content: str):
            self.content = content

    lc_messages.AIMessage = _BaseMessage
    lc_messages.HumanMessage = _BaseMessage
    lc_messages.SystemMessage = _BaseMessage
    lc_module.messages = lc_messages
    sys.modules["langchain_core"] = lc_module
    sys.modules["langchain_core.messages"] = lc_messages


if "bson" not in sys.modules:
    bson_module = types.ModuleType("bson")

    class ObjectId(str):
        pass

    bson_module.ObjectId = ObjectId
    sys.modules["bson"] = bson_module


if "motor.motor_asyncio" not in sys.modules:
    motor_module = types.ModuleType("motor")
    motor_asyncio = types.ModuleType("motor.motor_asyncio")

    class AsyncIOMotorDatabase:
        def __getitem__(self, name):
            return self

        async def command(self, _name):
            return {"ok": 1}

        async def create_index(self, *args, **kwargs):
            return None

    class AsyncIOMotorClient:
        def __init__(self, *_args, **_kwargs):
            self.db = AsyncIOMotorDatabase()

        def __getitem__(self, _name):
            return self.db

    motor_asyncio.AsyncIOMotorClient = AsyncIOMotorClient
    motor_asyncio.AsyncIOMotorDatabase = AsyncIOMotorDatabase
    motor_module.motor_asyncio = motor_asyncio
    sys.modules["motor"] = motor_module
    sys.modules["motor.motor_asyncio"] = motor_asyncio


if "duckduckgo_search" not in sys.modules:
    ddg_module = types.ModuleType("duckduckgo_search")

    class DDGS:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text(self, query, max_results=5):
            return [{"title": "Example", "href": "https://example.com", "body": query}] * max_results

    ddg_module.DDGS = DDGS
    sys.modules["duckduckgo_search"] = ddg_module


if "qdrant_client.models" not in sys.modules:
    qdrant_module = types.ModuleType("qdrant_client")
    qdrant_models = types.ModuleType("qdrant_client.models")

    class _Simple:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    qdrant_models.FieldCondition = _Simple
    qdrant_models.Filter = _Simple
    qdrant_models.MatchValue = _Simple
    qdrant_models.PointStruct = _Simple
    qdrant_models.Distance = _Simple
    qdrant_models.VectorParams = _Simple

    class QdrantClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_collections(self):
            class R:
                collections = []
            return R()

        def create_collection(self, *args, **kwargs):
            return None

        def upsert(self, *args, **kwargs):
            return None

        def search(self, *args, **kwargs):
            return []

    qdrant_module.QdrantClient = QdrantClient
    qdrant_module.models = qdrant_models
    sys.modules["qdrant_client"] = qdrant_module
    sys.modules["qdrant_client.models"] = qdrant_models


class FakeChatModel:
    def __init__(self, content: str = "ok") -> None:
        self.content = content

    async def ainvoke(self, _messages):
        class Response:
            def __init__(self, content: str) -> None:
                self.content = content

        return Response(self.content)


@pytest.fixture
def fake_chat_model():
    return FakeChatModel()
