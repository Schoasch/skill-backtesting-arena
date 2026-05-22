# Backtesting Arena — Agent Skill

Skill package for AI agents and LLMs that need programmatic access to the
**[Backtesting Arena](https://tradingstrategies.work)** API: daily Bitcoin /
crypto cycle scoring, on-chain indicators, aggregated strategy insights, and
on-demand backtests.

**Three channels, one product:**

| Channel | Auth | Use case |
|---|---|---|
| **Public** | none, fair-use cache | quick reads, no signup |
| **REST + MCP** | Bearer API key (Free tier available) | full surface, higher quotas |
| **x402 pay-per-call** | EIP-3009 wallet signature (USDC on Base) | autonomous agents, no account |

The full capability descriptor an agent should load is [`skill.md`](./skill.md).

---

## Install for Claude Code / Claude Desktop

```
# Coming soon when /install-skill GA's; for now clone + reference manually:
git clone https://github.com/Schoasch/skill-backtesting-arena.git
```

Reference `skill.md` as a context document in your agent runtime, or use the
MCP server directly (see below).

## Quick start

### 1. Cycle-aware trading bot (Bearer)

```bash
curl https://tradingstrategies.work/api/arena-pulse/today
# → { "score": 35, "band": "risk-off", ... } — no API key required
```

Want higher quotas + full surface? [Get a free Bearer key](https://tradingstrategies.work/dashboard/account/api-keys).

### 2. Autonomous agent with USDC wallet (x402)

```bash
# First call returns HTTP 402 + payment instructions:
curl -i https://tradingstrategies.work/api/v1/agent/btc-cycle/latest
# → 402 Payment Required, body has accepts[] with payTo, asset, amount, network

# Discovery descriptor lists all paid endpoints + pricing:
curl https://tradingstrategies.work/.well-known/x402
```

Full Python client showing the EIP-3009 sign + retry pattern: [`examples/python-x402-client.py`](./examples/python-x402-client.py).

### 3. MCP server (Claude Desktop, Cursor, etc.)

Two transports — HTTP (recommended, requires Bearer key) or stdio.

HTTP variant (drop into `claude_desktop_config.json` → `mcpServers`):

```json
{
  "backtesting-arena": {
    "url": "https://tradingstrategies.work/api/mcp",
    "headers": { "Authorization": "Bearer sk-arena-…" }
  }
}
```

Full example incl. stdio variant + Cursor config: [`examples/claude-desktop-config.json`](./examples/claude-desktop-config.json).

## Examples folder

| File | What |
|---|---|
| [`examples/curl-snippets.sh`](./examples/curl-snippets.sh) | Bash snippets for public + Bearer endpoints |
| [`examples/python-x402-client.py`](./examples/python-x402-client.py) | Python EIP-3009 signing + retry for x402 endpoints |
| [`examples/typescript-mcp-client.ts`](./examples/typescript-mcp-client.ts) | Connect to MCP server, list 44 tools, call one |
| [`examples/claude-desktop-config.json`](./examples/claude-desktop-config.json) | Drop-in config for Claude Desktop / Cursor |

## Discovery files (machine-readable)

For AI tooling that auto-discovers APIs:

- [`/openapi.json`](https://tradingstrategies.work/openapi.json) — full OpenAPI 3.1 spec, ~70 paths, `x-x402` extension on agent endpoints
- [`/skill.md`](https://tradingstrategies.work/skill.md) — this skill (canonical, kept in sync with this repo)
- [`/llms.txt`](https://tradingstrategies.work/llms.txt) — LLM-friendly summary
- [`/.well-known/api.json`](https://tradingstrategies.work/.well-known/api.json) — cross-tool discovery hub
- [`/.well-known/x402`](https://tradingstrategies.work/.well-known/x402) — Bazaar-v2 descriptor of paid endpoints (alias `.json`)
- [`/.well-known/ai-plugin.json`](https://tradingstrategies.work/.well-known/ai-plugin.json) — OpenAI-style plugin manifest

## Pricing

- **Free** — public endpoints + Free Bearer tier (30 req/h, 200/d)
- **API Pro €9,99/mo** — 300 req/h, 3k/d, backtest triggers, larger windows
- **API Power €29,99/mo** — 2000 req/h, 30k/d, universe-backtests (50 pairs)
- **x402 pay-per-call** — $0.01-$0.50 USDC per call, no subscription

One subscription covers both REST and MCP channels. Pricing is reviewed
quarterly against agent-economy benchmarks ([changelog](https://tradingstrategies.work/api)).

## License

MIT (this skill package). The Backtesting Arena API itself follows the
[Terms](https://tradingstrategies.work/agb).

## Operator

Solo-built crypto strategy backtesting platform from Germany/Austria. Public
since 2026. Educational and research focus, not signal-selling.

Contact: info@tradingstrategies.work · Issues: [github.com/Schoasch/skill-backtesting-arena/issues](https://github.com/Schoasch/skill-backtesting-arena/issues)
