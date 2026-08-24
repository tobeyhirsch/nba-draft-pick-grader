"""
Refreshes real_rosters_202627.py and draft_picks_data.py from ldsport.com,
via ldsport_scraper's deterministic HTML parser (not an LLM summarizer).

Usage: python -m src.refresh_ldsport_data [--dry-run]

Safety model: fetched data is sanity-checked (enough teams, no empty teams)
before anything is written -- a bad/partial fetch aborts with no file
changes rather than corrupting the trusted data. Each data file's dict
literal is regenerated from the fresh scrape; everything else in the file
(docstring, helper functions, hand-written "# NOTE" comments attached to a
team's block) is preserved as-is. Every run appends a summary of what
changed to ldsport_refresh_log.txt, so daily unattended runs stay auditable
even though nothing blocks on human approval.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import ldsport_scraper
from src.draft_picks_data import TEAM_FUTURE_PICKS as OLD_PICKS
from src.real_rosters_202627 import TEAM_DEPTH_CHARTS as OLD_ROSTERS

SRC_DIR = Path(__file__).resolve().parent
ROSTERS_PATH = SRC_DIR / "real_rosters_202627.py"
PICKS_PATH = SRC_DIR / "draft_picks_data.py"
LOG_PATH = SRC_DIR / "ldsport_refresh_log.txt"

MIN_TEAMS = 28
POSITIONS = ("PG", "SG", "SF", "PF", "C")
PICK_YEARS = range(2027, 2034)


def _pystr(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _sanity_check_rosters(charts: Dict[str, Dict[str, List[str]]]) -> List[str]:
    problems = []
    if len(charts) < MIN_TEAMS:
        problems.append(f"only {len(charts)} teams parsed (expected >= {MIN_TEAMS})")
    for team, positions in charts.items():
        missing = [p for p in POSITIONS if not positions.get(p)]
        if missing:
            problems.append(f"{team}: missing/empty position(s) {missing}")
    return problems


def _sanity_check_picks(picks: Dict[str, Dict[int, str]]) -> List[str]:
    problems = []
    if len(picks) < MIN_TEAMS:
        problems.append(f"only {len(picks)} teams parsed (expected >= {MIN_TEAMS})")
    for team, years in picks.items():
        missing = [y for y in PICK_YEARS if y not in years]
        if missing:
            problems.append(f"{team}: missing year(s) {missing}")
    return problems


def _extract_team_comments(old_source: str, dict_var_name: str) -> Dict[str, List[str]]:
    """Pulls forward hand-written '# NOTE' comment lines that appear as the
    first line(s) inside a team's block, keyed by team name, so regenerating
    the dict literal doesn't silently delete curator annotations."""
    block = re.search(
        rf"^{dict_var_name}[^=]*=\s*\{{\n(.*?)^\}}", old_source, re.S | re.M
    )
    if not block:
        return {}
    comments: Dict[str, List[str]] = {}
    current_team = None
    collecting = False
    for line in block.group(1).splitlines():
        m = re.match(r'^    "([^"]+)":\s*\{$', line)
        if m:
            current_team = m.group(1)
            collecting = True
            continue
        if collecting and current_team is not None:
            stripped = line.strip()
            if stripped.startswith("#"):
                comments.setdefault(current_team, []).append(line)
                continue
            collecting = False
    return comments


def _diff_rosters(old: dict, new: dict) -> List[str]:
    changes = []
    for team in sorted(set(old) | set(new)):
        if team not in old:
            changes.append(f"+ {team} (new team in source)")
            continue
        if team not in new:
            changes.append(f"- {team} (missing from source, kept old data)")
            continue
        if old[team] != new[team]:
            for pos in POSITIONS:
                if old[team].get(pos) != new[team].get(pos):
                    changes.append(
                        f"~ {team} {pos}: {old[team].get(pos)} -> {new[team].get(pos)}"
                    )
    return changes


def _diff_picks(old: dict, new: dict) -> List[str]:
    changes = []
    for team in sorted(set(old) | set(new)):
        if team not in old:
            changes.append(f"+ {team} (new team in source)")
            continue
        if team not in new:
            changes.append(f"- {team} (missing from source, kept old data)")
            continue
        if old[team] != new[team]:
            for year in PICK_YEARS:
                if old[team].get(year) != new[team].get(year):
                    changes.append(
                        f"~ {team} {year}: {old[team].get(year)!r} -> {new[team].get(year)!r}"
                    )
    return changes


def _render_rosters_block(charts: Dict[str, Dict[str, List[str]]], comments: Dict[str, List[str]]) -> str:
    lines = ["TEAM_DEPTH_CHARTS: Dict[str, Dict[str, List[str]]] = {"]
    for team in sorted(charts):
        lines.append(f'    {_pystr(team)}: {{')
        for c in comments.get(team, []):
            lines.append(c)
        for pos in POSITIONS:
            names = charts[team].get(pos, [])
            names_str = ", ".join(_pystr(n) for n in names)
            lines.append(f'        {_pystr(pos)}: [{names_str}],')
        lines.append("    },")
    lines.append("}")
    return "\n".join(lines)


def _render_picks_block(picks: Dict[str, Dict[int, str]], comments: Dict[str, List[str]]) -> str:
    lines = ["TEAM_FUTURE_PICKS: Dict[str, Dict[int, str]] = {"]
    for team in sorted(picks):
        lines.append(f'    {_pystr(team)}: {{')
        for c in comments.get(team, []):
            lines.append(c)
        for year in PICK_YEARS:
            desc = picks[team].get(year, "(NO PICKS)")
            lines.append(f"        {year}: {_pystr(desc)},")
        lines.append("    },")
    lines.append("}")
    return "\n".join(lines)


def _replace_dict_block(source: str, dict_var_name: str, new_block: str) -> str:
    pattern = re.compile(
        rf"^{dict_var_name}[^=]*=\s*\{{\n.*?^\}}", re.S | re.M
    )
    new_source, n = pattern.subn(new_block, source, count=1)
    if n != 1:
        raise RuntimeError(f"Could not locate {dict_var_name} dict block to replace")
    return new_source


def _update_last_synced(source: str, today: str) -> str:
    return re.sub(
        r"Last synced: \d{4}-\d{2}-\d{2}",
        f"Last synced: {today}",
        source,
        count=1,
    )


def run(dry_run: bool = False) -> None:
    today = date.today().isoformat()
    log_lines = [f"=== {today} ==="]

    try:
        new_rosters = ldsport_scraper.fetch_depth_charts()
        new_picks = ldsport_scraper.fetch_future_picks()
    except Exception as e:
        msg = f"FETCH FAILED, no files touched: {e}"
        print(msg)
        log_lines.append(msg)
        _append_log(log_lines)
        sys.exit(1)

    roster_problems = _sanity_check_rosters(new_rosters)
    pick_problems = _sanity_check_picks(new_picks)
    if roster_problems or pick_problems:
        msg = "SANITY CHECK FAILED, no files touched:\n" + "\n".join(
            roster_problems + pick_problems
        )
        print(msg)
        log_lines.append(msg)
        _append_log(log_lines)
        sys.exit(1)

    roster_changes = _diff_rosters(OLD_ROSTERS, new_rosters)
    pick_changes = _diff_picks(OLD_PICKS, new_picks)

    print(f"Rosters: {len(roster_changes)} change(s)")
    for c in roster_changes:
        print(f"  {c}")
    print(f"Picks: {len(pick_changes)} change(s)")
    for c in pick_changes:
        print(f"  {c}")

    log_lines.append(f"rosters: {len(roster_changes)} change(s)")
    log_lines.extend(f"  {c}" for c in roster_changes)
    log_lines.append(f"picks: {len(pick_changes)} change(s)")
    log_lines.extend(f"  {c}" for c in pick_changes)

    if dry_run:
        print("\n--dry-run: no files written.")
        _append_log(log_lines + ["(dry run, no files written)"])
        return

    roster_source = ROSTERS_PATH.read_text()
    team_comments = _extract_team_comments(roster_source, "TEAM_DEPTH_CHARTS")
    new_roster_block = _render_rosters_block(new_rosters, team_comments)
    roster_source = _replace_dict_block(roster_source, "TEAM_DEPTH_CHARTS", new_roster_block)
    roster_source = _update_last_synced(roster_source, today)
    ROSTERS_PATH.write_text(roster_source)

    picks_source = PICKS_PATH.read_text()
    pick_comments = _extract_team_comments(picks_source, "TEAM_FUTURE_PICKS")
    new_picks_block = _render_picks_block(new_picks, pick_comments)
    picks_source = _replace_dict_block(picks_source, "TEAM_FUTURE_PICKS", new_picks_block)
    picks_source = _update_last_synced(picks_source, today)
    PICKS_PATH.write_text(picks_source)

    print(f"\nWrote {ROSTERS_PATH.name} and {PICKS_PATH.name}.")
    _append_log(log_lines)


def _append_log(lines: List[str]) -> None:
    with open(LOG_PATH, "a") as f:
        f.write("\n".join(lines) + "\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
