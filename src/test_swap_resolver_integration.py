"""
End-to-end validation of the swap resolver against a real 30-team league
(real names + real conferences, but PLACEHOLDER spread ratings -- this is
just to exercise the mechanics correctly, not to produce meaningful grades;
real ratings come later from the market win-total spreadsheet).
"""

import random

from standings_sim import Team
from conferences import TEAM_CONFERENCE
from draft_picks_data import TEAM_FUTURE_PICKS
from pick_resolver import classify_team_picks, build_pick_assets
from pick_grading import grade_pick_portfolio

# Arbitrary spread of ratings across all 30 real teams, deterministic order,
# just so the season/lottery machinery has something realistic-shaped to
# simulate. NOT a real strength estimate.
rng = random.Random(42)
team_names = sorted(TEAM_FUTURE_PICKS.keys())
ratings = list(range(1360, 1360 + 12 * 30, 12))  # spread ~1360-1708
rng.shuffle(ratings)
teams = [Team(name=name, rating=rating, conference=TEAM_CONFERENCE[name])
         for name, rating in zip(team_names, ratings)]

print(f"Built {len(teams)} teams, "
      f"{sum(1 for t in teams if t.conference == 'East')} East / "
      f"{sum(1 for t in teams if t.conference == 'West')} West")

TRIALS = 2000

print("\n=== Atlanta Hawks: full pick portfolio, swaps resolved via real joint simulation ===")
assets, unresolved = build_pick_assets("Atlanta Hawks", teams_for_simulation=teams,
                                        trials=TRIALS, seed=7)
print(f"Resolved to gradable assets: {len(assets)}")
for a in assets:
    g = a.grade()
    print(f"  {g['label']:<65} grade={g['grade']:>4.1f}  ({g['grade_label']})")
print(f"\nStill unresolved: {len(unresolved)}")
for year, text, reason in unresolved:
    print(f"  {year}: {text}  [{reason}]")

print("\n=== Coverage across all 30 teams, WITH a real simulation league ===")
totals = {"assets": 0, "unresolved": 0}
reason_counts = {}
for team in team_names:
    a, u = build_pick_assets(team, teams_for_simulation=teams, trials=TRIALS, seed=7)
    totals["assets"] += len(a)
    totals["unresolved"] += len(u)
    for _, _, reason in u:
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

print(f"Total gradable pick assets across the league: {totals['assets']}")
print(f"Total still unresolved: {totals['unresolved']}")
print("\nUnresolved breakdown:")
for reason, count in sorted(reason_counts.items(), key=lambda kv: -kv[1]):
    print(f"  {count:>3}  {reason}")

# Sanity check: a swap's resolved distribution should never contain a pick
# number below 1 or above 60, and probabilities should sum to ~1.
print("\n=== Sanity check on every resolved swap distribution ===")
from swap_resolver import parse_swap_fragment, resolve_swap_distribution
from draft_pipeline_321 import joint_pick_number_trials
from team_codes import TEAM_ABBREV_TO_NAME

bad = 0
checked = 0
for team in team_names:
    _, swaps, _, _, _ = classify_team_picks(team)
    for swap in swaps:
        names = [TEAM_ABBREV_TO_NAME[c] for c in swap.teams]
        joint = joint_pick_number_trials(teams, names, trials=300, seed=3)
        # Round-aware: joint[name] is now {"1st": [...], "2nd": [...]} -- slice
        # to the round this swap actually concerns, same as pick_resolver.py does.
        joint_by_code = {c: joint[TEAM_ABBREV_TO_NAME[c]][swap.round_str] for c in swap.teams}
        dist = resolve_swap_distribution(swap, joint_by_code)
        checked += 1
        total_prob = sum(dist.values())
        round_lo, round_hi = (1, 30) if swap.round_str == "1st" else (31, 60)
        if not (0.99 <= total_prob <= 1.01) or min(dist) < round_lo or max(dist) > round_hi:
            bad += 1
            print(f"  BAD: {team} {swap.raw_text} -> {dist}")
print(f"Checked {checked} swap fragments across the league, {bad} failed sanity check")

# Same sanity check for the new same-year cross-pick conditionals: the
# CONDITIONED distribution (i.e. among only the trials where the condition
# held) should sum to ~1, land in the target round's range, and
# convey_probability should be a genuine probability in [0, 1].
print("\n=== Sanity check on every resolved cross-pick conditional ===")
from swap_resolver import resolve_conditional_pick

bad_cond = 0
checked_cond = 0
for team in team_names:
    _, _, conditionals, _, _ = classify_team_picks(team)
    for cond in conditionals:
        names = [TEAM_ABBREV_TO_NAME[cond.team_code], TEAM_ABBREV_TO_NAME[cond.cond_team_code]]
        joint = joint_pick_number_trials(teams, names, trials=300, seed=3)
        joint_by_code = {
            cond.team_code: joint[TEAM_ABBREV_TO_NAME[cond.team_code]],
            cond.cond_team_code: joint[TEAM_ABBREV_TO_NAME[cond.cond_team_code]],
        }
        dist, convey_probability = resolve_conditional_pick(cond, joint_by_code)
        checked_cond += 1
        round_lo, round_hi = (1, 30) if cond.round_str == "1st" else (31, 60)
        total_prob = sum(dist.values()) if dist else 1.0  # 0-convey trials -> empty dist is fine
        ok_convey = 0.0 <= convey_probability <= 1.0
        ok_dist = (not dist) or (0.99 <= total_prob <= 1.01 and round_lo <= min(dist) and max(dist) <= round_hi)
        if not (ok_convey and ok_dist):
            bad_cond += 1
            print(f"  BAD: {team} {cond.raw_text} -> convey={convey_probability}, dist={dist}")
print(f"Checked {checked_cond} cross-pick conditionals across the league, {bad_cond} failed sanity check")

# Same sanity check for the new nested swaps.
print("\n=== Sanity check on every resolved nested swap ===")
from swap_resolver import resolve_nested_swap_distribution, collect_nested_swap_teams

bad_nested = 0
checked_nested = 0
for team in team_names:
    _, _, _, nested_swaps, _ = classify_team_picks(team)
    for nested in nested_swaps:
        codes = sorted(collect_nested_swap_teams(nested.root))
        names = [TEAM_ABBREV_TO_NAME[c] for c in codes]
        joint = joint_pick_number_trials(teams, names, trials=300, seed=3)
        joint_by_code = {c: joint[TEAM_ABBREV_TO_NAME[c]] for c in codes}
        dist = resolve_nested_swap_distribution(nested, joint_by_code)
        checked_nested += 1
        total_prob = sum(dist.values())
        round_lo, round_hi = (1, 30) if nested.round_str == "1st" else (31, 60)
        if not (0.99 <= total_prob <= 1.01) or min(dist) < round_lo or max(dist) > round_hi:
            bad_nested += 1
            print(f"  BAD: {team} {nested.raw_text} -> {dist}")
print(f"Checked {checked_nested} nested swap fragments across the league, {bad_nested} failed sanity check")
