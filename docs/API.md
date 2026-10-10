# NURVEX HTTP API

All endpoints return JSON. Base URL: `http://HOST:PORT`.

## GET /status

Returns current chain status.

\`\`\`bash
curl http://127.0.0.1:8338/status
\`\`\`

Response:
\`\`\`json
{
  "project": "NURVEX",
  "protocol": "NURVEX-TESTNET-0.3",
  "height": 42,
  "issued": "360",
  "maximum_supply": "18000000",
  "chain_valid": true,
  "validation": "OK",
  "production_ready": false
}
\`\`\`

## GET /health

Alias for `/status`.

## GET /peers

Returns list of known peer URLs.

\`\`\`bash
curl http://127.0.0.1:8338/peers
\`\`\`

Response:
\`\`\`json
{
  "peers": [
    "http://192.168.1.10:8338",
    "http://192.168.1.11:8338"
  ]
}
\`\`\`

## GET /chain

Returns the full chain as a JSON array of blocks.

\`\`\`bash
curl http://127.0.0.1:8338/chain
\`\`\`

## GET /blocks

Paginated block list.

Query parameters:
- `from` (int, default 0): starting height.
- `limit` (int, default 10, max 100): number of blocks.

\`\`\`bash
curl "http://127.0.0.1:8338/blocks?from=0&limit=5"
\`\`\`

Response:
\`\`\`json
{
  "ok": true,
  "total": 43,
  "from": 0,
  "limit": 5,
  "returned": 5,
  "blocks": [ ... ]
}
\`\`\`

## GET /mempool

Returns pending transactions.

\`\`\`bash
curl http://127.0.0.1:8338/mempool
\`\`\`

Response (array):
\`\`\`json
[
  {
    "type": "transfer",
    "sender": "nvrx1...",
    "recipient": "nvrx1...",
    "amount": 100000000,
    "nonce": 1,
    "public_key": "...",
    "signature": "..."
  }
]
\`\`\`

## GET /tx/{txid}

Look up a transaction by its ID (SHA-256 hex).

\`\`\`bash
curl http://127.0.0.1:8338/tx/054b6cc0...
\`\`\`

Response (confirmed):
\`\`\`json
{
  "ok": true,
  "status": "confirmed",
  "txid": "054b6cc0...",
  "block_height": 12,
  "transaction": { ... }
}
\`\`\`

Response (pending):
\`\`\`json
{
  "ok": true,
  "status": "pending",
  "txid": "054b6cc0...",
  "transaction": { ... }
}
\`\`\`

Response (not found): HTTP 404
\`\`\`json
{"ok": false, "error": "Transaction not found"}
\`\`\`

## POST /transaction

Relay a signed transaction. Used internally by peers.

Body:
\`\`\`json
{
  "type": "transfer",
  "sender": "nvrx1...",
  "recipient": "nvrx1...",
  "amount": 100000000,
  "nonce": 1,
  "public_key": "...",
  "signature": "..."
}
\`\`\`

Response:
\`\`\`json
{"ok": true}
\`\`\`

## POST /block

Relay a mined block. Used internally by peers.

Body: a full block JSON object.

Response:
\`\`\`json
{"ok": true}
\`\`\`

## POST /peer

Add a peer to the local peers list.

Body:
\`\`\`json
{"url": "http://192.168.1.10:8338"}
\`\`\`

Response (added):
\`\`\`json
{"ok": true, "status": "added", "url": "http://192.168.1.10:8338", "total_peers": 3}
\`\`\`

Response (already known):
\`\`\`json
{"ok": true, "status": "already_known", "url": "http://192.168.1.10:8338"}
\`\`\`

Response (invalid URL): HTTP 400
\`\`\`json
{"ok": false, "error": "Invalid peer URL"}
\`\`\`

## GET /faucet

Faucet status. Available only if the faucet has been initialized.

\`\`\`bash
curl http://127.0.0.1:8338/faucet
\`\`\`

Response:
\`\`\`json
{
  "ok": true,
  "address": "nvrx1746277cd3e4a7a91cc09a02e3def9c3e793e9071",
  "balance": "42.85714285",
  "available": "32.85714285",
  "pending_out": "10",
  "amount_per_request": "10",
  "cooldown_seconds": 3600
}
\`\`\`

## POST /faucet

Request NVRX from the faucet.

Body:
\`\`\`json
{"address": "nvrx1..."}
\`\`\`

Response (success):
\`\`\`json
{
  "ok": true,
  "txid": "054b6cc0...",
  "amount": "10",
  "recipient": "nvrx1..."
}
\`\`\`

Response (cooldown): HTTP 400
\`\`\`json
{
  "ok": false,
  "error": "Cooldown active",
  "wait_seconds": 3567
}
\`\`\`

Response (empty faucet): HTTP 400
\`\`\`json
{"ok": false, "error": "Faucet empty"}
\`\`\`

## Error Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request (invalid params, business logic error) |
| 404 | Not found |
| 413 | Payload too large |
| 500 | Internal error |
