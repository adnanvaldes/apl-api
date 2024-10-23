from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import List, Optional

SQLALCHEMY_DATABASE_URL = "sqlite:///apl.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PatternLink(Base):
    __tablename__ = 'PatternLinks'
    pattern_id = Column(Integer, ForeignKey('Patterns.id'), primary_key=True)
    linked_pattern_id = Column(Integer, ForeignKey('Patterns.id'), primary_key=True)


class Pattern(Base):
    __tablename__ = 'Patterns'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    problem = Column(String)
    solution = Column(String)
    refs = Column(String, nullable=True)


    forward_links = relationship(
        "Pattern",
        secondary="PatternLinks",
        primaryjoin="Pattern.id == PatternLink.pattern_id",
        secondaryjoin="Pattern.id == PatternLink.linked_pattern_id",
        backref="backlinks"
    )



class PatternLinkResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class PatternResponse(BaseModel):
    id: int
    name: str
    problem: str
    solution: str
    refs: Optional[str] = None
    forward_links: List[PatternLinkResponse] = [] 
    backlinks: List[PatternLinkResponse] = [] 

    class Config:
        orm_mode = True


class PatternResponseFull(PatternResponse):
    forward_links: List[PatternResponse] = []
    backlinks: List[PatternResponse] = []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


def get_pattern(db: Session, id: Optional[int] = None, name: Optional[str] = None):
    if id:
        return db.query(Pattern).filter(Pattern.id == id).first()
    elif name:
        return db.query(Pattern).filter(Pattern.name == name).first()
    else:
        return None


@app.get("/patterns/{id}")
def get_pattern_by_id(id: int, expand: bool = False, db: Session = Depends(get_db)):
    pattern = get_pattern(db, id=id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    

    if expand:
        return PatternResponseFull(
            id=pattern.id,
            name=pattern.name,
            problem=pattern.problem,
            solution=pattern.solution,
            refs=pattern.refs,
            forward_links=[
                PatternResponse(
                    id=link.id, 
                    name=link.name,
                    problem=link.problem,
                    solution=link.solution,
                    refs=link.refs
                ) for link in pattern.forward_links
            ],
            backlinks=[
                PatternResponse(
                    id=link.id, 
                    name=link.name,
                    problem=link.problem,
                    solution=link.solution,
                    refs=link.refs
                ) for link in pattern.backlinks
            ]
        )
    else:
        return PatternResponse(
            id=pattern.id,
            name=pattern.name,
            problem=pattern.problem,
            solution=pattern.solution,
            refs=pattern.refs,
            forward_links=[
                PatternLinkResponse(id=link.id, name=link.name) for link in pattern.forward_links
            ],
            backlinks=[
                PatternLinkResponse(id=link.id, name=link.name) for link in pattern.backlinks
            ]
        )


@app.get("/patterns/name/{pattern_name}")
def get_pattern_by_name(pattern_name: str, expand: bool = False, db: Session = Depends(get_db)):
    pattern = get_pattern(db, name=pattern_name)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    

    if expand:
        return PatternResponseFull(
            id=pattern.id,
            name=pattern.name,
            problem=pattern.problem,
            solution=pattern.solution,
            refs=pattern.refs,
            forward_links=[
                PatternResponse(
                    id=link.id, 
                    name=link.name,
                    problem=link.problem,
                    solution=link.solution,
                    refs=link.refs
                ) for link in pattern.forward_links
            ],
            backlinks=[
                PatternResponse(
                    id=link.id, 
                    name=link.name,
                    problem=link.problem,
                    solution=link.solution,
                    refs=link.refs
                ) for link in pattern.backlinks
            ]
        )
    else:
        return PatternResponse(
            id=pattern.id,
            name=pattern.name,
            problem=pattern.problem,
            solution=pattern.solution,
            refs=pattern.refs,
            forward_links=[
                PatternLinkResponse(id=link.id, name=link.name) for link in pattern.forward_links
            ],
            backlinks=[
                PatternLinkResponse(id=link.id, name=link.name) for link in pattern.backlinks
            ]
        )
