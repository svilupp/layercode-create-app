# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2024-12-02

### Added

- New `outdoor_shop` agent: A customer service agent for the fictional "Nimbus Gear" outdoor equipment store
  - `search_products` tool with deeply nested product specifications (pricing, dimensions, materials, ratings, availability by warehouse)
  - `lookup_order` tool with nested order tracking, status history, and shipping details
  - `get_policy` tool with nested policy rules, exceptions, and process steps
  - Designed to exercise complex stream data parsing with multi-level nested structures
  - Distinct tone of voice: measured, safety-conscious, consultative (not salesy)
  - Clear behavioral boundaries for testing agent guardrails

## [0.0.1] - 2024-11-28

### Added

- Initial release
- Core SDK with `StreamHelper` for building agents
- Built-in agents: `echo`, `starter`, `bakery`
- FastAPI server with webhook handling
- Cloudflare tunnel integration
- CLI with `run` and `list-agents` commands
