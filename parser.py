import os
import re
import sqlite3
import sys
import subprocess

PATTERNS_DIR = "apl-md/Patterns"
DATABASE = "apl.db"

# Matches wiki-link style patterns e.g., [[Independent Regions (1)]]
RELATED_PATTERN_RE = re.compile(r"\[\[(.*?) \((\d+)\)\]\]")

links = {}
backlinks = {}
patterns_data = {}


def strip_angle_bracket(text):
    """
    Remove ">" from the start of lines in block quotes and citations
    """
    stripped_lines = [line.lstrip(">").strip() for line in text.splitlines()]
    return "\n".join(stripped_lines).strip()


def split_content(text):
    """
    Split content into sections by markdown headers and references (marked by "---")
    """
    try:
        # Split the text first so that references don't match in the "related" section later
        body, references = text.split("---\n")
    except IndexError:
        print("Could not find references section (looked for '---')")
        sys.exit(IndexError)

    sections = ["Problem", "Solution", "Related Patterns"]
    # Match the header pattern e.g., ('## Problem')
    results = [
        re.search(rf"## {section}\n(.*?)(##|$)", body, re.DOTALL)
        for section in sections
    ]

    try:
        problem, solution, related = [
            match.group(1).strip() if match else "" for match in results
        ]
    except AttributeError:
        raise ValueError("Missing one or more sections")

    return problem, solution, related, references.strip()


def extract_name_and_id(filename):
    # Extract pattern name and number from filename
    match = re.match(r"(.*?) \((\d+)\)\.md", filename)
    if match:
        pattern_name = match.group(1).strip()
        pattern_id = int(match.group(2))

    return pattern_name.lower(), pattern_id


def extract_links(text):
    """
    Extracts all forward links from Related Patterns section of the text

    Returns a list of tuples, where the first item in the tuple is the pattern name, second is id
    """
    return re.findall(RELATED_PATTERN_RE, text)


def extract_citation_details(references_text):
    """
    Extracts page_number, confidence, and tag from references section
    """
    page_number = extract_page_referece(references_text)
    confidence, tag = map_confidence_and_tag(references_text)
    return page_number, confidence, tag.lower()


def extract_page_referece(text):
    # Matches citation format and uses capture group 1 to match a digit up to 10 times (\d{1,10}) to find page number
    page_ref_re = r"\[!cite\]- Alexander, Christopher. _A Pattern Language: Towns, Buildings, Construction_. Oxford University Press, 1977, p. (\d{1,10})"
    return re.match(page_ref_re, text).group(1)


def map_confidence_and_tag(text):
    tags_re = r"(#[\w\/-]+)"
    match = re.findall(tags_re, text)

    # Convert confidence to integer values (low = 1, medium = 2, high = 3)
    confidence_map = {
        "#low-confidence": 1,
        "#medium-confidence": 2,
        "#high-confidence": 3,
    }

    # Remove "#" from beginning of string
    return confidence_map[match[0]], match[1][1:]


def create_database():
    """
    Creates a SQLite database with the required schema
    """
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Create Patterns table
    cur.execute(
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

    # Create PatternLinks table
    cur.execute(
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

    conn.commit()
    conn.close()


def load_data_to_database():
    """
    Loads the patterns and links data into the SQLite database
    """
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Insert patterns data
    for pattern_id, (
        id,
        name,
        problem,
        solution,
        related,
        page_number,
        confidence,
        tag,
    ) in patterns_data.items():
        cur.execute(
            """
        INSERT INTO Patterns (id, name, problem, solution, page_number, confidence, tag)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (id, name, problem, solution, page_number, confidence, tag),
        )

    # Insert forward and backward links into PatternLinks table
    for pattern_id, linked_patterns in links.items():
        for linked_pattern in linked_patterns:
            cur.execute(
                """
            INSERT OR IGNORE INTO PatternLinks (pattern_id, linked_pattern_id)
            VALUES (?, ?)
            """,
                (pattern_id, linked_pattern),
            )

    conn.commit()
    conn.close()


def update_subtree():
    try:
        subprocess.run(
            [
                "git",
                "subtree",
                "pull",
                "--prefix",
                "apl-md",
                "https://github.com/zenodotus280/apl-md.git",
                "master",
                "--squash",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to update subtree: {e}")


def load_data():
    create_database()
    update_subtree()

    for filename in os.listdir(PATTERNS_DIR):
        if filename.endswith(".md"):
            pattern_name, pattern_id = extract_name_and_id(filename)

            with open(os.path.join(PATTERNS_DIR, filename), "r") as file:
                content = file.read()
                content = strip_angle_bracket(content)
                problem, solution, related, references = split_content(content)

                # Extract page_number, confidence, and tag from references section
                page_number, confidence, tag = extract_citation_details(references)

                patterns_data[pattern_id] = (
                    pattern_id,
                    pattern_name,
                    problem,
                    solution,
                    related,
                    page_number,
                    confidence,
                    tag,
                )

                # Extract links from the 'related' section, not 'references'
                links[pattern_id] = [int(link[1]) for link in extract_links(related)]

    # Process backlinks
    for pattern_id in links:
        backlinks[pattern_id] = []

    for pattern_id, linked_patterns in links.items():
        for linked_pattern in linked_patterns:
            if linked_pattern in backlinks:
                backlinks[linked_pattern].append(pattern_id)
            else:
                backlinks[linked_pattern] = [pattern_id]

    load_data_to_database()


if __name__ == "__main__":
    load_data()
