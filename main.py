from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import List, Optional

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///apl.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# PatternLink Model
class PatternLink(Base):
    __tablename__ = 'PatternLinks'  # Use lowercase for table names
    pattern_id = Column(Integer, ForeignKey('Patterns.id'), primary_key=True)
    linked_pattern_id = Column(Integer, ForeignKey('Patterns.id'), primary_key=True)

# Pattern Model
class Pattern(Base):
    __tablename__ = 'Patterns'  # Use lowercase for table names
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    problem = Column(String)
    solution = Column(String)
    refs = Column(String, nullable=True)

    # Relationship to itself through PatternLink
    forward_links = relationship(
        "Pattern",
        secondary="PatternLinks",  # Use the lowercase table name
        primaryjoin="Pattern.id == PatternLink.pattern_id",
        secondaryjoin="Pattern.id == PatternLink.linked_pattern_id",
        backref="backlinks"
    )

# Pydantic Models
class PatternBase(BaseModel):
    name: str
    problem: str
    solution: str
    refs: Optional[str] = None

class PatternCreate(PatternBase):
    pass

class PatternResponse(PatternBase):
    id: int
    forward_links: List[Optional[PatternBase]] = []
    backlinks: List[Optional[PatternBase]] = []

    class Config:
        orm_mode = True

# Dependency to get DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app

app = FastAPI()

# Utility function to get pattern by ID or name
def get_pattern(db: Session, id: Optional[int] = None, name: Optional[str] = None):
    if id:
        return db.query(Pattern).filter(Pattern.id == id).first()
    elif name:
        return db.query(Pattern).filter(Pattern.name == name).first()
    else:
        return None

# Endpoint to get pattern by ID
@app.get("/patterns/{id}/", response_model=PatternResponse)
def get_pattern_by_id(id: int, db: Session = Depends(get_db)):
    pattern = get_pattern(db, id=id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return pattern

# Endpoint to get pattern by name
@app.get("/patterns/name/{pattern_name}", response_model=PatternResponse)
def get_pattern_by_name(pattern_name: str, db: Session = Depends(get_db)):
    pattern = get_pattern(db, name=pattern_name)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return pattern
