#!/usr/bin/env python3
"""Citation Helper - Semantic Scholar MCP Citation Bug Workaround

Semantic Scholar MCP의 get_citation API 버그를 우회하여
논문 메타데이터에서 인용 형식을 생성합니다.

버그 원인: _handle_get_citation에서 "fields": "citationStyles, abstract" 요청
수정: abstract 필드 제거 필요

사용법:
    python citation-helper.py <paper_id> [--format bibtex|apa|mla|chicago]

예시:
    python citation-helper.py ARXIV:1706.03762 --format bibtex
"""

import argparse
import json
import re
import sys
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper"


def fetch_paper(paper_id: str) -> Optional[dict]:
    """Semantic Scholar에서 논문 메타데이터 가져오기"""
    fields = "paperId,title,authors,year,venue,publicationDate,externalIds"
    url = f"{SEMANTIC_SCHOLAR_API}/{paper_id}?fields={fields}"

    try:
        req = Request(url, headers={"User-Agent": "citation-helper/1.0"})
        with urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        print(f"API Error: {e.code} - {e.reason}", file=sys.stderr)
        return None
    except URLError as e:
        print(f"Connection Error: {e.reason}", file=sys.stderr)
        return None


def format_authors_bibtex(authors: list) -> str:
    """BibTeX 형식으로 저자 포맷팅"""
    if not authors:
        return ""
    names = [a.get("name", "") for a in authors]
    return " and ".join(names)


def format_authors_apa(authors: list) -> str:
    """APA 형식으로 저자 포맷팅"""
    if not authors:
        return ""

    formatted = []
    for i, author in enumerate(authors):
        name = author.get("name", "")
        parts = name.split()
        if len(parts) >= 2:
            # Last, F. M. format
            last = parts[-1]
            initials = ". ".join([p[0] for p in parts[:-1]]) + "."
            formatted.append(f"{last}, {initials}")
        else:
            formatted.append(name)

    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} & {formatted[1]}"
    else:
        return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"


def format_authors_mla(authors: list) -> str:
    """MLA 형식으로 저자 포맷팅"""
    if not authors:
        return ""

    names = [a.get("name", "") for a in authors]

    if len(names) == 1:
        parts = names[0].split()
        if len(parts) >= 2:
            return f"{parts[-1]}, {' '.join(parts[:-1])}"
        return names[0]
    elif len(names) == 2:
        first = names[0].split()
        if len(first) >= 2:
            first_formatted = f"{first[-1]}, {' '.join(first[:-1])}"
        else:
            first_formatted = names[0]
        return f"{first_formatted}, and {names[1]}"
    else:
        first = names[0].split()
        if len(first) >= 2:
            first_formatted = f"{first[-1]}, {' '.join(first[:-1])}"
        else:
            first_formatted = names[0]
        return f"{first_formatted}, et al."


def generate_bibtex_key(paper: dict) -> str:
    """BibTeX 키 생성"""
    first_author = ""
    if paper.get("authors"):
        name = paper["authors"][0].get("name", "")
        parts = name.split()
        if parts:
            first_author = parts[-1].lower()
            first_author = re.sub(r'[^a-z]', '', first_author)

    year = paper.get("year", "")
    title_word = ""
    if paper.get("title"):
        words = paper["title"].split()
        for word in words:
            if len(word) > 3 and word.lower() not in ["the", "and", "for", "with"]:
                title_word = word.lower()
                title_word = re.sub(r'[^a-z]', '', title_word)
                break

    return f"{first_author}{year}{title_word}"


def to_bibtex(paper: dict) -> str:
    """BibTeX 형식 생성"""
    key = generate_bibtex_key(paper)
    authors = format_authors_bibtex(paper.get("authors", []))
    title = paper.get("title", "")
    year = paper.get("year", "")
    venue = paper.get("venue", "")

    # Determine entry type
    venue_lower = venue.lower() if venue else ""
    if any(kw in venue_lower for kw in ["conference", "proceedings", "workshop", "symposium"]):
        entry_type = "inproceedings"
        venue_field = f'  booktitle = {{{venue}}},\n' if venue else ''
    elif any(kw in venue_lower for kw in ["journal", "transactions"]):
        entry_type = "article"
        venue_field = f'  journal = {{{venue}}},\n' if venue else ''
    else:
        entry_type = "misc"
        venue_field = f'  howpublished = {{{venue}}},\n' if venue else ''

    # Add arXiv info if available
    arxiv_id = ""
    if paper.get("externalIds", {}).get("ArXiv"):
        arxiv_id = paper["externalIds"]["ArXiv"]

    arxiv_note = f'  note = {{arXiv:{arxiv_id}}},\n' if arxiv_id else ''

    return f"""@{entry_type}{{{key},
  title = {{{title}}},
  author = {{{authors}}},
  year = {{{year}}},
{venue_field}{arxiv_note}}}"""


def to_apa(paper: dict) -> str:
    """APA 형식 생성"""
    authors = format_authors_apa(paper.get("authors", []))
    year = paper.get("year", "")
    title = paper.get("title", "")
    venue = paper.get("venue", "")

    citation = f"{authors} ({year}). {title}."
    if venue:
        citation += f" {venue}."

    return citation


def to_mla(paper: dict) -> str:
    """MLA 형식 생성"""
    authors = format_authors_mla(paper.get("authors", []))
    title = paper.get("title", "")
    venue = paper.get("venue", "")
    year = paper.get("year", "")

    citation = f'{authors}. "{title}."'
    if venue:
        citation += f" {venue},"
    citation += f" {year}."

    return citation


def to_chicago(paper: dict) -> str:
    """Chicago 형식 생성"""
    authors = format_authors_mla(paper.get("authors", []))  # Similar to MLA
    title = paper.get("title", "")
    venue = paper.get("venue", "")
    year = paper.get("year", "")

    citation = f'{authors}. "{title}."'
    if venue:
        citation += f" {venue}"
    citation += f" ({year})."

    return citation


def generate_citation(paper_id: str, format: str = "bibtex") -> Optional[str]:
    """인용 생성"""
    paper = fetch_paper(paper_id)
    if not paper:
        return None

    formatters = {
        "bibtex": to_bibtex,
        "apa": to_apa,
        "mla": to_mla,
        "chicago": to_chicago,
    }

    formatter = formatters.get(format.lower())
    if not formatter:
        print(f"Unknown format: {format}. Using bibtex.", file=sys.stderr)
        formatter = to_bibtex

    return formatter(paper)


def main():
    parser = argparse.ArgumentParser(
        description="Generate citations from Semantic Scholar paper IDs"
    )
    parser.add_argument("paper_id", help="Paper ID (e.g., ARXIV:1706.03762, DOI:10.xxx)")
    parser.add_argument(
        "--format", "-f",
        choices=["bibtex", "apa", "mla", "chicago"],
        default="bibtex",
        help="Citation format (default: bibtex)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output raw paper metadata as JSON"
    )

    args = parser.parse_args()

    if args.json:
        paper = fetch_paper(args.paper_id)
        if paper:
            print(json.dumps(paper, indent=2, ensure_ascii=False))
        else:
            sys.exit(1)
    else:
        citation = generate_citation(args.paper_id, args.format)
        if citation:
            print(citation)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
