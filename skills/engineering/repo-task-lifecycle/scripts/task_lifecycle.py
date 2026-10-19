from __future__ import annotations

import argparse
import sys

import okf_tasks


def legacy_init(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Compatibility alias for repo-task-lifecycle create.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--owner")
    args = parser.parse_args(argv)
    return okf_tasks.create_task(
        argparse.Namespace(
            root=args.root,
            bundle="tasks",
            slug=args.slug,
            title=args.title,
            description=args.title,
            owner=args.owner,
        )
    )


def legacy_add_workstream(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Compatibility alias for repo-task-lifecycle add-workstream.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--branch", required=True)
    args = parser.parse_args(argv)
    return okf_tasks.add_workstream(
        argparse.Namespace(
            root=args.root,
            bundle="tasks",
            task=args.task,
            slug=args.slug,
            title=args.title,
            description=args.title,
            owner=args.owner,
            branch=args.branch,
        )
    )


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] == "init":
        return legacy_init(argv[1:])
    if argv and argv[0] == "add-workstream" and "--description" not in argv and "--bundle" not in argv:
        return legacy_add_workstream(argv[1:])
    return okf_tasks.main()


if __name__ == "__main__":
    raise SystemExit(main())
