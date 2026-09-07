"""Command-line interface for GameGraph Core."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

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
    else:
        result = graph_status(project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
