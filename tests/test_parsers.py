import pytest
from app.document_processing.sanitizer import text_sanitizer
from app.document_processing.section_segmenter import section_segmenter


def test_text_sanitizer_ligatures():
    dirty = "Built an eﬃcient and afﬁliated deep learning model \u2013 improving throughput."
    cleaned = text_sanitizer.clean(dirty)
    assert "efficient" in cleaned
    assert "affiliated" in cleaned
    assert "-" in cleaned


def test_text_sanitizer_excessive_whitespace():
    dirty = "Senior   Machine    Learning   Engineer\n\n\n\nSan Francisco"
    cleaned = text_sanitizer.clean(dirty)
    assert "Senior Machine Learning Engineer" in cleaned
    assert "\n\n" in cleaned


def test_section_segmenter():
    sample_resume = """John Doe
john.doe@example.com | 555-0199

PROFESSIONAL SUMMARY
Experienced software engineer.

WORK EXPERIENCE
Senior Engineer at Tech Corp (2020 - Present)
* Built microservices with FastAPI.

EDUCATION
Stanford University
B.S. in Computer Science

TECHNICAL SKILLS
Python, Docker, SQL
"""
    sections = section_segmenter.segment(sample_resume)
    assert "header" in sections
    assert "summary" in sections
    assert "experience" in sections
    assert "education" in sections
    assert "skills" in sections
    assert "FastAPI" in sections["experience"]
    assert "Stanford" in sections["education"]
