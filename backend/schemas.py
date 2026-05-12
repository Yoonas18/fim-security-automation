from typing import Literal

from pydantic import BaseModel, Field


EventType = Literal["file_created", "file_modified", "file_deleted"]


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=200)


class Report(BaseModel):
    agent_id: str = Field(min_length=1, max_length=80)
    file: str = Field(min_length=1, max_length=2048)
    event: EventType
    hash: str | None = Field(default=None, max_length=128)
    size: int | None = Field(default=None, ge=0)


class EventRecord(BaseModel):
    id: int
    agent: str
    file: str
    event: EventType
    severity: str
    time: int
    hash: str | None = None
    size: int | None = None
