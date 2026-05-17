from __future__ import annotations

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, description="The note content text")


class NoteRead(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemRead(BaseModel):
    id: int
    note_id: int | None = None
    text: str
    done: bool
    created_at: str


class ActionItemSummary(BaseModel):
    id: int
    text: str


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the text as a note")


class ExtractResponse(BaseModel):
    note_id: int | None = None
    items: list[ActionItemSummary]


class MarkDoneRequest(BaseModel):
    done: bool = Field(default=True, description="Whether the action item is done")
