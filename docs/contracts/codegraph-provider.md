# CodeGraph Provider Contract

## Status

Stable for GameMakerGraph `0.2`; verified with CodeGraph `1.1.6` on 2026-09-07.

## Boundary

CodeGraph is an optional code-intelligence Provider. GameMakerGraph invokes its public CLI and normalizes results;
it does not import CodeGraph internals, read `.codegraph/codegraph.db`, manage its watcher, or reproduce its parsers.

| GameMakerGraph operation | CodeGraph public command |
| --- | --- |
| provider health | `codegraph status PROJECT --json` |
| code seeds for task context | `codegraph query QUERY --path PROJECT --limit N --json` |
| symbol blast radius | `codegraph impact SYMBOL --path PROJECT --depth N --json` |

The future MCP adapter may use equivalent `codegraph_*` tools but must produce the same normalized values.

## Provider states

- `current`: executable and index are available, with no pending file changes;
- `stale`: CodeGraph reports added, modified, or removed files awaiting synchronization;
- `unavailable`: executable cannot be found;
- `uninitialized`: project has no `.codegraph/` directory;
- `error`: the command fails, times out, or returns invalid JSON;
- `disabled`: the caller supplied `--no-codegraph`;
- `not_requested`: GameGraph impact was requested without a code symbol.

Provider failure is data, not a GameGraph failure. It cannot block local gameplay/document context unless the
GameGraph index itself is stale.

## Normalized symbol

```json
{
  "id": "function:...",
  "kind": "function",
  "name": "build_graph",
  "qualified_name": "build_graph",
  "source": "src/gamemaker_graph/graph.py",
  "line": 155,
  "signature": "(project_root: Path) -> dict[str, Any]",
  "score": 99.0
}
```

Paths remain repository-relative. GameMakerGraph deliberately drops CodeGraph timestamps, database paths and
machine-specific project paths from combined context.

## Lifecycle and consent

GameMakerGraph never installs CodeGraph or runs `codegraph init` implicitly. Installation, telemetry preference,
initial indexing and `codegraph sync` remain explicit CodeGraph/user operations. A `.codegraph/` directory is a
derived local index and is ignored by this repository.

## Compatibility

The JSON CLI is normalized behind `CodeGraphProvider`. Upstream fields may evolve; missing optional fields become
`null`, malformed output becomes `error`, and the GameGraph result remains usable. Compatibility with versions
other than the verified version is best effort until covered by a fixture or live integration test.
