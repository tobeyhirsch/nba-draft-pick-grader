"""
Locates data files (the .xlsx/.csv inputs) needed at runtime, without
assuming a fixed relationship between where the .py files live and where
the data/ folder is -- different setups put them differently (data/ next
to the scripts, data/ as a sibling of a src/ folder the scripts live in,
data/ under wherever you happen to run python from). Checks the common
layouts and raises one clear, actionable error listing every path it tried
if none of them exist, instead of a bare FileNotFoundError pointing at
just the one guess that happened to be wrong.
"""

import os


def find_data_file(filename: str, start_dir: str) -> str:
    """
    filename: e.g. "market_win_totals.xlsx".
    start_dir: the directory of the .py file doing the lookup (pass
        os.path.dirname(os.path.abspath(__file__)) from the caller).
    """
    candidates = [
        os.path.join(start_dir, "data", filename),        # data/ next to this file
        os.path.join(start_dir, "..", "data", filename),   # data/ as a sibling of this file's folder (e.g. src/../data)
        os.path.join(os.getcwd(), "data", filename),       # data/ under wherever python was invoked from
        os.path.join(os.getcwd(), filename),               # filename directly in the cwd
    ]
    seen = set()
    for path in candidates:
        norm = os.path.normpath(path)
        if norm in seen:
            continue
        seen.add(norm)
        if os.path.isfile(norm):
            return norm

    tried = "\n  ".join(sorted(seen))
    raise FileNotFoundError(
        f"Could not find {filename!r}. Looked in:\n  {tried}\n"
        f"Move {filename!r} to one of the folders above, or edit the path "
        f"constant at the top of the file that imports data_paths to point "
        f"at it directly."
    )


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for fname in ["market_win_totals.xlsx", "PlayerSalariesCSV.csv", "NBA_Draft_Picks_20152025.xlsx"]:
        try:
            found = find_data_file(fname, here)
            print(f"FOUND {fname} -> {found}")
        except FileNotFoundError as e:
            print(f"MISSING {fname}:\n{e}\n")
