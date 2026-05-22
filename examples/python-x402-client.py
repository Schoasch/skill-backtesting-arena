"""
Backtesting Arena — x402 pay-per-call client (Python).

Demonstrates the EIP-3009 TransferAuthorization signing flow for x402-paid
endpoints. Pattern:

    1. Call endpoint → server returns HTTP 402 + payment-required JSON
       (network, asset/contract, amount, payTo, validity window)
    2. Build & sign an EIP-712 TransferAuthorization (USDC)
    3. Retry with `X-PAYMENT` header containing base64(signed-auth)
    4. Server verifies, settles via facilitator, returns 200 + data
       + `X-PAYMENT-RESPONSE` receipt header

Prerequisites (uv / pip):

    pip install web3 requests eth-account

Env:

    EVM_PRIVATE_KEY   - hex private key for the EOA paying in USDC.
                        Fund it with Base-USDC first (mainnet or sepolia).
    AGENT_NETWORK     - 'mainnet' (default) | 'sepolia'

Disclaimer: example only — handle your private key responsibly. Production
agents should use a dedicated hot wallet with strict daily caps and rotate
keys.
"""
import base64
import json
import os
import time
import uuid
from dataclasses import dataclass

import requests
from eth_account import Account
from eth_account.messages import encode_typed_data


BASE = "https://tradingstrategies.work"

USDC_BY_NETWORK = {
    "mainnet": {
        "chain_id":  8453,
        "address":   "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "name":      "USDC",
        "version":   "2",
    },
    "sepolia": {
        "chain_id":  84532,
        "address":   "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        "name":      "USDC",
        "version":   "2",
    },
}


@dataclass
class PaymentRequirement:
    scheme: str
    network: str          # CAIP-2, e.g. 'eip155:8453'
    pay_to: str
    asset: str            # contract address
    amount: str           # atomic units (string!)
    max_timeout_seconds: int
    extra: dict


def parse_payment_required(resp: requests.Response) -> PaymentRequirement:
    """Extract first accepts[] entry from a 402 response body."""
    if resp.status_code != 402:
        raise RuntimeError(f"Expected 402, got {resp.status_code}: {resp.text[:200]}")
    body = resp.json()
    if "accepts" not in body or not body["accepts"]:
        raise RuntimeError(f"402 body missing accepts[]: {body}")
    a = body["accepts"][0]
    return PaymentRequirement(
        scheme              = a["scheme"],
        network             = a["network"],
        pay_to              = a["payTo"],
        asset               = a["asset"],
        amount              = str(a["amount"]),
        max_timeout_seconds = int(a.get("maxTimeoutSeconds", 60)),
        extra               = a.get("extra", {}),
    )


def sign_payment(req: PaymentRequirement, private_key: str, network_short: str) -> dict:
    """Sign an EIP-3009 TransferWithAuthorization. Returns the payload Stripe
    Backtesting Arena's facilitator can settle on-chain.
    """
    usdc = USDC_BY_NETWORK[network_short]
    if int(req.network.split(":")[-1]) != usdc["chain_id"]:
        raise RuntimeError(
            f"Network mismatch: server={req.network}, configured={network_short} (chain {usdc['chain_id']})"
        )
    if req.asset.lower() != usdc["address"].lower():
        raise RuntimeError(f"Asset mismatch: server={req.asset}, expected={usdc['address']}")

    account = Account.from_key(private_key)
    valid_after  = int(time.time()) - 5
    valid_before = int(time.time()) + req.max_timeout_seconds
    # nonce: random 32 bytes hex
    nonce = "0x" + uuid.uuid4().hex + uuid.uuid4().hex   # 32 bytes

    domain = {
        "name":              usdc["name"],
        "version":           usdc["version"],
        "chainId":           usdc["chain_id"],
        "verifyingContract": usdc["address"],
    }
    types = {
        "TransferWithAuthorization": [
            {"name": "from",        "type": "address"},
            {"name": "to",          "type": "address"},
            {"name": "value",       "type": "uint256"},
            {"name": "validAfter",  "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce",       "type": "bytes32"},
        ],
    }
    message = {
        "from":        account.address,
        "to":          req.pay_to,
        "value":       int(req.amount),
        "validAfter":  valid_after,
        "validBefore": valid_before,
        "nonce":       nonce,
    }
    typed = {"types": types, "primaryType": "TransferWithAuthorization",
             "domain": domain, "message": message}

    signed = Account.sign_message(encode_typed_data(full_message=typed), private_key=private_key)

    payload = {
        "x402Version": 2,
        "scheme":      req.scheme,
        "network":     req.network,
        "payload": {
            "signature":     signed.signature.hex(),
            "authorization": {
                "from":        account.address,
                "to":          req.pay_to,
                "value":       req.amount,
                "validAfter":  str(valid_after),
                "validBefore": str(valid_before),
                "nonce":       nonce,
            },
        },
    }
    return payload


def x402_get(path: str, private_key: str, network_short: str = "mainnet", idempotency_key: str | None = None) -> requests.Response:
    """Generic GET that handles the 402 → sign → retry dance."""
    url     = f"{BASE}{path}"
    headers = {}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    first = requests.get(url, headers=headers, timeout=30)
    if first.status_code == 200:
        return first   # cached / promo / replay — no payment needed

    req = parse_payment_required(first)
    payload = sign_payment(req, private_key, network_short)
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()

    headers["X-PAYMENT"] = encoded
    return requests.get(url, headers=headers, timeout=60)


def x402_post(path: str, body: dict, private_key: str, network_short: str = "mainnet", idempotency_key: str | None = None) -> requests.Response:
    """POST variant with optional idempotency."""
    url     = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    first = requests.post(url, json=body, headers=headers, timeout=30)
    if first.status_code == 200:
        return first

    req = parse_payment_required(first)
    payload = sign_payment(req, private_key, network_short)
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()

    headers["X-PAYMENT"] = encoded
    return requests.post(url, json=body, headers=headers, timeout=60)


# ─── Example usage ────────────────────────────────────────────────────────

if __name__ == "__main__":
    pk      = os.environ.get("EVM_PRIVATE_KEY")
    network = os.environ.get("AGENT_NETWORK", "mainnet")
    if not pk:
        raise SystemExit("Set EVM_PRIVATE_KEY (hex) — and fund the wallet with Base-USDC.")

    print("=== GET /api/v1/agent/btc-cycle/latest ($0.01) ===")
    r = x402_get("/api/v1/agent/btc-cycle/latest", pk, network)
    print("status:", r.status_code)
    print("body:",   r.json())
    print("receipt:", r.headers.get("X-PAYMENT-RESPONSE", "—")[:80], "...")

    print("\n=== POST /api/v1/agent/backtests/run ($0.10) — with idempotency ===")
    key = str(uuid.uuid4())
    body = {
        "strategy":  "rsi_sma",
        "pair":      "BTCUSDT",
        "asset_type":"crypto",
        "interval":  "1d",
        "date_from": "2024-01-01",
        "date_to":   "2024-12-31",
    }
    r = x402_post("/api/v1/agent/backtests/run", body, pk, network, idempotency_key=key)
    print("status:", r.status_code)
    if r.status_code == 200:
        d = r.json()
        print(f"cagr={d.get('cagr')}, win_rate={d.get('win_rate')}, trades={d.get('trades_count')}")

    print("\n=== Same idempotency-key → cached replay (no second payment) ===")
    r2 = x402_post("/api/v1/agent/backtests/run", body, pk, network, idempotency_key=key)
    print("status:", r2.status_code, "replayed:", r2.headers.get("X-Idempotent-Replayed", "?"))
