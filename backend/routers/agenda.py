from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.tools import calendar as cal_tools
from backend.tools import tasks as task_tools

router = APIRouter(prefix="/api", tags=["agenda"])


class EventCreate(BaseModel):
    title: str
    date: str
    time: str
    description: str = ""
    duration_minutes: int = 60


class TodoCreate(BaseModel):
    task: str
    priority: str = "normal"


class NoteCreate(BaseModel):
    content: str


@router.get("/events")
def get_events(days_ahead: int = 7):
    try:
        return cal_tools.list_events(days_ahead)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/events")
def create_event(event: EventCreate):
    try:
        return cal_tools.create_event(**event.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/events/{event_id}")
def delete_event(event_id: str):
    try:
        return cal_tools.delete_event(event_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/todos")
def get_todos(only_pending: bool = True):
    return task_tools.list_todos(only_pending)


@router.post("/todos")
def create_todo(todo: TodoCreate):
    return task_tools.add_todo(todo.task, todo.priority)


@router.patch("/todos/{todo_id}/complete")
def complete_todo(todo_id: int):
    return task_tools.complete_todo(todo_id)


@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    return task_tools.delete_todo(todo_id)


@router.get("/notes")
def get_notes():
    return task_tools.list_notes()


@router.post("/notes")
def create_note(note: NoteCreate):
    return task_tools.add_note(note.content)
