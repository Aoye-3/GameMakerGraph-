"""Command-line interface for GameGraph Core."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .context import impact_graph, task_context
from .docs import check_docs, init_docs, inspect_docs, suggest_docs
from .graph import graph_overview, graph_status, rebuild_graph, search_graph
from .trial import prepare_trial, trial_plan, trial_status


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gamegraph")
    commands = parser.add_subparsers(dest="command", required=True)

    for command in ("build", "overview", "status"):
        child = commands.add_parser(command)
        child.add_argument("project", nargs="?", default=".")

    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("project", nargs="?", default=".")
    search.add_argument("--limit", type=int, default=20)

    context = commands.add_parser("context")
    context.add_argument("query")
    context.add_argument("project", nargs="?", default=".")
    context.add_argument("--depth", type=int, default=2)
    context.add_argument("--limit", type=int, default=20)
    context.add_argument("--no-codegraph", action="store_true")

    impact = commands.add_parser("impact")
    impact.add_argument("root")
    impact.add_argument("project", nargs="?", default=".")
    impact.add_argument("--depth", type=int, default=2)
    impact.add_argument("--code-symbol")
    impact.add_argument("--no-codegraph", action="store_true")

    docs = commands.add_parser("docs")
    docs_commands = docs.add_subparsers(dest="docs_command", required=True)
    for operation in ("inspect", "suggest", "init", "check"):
        docs_command = docs_commands.add_parser(operation)
        docs_command.add_argument("project", nargs="?", default=".")

    trial = commands.add_parser("trial")
    trial_commands = trial.add_subparsers(dest="trial_command", required=True)
    for operation in ("status", "prepare", "plan"):
        trial_command = trial_commands.add_parser(operation)
        trial_command.add_argument("project", nargs="?", default=".")
        trial_command.add_argument("--provider", default="taptap-maker")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    project = Path(args.project)
    if args.command == "build":
        result = rebuild_graph(project)
    elif args.command == "overview":
        result = graph_overview(project)
    elif args.command == "search":
        result = search_graph(project, args.query, limit=args.limit)
    elif args.command == "context":
        result = task_context(
            project,
            args.query,
            depth=args.depth,
            limit=args.limit,
            include_code=not args.no_codegraph,
        )
    elif args.command == "impact":
        result = impact_graph(
            project,
            args.root,
            depth=args.depth,
            code_symbol=args.code_symbol,
            include_code=not args.no_codegraph,
        )
    elif args.command == "docs":
        operations = {
            "inspect": inspect_docs,
            "suggest": suggest_docs,
            "init": init_docs,
            "check": check_docs,
        }
        result = operations[args.docs_command](project)
    elif args.command == "trial":
        operations = {
            "status": trial_status,
            "prepare": prepare_trial,
            "plan": trial_plan,
        }
        result = operations[args.trial_command](project, args.provider)
    else:
        result = graph_status(project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
