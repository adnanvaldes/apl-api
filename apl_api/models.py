from pydantic import BaseModel
from typing import List
from sqlmodel import Field, SQLModel, create_engine
from apl_api.config import settings

sqlite_file = settings.database
sqlite_url = f"sqlite:///{sqlite_file}"
engine = create_engine(sqlite_url)


class PatternLinks(SQLModel, table=True):
    pattern_id: int = Field(foreign_key="patterns.id", primary_key=True)
    linked_pattern_id: int = Field(foreign_key="patterns.id", primary_key=True)


class Patterns(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    problem: str
    solution: str
    page_number: int
    confidence: int
    tag: str


class PatternResponse(BaseModel):
    id: int
    name: str
    problem: str
    solution: str
    page_number: int
    confidence: int
    tag: str
    forward_links: List["PatternResponse"] = []
    backlinks: List["PatternResponse"] = []

    class Config:
        from_attributes = True
