#!/usr/bin/env python3
"""Thin Pandoc wrapper with sane defaults for file conversion."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


FORMAT_EXTENSION_MAP = {
    "asciidoc": ".adoc",
    "beamer": ".tex",
    "commonmark": ".md",
    "docbook": ".xml",
    "docx": ".docx",
    "epub": ".epub",
    "gfm": ".md",
    "html": ".html",
    "html4": ".html",
    "html5": ".html",
    "latex": ".tex",
    "markdown": ".md",
    "odt": ".odt",
    "org": ".org",
    "plain": ".txt",
    "pptx": ".pptx",
    "rst": ".rst",
}


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description=(
            "Convert files with pandoc. Defaults to a straightforward conversion "
            "with --wrap=none and passes unknown flags through to pandoc."
        )
    )
    parser.add_argument("input_file", help="Input file path")
    parser.add_argument(
        "output_file",
        nargs="?",
        help="Output file path (optional if --output, --stdout, or inferable from --to)",
    )
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-f", "--from", dest="from_format", help="Input format")
    parser.add_argument("-t", "--to", dest="to_format", help="Output format")
    parser.add_argument(
        "--wrap",
        default="none",
        choices=("auto", "none", "preserve"),
        help="Word wrapping mode (default: none)",
    )
    parser.add_argument(
        "-s",
        "--standalone",
        action="store_true",
        help="Produce a standalone document",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Write output to stdout instead of a file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print pandoc command and exit without running it",
    )

    args, passthrough = parser.parse_known_args()
    return args, passthrough


def normalize_format_name(fmt: str) -> str:
    # pandoc formats can include extensions, e.g. markdown+smart
    return re.split(r"[+-]", fmt.strip().lower(), maxsplit=1)[0]


def infer_output_path(input_path: Path, to_format: str | None) -> Path | None:
    if not to_format:
        return None

    normalized = normalize_format_name(to_format)
    extension = FORMAT_EXTENSION_MAP.get(normalized)
    if not extension:
        return None

    return input_path.with_suffix(extension)


def resolve_output(
    positional_output: str | None,
    output_option: str | None,
    input_path: Path,
    to_format: str | None,
    use_stdout: bool,
) -> Path | None:
    if positional_output and output_option:
        pos_path = Path(positional_output)
        opt_path = Path(output_option)
        if pos_path != opt_path:
            raise ValueError("Specify output only once (positional output_file or --output).")

    if use_stdout:
        return None

    output = output_option or positional_output
    if output:
        return Path(output)

    inferred = infer_output_path(input_path, to_format)
    if inferred:
        if inferred.resolve() == input_path.resolve():
            raise ValueError(
                "Inferred output path matches input path; provide a different output path."
            )
        return inferred

    raise ValueError(
        "Output is required. Provide output_file/--output, use --stdout, or set --to for inference."
    )


def build_command(
    input_path: Path,
    output_path: Path | None,
    from_format: str | None,
    to_format: str | None,
    wrap_mode: str,
    standalone: bool,
    passthrough: list[str],
) -> list[str]:
    cmd = ["pandoc", str(input_path)]

    if from_format:
        cmd.extend(["--from", from_format])
    if to_format:
        cmd.extend(["--to", to_format])
    if standalone:
        cmd.append("--standalone")

    cmd.extend(["--wrap", wrap_mode])

    if output_path:
        cmd.extend(["-o", str(output_path)])

    cmd.extend(passthrough)
    return cmd


def main() -> int:
    args, passthrough = parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        return 1
    if not input_path.is_file():
        print(f"[ERROR] Input path is not a file: {input_path}", file=sys.stderr)
        return 1

    try:
        output_path = resolve_output(
            positional_output=args.output_file,
            output_option=args.output,
            input_path=input_path,
            to_format=args.to_format,
            use_stdout=args.stdout,
        )
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    cmd = build_command(
        input_path=input_path,
        output_path=output_path,
        from_format=args.from_format,
        to_format=args.to_format,
        wrap_mode=args.wrap,
        standalone=args.standalone,
        passthrough=passthrough,
    )

    if args.dry_run:
        print(subprocess.list2cmdline(cmd))
        return 0

    if shutil.which("pandoc") is None:
        print(
            "[ERROR] pandoc is not installed or not on PATH. Install pandoc first.",
            file=sys.stderr,
        )
        return 127

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(cmd, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
