/**
 * Backtesting Arena — MCP client example (TypeScript).
 *
 * Connects to the Backtesting Arena MCP server via Streamable HTTP transport,
 * lists all ~44 tools, and calls one. Same Bearer API key as REST — one
 * subscription covers both channels.
 *
 * Install:
 *
 *   npm i @modelcontextprotocol/sdk
 *   # or:
 *   pnpm add @modelcontextprotocol/sdk
 *
 * Env:
 *   ARENA_API_KEY=sk-arena-...
 *
 * Run:
 *   npx tsx examples/typescript-mcp-client.ts
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'

const API_KEY = process.env.ARENA_API_KEY
if (!API_KEY) {
  console.error('Set ARENA_API_KEY (sk-arena-...). Get one at https://tradingstrategies.work/dashboard/account/api-keys')
  process.exit(1)
}

async function main() {
  const transport = new StreamableHTTPClientTransport(
    new URL('https://tradingstrategies.work/api/mcp'),
    {
      requestInit: {
        headers: { Authorization: `Bearer ${API_KEY}` },
      },
    },
  )

  const client = new Client({ name: 'arena-mcp-demo', version: '0.1.0' }, { capabilities: {} })
  await client.connect(transport)

  // ── 1. List all tools (categories: snapshots, history, onchain, catalog,
  //         insights, backtests-read, triggers, reports, live-subscriptions) ──
  const tools = await client.listTools()
  console.log(`Connected — ${tools.tools.length} tools available:`)
  for (const t of tools.tools.slice(0, 10)) {
    console.log(`  - ${t.name.padEnd(40)} ${t.description?.slice(0, 60) ?? ''}`)
  }
  console.log(`  ... ${tools.tools.length - 10} more`)

  // ── 2. Call a snapshot tool ──
  console.log('\n→ arena_get_arena_pulse_today')
  const pulse = await client.callTool({ name: 'arena_get_arena_pulse_today', arguments: {} })
  console.log(JSON.stringify(pulse.content, null, 2).slice(0, 400))

  // ── 3. Call a Pro-tier tool (will return tier_insufficient error if Free) ──
  console.log('\n→ arena_run_backtest (Pro-tier)')
  try {
    const bt = await client.callTool({
      name: 'arena_run_backtest',
      arguments: {
        strategy:  'rsi_sma',
        pair:      'BTCUSDT',
        asset_type:'crypto',
        interval:  '1d',
        date_from: '2024-01-01',
        date_to:   '2024-06-30',
      },
    })
    const text = bt.content?.[0]?.type === 'text' ? bt.content[0].text : JSON.stringify(bt.content)
    console.log(text.slice(0, 600))
  } catch (e: unknown) {
    // Tier-mismatch comes back as a structured tool-error with upgrade_url.
    console.log('  →', e instanceof Error ? e.message : e)
  }

  await client.close()
}

main().catch(e => { console.error(e); process.exit(1) })
