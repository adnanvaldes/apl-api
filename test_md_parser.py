import pytest
from md_parser import strip_angle_bracket, split_content, extract_name_and_id

SAMPLE = """### Problem
>The land

### Solution
>Preserve  

### Related Patterns
... this [[City Country Fingers (3)]]

---

> [!cite]- Alexander
> #medium-confidence 
> 
> #APL/Towns/Regional-Policies """

def test_strip_angle_bracket():
    SAMPLE = """### Problem
>The land

### Solution
>Preserve  

### Related Patterns
... this [[City Country Fingers (3)]]

---

> [!cite]- Alexander
> #medium-confidence 
> 
> #APL/Towns/Regional-Policies """
    assert strip_angle_bracket(SAMPLE) == """### Problem
The land

### Solution
Preserve

### Related Patterns
... this [[City Country Fingers (3)]]

---

[!cite]- Alexander
#medium-confidence

#APL/Towns/Regional-Policies"""

def test_split_content():
    expected_problem = ">The land"
    expected_solution = ">Preserve"
    expected_related = '... this [[City Country Fingers (3)]]'
    expected_references = '> [!cite]- Alexander\n> #medium-confidence \n> \n> #APL/Towns/Regional-Policies'

    problem, solution, related, references = split_content(SAMPLE)
    assert problem == expected_problem
    assert solution == expected_solution
    assert related == expected_related
    assert references == expected_references

def test_extract_name_and_id():
    name, id = extract_name_and_id("Agricultural Valleys (4).md")
    assert name == "Agricultural Valleys"
    assert id == 4