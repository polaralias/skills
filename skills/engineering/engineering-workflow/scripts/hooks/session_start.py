from __future__ import annotations

import argparse
from pathlib import Path

from _invoke import invoke


def main() -> int:
    parser = argparse.ArgumentParser(description="Idempotently establish engineering workflow state.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    return invoke(["activate", "--root", str(args.root.resolve())])


if __name__ == "__main__":
    raise SystemExit(main())
