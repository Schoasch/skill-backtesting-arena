# Backtesting Arena Skill

**Description:** Battle-tested market intelligence — programmatic access to
crypto market cycle scoring, on-chain indicators, and aggregated sentiment
data. Every claim backtested, versioned, and explainable; evidence and base
rates, never financial advice. Built for AI agents and LLMs that need
structured, reproducible Bitcoin/crypto market context.

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
- Get a **per-coin cycle read for ETH or SOL** — the transferable price-derived
  indicators (Mayer, Weekly RSI, 200-week-MA distance) with renormalized weights;
  BTC-native indicators are returned as `not_applicable` rather than faked.
- Get **reproducible BTC support/resistance key levels** — swing-fractal clusters
  with touch-count, band and distance from spot (no eyeballing a fractal chart).
- Read the **alternative.me Fear & Greed Index** via a DSGVO-compliant
  server-side proxy (your client never directly hits alternative.me).
- Read the **historical series** of Arena Pulse and BTC cycle scores for
  trend analysis and regime detection.

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
3. **x402 Pay-per-Call** — autonomous agents pay per call in USDC on Base. No account, no API key. 26 endpoints from $0.01 (snapshots) to $0.50 (universe-express). HTTP 402 + EIP-3009 wallet signature.

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
| `GET /api/v1/strategies?asset_class=&plan=&lang=` | Strategy catalog — 25 strategies with key, name, tagline, plan, asset-class support, primary indicators. **Call before `/backtests/run` to discover valid strategy keys.** | Free |
| `GET /api/v1/strategy/performance?strategy=&asset=&interval=&ref_strategy=` | **Per-(strategy, asset) performance snapshot** — run_count, avg_cagr, avg_win_rate, avg_drawdown, effective_years, avg_trades + total_trades, arena_score (0-100 composite robustness — honest Sharpe-replacement) + vs_buy_hold (beats + cagr_delta). Quick lookup for "How does X work on Y?". | Free |
| `GET /api/v1/strategy/filter-effect?strategy=&asset=&interval=` | **Per-(strategy, asset) filter-effect snapshot** — baseline + per-variant cagr/drawdown/win-rate deltas + best_by_cagr + not_applicable_filters (e.g. altcoin_season excluded on BTC). Real-data aggregation, no theoretical permutations. Answers "which filters improve X on Y?". | Free |
| `GET /api/v1/strategy/performance-by-regime?strategy=&asset=&interval=` | **Regime-aware performance** — backtest split by macro regime (sweet_spot / late_cycle_warning / crisis / recovery, classified at each trade's entry date) + a recommendation for the CURRENT live regime. Each bucket: trades, win_rate, avg_pnl_pct, reward_risk_ratio (per-trade, honest — not annualized Sharpe), share_of_time_pct, rating. Answers **"should I trade X now?"**. | Free |
| `GET /api/v1/universes` | Asset-universe catalog (7 universes: crypto-top-10/50/100/250, stocks-top-50, etf-top-50, commodities). Used by `/reports/quote` + `/backtests/universe`. | Free |
| `GET /api/v1/universes/{id}` | Universe detail incl. full pair list | Free |
| `GET /api/v1/signals/{strategy}/{pair}/{timeframe}` | Current live signal state (BUY/SELL/no-signal) — daily cron-computed. Optional filter + trailing-stop state. | Free |
| `GET /api/v1/onchain/series` | Catalog of 21 BRK on-chain series (full history from 2009) | Free |
| `GET /api/v1/onchain/series/{id}/latest` | Latest daily value (e.g. mvrv, realized_price, sth_sopr_24h, puell_multiple, addrs_over_1k_btc_supply, hash_rate, difficulty) | Free |
| `GET /api/v1/onchain/series/{id}/history?from=&to=&limit=` | Time series, Free 30d / Pro 365d / Power unlimited | Free+ |
| `GET /api/v1/data-quality/drift?days=90` | BRK vs bgeometrics drift log — transparency tool for data reliability | Free |
| `GET /api/v1/charts/{slug}/latest` | Chart snapshot — all ~23 slugs (mvrv-zscore, nupl, sopr, mayer, pi-cycle, rainbow, power-law, 200wma-heatmap, hodl-waves, funding-rates, hash-ribbons, fear-greed, etf-treasury-flows, monthly-returns, cycle-overlay, btc-cci-oecd-cli, …); uniform multi-field `{date,...fields}` | Free |
| `GET /api/v1/macro/regime/latest` | Macro Regime snapshot — 18 components in 6 tiers, composite + 2D-matrix quadrant. FRED-sourced. | Free |
| `GET /api/v1/macro/regime/history?days=N` | Macro Regime timeline (composite + quadrant + tier1/tier5 scores), max 365d. | Free |
| `GET /api/v1/onchain/btc-market-structure/latest` | BTC Market Structure (Phantomflow): current trend, fractals + waves counts, last-5 pivot points. | Free |
| `GET /api/v1/alt-cycle/latest?asset=ETH\|SOL` | **ETH/SOL per-coin cycle** — price-derived indicators (Mayer, weekly RSI, 200-week-MA distance) with renormalized weights + score + signal + same-composition percentile block. BTC-native indicators returned as `not_applicable`, not faked. BTC uses `/api/v1/btc-cycle/latest`. MCP: `arena_get_cycle` with `asset=`. | Free |
| `GET /api/v1/onchain/btc-key-levels/latest` | **BTC key levels (S/R clusters)** — reproducible support/resistance zones from clustering the market-structure swing fractals into price bands: touch-count, band, last-touch date, signed distance from spot; resistance above spot, support below, nearest-first. Descriptive only, not a signal. MCP: `arena_get_key_levels`. | Free |
| `GET /api/v1/volatility/phase-snapshots?asset_type=` | **Live Volatility Phases** — ATR phase (low/normal/high/expansion) for 30 tracked assets. Daily 08:00 UTC. Useful for regime-aware strategy selection. | Free |
| `GET /api/v1/volatility/recommendations?pair=&asset_type=` | **Phase-Aware Strategy Recommendations** — top-3 strategies by win-rate in current volatility regime for a given pair. Min 20 trades. Answers "which strategies work best right now?". | Pro |
| `GET /api/v1/gem/scores?limit=N` | **Altcoin Screener** — CoinGecko Top-200 ranked by 3 factor groups: A=Mean-Reversion (RSI Z-Score, SMA200, ATH drawdown), B=Tokenomics (FDV/MC, supply ratio, liquidity), C=Market-Structure (BTC correlation, decoupling, volume trend). Composite 33/33/33. Free ≤10 / Pro ≤50 / Power ≤200. | Free |
| `GET /api/v1/gem/scores/{coinId}` | Altcoin Screener detail for one coin. Pro+ gets `factors_raw` (all 9 raw factor values). | Free |
| `GET /api/v1/gem/scores/{coinId}/history?from=&to=` | Daily composite + group scores for one coin. Max 1 year per call. | Pro |
| `GET /api/v1/gem/validation?top_n=N` | Backtest-Lite: bi-weekly equal-weight basket vs BTC + market average. CAGR, MaxDD, win-rate. `is_anecdote=true` when < 6 periods. | Free |
| `GET /api/v1/edge/reports?market=&[strategy=]&[verdict=]` | **Edge Library** — platform-wide filter-effect analysis: baseline vs. filtered median CAGR + Sharpe delta, DSR (Deflated Sharpe Ratio, Bailey & López de Prado 2014), verdict (helps/neutral/hurts/insufficient_data) for every strategy × market × filter combination. Public pages at `/edge/{market}/{strategy}/{filter}` with JSON-LD. | Free |
| `GET /api/v1/knowledge` | **Knowledge Objects catalog** — discover every published, versioned, explainable Knowledge Object: each type + its subjects (`min_tier`, `api_path`, `seo_slug`, latest `as_of`). Call before `/knowledge/{type}/{subject}` to learn valid pairs instead of guessing. New types appear automatically. MCP: `arena_list_knowledge`. | Free |
| `GET /api/v1/knowledge/{type}/{subject}` | A single versioned, explainable Knowledge Object. **23 types** (call the catalog for the live list), e.g. `market_regime/GLOBAL`, `market_pulse/BTC`, `asset_correlation/BTC`, `market_structure/BTC`, `gem_score/GLOBAL`, `max_pain/BTC`, `etf_flows/GLOBAL`, `strategy_dna/{strategy}`, `market_analogue/BTC` (conditional forward-return distribution), `return_probability/BTC` (unconditional base rate), `volatility_premium/BTC` (VRP + IV rank), `market_briefing/BTC` (composite → net tilt, first with knowledge-graph edges; human page `/market/bitcoin-today`), `strategy_regime_sensitivity/{strategy}` (which macro regime a strategy's edge lives in), `btc_valuation/BTC` (on-chain valuation: MVRV-Z/Puell/…), `supply_distribution/BTC` (whale address-cohort accumulation), `spending_behavior/BTC` (SOPR STH/LTH profit vs loss), `miner_state/BTC` (hash-rate/difficulty/hash-ribbon). Returns payload + explanation (factors + weights + confidence) + provenance + ontology binding + compute version + repro_hash. ONE endpoint covers ALL types. `?as_of=YYYY-MM-DD` optional. MCP: `arena_get_knowledge`. | Free |
| `GET /api/v1/ontology` · `/{term}` | Canonical term definitions (label + definition EN/DE + calculation + unit + source + related) that resolve the `onto:<term>@<version>` references inside Knowledge Objects. `?category=` filters the catalog. MCP: `arena_get_ontology_term`. | Free |
| `GET /api/v1/insights/...` | Strategy insights, sentiment, winners | Free / Pro+ |
| `POST /api/v1/backtests/run` | Trigger a single-asset backtest. Add `?montecarlo=true` for a trade-order bootstrap robustness block (CAGR/drawdown/equity P5–P95 percentile bands + probability of ruin / of beating Buy & Hold; measures sequencing fragility, not a forecast). | Pro |
| `POST /api/v1/validate` | **Validate before you execute** — honest, look-ahead-aware validation of a named strategy (`type=rules`), a BUY/SELL `signal_list` or a `trade_list`. Returns an EVIDENCE verdict (`insufficient_evidence` / `anecdote` / `failed_oos` / `passed_oos`) + metrics/flags/caveats, NOT a buy/sell call. Checks realistic next-bar fills, net-of-cost, out-of-sample split, 30-round-trip sample gate. MCP: `validate_strategy`. | Pro |
| `POST /api/v1/backtests/universe` | **Async** — backtest one strategy on up to 50 pairs. Returns `job_id` + `poll_url`; client polls `/api/v1/jobs/{job_id}` until done. Quota: Pro 5/d, Power 50/d. | Pro |
| `GET /api/v1/jobs/{job_id}` | Poll async job status (status, progress_pct, result when done) | Free |
| `POST /api/v1/backtests/grid` | Trigger a grid-bot backtest | Free (BTC/ETH) / Pro+ |
| MCP `arena_dip_decision` *(MCP only)* | **Buy now or wait for the dip?** Decision-math over the user's own assumptions. `mode=compare`: expected value of Buy-Now vs Wait vs Split + breakeven dip probability. `mode=allocate`: risk-adjusted (Kelly/γ) optimal deploy-now fraction. Scenario numbers + which option wins on EV — NOT a recommendation. Full interactive version at `/analyse/dip-decision`. | Free |
| MCP `arena_get_historical_analog` *(MCP only)* | **What happened historically after the Bitcoin cycle looked like this?** Conditional forward-return distribution for a named preset cycle state (`cycle_bottom_cluster`, `cycle_top_cluster`, `deep_fear`, `euphoria`) — median/IQR/positive-share over N distinct historical episodes (30/90/180/365d), with effective-n, small-n warnings and point-in-time integrity. Accepts `asset=BTC/ETH/SOL`. A distribution, NOT a recommendation. | API Pro |
| MCP `arena_get_key_levels` *(MCP only)* | **Where are the reproducible BTC support/resistance levels?** Swing-fractal clusters from the market-structure snapshot grouped into price zones: touch-count (strength), band, last-touch date, signed distance from spot; resistance above spot, support below, nearest-first. Same data as `/api/v1/onchain/btc-key-levels/latest`. Descriptive only, not a signal. | Free |
| MCP `arena_dip_scenario` *(MCP only)* | **Frame a dip/accumulation thesis WITHOUT a recommendation.** Given an asset (BTC/ETH/SOL), a named cycle-state preset and a thesis horizon: (1) a tranche LADDER anchored to structural marks (200-week MA, support clusters) below spot — not calendar-DCA, not a forecast; (2) the cited historical base rate from the analog engine (with effective-n / small-n); (3) the lump-sum-vs-tranche tradeoff (laddering buys lower timing variance, NOT higher expected value). Requires a mandatory invalidation point. Descriptive only, never a buy/sell signal. | API Pro |

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
| `GET /api/v1/agent/max-pain/latest`           | Deribit BTC Max Pain       | $0.01 |
| `GET /api/v1/agent/macro-regime/today`        | Macro Regime (18 components) | $0.01 |
| `GET /api/v1/agent/btc-market-structure/today` | BTC Market Structure (Phantomflow) | $0.01 |
| `GET /api/v1/agent/alt-cycle/latest?asset=ETH\|SOL` | ETH/SOL per-coin cycle | $0.01 |
| `GET /api/v1/agent/btc-key-levels/latest`     | BTC key levels (S/R clusters) | $0.01 |
| `GET /api/v1/agent/strategy/performance`      | Per-(strategy, asset) performance | $0.01 |
| `GET /api/v1/agent/strategy/filter-effect`    | Per-(strategy, asset) filter effect | $0.01 |
| `GET /api/v1/agent/insights/strategies`       | Strategy Insights matrix   | $0.05 |
| `GET /api/v1/agent/insights/strategy-filters` | Strategy Filter Insights   | $0.05 |
| `GET /api/v1/agent/insights/volatility`       | Volatility Insights heatmap| $0.05 |
| `GET /api/v1/agent/insights/sentiment`        | Sentiment Dashboard        | $0.05 |
| `GET /api/v1/agent/insights/winners`          | Backtest Winners list      | $0.05 |
| `GET /api/v1/agent/strategy/performance-by-regime` | Regime-aware performance + "trade now?" recommendation | $0.05 |
| `POST /api/v1/agent/backtests/run`            | Single-asset backtest      | $0.10 |
| `POST /api/v1/agent/backtests/grid`           | Grid-bot backtest          | $0.10 |
| `POST /api/v1/agent/backtests/compare`        | Compare 2-5 strategies     | $0.30 |
| `POST /api/v1/agent/backtests/universe`       | Universe-Express, max 10 pairs inline | $0.50 |
| `GET /api/v1/agent/gem/scores/today`          | Altcoin Screener Top-10 today | $0.01 |

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
  "verdict_de": "Vorsicht: Crypto-Stress aktiv...",
  "verdict_en": "Caution: crypto-market stress active...",
  "components": [
    { "key": "bullmarket_ampel", "rawValue": "Stage 1/5", "earnedPoints": 4, "maxPoints": 20 },
    { "key": "fear_greed", "rawValue": "43/100", "earnedPoints": 6.5, "maxPoints": 15 },
    ...
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
- Backtest-trigger API is available via authenticated REST/MCP (API Pro tier).
  Pay-per-call backtest-triggers via x402 are planned for a later phase.

## Contact

- Documentation: https://tradingstrategies.work/dashboard/arena-pulse
- General: info@tradingstrategies.work
- All three channels (REST, MCP, x402) are live; contact for partnership / volume use cases

## Operator

Solo-built crypto strategy backtesting platform from Germany/Austria. Public
since 2026. Educational and research focus, not signal-selling. Source of all
data is documented and reproducible.
