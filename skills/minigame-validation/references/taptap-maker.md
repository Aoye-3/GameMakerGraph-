# TapTap Maker Adapter Notes

Use the current official TapTap Maker instructions; the tool changes independently of GameMakerGraph.

## Stable local flow

1. Installation or client registration: follow the official `@taptap/maker` installer for the current
   Agent host. This changes user configuration and requires the user's authorization.
2. Authentication and project selection: prefer `taptap-maker login`, `taptap-maker apps`, and
   `taptap-maker init`. Do not ask the user to paste a PAT into a shell unless they explicitly choose the
   documented automation fallback.
3. A successful local checkout writes `.maker-mcp/config.json` and creates the Maker project structure.
   Never print the config content or treat the file as proof of a live MCP connection.
4. Use `taptap-maker doctor` or the current Maker MCP status resource/tool for diagnostics. Confirm the
   project identity before any edit, build, or run.
5. Do not run `init` over an already bound directory. Do not build or publish without explicit scope.

## Sources

- [Official repository](https://github.com/taptap/instant-games-open-mcp)
- [Maker local development guide](https://github.com/taptap/instant-games-open-mcp/blob/main/docs/MAKER.md)
- [Maker NPM package](https://www.npmjs.com/package/@taptap/maker)

If current official behavior differs from this note, follow the official source and record the version or
date used in the validation report.
