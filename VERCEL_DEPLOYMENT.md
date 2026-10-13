# Deploying MindFlow AI to Vercel

This repository is pre-configured for deployment on **Vercel** with full connectivity between the React frontend and FastAPI backend.

---

## Architecture on Vercel

```
                        ┌──────────────────────────────────────┐
                        │             Vercel Edge              │
                        │                                      │
  Client Requests ─────►│  • /api/*, /health ──► api/index.py  │ (FastAPI Serverless Function)
                        │  • /* (UI)         ──► frontend/dist │ (React + Vite SPA)
                        └──────────────────┬───────────────────┘
                                           │
                        ┌──────────────────▼───────────────────┐
                        │       External AI Services           │
                        │  • Lyzr Studio Multi-Agent API       │
                        │  • Qdrant Cloud Vector Database      │
                        └──────────────────────────────────────┘
```

---

## Deployment Option A: All-in-One Full-Stack Monorepo (Recommended)

In this option, Vercel hosts both the React Vite frontend and the Python FastAPI backend in a single project.

### Step 1: Connect Repository to Vercel
1. Log in to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** -> **Project**.
3. Import `Boini-shiva/mindflow-ai`.
4. Keep the **Root Directory** as `./` (default).
5. The root `vercel.json` will automatically configure:
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
   - Serverless Function: `api/index.py` (FastAPI)
   - Rewrites: `/health` and `/api/*` route to `api/index.py`, all other routes serve the React SPA.

### Step 2: Configure Environment Variables in Vercel
In the Vercel project settings (**Settings** -> **Environment Variables**), add:

| Variable | Description | Example / Default |
|---|---|---|
| `LYZR_API_KEY` | Lyzr Studio API Key | `your_lyzr_api_key` |
| `LYZR_MANAGER_AGENT_ID` | Manager Agent ID | `your_manager_agent_id` |
| `LYZR_SUMMARIZER_AGENT_ID` | Summarizer Agent ID | `your_summarizer_agent_id` |
| `LYZR_TASK_AGENT_ID` | Task Extractor Agent ID | `your_task_agent_id` |
| `LYZR_MEMORY_AGENT_ID` | Memory Assistant Agent ID | `your_memory_agent_id` |
| `QDRANT_URL` | Qdrant Cloud Cluster URL | `https://your-cluster.qdrant.io:6333` |
| `QDRANT_API_KEY` | Qdrant Cloud API Key | `your_qdrant_api_key` |
| `QDRANT_COLLECTION` | Qdrant Collection Name | `mindflow_memories` |
| `EMBEDDING_PROVIDER` | Vector Embedding Provider | `fastembed` (or `openai`) |
| `EMBEDDING_API_KEY` | API Key if using `openai` embeddings | `sk-...` (optional) |
| `OMI_WEBHOOK_SECRET` | Secret token for Omi webhook authentication | `your_token` (optional) |

> **Note on Frontend-Backend Connection:**
> When deployed together, the frontend automatically routes all requests to `/api` and `/health` on the same origin (no CORS or manual URL configuration needed).

### Step 3: Deploy
Click **Deploy**. Once completed, your application is live with both the frontend interface and FastAPI backend!

---

## Deployment Option B: Split Deployment (Frontend on Vercel + Backend on Render/Railway)

If you prefer running the Python FastAPI backend as a persistent long-running service (e.g. on [Render](https://render.com), [Railway](https://railway.app), [Fly.io](https://fly.io), or Docker) while hosting the frontend on Vercel:

### Step 1: Deploy Backend to Render or Railway
- Deploy `backend/` using Docker or Python runtime.
- Start command: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Set your Lyzr and Qdrant environment variables.
- Copy your deployed backend URL (e.g. `https://mindflow-api.onrender.com`).

### Step 2: Deploy Frontend to Vercel
1. Import repository `Boini-shiva/mindflow-ai` into Vercel.
2. Set **Root Directory** to `frontend`.
3. Add the following environment variable:
   - `VITE_API_BASE_URL` = `https://mindflow-api.onrender.com` (your backend URL)
4. Click **Deploy**.
5. The frontend will automatically connect to your hosted backend!

---

## Verification & Health Check

After deployment, test the following endpoints:
- **Frontend UI**: `https://your-app.vercel.app`
- **Health Check**: `https://your-app.vercel.app/health`
- **System Stats**: `https://your-app.vercel.app/api/stats`
- **Memories**: `https://your-app.vercel.app/api/memories`
- **Agent Activity**: `https://your-app.vercel.app/api/agents/activity`
