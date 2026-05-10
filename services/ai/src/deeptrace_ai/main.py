import os
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import httpx
import structlog
from pydantic import BaseModel

from .embeddings import get_or_cache_embedding

logger = structlog.get_logger()

app = FastAPI(title="DeepTrace AI Service", version="0.1.0")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")


class ChatRequest(BaseModel):
    messages: list[dict]
    context: str | None = None
    stream: bool = True


class SummarizeRequest(BaseModel):
    findings: dict


class ExplainRelationshipRequest(BaseModel):
    graph_path: dict


class AnomalyRequest(BaseModel):
    investigation_data: dict


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai"}


@app.post("/ai/chat")
async def chat(request: ChatRequest):
    async def event_generator():
        await get_or_cache_embedding({"messages": request.messages})
        
        payload = {
            "model": DEFAULT_MODEL,
            "messages": request.messages,
            "stream": request.stream,
        }
        if request.context:
            payload["context"] = request.context

        async with httpx.AsyncClient(base_url=OLLAMA_BASE_URL) as client:
            async with client.stream("POST", "/api/chat", json=payload, timeout=60.0) as response:
                async for line in response.aiter_lines():
                    if line:
                        yield line

    return EventSourceResponse(event_generator())


@app.post("/ai/summarize")
async def summarize(request: SummarizeRequest):
    await get_or_cache_embedding(request.findings)
    
    prompt = f"""Summarize the following investigation findings concisely:

{request.findings}

Provide a brief summary highlighting key discoveries, evidence links, and notable patterns."""

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    async with httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=60.0) as client:
        response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        result = response.json()
        return {"summary": result.get("message", {}).get("content", "")}


@app.post("/ai/explain-relationship")
async def explain_relationship(request: ExplainRelationshipRequest):
    await get_or_cache_embedding(request.graph_path)
    
    prompt = f"""Explain this graph relationship in natural language:

Graph Path: {request.graph_path}

Describe the connection between entities, the relationship type, and any significance for an investigation."""

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    async with httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=60.0) as client:
        response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        result = response.json()
        return {"explanation": result.get("message", {}).get("content", "")}


@app.post("/ai/anomaly")
async def detect_anomalies(request: AnomalyRequest):
    await get_or_cache_embedding(request.investigation_data)
    
    prompt = f"""Analyze this investigation data for anomalies and suspicious patterns:

{request.investigation_data}

Identify potential red flags, unusual connections, suspicious timing, or data inconsistencies. Return a JSON list of anomaly flags with confidence scores."""

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    async with httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=60.0) as client:
        response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        result = response.json()
        return {"anomalies": result.get("message", {}).get("content", "")}