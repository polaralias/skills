from __future__ import annotations

import argparse
from pathlib import Path

from _invoke import invoke


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess closure gates before merge consideration.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--base",
        help="Git base used for causal explanation and documentation-receipt checks.",
    )
    args = parser.parse_args()
    arguments = ["closure", "assess", "--root", str(args.root.resolve())]
    if args.base:
        arguments.extend(["--base", args.base])
    return invoke(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
