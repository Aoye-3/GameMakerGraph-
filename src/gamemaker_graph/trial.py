"""Prepare a local project for a bounded minigame validation."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .docs import check_docs, init_docs
from .graph import graph_status, rebuild_graph

SCHEMA_VERSION = "0.1"
SUPPORTED_PROVIDERS = ("taptap-maker",)


def _root(project_root: Path) -> Path:
    root = project_root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    return root


def _provider(provider: str) -> str:
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported trial provider: {provider}")
    return provider


def _launcher() -> str | None:
    if shutil.which("taptap-maker"):
        return "taptap-maker"
    if shutil.which("npx") or shutil.which("npx.cmd"):
        return "npx"
    return None


def _missing_document_errors(document_check: dict[str, Any]) -> list[dict[str, Any]]:
    return [issue for issue in document_check["issues"] if issue["code"] == "missing-document"]


def _next_actions(*, bound: bool, structure_present: bool, prepared: bool, root: Path) -> list[str]:
    if not bound:
        return [
            "Run `taptap-maker init` in an empty, dedicated game directory after user approval.",
            "Then run `gamegraph trial prepare <maker-project>` from the initialized project.",
        ]
    if not structure_present:
        return [
            "Run `taptap-maker doctor` and repair the Maker checkout before "
            "GameMakerGraph writes files."
        ]
    if not prepared:
        return [f"Run `gamegraph trial prepare {root}` to add missing docs and rebuild GameGraph."]
    return [
        "Use `$minigame-validation` in an Agent session with TapTap Maker MCP available.",
        "Verify the live Maker project identity before editing or running the game.",
    ]


def trial_status(project_root: Path, provider: str = "taptap-maker") -> dict[str, Any]:
    """Return local readiness without claiming that an MCP session is connected."""

    root = _root(project_root)
    provider = _provider(provider)
    bound = (root / ".maker-mcp/config.json").is_file()
    structure_present = (root / "scripts").is_dir() and (root / "assets").is_dir()
    gamegraph = graph_status(root)
    document_check = check_docs(root)
    documents_present = not _missing_document_errors(document_check)
    prepared = gamegraph["status"] == "current" and documents_present

    if not bound or not structure_present:
        status = "blocked"
    elif prepared:
        status = "ready_for_live_validation"
    else:
        status = "preparation_required"

    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "status",
        "provider": provider,
        "project_root": str(root),
        "status": status,
        "provider_connection": "unverified",
        "checks": {
            "maker_project_bound": bound,
            "maker_structure_present": structure_present,
            "provider_launcher": _launcher(),
            "gamegraph_current": gamegraph["status"] == "current",
            "documents_present": documents_present,
        },
        "gamegraph": gamegraph,
        "documentation": {
            "status": document_check["status"],
            "missing": [issue["source"] for issue in _missing_document_errors(document_check)],
        },
        "next_actions": _next_actions(
            bound=bound,
            structure_present=structure_present,
            prepared=prepared,
            root=root,
        ),
    }


def prepare_trial(project_root: Path, provider: str = "taptap-maker") -> dict[str, Any]:
    """Add missing docs and rebuild GameGraph for an initialized Maker project."""

    root = _root(project_root)
    initial = trial_status(root, provider)
    if initial["status"] == "blocked":
        return {
            **initial,
            "operation": "prepare",
            "changed": False,
            "documents": {"created": [], "preserved": []},
        }

    documents = init_docs(root)
    rebuild_graph(root)
    final = trial_status(root, provider)
    return {
        **final,
        "operation": "prepare",
        "changed": True,
        "documents": {
            "created": documents["created"],
            "preserved": documents["preserved"],
        },
    }


def trial_plan(project_root: Path, provider: str = "taptap-maker") -> dict[str, Any]:
    """Return a provider-neutral observable acceptance plan without writing files."""

    status = trial_status(project_root, provider)
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "plan",
        "provider": status["provider"],
        "project_root": status["project_root"],
        "readiness": status["status"],
        "provider_connection": "unverified",
        "scope": {
            "primary_verbs": 1,
            "observable_state_changes": 1,
            "success_goals": 1,
            "creative_direction": "human-confirmed",
        },
        "acceptance": [
            {
                "id": "launch",
                "claim": "The current Maker project launches in its real preview/runtime.",
                "evidence": "current run identity and preview capture",
            },
            {
                "id": "primary-verb",
                "claim": "One player input causes an observable game-state change.",
                "evidence": "input trace plus before/after state or capture",
            },
            {
                "id": "goal",
                "claim": "The player can reach one explicit success outcome.",
                "evidence": "runtime state and player-visible result",
            },
            {
                "id": "restart",
                "claim": "The shortest loop can be started again without manual repair.",
                "evidence": "second bounded run",
            },
            {
                "id": "diagnostics",
                "claim": "No blocking runtime or build diagnostic invalidates the run.",
                "evidence": "current diagnostics from the same run",
            },
            {
                "id": "fresh-context",
                "claim": "GameGraph and implementation documentation match the final source.",
                "evidence": "current graph revision and implementation-map sources",
            },
        ],
        "completion_rule": (
            "MCP connection and every acceptance claim require current real evidence; "
            "a generated file, successful tool call, or build alone is insufficient."
        ),
        "next_actions": status["next_actions"],
    }
