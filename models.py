from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

# class RelatedPattern(SQLModel, table=True):
#     """Join table for many-to-many relationships between patterns."""
#     pattern_id: Optional[int] = Field(default=None, foreign_key="pattern.id", primary_key=True)
#     related_pattern_id: Optional[int] = Field(default=None, foreign_key="pattern.id", primary_key=True)

class Backlink(SQLModel, table=True):
    """Join table for backlinks (reverse relationships between patterns)."""
    pattern_id: Optional[int] = Field(default=None, foreign_key="pattern.id", primary_key=True)
    backlink_pattern_id: Optional[int] = Field(default=None, foreign_key="pattern.id", primary_key=True)

class Patterns(SQLModel, table=True):
    """Represents a pattern."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    problem: Optional[str] = None
    solution: Optional[str] = None
    related_text: Optional[str] = None

    # # Forward and backward relationships
    # related_patterns: List["Pattern"] = Relationship(
    #     back_populates="backlinks", link_model=RelatedPattern
    # )
    # backlinks: List["Pattern"] = Relationship(
    #     back_populates="related_patterns", link_model=Backlink
    # )
