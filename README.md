# RAG Ingestion Checkpoint Workbench

FastAPI + React control plane for running RAG document ingestion as checkpointed, resumable workflows.

## What it does

• Upload documents and watch each one move through parse → chunk → embed → index checkpoints.
• Retry failed stages from the last good checkpoint instead of re-running the whole pipeline.
• Inspect a dead-letter queue of permanent failures with error context.
• View live pipeline health metrics (throughput, failure rate, stage latency).

## Why

Most RAG demos stop at "the file got indexed." Production ingestion breaks silently:
synchronous endpoints time out on large files, partial embedding/upsert leaves the index
inconsistent, rate-limit fallbacks return HTTP 200 with empty arrays, and no one notices
missing chunks until retrieval quality drops. This workbench surfaces and replays those
operational failures.

## Stack

• Backend: Python 3.11+, FastAPI, SQLite (durable checkpoint store), pytest
• Frontend: React + Vite
• Pipeline concepts: durable execution, dead-letter queue, checkpoint/replay, metrics

## Run locally

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Backend defaults to `http://localhost:8000`. Open the frontend at the Vite URL and use
the workbench to create a project, upload documents, and replay failed jobs.
