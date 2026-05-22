#!/usr/bin/env bash
# Backtesting Arena — curl snippets.
# Covers Public + Bearer REST. x402 pay-per-call lives in python-x402-client.py
# (curl alone cannot sign EIP-3009 payment authorizations).

set -euo pipefail

BASE="https://tradingstrategies.work"

# ─── PUBLIC (no auth) ─────────────────────────────────────────────────────

echo "=== Arena Pulse today ==="
curl -s "$BASE/api/arena-pulse/today" | jq '{date, score, band, label_en}'

echo "=== BTC cycle latest ==="
curl -s "$BASE/api/btc-cycle" | jq '{date, signal, raw_score, z_score, phase: .latest.phase_label_en}'

echo "=== Fear & Greed (last 7 days) ==="
curl -s "$BASE/api/fear-greed" | jq '.data[:7] | map({date, value, classification})'

echo "=== Arena Pulse history (30 days) ==="
curl -s "$BASE/api/arena-pulse/history?days=30" | jq 'length'

# ─── DISCOVERY ────────────────────────────────────────────────────────────

echo "=== OpenAPI spec (full surface) ==="
curl -s "$BASE/openapi.json" | jq '.paths | keys | length'

echo "=== Skill descriptor ==="
curl -s "$BASE/skill.md" | head -10

echo "=== x402 discovery (Bazaar-v2 shape) ==="
curl -s "$BASE/.well-known/x402" | jq '{x402Version, items_count: (.items | length), payee: .payee.network}'

# ─── BEARER (free tier, get a key at /dashboard/account/api-keys) ─────────

if [ -n "${ARENA_API_KEY:-}" ]; then

echo "=== Strategy catalog (call before backtests/run!) ==="
curl -s "$BASE/api/v1/strategies" \
     -H "Authorization: Bearer $ARENA_API_KEY" \
  | jq '.strategies[:3] | map({key, name, plan})'

echo "=== Universes catalog ==="
curl -s "$BASE/api/v1/universes" \
     -H "Authorization: Bearer $ARENA_API_KEY" \
  | jq '.universes | map({id, label, pair_count})'

echo "=== Live signal for rsi_sma BTCUSDT 1d ==="
curl -s "$BASE/api/v1/signals/rsi_sma/BTCUSDT/1d" \
     -H "Authorization: Bearer $ARENA_API_KEY" \
  | jq

echo "=== Trigger a backtest (Pro tier; idempotency-key optional) ==="
curl -s -X POST "$BASE/api/v1/backtests/run" \
  -H "Authorization: Bearer $ARENA_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
        "strategy":  "rsi_sma",
        "pair":      "BTCUSDT",
        "asset_type":"crypto",
        "interval":  "1d",
        "date_from": "2024-01-01",
        "date_to":   "2024-12-31"
      }' \
  | jq '{cagr: .results.cagr, beats_bh: .results.beats_bh, trades_count: .results.trades_count}'

echo "=== Async universe backtest (returns 202 + job_id) ==="
JOB=$(curl -s -X POST "$BASE/api/v1/backtests/universe" \
  -H "Authorization: Bearer $ARENA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "universe_id": "crypto-top-10",
        "strategy":    "rsi_sma",
        "interval":    "1d",
        "date_from":   "2023-01-01"
      }' | jq -r '.job_id')
echo "Job $JOB queued — polling /api/v1/jobs/$JOB..."

else
  echo "Skipping Bearer examples — set ARENA_API_KEY to enable."
fi
