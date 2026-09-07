"""Parse source-backed semantic facts from controlled Markdown blocks."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

START_MARKER = "<!-- GAMEGRAPH:START -->"
END_MARKER = "<!-- GAMEGRAPH:END -->"
SEMANTIC_NODE_KINDS = {
    "feature",
    "player_action",
    "game_state",
    "rule",
    "milestone",
    "acceptance_criterion",
    "decision",
    "issue",
    "validation_evidence",
}
SEMANTIC_EDGE_KINDS = {
    "documents",
    "implemented_by",
    "depends_on",
    "changes",
    "validated_by",
    "blocked_by",
}
_IGNORED_DIRECTORIES = {
    ".gamemakergraph",
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
}
_BLOCK = re.compile(
    rf"^{re.escape(START_MARKER)}\s*$\n?(.*?)^\s*{re.escape(END_MARKER)}\s*$",
    re.MULTILINE | re.DOTALL,
)
_SLUG = re.compile(r"[^a-z0-9_-]+")


def stable_semantic_id(kind: str, key: str) -> str:
    """Return a deterministic ID whose identity is independent from its label."""

    normalized = key.strip().casefold()
    slug = _SLUG.sub("-", normalized).strip("-") or "fact"
    digest = hashlib.sha256(f"{kind}\0{normalized}".encode()).hexdigest()[:10]
    return f"semantic:{kind}:{slug[:48]}:{digest}"


def _markdown_files(root: Path) -> Iterable[Path]:
    for directory, folders, filenames in os.walk(root, followlinks=False):
        folders[:] = sorted(
            folder
            for folder in folders
            if not folder.startswith(".") and folder not in _IGNORED_DIRECTORIES
        )
        for filename in sorted(filenames):
            if filename.casefold().endswith(".md"):
                path = (Path(directory) / filename).resolve()
                if path.is_file() and path.is_relative_to(root):
                    yield path


def _json_text(block: str) -> str:
    text = block.strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if len(lines) < 3 or lines[-1].strip() != "```":
        raise ValueError("controlled block has an unterminated fenced code block")
    if lines[0].strip().casefold() not in {"```", "```json"}:
        raise ValueError("controlled block fence must be JSON")
    return "\n".join(lines[1:-1])


def _relative_path(root: Path, value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = PurePosixPath(value.replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (root / Path(*candidate.parts)).resolve()
    if not resolved.is_relative_to(root):
        return None
    return candidate.as_posix()


def _relationship_allowed(
    source_kind: str,
    target_kind: str | None,
    edge_kind: str,
    *,
    target_is_file: bool,
) -> bool:
    if edge_kind == "documents":
        return source_kind in SEMANTIC_NODE_KINDS and target_is_file
    if edge_kind == "implemented_by":
        return source_kind != "validation_evidence" and target_is_file
    if edge_kind == "depends_on":
        return source_kind != "validation_evidence" and (
            target_is_file or target_kind != "validation_evidence"
        )
    if edge_kind == "changes":
        return source_kind in {"feature", "player_action", "decision"} and target_kind in {
            "feature",
            "game_state",
            "rule",
            "milestone",
        }
    if edge_kind == "validated_by":
        return source_kind in {
            "feature",
            "player_action",
            "game_state",
            "rule",
            "milestone",
            "acceptance_criterion",
        } and target_kind == "validation_evidence"
    if edge_kind == "blocked_by":
        return source_kind != "validation_evidence" and target_kind == "issue"
    return False


def _public_details(
    root: Path, item: Mapping[str, Any], warnings: list[str], location: str
) -> dict[str, Any] | None:
    details = {
        key: value
        for key, value in item.items()
        if key not in {"key", "kind", "label", "source", "id"}
    }
    if "path" in details:
        relative = _relative_path(root, details["path"])
        if relative is None:
            warnings.append(f"Invalid evidence path at {location}")
            return None
        details["path"] = relative
    return details


def parse_semantic_documents(project_root: Path) -> dict[str, Any]:
    """Parse every valid controlled block without modifying the project."""

    root = project_root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)

    nodes: list[dict[str, Any]] = []
    pending_edges: list[tuple[dict[str, Any], str]] = []
    warnings: list[str] = []
    by_key: dict[str, dict[str, Any]] = {}

    for path in _markdown_files(root):
        relative = path.relative_to(root).as_posix()
        text = path.read_text("utf-8-sig", errors="replace")
        for match in _BLOCK.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            location = f"{relative}:{line}"
            try:
                payload = json.loads(_json_text(match.group(1)))
            except (ValueError, json.JSONDecodeError) as exc:
                warnings.append(f"Invalid GAMEGRAPH block at {location}: {exc}")
                continue
            if not isinstance(payload, dict):
                warnings.append(f"Invalid GAMEGRAPH payload at {location}: expected object")
                continue

            raw_nodes = payload.get("nodes", [])
            if not isinstance(raw_nodes, list):
                warnings.append(f"Invalid GAMEGRAPH nodes at {location}: expected array")
                raw_nodes = []
            for item in raw_nodes:
                if not isinstance(item, dict):
                    warnings.append(f"Invalid semantic node at {location}: expected object")
                    continue
                kind = item.get("kind")
                key_value = item.get("key")
                label = item.get("label")
                if (
                    kind not in SEMANTIC_NODE_KINDS
                    or not isinstance(key_value, str)
                    or not key_value.strip()
                    or not isinstance(label, str)
                    or not label.strip()
                ):
                    warnings.append(f"Invalid semantic node at {location}")
                    continue
                key = key_value.strip().casefold()
                if key in by_key:
                    warnings.append(f"Duplicate semantic key at {location}: {key}")
                    continue
                details = _public_details(root, item, warnings, location)
                if details is None:
                    continue
                node = {
                    "id": stable_semantic_id(kind, key),
                    "kind": kind,
                    "label": label.strip(),
                    "source": relative,
                    "details": {"key": key, **details},
                }
                by_key[key] = node
                nodes.append(node)

            raw_edges = payload.get("edges", [])
            if not isinstance(raw_edges, list):
                warnings.append(f"Invalid GAMEGRAPH edges at {location}: expected array")
                raw_edges = []
            pending_edges.extend(
                (dict(item), location) for item in raw_edges if isinstance(item, dict)
            )

    edges: list[dict[str, str]] = []
    for item, location in pending_edges:
        source_key = item.get("source")
        target_ref = item.get("target")
        kind = item.get("kind")
        if not isinstance(source_key, str) or not isinstance(target_ref, str):
            warnings.append(f"Invalid semantic relationship at {location}")
            continue
        source = by_key.get(source_key.strip().casefold())
        target = by_key.get(target_ref.strip().casefold())
        target_path = None if target else _relative_path(root, target_ref)
        target_is_file = (
            target is None and target_path is not None and (root / target_path).is_file()
        )
        if (
            source is None
            or kind not in SEMANTIC_EDGE_KINDS
            or (target is None and not target_is_file)
            or not _relationship_allowed(
                source["kind"],
                target["kind"] if target else None,
                kind,
                target_is_file=target_is_file,
            )
        ):
            warnings.append(
                f"Invalid semantic relationship at {location}: "
                f"{source_key} -[{kind}]-> {target_ref}"
            )
            continue
        edges.append(
            {
                "source": source["id"],
                "target": target["id"] if target else "file:" + str(target_path),
                "kind": kind,
                "evidence": location,
            }
        )

    return {
        "nodes": sorted(nodes, key=lambda item: item["id"]),
        "edges": sorted(
            edges, key=lambda item: (item["source"], item["target"], item["kind"])
        ),
        "warnings": sorted(set(warnings)),
    }
