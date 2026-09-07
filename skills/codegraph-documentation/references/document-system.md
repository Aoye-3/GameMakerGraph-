# Local Technical Documentation System

Choose documents from evidence in the repository. This is a menu, not a required directory tree.

| Repository evidence | Useful document | Required content |
| --- | --- | --- |
| Multiple documentation areas | `docs/README.md` | Purpose, current/plan distinction, navigation |
| Confirmed gameplay or product rules | `docs/product/gameplay.md` | Player-facing rule, constraints, source, implementation links |
| Multiple runtime components | `docs/architecture/overview.md` | Boundaries, dependency direction, entry points, data flow |
| Browser/client UI exists | `docs/architecture/frontend.md` | Routes/screens, state, components, API boundary, tests |
| Server/API exists | `docs/architecture/backend.md` | Services, API, persistence, jobs, failure boundaries, tests |
| Engine scenes/scripts/assets exist | `docs/architecture/gameplay-implementation.md` | Gameplay concept → scene/data/asset → module/symbol → test |
| Persistent or shared state exists | `docs/architecture/data-and-state.md` | Ownership, schema, lifecycle, migrations, save compatibility |
| External tools or providers exist | `docs/architecture/integrations.md` | Stable boundary, configuration, fallback, failure behavior |
| Non-obvious local setup | `docs/development/setup.md` | Prerequisites, commands, generated files, troubleshooting |
| Multiple verification layers | `docs/development/testing.md` | Test types, commands, fixtures, runtime/manual evidence |
| Build or release pipeline exists | `docs/delivery/release.md` | Build, package, deploy/publish, rollback, acceptance |
| Costly architecture choice is proposed | `docs/decisions/ADR-NNN-title.md` | Context, decision, alternatives, consequences, status |

## Implementation map

For cross-layer features, prefer a compact mapping:

| Concept or behavior | Game project sources | Code entry points | Data/assets | Verification | Confidence |
| --- | --- | --- | --- | --- | --- |

Use `confirmed` only for direct source evidence or explicit user confirmation. Use `inferred` for a defensible relationship that still needs confirmation, and `unknown` when evidence is missing.

## Maintenance metadata

Avoid elaborate headers. Add only metadata that can be maintained, such as status (`current`, `proposed`, `deprecated`), last verified revision, and owner when the repository already uses ownership. Never use a date alone as proof that documentation matches implementation.
