"""
Deterministic HTML scraper for ldsport.com's depth-charts and
future-draft-picks pages.

Site owner (Blake Stern, @ldsportnba) gave explicit permission to pull this
data programmatically (permission obtained 2026-08-23).

This deliberately does NOT route page content through any LLM summarization
step. An earlier refresh attempt using the WebFetch tool (which converts a
page to markdown and summarizes it through a small model) fabricated
notation that wasn't on the page and silently dropped real entries -- see
draft_picks_data.py's docstring for specifics. Both target pages are plain
static HTML (no JS rendering required), so this module parses the raw
markup directly with BeautifulSoup: extraction is exact and reproducible,
not a paraphrase.
"""

from __future__ import annotations

import re
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.ldsport.com"
DEPTH_CHARTS_URL = f"{BASE_URL}/depth-charts.html"
FUTURE_PICKS_URL = f"{BASE_URL}/future-draft-picks.html"

HEADERS = {
    "User-Agent": "nba-draft-pick-grader/1.0 (personal project; contact: elimizh@gmail.com)"
}

POSITIONS = ("PG", "SG", "SF", "PF", "C")

_ZERO_WIDTH_SPACE = "​"


def _clean_text(text: str) -> str:
    return text.replace(_ZERO_WIDTH_SPACE, "").replace("\xa0", " ").strip()


def _get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def fetch_depth_charts() -> Dict[str, Dict[str, List[str]]]:
    """Scrapes https://www.ldsport.com/depth-charts.html.

    Returns {team_name: {position: [player_name, ...]}} in the same shape
    and player-name-annotation style as real_rosters_202627.TEAM_DEPTH_CHARTS.
    """
    soup = _get_soup(DEPTH_CHARTS_URL)
    charts: Dict[str, Dict[str, List[str]]] = {}

    for h2 in soup.select("h2.wsite-content-title"):
        team = _clean_text(h2.get_text(strip=True))
        if not team:
            continue
        para = h2.find_next_sibling("div", class_="paragraph")
        if para is None:
            continue

        positions: Dict[str, List[str]] = {}
        for line in re.split(r"<br\s*/?>", str(para)):
            text = _clean_text(BeautifulSoup(line, "html.parser").get_text())
            if not text:
                continue
            m = re.match(r"^(PG|SG|SF|PF|C)\s+(.*)$", text)
            if not m:
                continue
            pos, rest = m.group(1), m.group(2)
            names = [n.strip() for n in rest.split(",") if n.strip()]
            if names:
                positions[pos] = names

        if positions:
            charts[team] = positions

    return charts


def fetch_future_picks() -> Dict[str, Dict[int, str]]:
    """Scrapes https://www.ldsport.com/future-draft-picks.html.

    Returns {team_name: {year: description}} in the same shape and text
    style as draft_picks_data.TEAM_FUTURE_PICKS (trailing "*" footnote
    markers stripped, matching that module's existing convention).
    """
    soup = _get_soup(FUTURE_PICKS_URL)
    picks: Dict[str, Dict[int, str]] = {}

    for h2 in soup.select("h2.wsite-content-title"):
        header_text = _clean_text(h2.get_text(" ", strip=True))
        team = _clean_text(header_text.split("Tradable")[0])
        if not team:
            continue
        para = h2.find_next_sibling("div", class_="paragraph")
        if para is None:
            continue

        years: Dict[int, str] = {}
        for line in re.split(r"<br\s*/?>", str(para)):
            text = _clean_text(BeautifulSoup(line, "html.parser").get_text())
            if not text:
                continue
            m = re.match(r"^(\d{4})\s*(?:\([^)]*\))?:\s*(.*)$", text)
            if not m:
                continue
            year = int(m.group(1))
            desc = re.sub(r"\*+", "", m.group(2).strip()).strip()
            years[year] = desc if desc else "(NO PICKS)"

        if years:
            picks[team] = years

    return picks


if __name__ == "__main__":
    charts = fetch_depth_charts()
    picks = fetch_future_picks()
    print(f"Depth charts: {len(charts)} teams")
    print(f"Future picks: {len(picks)} teams")
