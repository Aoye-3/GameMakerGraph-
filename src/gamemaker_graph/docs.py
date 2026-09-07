"""Inspect, suggest, initialize, and check a local project documentation set."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Iterable

from .graph import IGNORED_DIRECTORIES, graph_status

SCHEMA_VERSION = "0.1"
CAPABILITY_ORDER = ("game", "frontend", "backend", "delivery")
BASE_DOCUMENTS = (
    "docs/README.md",
    "docs/product/overview.md",
    "docs/architecture/overview.md",
    "docs/architecture/implementation-map.md",
    "docs/development/setup.md",
    "docs/development/testing.md",
)
CAPABILITY_DOCUMENTS = {
    "game": "docs/product/gameplay.md",
    "frontend": "docs/architecture/frontend.md",
    "backend": "docs/architecture/backend.md",
    "delivery": "docs/delivery/release.md",
}
DOCUMENT_PURPOSES = {
    "docs/README.md": "Index the maintained project documentation and its status.",
    "docs/product/overview.md": "Record confirmed product direction, audience, and scope.",
    "docs/product/gameplay.md": "Record confirmed player verbs, rules, loops, and boundaries.",
    "docs/architecture/overview.md": "Explain component boundaries, entry points, and data flow.",
    "docs/architecture/implementation-map.md": (
        "Map product or gameplay concepts to files, symbols, data, assets, and verification."
    ),
    "docs/architecture/frontend.md": "Describe screens, client state, APIs, and frontend tests.",
    "docs/architecture/backend.md": (
        "Describe services, APIs, persistence, jobs, and backend tests."
    ),
    "docs/development/setup.md": "Keep local setup and run commands executable.",
    "docs/development/testing.md": (
        "Define automated, runtime, and manual verification entry points."
    ),
    "docs/delivery/release.md": (
        "Describe the existing build and release path without inventing one."
    ),
}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")


def _markdown_files(root: Path) -> Iterable[Path]:
    for directory, folders, filenames in os.walk(root, followlinks=False):
        folders[:] = sorted(
            folder
            for folder in folders
            if not folder.startswith(".") and folder not in IGNORED_DIRECTORIES
        )
        for filename in sorted(filenames):
            if not filename.casefold().endswith(".md"):
                continue
            path = (Path(directory) / filename).resolve()
            if path.is_file() and path.is_relative_to(root):
                yield path


def _manifest_text(root: Path) -> str:
    parts = []
    for filename in ("package.json", "pyproject.toml", "requirements.txt", "Cargo.toml"):
        path = root / filename
        if path.is_file() and path.stat().st_size <= 256 * 1024:
            parts.append(path.read_text("utf-8", errors="replace").casefold())
    return "\n".join(parts)


def detect_project_capabilities(project_root: Path) -> tuple[list[str], dict[str, list[str]]]:
    root = project_root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    evidence: dict[str, list[str]] = {name: [] for name in CAPABILITY_ORDER}

    if (root / "project.godot").is_file():
        evidence["game"].append("project.godot")
    evidence["game"].extend(path.name for path in sorted(root.glob("*.uproject")))
    if (root / "scenes").is_dir() and (root / "assets").is_dir():
        evidence["game"].append("scenes/assets directory")

    web_directories = ("src", "app", "pages", "components")
    if (root / "package.json").is_file() and any(
        (root / directory).is_dir() for directory in web_directories
    ):
        evidence["frontend"].append("package.json with web source directory")
    if (root / "index.html").is_file():
        evidence["frontend"].append("index.html")

    for directory in ("backend", "server", "api"):
        if (root / directory).is_dir():
            evidence["backend"].append(f"{directory}/")
    manifest = _manifest_text(root)
    backend_markers = ("fastapi", "django", "flask", "express", "nestjs", "hono")
    matched_backend = sorted(marker for marker in backend_markers if marker in manifest)
    if matched_backend:
        evidence["backend"].append("backend dependency: " + ", ".join(matched_backend))

    delivery_paths = (
        ".github/workflows",
        "Dockerfile",
        "docker-compose.yml",
        "export_presets.cfg",
        "netlify.toml",
        "vercel.json",
    )
    for relative in delivery_paths:
        if (root / relative).exists():
            evidence["delivery"].append(relative)

    capabilities = [name for name in CAPABILITY_ORDER if evidence[name]]
    return capabilities, {name: evidence[name] for name in capabilities}


def _document_paths(capabilities: list[str]) -> list[str]:
    paths = list(BASE_DOCUMENTS)
    paths.extend(CAPABILITY_DOCUMENTS[name] for name in capabilities)
    return sorted(paths)


def suggest_docs(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    capabilities, evidence = detect_project_capabilities(root)
    suggestions = []
    for relative in _document_paths(capabilities):
        capability = next(
            (name for name, path in CAPABILITY_DOCUMENTS.items() if path == relative), "baseline"
        )
        suggestions.append(
            {
                "path": relative,
                "state": "existing" if (root / relative).is_file() else "missing",
                "capability": capability,
                "reason": DOCUMENT_PURPOSES[relative],
                "evidence": evidence.get(capability, ["documentation baseline"]),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "suggest",
        "project_root": str(root),
        "project_capabilities": capabilities,
        "capability_evidence": evidence,
        "suggestions": suggestions,
    }


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return fallback


def inspect_docs(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    suggestions = suggest_docs(root)
    documents = []
    for path in _markdown_files(root):
        relative = path.relative_to(root).as_posix()
        text = path.read_text("utf-8-sig", errors="replace")
        documents.append(
            {
                "path": relative,
                "title": _title(text, path.stem),
                "bytes": path.stat().st_size,
                "recommended": relative in {item["path"] for item in suggestions["suggestions"]},
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "inspect",
        "project_root": str(root),
        "project_capabilities": suggestions["project_capabilities"],
        "capability_evidence": suggestions["capability_evidence"],
        "gamegraph": graph_status(root),
        "documents": documents,
        "recommendations": suggestions["suggestions"],
    }


def _display_title(relative: str) -> str:
    return Path(relative).stem.replace("-", " ").title()


def _index_template(paths: list[str]) -> str:
    links = []
    for relative in paths:
        if relative == "docs/README.md":
            continue
        target = Path(relative).relative_to("docs").as_posix()
        links.append(f"- [{_display_title(relative)}]({target})")
    return (
        "# Project Documentation\n\n"
        "Status: draft\n\n"
        "## Documents\n\n"
        + "\n".join(links)
        + "\n\n## Confirmed\n\n- Native project files remain the source of truth.\n\n"
        "## To confirm\n\n- [ ] Confirm documentation owners and maintenance cadence.\n"
    )


def _document_template(relative: str) -> str:
    title = _display_title(relative)
    purpose = DOCUMENT_PURPOSES[relative]
    content = (
        f"# {title}\n\n"
        "Status: draft\n\n"
        f"> Purpose: {purpose}\n\n"
        "## Confirmed\n\n"
        "Record only facts supported by project sources or explicit human confirmation.\n\n"
        "## To confirm\n\n"
        "- [ ] Replace this item with the smallest unresolved decision for this project.\n\n"
        "## Sources\n\n"
        "- Add repository-relative source paths and relevant symbols.\n"
    )
    if relative == "docs/architecture/implementation-map.md":
        content += (
            "\n## Implementation map\n\n"
            "| Concept or behavior | Game sources | Code entry points | "
            "Verification | Confidence |\n"
            "| --- | --- | --- | --- | --- |\n"
            "<!-- Add mapping rows below. -->\n"
        )
    return content


def init_docs(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    suggestions = suggest_docs(root)
    paths = [item["path"] for item in suggestions["suggestions"]]
    created: list[str] = []
    preserved: list[str] = []
    for relative in paths:
        path = root / relative
        if path.exists():
            preserved.append(relative)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            _index_template(paths) if relative == "docs/README.md" else _document_template(relative)
        )
        path.write_text(content, encoding="utf-8")
        created.append(relative)
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "init",
        "project_root": str(root),
        "project_capabilities": suggestions["project_capabilities"],
        "created": created,
        "preserved": preserved,
    }


def _relative_link(root: Path, source: Path, raw_target: str) -> Path | None:
    if raw_target.startswith(("#", "http://", "https://", "mailto:", "data:")):
        return None
    target_text = raw_target.split("#", 1)[0].split("?", 1)[0]
    if not target_text:
        return None
    target = (source.parent / target_text).resolve()
    if not target.is_relative_to(root):
        return target
    return target / "README.md" if target.is_dir() else target


def check_docs(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    suggestions = suggest_docs(root)
    issues: list[dict[str, Any]] = []

    for item in suggestions["suggestions"]:
        if item["state"] == "missing":
            issues.append(
                {
                    "severity": "error",
                    "code": "missing-document",
                    "source": item["path"],
                    "message": "Recommended project document is missing.",
                }
            )

    for path in _markdown_files(root):
        relative = path.relative_to(root).as_posix()
        text = path.read_text("utf-8-sig", errors="replace")
        for match in MARKDOWN_LINK.finditer(text):
            target = _relative_link(root, path, match.group(1))
            if target is not None and (not target.is_relative_to(root) or not target.is_file()):
                line = text.count("\n", 0, match.start()) + 1
                issues.append(
                    {
                        "severity": "error",
                        "code": "broken-link",
                        "source": f"{relative}:{line}",
                        "message": f"Markdown target does not exist: {match.group(1)}",
                    }
                )
        if "- [ ]" in text:
            issues.append(
                {
                    "severity": "warning",
                    "code": "unconfirmed-items",
                    "source": relative,
                    "message": "Document still contains items that require confirmation.",
                }
            )

    implementation_map = root / "docs/architecture/implementation-map.md"
    if (
        implementation_map.is_file()
        and "<!-- Add mapping rows below. -->"
        in implementation_map.read_text("utf-8-sig", errors="replace")
    ):
        issues.append(
            {
                "severity": "warning",
                "code": "empty-implementation-map",
                "source": "docs/architecture/implementation-map.md",
                "message": "Implementation map has no project-specific rows.",
            }
        )

    gamegraph = graph_status(root)
    if gamegraph["status"] != "current":
        issues.append(
            {
                "severity": "warning" if gamegraph["status"] == "stale" else "info",
                "code": "gamegraph-" + gamegraph["status"],
                "source": ".gamemakergraph/graph.json",
                "message": f"GameGraph status is {gamegraph['status']}.",
            }
        )

    blocking = any(issue["severity"] in {"error", "warning"} for issue in issues)
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "check",
        "project_root": str(root),
        "project_capabilities": suggestions["project_capabilities"],
        "status": "issues" if blocking else "ok",
        "issues": sorted(issues, key=lambda item: (item["severity"], item["code"], item["source"])),
    }
