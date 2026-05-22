# Backtesting Arena Skill

**Description:** Programmatic access to crypto market cycle scoring, on-chain
indicators, and aggregated sentiment data. Built for AI agents and LLMs that
need structured, reproducible Bitcoin/crypto market context.

> Canonical source: https://tradingstrategies.work/skill.md — this repo file
> is kept in sync. If you spot a drift, file an issue or refer to the live one.

## Capabilities

- Get the daily **Arena Pulse heat score** (0-100) — multi-dimensional aggregate
  from 8 indicators (Bullmarket gauge, Fear & Greed, MVRV Z-score, 200-WMA
  distance, Mayer Multiple, Altcoin Season, Funding rates, Hash Ribbons).
  Inspired by Fear & Greed but multidimensional.
- Get the **BTC cycle phase** (accumulation / recovery / expansion / distribution
  / overheated) with all 10 component indicators (Pi-Cycle Top/Bottom, Mayer,
  Weekly RSI, MA200W, Halving position, Fear & Greed, BTC Dominance, Mining
  Difficulty, Macro Liquidity).
- Read the **alternative.me Fear & Greed Index** via a DSGVO-compliant
  server-side proxy (your client never directly hits alternative.me).
- Read the **historical series** of Arena Pulse and BTC cycle scores for
  trend analysis and regime detection.
- Trigger **on-demand backtests** (single asset, grid bot, compare 2-5
  strategies, universe up to 50 pairs) via authenticated REST/MCP or x402.

## Use Cases

- Trading bots that need market regime context before placing orders
- Research agents that compare current market state against historical analogues
- Newsletter / content generators that need daily market sentiment data
- Risk-management agents that throttle exposure based on cycle phase
- Backtesting frameworks that want a reproducible "as-of-date" market context

## Authentication

**Three options:**

1. **Public endpoints below** — no auth, fair-use rate limit (~60 req/h per IP) via server-side caching.
2. **Authenticated REST + MCP** — Bearer-token (Free tier available, no credit card). Higher quotas, full surface. Same key works for both channels.
3. **x402 Pay-per-Call** — autonomous agents pay per call in USDC on Base. No account, no API key. 17 endpoints from $0.01 (snapshots) to $0.50 (universe-express). HTTP 402 + EIP-3009 wallet signature.

## Endpoints — Public (no authentication)

| URL | What | Cache |
|---|---|---|
| `https://tradingstrategies.work/api/arena-pulse/today` | Today's score + 8 components + verdict | 5 min |
| `https://tradingstrategies.work/api/arena-pulse/history?days=N` | Last N days, default 30 | 1 h |
| `https://tradingstrategies.work/api/btc-cycle` | Latest cycle phase + 10 indicators | 1 h |
| `https://tradingstrategies.work/api/btc-cycle?days=N` | + historical chart data | 1 h |
| `https://tradingstrategies.work/api/fear-greed` | Full F&G history (JSON) | 1 h |

## Endpoints — Authenticated `/api/v1/*` (Bearer key, Free tier available)

| URL | What | Tier |
|---|---|---|
| `GET /api/v1/strategies?asset_class=&plan=&lang=` | Strategy catalog — 19 strategies with key, name, tagline, plan, asset-class support, primary indicators. **Call before `/backtests/run` to discover valid strategy keys.** | Free |
| `GET /api/v1/universes` | Asset-universe catalog (7 universes: crypto-top-10/50/100/250, stocks-top-50, etf-top-50, commodities). Used by `/reports/quote` + `/backtests/universe`. | Free |
| `GET /api/v1/universes/{id}` | Universe detail incl. full pair list | Free |
| `GET /api/v1/signals/{strategy}/{pair}/{timeframe}` | Current live signal state (BUY/SELL/no-signal) — daily cron-computed. Optional filter + trailing-stop state. | Free |
| `GET /api/v1/onchain/series` | Catalog of 21 BRK on-chain series (full history from 2009) | Free |
| `GET /api/v1/onchain/series/{id}/latest` | Latest daily value (e.g. mvrv, realized_price, sth_sopr_24h, puell_multiple, addrs_over_1k_btc_supply, hash_rate, difficulty) | Free |
| `GET /api/v1/onchain/series/{id}/history?from=&to=&limit=` | Time series, Free 30d / Pro 365d / Power unlimited | Free+ |
| `GET /api/v1/data-quality/drift?days=90` | BRK vs bgeometrics drift log — transparency tool for data reliability | Free |
| `GET /api/v1/charts/{slug}/latest` | Tier-1 chart snapshot (mvrv-zscore, nupl, sopr, mayer, pi-cycle, rainbow, hash-ribbons, etc.) | Free |
| `GET /api/v1/insights/...` | Strategy insights, sentiment, winners | Free / Pro+ |
| `POST /api/v1/backtests/run` | Trigger a single-asset backtest. Optional `Idempotency-Key` header. | Pro |
| `POST /api/v1/backtests/universe` | **Async** — backtest one strategy on up to 50 pairs. Returns `job_id` + `poll_url`; client polls `/api/v1/jobs/{job_id}` until done. Quota: Pro 5/d, Power 50/d. Optional `Idempotency-Key`. | Pro |
| `GET /api/v1/jobs/{job_id}` | Poll async job status (status, progress_pct, result when done) | Free |
| `POST /api/v1/backtests/grid` | Trigger a grid-bot backtest | Free (BTC/ETH) / Pro+ |

Get a Free-tier API key at [/dashboard/account/api-keys](https://tradingstrategies.work/dashboard/account/api-keys). See the full surface at [openapi.json](https://tradingstrategies.work/openapi.json).

## Endpoints — Agent x402 Pay-per-Call (no account, USDC on Base)

For autonomous AI agents that want to consume data without setting up an account, sign a USDC payment with any EVM wallet (Rabby/MetaMask/Ledger). Server returns HTTP 402 + payment instructions; agent signs EIP-3009 TransferAuthorization, retries with `X-PAYMENT` header. Settled gas-free via facilitator. Network: Base (mainnet eip155:8453, Sepolia eip155:84532 for testing).

| URL | What | Price |
|---|---|---|
| `GET /api/v1/agent/arena-pulse/today`         | Daily Arena Pulse score    | $0.01 |
| `GET /api/v1/agent/btc-cycle/latest`          | BTC Cycle snapshot         | $0.01 |
| `GET /api/v1/agent/altcoin-season/latest`     | Altcoin Season Indicator   | $0.01 |
| `GET /api/v1/agent/fear-greed/today`          | F&G Index (today)          | $0.01 |
| `GET /api/v1/agent/bullmarket-ampel/latest`   | Bullmarket Ampel state     | $0.01 |
| `GET /api/v1/agent/funding-rate/latest`       | BTC perpetual funding      | $0.01 |
| `GET /api/v1/agent/hash-ribbons/latest`       | Hash Ribbons state         | $0.01 |
| `GET /api/v1/agent/mayer-multiple/latest`     | Mayer Multiple             | $0.01 |
| `GET /api/v1/agent/insights/strategies`       | Strategy Insights matrix   | $0.05 |
| `GET /api/v1/agent/insights/strategy-filters` | Strategy Filter Insights   | $0.05 |
| `GET /api/v1/agent/insights/volatility`       | Volatility Insights heatmap| $0.05 |
| `GET /api/v1/agent/insights/sentiment`        | Sentiment Dashboard        | $0.05 |
| `GET /api/v1/agent/insights/winners`          | Backtest Winners list      | $0.05 |
| `POST /api/v1/agent/backtests/run`            | Single-asset backtest      | $0.10 |
| `POST /api/v1/agent/backtests/grid`           | Grid-bot backtest          | $0.10 |
| `POST /api/v1/agent/backtests/compare`        | Compare 2-5 strategies     | $0.30 |
| `POST /api/v1/agent/backtests/universe`       | Universe-Express, max 10 pairs inline | $0.50 |

POST endpoints accept an optional `Idempotency-Key` header (UUID-like, 8-128
chars). Retries with the same key + body return the cached response and do
**not** trigger a second payment.

**Discovery for autonomous agents:** the same list (with USDC contract address per network, payTo wallet, facilitator hint) is available as a machine-readable descriptor at `/.well-known/x402` (alias `/.well-known/x402.json`). Bazaar-v2 shape, CORS `*`, no auth, 1h cache.

## Example Calls

Get today's Arena Pulse score:

```
curl https://tradingstrategies.work/api/arena-pulse/today
```

Response shape (truncated):

```json
{
  "date": "2026-05-15",
  "score": 35,
  "band": "risk-off",
  "label_de": "Risk-Off",
  "label_en": "Risk-Off",
  "verdict_de": "Vorsicht: Macro-Stress aktiv...",
  "verdict_en": "Caution: macro stress active...",
  "components": [
    { "key": "bullmarket_ampel", "rawValue": "Stage 1/5", "earnedPoints": 4, "maxPoints": 20 },
    { "key": "fear_greed", "rawValue": "43/100", "earnedPoints": 6.5, "maxPoints": 15 }
  ],
  "confidence": "8/8"
}
```

Get last 30 days of Arena Pulse for trend analysis:

```
curl 'https://tradingstrategies.work/api/arena-pulse/history?days=30'
```

Get BTC cycle phase:

```
curl https://tradingstrategies.work/api/btc-cycle
```

## Methodology Links

- [Arena Pulse explanation](https://tradingstrategies.work/dashboard/arena-pulse) — full breakdown of all 8 components, score bands, and update process
- [Bitcoin Charts gallery](https://tradingstrategies.work/dashboard/bitcoin/charts) — visual reference for all on-chain indicators (800-word methodology each)
- [Open-source score logic](https://tradingstrategies.work/dashboard/arena-pulse#methodology) — the entire scoring is pure-function code, reproducible from any historical input

## What this Skill is NOT

- Not investment advice. All data is for informational purposes only.
- Not a real-time market data feed. Daily snapshots, not tick-level data.
- Not a trade-execution API. We provide context, not order routing.

## Contact

- Documentation: https://tradingstrategies.work/dashboard/arena-pulse
- General: info@tradingstrategies.work
- All three channels (REST, MCP, x402) are live; contact for partnership / volume use cases

## Operator

Solo-built crypto strategy backtesting platform from Germany/Austria. Public
since 2026. Educational and research focus, not signal-selling. Source of all
data is documented and reproducible.
