"""FastAPI proxy transparente entre Karakeep y los providers de AI.

Ruteo:
- /v1/chat/completions -> MiniMax (api.minimax.io/v1) + inject thinking:{type:disabled} y reasoning_split=true
- /v1/models             -> MiniMax
- /v1/embeddings         -> Ollama interno (ollama:11434/v1) sirviendo embeddinggemma
- /health                -> health check local
"""
import os
import json
import httpx
from fastapi import FastAPI, Request, Response

app = FastAPI(title="karakeep-ai-proxy")

MINIMAX_BASE = os.environ.get("MINIMAX_BASE", "https://api.minimax.io/v1")
MINIMAX_KEY = os.environ.get("MINIMAX_KEY", "")
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://ollama:11434/v1")
OLLAMA_KEY = os.environ.get("OLLAMA_KEY", "")  # usually empty (no auth on local ollama)

TIMEOUT_SEC = int(os.environ.get("PROXY_TIMEOUT_SEC", "300"))


def is_chat(path: str) -> bool:
    return "chat/completions" in path


def is_embed(path: str) -> bool:
    return "embeddings" in path


def inject_thinking(body_json):
    """M3 default emite 思考; force off y separamos en reasoning_details."""
    if isinstance(body_json, dict) and "messages" in body_json:
        body_json["thinking"] = {"type": "disabled"}
        body_json["reasoning_split"] = True
    return body_json


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def passthrough(full_path: str, request: Request):
    body_bytes = await request.body()
    body_json = None
    if body_bytes:
        try:
            body_json = json.loads(body_bytes)
        except json.JSONDecodeError:
            pass

    target_base = OLLAMA_BASE if is_embed(full_path) else MINIMAX_BASE
    target_key = OLLAMA_KEY if is_embed(full_path) else MINIMAX_KEY

    if is_chat(full_path):
        body_json = inject_thinking(body_json)
        if body_json is not None:
            body_bytes = json.dumps(body_json).encode()

    forward_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length", "authorization"}
    }
    if target_key:
        forward_headers["Authorization"] = f"Bearer {target_key}"

    async with httpx.AsyncClient(timeout=TIMEOUT_SEC) as client:
        upstream = await client.request(
            method=request.method,
            url=f"{target_base}/{full_path}",
            params=request.query_params,
            headers=forward_headers,
            content=body_bytes,
        )

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers={k: v for k, v in upstream.headers.items()
                 if k.lower() not in {"content-encoding", "transfer-encoding"}},
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "minimax_key_present": bool(MINIMAX_KEY),
        "ollama_target": OLLAMA_BASE,
    }
