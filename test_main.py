# Import dependencies
import os
import pytest
from sqlmodel import SQLModel, Session, create_engine
from main import (
    app,
    get_pattern_by_id,
    get_pattern_by_name,
    find_pattern_by_name,
    get_pattern_by_page_number,
    get_patterns_by_confidence,
    get_patterns_by_tag,
    Patterns,
    PatternLinks,
)

# Setup test database
DATABASE_URL = "sqlite:///test_apl.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# Dependency override
def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[override_get_session] = override_get_session


# Initialize the database for testing
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)
    os.remove("test_apl.db")



@pytest.fixture(scope="function")
def session():
    with Session(engine) as s:
        yield s


def insert_sample_data(session: Session):
    pattern1 = Patterns(
        id=1,
        name="pattern one",
        problem="Problem One",
        solution="Solution One",
        page_number=10,
        confidence=3,
        tag="tag1",
    )
    pattern2 = Patterns(
        id=2,
        name="pattern two",
        problem="Problem Two",
        solution="Solution Two",
        page_number=20,
        confidence=2,
        tag="tag2",
    )
    link = PatternLinks(pattern_id=1, linked_pattern_id=2)
    session.add_all([pattern1, pattern2, link])
    session.commit()


@pytest.fixture(scope="function", autouse=True)
def setup_sample_data(session):
    session.query(PatternLinks).delete()
    session.query(Patterns).delete()
    insert_sample_data(session)


# Now we create the test cases for each function directly
def test_get_pattern_by_id(session):
    result = get_pattern_by_id(pattern_id=1, session=session, depth=1)
    assert result.id == 1
    assert result.name == "Pattern One"


def test_get_pattern_by_name(session):
    result = get_pattern_by_name(pattern_name="pattern one", session=session, depth=1)
    assert result.id == 1


def test_find_pattern_by_name(session):
    results = find_pattern_by_name(name="one", session=session)
    assert any("pattern one" in pattern.name for pattern in results)


def test_get_pattern_by_page_number(session):
    result = get_pattern_by_page_number(page_number=15, session=session)
    assert result.page_number <= 15


def test_get_patterns_by_confidence(session):
    results = get_patterns_by_confidence(confidence=3, session=session)
    assert all(pattern.confidence == 3 for pattern in results)


def test_get_patterns_by_tag(session):
    results = get_patterns_by_tag(tag="tag1", session=session)
    assert any("tag1" in pattern.tag for pattern in results)
