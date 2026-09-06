"""
Ponto de entrada da API. Rodar localmente com:

    uvicorn panel_backend.api.app:app --reload

Isso sobe em http://localhost:8000 — que é exatamente o default que
panel_client/api_client.py já espera (troque via variável de ambiente
PANEL_API_BASE_URL dos dois lados se for rodar em outro endereço).
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from panel_backend.api.routes import account, auth, moderation, moderator_tokens, moderators, publications, reports
from panel_backend.db import init_db

@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Panel API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(account.router)
app.include_router(publications.router)
app.include_router(moderation.router)
app.include_router(moderator_tokens.router)
app.include_router(moderators.router)
app.include_router(reports.router)
