"""
Produce a candidate-facing copy of this repo with interviewer material removed.

    python scripts/make_candidate_copy.py ../candidate-copy
"""

import shutil
import sys
from pathlib import Path

EXCLUDE = {"interviewer", ".git", ".venv", "data", "__pycache__", ".pytest_cache"}


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: make_candidate_copy.py <dest-dir>")
    src = Path(__file__).resolve().parents[1]
    dest = Path(sys.argv[1]).resolve()
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=lambda _d, names: [n for n in names if n in EXCLUDE])
    print(f"candidate copy written to {dest}")


if __name__ == "__main__":
    main()
