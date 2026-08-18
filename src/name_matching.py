"""
Shared player-name normalization for joining across this project's data
sources, which don't all spell names identically -- diacritics present on
one side and stripped on the other (Nikola Jokic vs. "Nikola Jokić"),
periods in initials ("A.J. Lawson" vs. "AJ Lawson"), curly vs. straight
apostrophes, and "Jr."/"Sr."/"II"/"III"/"IV" suffixes present on only one
side.

normalize_name() is NOT a fuzzy matcher -- it's exact string equality after
stripping the cosmetic differences above, so two callers using it on the
same two names will always agree. It does NOT catch true nickname/legal-
name mismatches (e.g. "Bones Hyland" for "Nah'Shon Hyland", "Bub
Carrington" for "Carlton Carrington") -- those need a small hand-verified
alias table alongside it, kept local to whichever module is doing the join
(see build_multi_year_stats.py's NAME_ALIASES for an example), since the
right alias set depends on which two specific sources are being joined.
"""

import re
import unicodedata

SUFFIX_TOKENS = {"jr", "sr", "ii", "iii", "iv", "v"}


def normalize_name(name: str) -> str:
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    n = n.replace(".", "").replace("'", "")
    n = re.sub(r"[^a-zA-Z ]", " ", n).lower()
    tokens = [t for t in n.split() if t not in SUFFIX_TOKENS]
    return " ".join(tokens)
