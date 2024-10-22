from typing import Annotated, List, Optional
from sqlalchemy.orm import joinedload

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship

class Related_Patterns(SQLModel, table=True):
    __tablename__ = "related_patterns"
    pattern_id: int = Field(foreign_key="pattern.id", primary_key=True)
    related_patterns_id: int = Field(foreign_key="pattern.id", primary_key=True)

class Backlinks(SQLModel, table=True):
    __tablename__ = "backlinks"
    pattern_id: int = Field(foreign_key="pattern.id", primary_key=True)
    backlink_pattern_id: int = Field(foreign_key="pattern.id", primary_key=True)

class Pattern(SQLModel, table=True):
    __tablename__ = "pattern"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    problem: str
    solution: str
    related_text: str

    # Related patterns (forward links to other patterns)
    related_patterns: List["Pattern"] = Relationship(
        back_populates="backlinks", 
        link_model=Related_Patterns,
        sa_relationship_kwargs={
            "primaryjoin": "Pattern.id == Related_Patterns.pattern_id",
            "secondaryjoin": "Pattern.id == Related_Patterns.related_patterns_id",
            "foreign_keys": "[Related_Patterns.pattern_id, Related_Patterns.related_patterns_id]"
        }
    )

    # Backlinks (patterns that link to this pattern)
    backlinks: List["Pattern"] = Relationship(
        back_populates="related_patterns", 
        link_model=Backlinks,
        sa_relationship_kwargs={
            "primaryjoin": "Pattern.id == Backlinks.backlink_pattern_id",
            "secondaryjoin": "Pattern.id == Backlinks.pattern_id",
        }
    )


sqlite_file_name = "apl.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()

@app.get("/patterns/{id}")
async def get_pattern(id: int, session: SessionDep):
    # Query the pattern by ID and load related patterns and backlinks eagerly
    pattern = session.exec(
    select(Pattern)
    .where(Pattern.id == id)
    ).first()

    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    # Debug: Print all related patterns and backlinks
    all_related_patterns = [{"id": p.id, "name": p.name} for p in pattern.related_patterns]
    all_backlinks = [{"id": p.id, "name": p.name} for p in pattern.backlinks]

    print(pattern)
    print("\n\n\n\n")
    print(pattern.backlinks)
    print("\n\n\n\n")
    # Return the pattern details along with related patterns and backlinks
    return {
        "id": pattern.id,
        "name": pattern.name,
        "problem": pattern.problem,
        "solution": pattern.solution,
        "related_text": pattern.related_text,
        "related_patterns": all_related_patterns,
        "backlinks": all_backlinks
    }

@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]


