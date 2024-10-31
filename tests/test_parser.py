import pytest
import re
from apl_api.parser import (
    strip_angle_bracket,
    split_content,
    extract_name_and_id,
    extract_links,
    extract_citation_details,
    extract_page_referece,
    map_confidence_and_tag,
    create_database,
)


def test_strip_angle_bracket():
    text = ">This is a line.\n>Another line."
    expected = "This is a line.\nAnother line."
    assert strip_angle_bracket(text) == expected


def test_split_content():
    text = "## Problem\nProblem text\n## Solution\nSolution text\n## Related Patterns\nRelated text\n---\nReference text"
    expected = ("Problem text", "Solution text", "Related text", "Reference text")
    assert split_content(text) == expected


def test_extract_name_and_id():
    filename = "Pattern Name (42).md"
    expected = ("pattern name", 42)
    assert extract_name_and_id(filename) == expected


def test_extract_links():
    text = "This pattern links to [[Pattern One (1)]], [[Pattern Two (2)]]."
    expected = [("Pattern One", "1"), ("Pattern Two", "2")]
    assert extract_links(text) == expected


def test_extract_citation_details():
    references_text = "[!cite]- Alexander, Christopher. _A Pattern Language: Towns, Buildings, Construction_. Oxford University Press, 1977, p. 163\n#high-confidence\n#APL/Town-Patterns/Local-Centers"
    expected = ("163", 3, "apl/town-patterns/local-centers")
    assert extract_citation_details(references_text) == expected


def test_extract_page_reference():
    text = "[!cite]- Alexander, Christopher. _A Pattern Language: Towns, Buildings, Construction_. Oxford University Press, 1977, p. 42."
    assert extract_page_referece(text) == "42"


def test_map_confidence_and_tag():
    text = "#high-confidence #APL/Town-Patterns/Local-Centers"
    expected = (3, "APL/Town-Patterns/Local-Centers")
    assert map_confidence_and_tag(text) == expected


def test_create_database(mocker):
    # Mock sqlite3 connection and cursor
    mock_conn = mocker.patch("sqlite3.connect")
    mock_cur = mock_conn.return_value.cursor.return_value

    create_database()

    mock_cur.execute.assert_any_call(
        """
    CREATE TABLE IF NOT EXISTS Patterns (
        id INTEGER PRIMARY KEY, 
        name TEXT NOT NULL,
        problem TEXT NOT NULL,
        solution TEXT NOT NULL,
        page_number INTEGER,
        confidence INTEGER,
        tag TEXT
    );
    """
    )
    mock_cur.execute.assert_any_call(
        """
    CREATE TABLE IF NOT EXISTS PatternLinks (
        pattern_id INTEGER,
        linked_pattern_id INTEGER,
        PRIMARY KEY (pattern_id, linked_pattern_id),
        FOREIGN KEY (pattern_id) REFERENCES Patterns(id) ON DELETE CASCADE,
        FOREIGN KEY (linked_pattern_id) REFERENCES Patterns(id) ON DELETE CASCADE
    );
    """
    )
