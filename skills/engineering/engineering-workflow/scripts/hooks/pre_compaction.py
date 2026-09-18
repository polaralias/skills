from __future__ import annotations

import argparse
from pathlib import Path

from _invoke import invoke


def main() -> int:
    parser = argparse.ArgumentParser(description="Checkpoint compact verified restart context.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--summary", required=True)
    parser.add_argument("--next-action", required=True)
    args = parser.parse_args()
    return invoke(
        [
            "checkpoint",
            "--root",
            str(args.root.resolve()),
            "--summary",
            args.summary,
            "--next-action",
            args.next_action,
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
