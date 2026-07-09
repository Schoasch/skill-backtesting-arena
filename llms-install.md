# Installing the Backtesting Arena MCP Server

This guide lets an AI coding agent (e.g. Cline) install and verify the
**Backtesting Arena** MCP server with no build step.

> **Important — this is a remote, hosted server.** There is nothing to clone,
> `npm install`, or `uvx`. The server runs at `https://tradingstrategies.work/api/mcp`
> (Streamable HTTP). You "install" it by adding a small entry to your MCP client
> config that points at that URL with an auth header. Free tier, no credit card.

---

## Step 1 — Get a free Bearer key (30 seconds)

MCP tool calls require a Bearer key. The Free tier is enough to try every tool
(Pro/Power tools return a structured upgrade hint instead of failing).

1. Open <https://tradingstrategies.work/dashboard/account/api-keys>.
2. Register (email only, no credit card) and create an API key.
3. Copy the key — it looks like `sk-arena-…`.

*(Alternative: in claude.ai you can add this server as a one-click OAuth
connector instead of a Bearer key. For Cline / Cursor / Claude Desktop, use the
Bearer key below.)*

---

## Step 2 — Add the server to your MCP config

### Option A — HTTP transport (recommended)

Add this entry to your client's MCP settings file (for Cline:
`cline_mcp_settings.json`; for Claude Desktop: `claude_desktop_config.json`),
under `mcpServers`. Replace `sk-arena-…` with your key from Step 1:

```json
{
  "mcpServers": {
    "backtesting-arena": {
      "url": "https://tradingstrategies.work/api/mcp",
      "headers": { "Authorization": "Bearer sk-arena-…" }
    }
  }
}
```

### Option B — stdio transport (for clients without HTTP support)

If your client only supports stdio, bridge to the remote server with
[`mcp-remote`](https://www.npmjs.com/package/mcp-remote) (needs Node.js):

```json
{
  "mcpServers": {
    "backtesting-arena": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://tradingstrategies.work/api/mcp",
        "--header", "Authorization:Bearer sk-arena-…"
      ]
    }
  }
}
```

Save the file and restart / reload the MCP client so it picks up the new server.

---

## Step 3 — Verify the installation

After the client reconnects, confirm the server is live:

1. **List tools** — the server should expose **69 tools** (names prefixed
   `arena_…`, plus `validate_strategy`). Discovery (`initialize` / `tools/list`)
   works even unauthenticated, so the catalog appears immediately.
2. **Call a free tool** — e.g. `arena_get_pulse` (the Arena Pulse market
   heat-score 0–100) or `arena_get_cycle` (point-in-time Bitcoin cycle score).
   A valid Bearer key returns a JSON payload; a Pro/Power-only tool on the Free
   tier returns a structured tool-error with an `upgrade_url` (not a hard fail).

If tools list but calls return `401`, re-check the `Authorization` header value.

---

## What you get

- **69 MCP tools**: point-in-time Bitcoin cycle scoring (plus per-coin cycle for
  ETH & SOL), macro-regime composites, Edge-Library filter effects, 21 on-chain
  BRK series (since 2009), altcoin screener, sentiment, "buy now or wait?"
  decision-math, conditional historical-analog base rates, on-demand backtests,
  and live subscriptions.
- Versioned, explainable Knowledge Objects + ontology; DSR / multiple-testing-
  corrected, look-ahead-aware backtest validation.

Core outputs are **not reproducible from public OHLCV/market-data APIs or web
search** — evidence, distributions and base rates, never buy/sell
recommendations.

- **Homepage:** <https://tradingstrategies.work/api>
- **Docs:** <https://tradingstrategies.work/api-docs>
- **OpenAPI 3.1:** <https://tradingstrategies.work/openapi.json>
- **Capability descriptor:** [`skill.md`](./skill.md)
