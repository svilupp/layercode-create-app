# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-12-02

### Added

- Full support for all LayerCode webhook event types: `session.start`, `message`, `data`, `session.update`, `session.end`
- New `outdoor_shop` agent: A customer service agent for the fictional "Nimbus Gear" outdoor equipment store with more complex tool responses (to mimic `stream.data` payloads)
- Auto-update webhook URL via `--unsafe-update-webhook` flag when using `--tunnel` (requires `LAYERCODE_AGENT_ID`)


## [0.0.1] - 2025-11-02

### Added

- Initial release
- Core SDK with `StreamHelper` for building agents
- Built-in agents: `echo`, `starter`, `bakery`
- FastAPI server with webhook handling
- Cloudflare tunnel integration
- CLI with `run` and `list-agents` commands
