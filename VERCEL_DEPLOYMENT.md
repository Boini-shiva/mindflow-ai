# Deploying MindFlow AI to Vercel (Services)

This repo deploys as **one Vercel project with two services**, configured in the root [`vercel.json`](vercel.json).

| Service    | Root        | Framework | Public paths                                                                 |
|------------|-------------|-----------|------------------------------------------------------------------------------|
| `backend`  | `backend/`  | FastAPI (`main:app`) | `/api/*`, `/health`, `/omi`, `/omi/*`, `/webhook/*`, `/docs`, `/openapi.json` |
| `frontend` | `frontend/` | Vite (React SPA)     | everything else (`/*`), with SPA fallback to `index.html`                    |

The backend service receives the **original request path** (e.g. `/api/stats`), which matches the FastAPI router prefixes as-is — no path rewriting is needed.

## Service-to-service calls (bindings)

There are **no bindings**. The frontend is a static SPA: all API calls are made by the browser to same-origin relative URLs (`/api/...`, `/health`), and the top-level rewrites route them to `backend`. The backend only calls external services (Lyzr, Qdrant, OpenAI embeddings), never the frontend.

## Deploy

1. Import `Boini-shiva/mindflow-ai` in the [Vercel Dashboard](https://vercel.com/new). Keep Root Directory as `./`.
2. Add environment variables (shared by all services):

   | Variable | Notes |
   |---|---|
   | `LYZR_API_KEY`, `LYZR_MANAGER_AGENT_ID`, `LYZR_SUMMARIZER_AGENT_ID`, `LYZR_TASK_AGENT_ID`, `LYZR_MEMORY_AGENT_ID` | Lyzr Studio |
   | `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION` | Qdrant Cloud |
   | `EMBEDDING_PROVIDER` (`fastembed` or `openai`), `EMBEDDING_API_KEY` | Embeddings |
   | `OMI_WEBHOOK_SECRET` | Optional |

   Do **not** set `VITE_API_BASE_URL` — leave it empty so the frontend stays same-origin.
3. Deploy.

## Local development

- **All services together (recommended):** `vercel dev` (or `vercel dev -L` without logging in).
- **Separately:** run `uvicorn app.main:app --port 8000` in `backend/` and `npm run dev` in `frontend/`; the Vite proxy forwards `/api`, `/health`, `/omi` to port 8000.

## Notes / limitations

- Local JSON storage lives in `/tmp` on Vercel and is **not persistent** across function instances. Qdrant is the durable store for memories.
- FastEmbed downloads its model into `/tmp` on cold start; if that fails, a deterministic fallback vector is used. For production-quality retrieval, consider `EMBEDDING_PROVIDER=openai`.
