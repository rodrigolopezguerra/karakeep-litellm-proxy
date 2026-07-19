# karakeep-litellm-proxy

Proxy LiteLLM para Karakeep: multiplexa el endpoint OpenAI-compatible que Karakeep consume, ruteando:

- `/v1/chat/completions` (model `MiniMax-M3`) → MiniMax API cloud
- `/v1/embeddings` (model `embeddinggemma`) → Ollama local en la red `karakeep-shared`

## Variables de entorno requeridas

| Variable | Descripción |
|---|---|
| `MINIMAX_KEY` | API key de MiniMax (`https://api.minimax.io/v1`). Inyectada por el proxy al forwardear requests de chat. |
| `OLLAMA_BASE_URL` | (opcional, default `http://ollama:11434/v1`) URL del Ollama local para embeddings. |

## Variables internas

El proxy inyecta automáticamente `extra_body.thinking = {type: disabled}` y `extra_body.reasoning_split = true` en cada request al modelo `MiniMax-M3`, vía el callback `MiniMaxThinkingDisabler` definido en `callbacks.py`. Esto es requisito de MiniMax M3 para omitir el bloque de razonamiento en la respuesta.

## Healthcheck

- `GET /health/liveliness` — liveness
- `GET /health/readiness` — readiness

## Uso desde Karakeep

```yaml
OPENAI_BASE_URL: http://embedding-proxy:4000/v1
INFERENCE_TEXT_MODEL: MiniMax-M3
INFERENCE_IMAGE_MODEL: MiniMax-M3
EMBEDDING_TEXT_MODEL: embeddinggemma
```

`OPENAI_API_KEY` puede ir vacío: el proxy no valida el bearer entrante y reenvía con su propia key al upstream.

## Red

El contenedor debe estar en la red Docker externa `karakeep-shared` (id `u10t66t72qsaj7izfqvplp3a`) para poder resolver los hostnames `ollama` y `embedding-proxy` desde Karakeep.