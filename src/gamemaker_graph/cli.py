"""Command-line interface for GameGraph Core."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .context import impact_graph, task_context
from .graph import graph_overview, graph_status, rebuild_graph, search_graph


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
    else:
        result = graph_status(project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
