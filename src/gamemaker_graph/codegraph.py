"""Optional adapter for the upstream CodeGraph command-line interface."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

Runner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass
class CodeGraphProvider:
    """Query CodeGraph through its public JSON CLI without reading its database."""

    executable: str | None
    runner: Runner = subprocess.run
    timeout_seconds: float = 30.0

    @classmethod
    def auto(cls) -> CodeGraphProvider:
        return cls(executable=shutil.which("codegraph"))

    def _run_json(self, root: Path, arguments: list[str]) -> tuple[Any | None, str | None]:
        if self.executable is None:
            return None, "CodeGraph executable was not found"
        try:
            completed = self.runner(
                [self.executable, *arguments],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return None, f"{type(exc).__name__}: {exc}"
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
            return None, f"CodeGraph exited with {completed.returncode}: {message}"
        try:
            return json.loads(completed.stdout), None
        except ValueError as exc:
            return None, f"CodeGraph returned invalid JSON: {exc}"

    def status(self, project_root: Path) -> dict[str, Any]:
        root = project_root.resolve()
        base: dict[str, Any] = {"provider": "codegraph"}
        if self.executable is None:
            return base | {"status": "unavailable", "error": "executable not found"}
        if not (root / ".codegraph").is_dir():
            return base | {"status": "uninitialized", "error": None}

        payload, error = self._run_json(root, ["status", str(root), "--json"])
        if error or not isinstance(payload, dict):
            return base | {"status": "error", "error": error or "invalid status payload"}

        pending = payload.get("pendingChanges")
        changes = pending if isinstance(pending, dict) else {}
        stale = any(isinstance(value, int) and value > 0 for value in changes.values())
        return base | {
            "status": "stale" if stale else "current",
            "version": payload.get("version"),
            "files": payload.get("fileCount"),
            "nodes": payload.get("nodeCount"),
            "edges": payload.get("edgeCount"),
            "pending_changes": {
                key: changes.get(key, 0) for key in ("added", "modified", "removed")
            },
            "error": None,
        }

    def context(self, project_root: Path, query: str, *, limit: int = 10) -> dict[str, Any]:
        root = project_root.resolve()
        state = self.status(root)
        if state["status"] != "current":
            return state | {"query": query, "symbols": []}

        limit = max(1, min(limit, 50))
        payload, error = self._run_json(
            root,
            ["query", query, "--path", str(root), "--limit", str(limit), "--json"],
        )
        if error or not isinstance(payload, list):
            return state | {
                "status": "error",
                "query": query,
                "symbols": [],
                "error": error or "invalid query payload",
            }

        symbols: list[dict[str, Any]] = []
        for result in payload[:limit]:
            if not isinstance(result, dict) or not isinstance(result.get("node"), dict):
                continue
            node = result["node"]
            symbols.append(
                {
                    "id": node.get("id"),
                    "kind": node.get("kind"),
                    "name": node.get("name"),
                    "qualified_name": node.get("qualifiedName"),
                    "source": node.get("filePath"),
                    "line": node.get("startLine"),
                    "signature": node.get("signature"),
                    "score": result.get("score"),
                }
            )
        return state | {"query": query, "symbols": symbols}

    def impact(self, project_root: Path, symbol: str, *, depth: int = 2) -> dict[str, Any]:
        root = project_root.resolve()
        state = self.status(root)
        if state["status"] != "current":
            return state | {"symbol": symbol, "affected": []}

        depth = max(1, min(depth, 5))
        payload, error = self._run_json(
            root,
            ["impact", symbol, "--path", str(root), "--depth", str(depth), "--json"],
        )
        if error or not isinstance(payload, dict):
            return state | {
                "status": "error",
                "symbol": symbol,
                "affected": [],
                "error": error or "invalid impact payload",
            }

        affected = []
        for item in payload.get("affected", []):
            if not isinstance(item, dict):
                continue
            affected.append(
                {
                    "name": item.get("name"),
                    "kind": item.get("kind"),
                    "source": item.get("filePath"),
                    "line": item.get("startLine"),
                }
            )
        return state | {
            "symbol": payload.get("symbol", symbol),
            "depth": payload.get("depth", depth),
            "affected": affected,
        }
