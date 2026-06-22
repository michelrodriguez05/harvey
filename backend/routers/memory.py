from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from backend.memory.store import MemoryStore

router = APIRouter(prefix="/api/memory", tags=["memory"])
store = MemoryStore()


class RememberRequest(BaseModel):
    key: str
    value: str
    category: str = "general"
    importance: int = 5


class PreferenceRequest(BaseModel):
    key: str
    value: Any


class ProjectRequest(BaseModel):
    name: str
    description: str = ""
    status: str = "active"


class UserNameRequest(BaseModel):
    name: str


@router.get("/context")
def get_context():
    ctx = store.get_context()
    return {
        "user_name": ctx.user_name,
        "preferences": ctx.preferences,
        "facts": ctx.facts,
        "projects": ctx.projects,
    }


@router.get("/facts")
def list_facts(category: str | None = None):
    return {"facts": store.list_facts(category)}


@router.post("/facts")
def remember(req: RememberRequest):
    return store.remember(req.key, req.value, req.category, req.importance)


@router.delete("/facts/{key}")
def forget(key: str):
    return {"deleted": store.forget(key)}


@router.get("/projects")
def list_projects():
    return {"projects": store.list_projects()}


@router.post("/projects")
def save_project(req: ProjectRequest):
    return store.upsert_project(req.name, req.description, status=req.status)


@router.post("/preferences")
def set_preference(req: PreferenceRequest):
    store.set_preference(req.key, req.value)
    return {"ok": True}


@router.post("/user")
def set_user_name(req: UserNameRequest):
    store.set_user_name(req.name)
    return {"name": req.name}


@router.get("/sessions")
def recent_sessions():
    return {"sessions": store.get_recent_sessions()}
