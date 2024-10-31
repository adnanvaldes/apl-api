import os
from contextlib import asynccontextmanager

from typing import Annotated, List
from pydantic import BaseModel

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from apl_api.parser import load_data


sqlite_file = "apl.db"
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


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.path.exists("apl.db"):
        os.remove("apl.db")
    load_data()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(load_data, IntervalTrigger(days=1))
    scheduler.start()
    yield
    if os.path.exists("apl.db"):
        os.remove("apl.db")
    scheduler.shutdown()


sqlite_file = "apl.db"
sqlite_url = f"sqlite:///{sqlite_file}"
engine = create_engine(sqlite_url)

SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI(lifespan=lifespan)


def get_pattern(
    pattern_id: int, session: SessionDep, depth: Annotated[int, Query(le=3)] = 0
) -> PatternResponse:
    pattern = session.get(Patterns, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    if depth > 0:
        # Recursively fetch forward links
        forward_link_ids = session.exec(
            select(PatternLinks.linked_pattern_id).where(
                PatternLinks.pattern_id == pattern_id
            )
        ).all()
        forward_links = session.exec(
            select(Patterns).where(Patterns.id.in_(forward_link_ids))
        ).all()
        forward_link_responses = [
            get_pattern_by_id(pattern_id=link.id, session=session, depth=depth - 1)
            for link in forward_links
        ]

        # Recursively fetch backlinks
        backlink_ids = session.exec(
            select(PatternLinks.pattern_id).where(
                PatternLinks.linked_pattern_id == pattern_id
            )
        ).all()
        backlinks = session.exec(
            select(Patterns).where(Patterns.id.in_(backlink_ids))
        ).all()
        backlink_responses = [
            get_pattern_by_id(pattern_id=link.id, session=session, depth=depth - 1)
            for link in backlinks
        ]
    else:
        forward_link_responses = []
        backlink_responses = []

    # Return the pattern data with links
    return PatternResponse(
        id=pattern.id,
        name=pattern.name.title(),
        problem=pattern.problem,
        solution=pattern.solution,
        page_number=pattern.page_number,
        confidence=pattern.confidence,
        tag=pattern.tag,
        forward_links=forward_link_responses,
        backlinks=backlink_responses,
    )


@app.get("/patterns/id/{id}", response_model=PatternResponse)
def get_pattern_by_id(
    pattern_id: int, session: SessionDep, depth: Annotated[int, Query(le=3)] = 0
) -> PatternResponse:
    return get_pattern(pattern_id=pattern_id, session=session, depth=depth)


@app.get("/patterns/name/{pattern_name}", response_model=PatternResponse)
def get_pattern_by_name(
    pattern_name: str, session: SessionDep, depth: Annotated[int, Query(le=3)] = 0
) -> PatternResponse:
    statement = select(Patterns).where(Patterns.name == pattern_name.lower())
    pattern = session.exec(statement).first()

    return get_pattern(pattern_id=pattern.id, session=session, depth=depth)


@app.get("/patterns/find/{name}", response_model=List[Patterns])
def find_pattern_by_name(name: str, session: SessionDep) -> List[Patterns]:
    statement = select(Patterns).where(Patterns.name.like(f"%{name}%"))
    return session.exec(statement).all()


@app.get("/patterns/page_number/{page_number}", response_model=Patterns)
def get_pattern_by_page_number(page_number: int, session: SessionDep) -> Patterns:
    # Find the pattern with the highest page_number less than or equal to the specified page_number
    statement = (
        select(Patterns)
        .where(Patterns.page_number <= page_number)
        .order_by(Patterns.page_number.desc())
    )
    closest_pattern = session.exec(statement).first()

    if closest_pattern is None:
        raise HTTPException(
            status_code=404,
            detail="No pattern found at or below the specified page number, first pattern at page_number = 10",
        )

    return closest_pattern


@app.get("/patterns/confidence/{confidence}", response_model=List[Patterns])
def get_patterns_by_confidence(confidence: int, session: SessionDep) -> List[Patterns]:
    statement = select(Patterns).where(Patterns.confidence == confidence)
    return session.exec(statement).all()


@app.get("/patterns/tag/{tag}", response_model=List[Patterns])
def get_patterns_by_tag(tag: str, session: SessionDep) -> List[Patterns]:
    statement = select(Patterns).where(Patterns.tag.like(f"%{tag}%"))
    return session.exec(statement).all()