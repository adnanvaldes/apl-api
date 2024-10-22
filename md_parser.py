import os
import re
import sys

PATTERNS_DIR = "/home/einhard/Desktop/apl-md/Patterns/"

# Matches wiki-link style patterns eg. [[Independent Regions (1)]]
RELATED_RE = re.compile(r"\[\[(.*?) \((\d+)\)\]\]")

related_links = {}
patterns_data = []

def strip_angle_bracket(text):
    """
    Remove ">" from start of line in block quotes and citations
    """
    stripped_lines = [line.lstrip(">").strip() for line in text.splitlines()]
    print("\n".join(stripped_lines).strip())
    return "\n".join(stripped_lines).strip()

def split_content(text):
    """
    Split content into sections by markdown headers and references (marked by "---")
    """

    try:
        # Split the text first so that references don't match in the "related" section later
        body, references = text.split("---")
    except IndexError:
        print("Could not find references section (looked for '---')")
        sys.exit(IndexError)

    sections = ["Problem", "Solution", "Related Patterns"]
    # Match the header pattern eg ('## Problem')
    results = [re.search(rf'## {section}\n(.*?)(##|$)', body, re.DOTALL) for section in sections]

    try:
        problem, solution, related = [match.group(1).strip() if match else "" for match in results]
    except AttributeError:
        raise ValueError("Missing one or more sections")


    return problem, solution, related, references.strip()

def extract_name_and_id(filename):
    # Extract pattern name and number from filename
    match = re.match(r'(.*?) \((\d+)\)\.md', filename)
    if match:
        pattern_name = match.group(1).strip()
        pattern_id = int(match.group(2))

    return pattern_name, pattern_id

def main():
    for filename in os.listdir(PATTERNS_DIR):
        if filename.endswith(".md"):
            extract_name_and_id(filename)
