"""
BMad Studio — FastAPI Backend
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.bmad_loader import BmadLoader
from core.persona_engine import PersonaEngine
from core.prompt_compiler import PromptCompiler
from core.artifact_store import ArtifactStore

from routers.common import (
    status_router, persona_router, agents_router,
    workflows_router, templates_router, artifacts_router,
    workspace_router, config_router, export_router,
)
from routers.pipeline import router as pipeline_router
from routers.agent_builder import router as agent_builder_router
from routers.chat_validate import chat_router, validate_router


# ─── LIFESPAN ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load everything
    print("\n🚀 BMad Studio API starting up...")

    bmad = BmadLoader()
    bmad.load()

    persona_engine = PersonaEngine(bmad_loader=bmad)
    prompt_compiler = PromptCompiler(bmad_loader=bmad, persona_engine=persona_engine)
    artifact_store = ArtifactStore()

    app.state.bmad = bmad
    app.state.persona_engine = persona_engine
    app.state.prompt_compiler = prompt_compiler
    app.state.artifact_store = artifact_store

    print(f"✅ Ready — {bmad.agent_count} agents, {bmad.workflow_count} workflows loaded")
    print(f"📝 Docs: http://localhost:8000/docs\n")

    yield

    print("👋 BMad Studio shutting down")


# ─── APP ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="BMad Studio API",
    description="AI Development Platform — structured agent teams, industry knowledge, human-in-the-loop",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── ROUTERS ──────────────────────────────────────────────────────────────────

app.include_router(status_router,        prefix="/status",        tags=["Status"])
app.include_router(persona_router,       prefix="/persona",       tags=["Persona"])
app.include_router(agents_router,        prefix="/agents",        tags=["Agents"])
app.include_router(workflows_router,     prefix="/workflows",     tags=["Workflows"])
app.include_router(templates_router,     prefix="/templates",     tags=["Templates"])
app.include_router(artifacts_router,     prefix="/artifact",      tags=["Artifacts"])
app.include_router(workspace_router,     prefix="/workspace",     tags=["Workspace"])
app.include_router(config_router,        prefix="/config",        tags=["Config"])
app.include_router(export_router,        prefix="/export",        tags=["Export"])
app.include_router(pipeline_router,      prefix="/pipeline",      tags=["Pipeline"])
app.include_router(agent_builder_router, prefix="/agent-builder", tags=["Agent Builder"])
app.include_router(chat_router,          prefix="/chat",          tags=["Chat"])
app.include_router(validate_router,      prefix="/validate",      tags=["Validate"])


# ─── ROOT ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "BMad Studio API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "/status",
    }
