# NURVEX Testnet — Complete Blockchain Project FOR SALE

**Price:** $6,000 USD (OBO — quick sale possible)

**Type:** Complete source code + working testnet + documentation

**Contact:** GitHub issues or X DM

---

## Executive Summary

NURVEX is a fully functional blockchain testnet written in pure Python.
It is complete, documented, tested, and running live on the internet.

If you are looking for a ready-to-build-upon blockchain foundation
without spending 3-6 months and $50,000+ on initial development,
this is it.

---

## What You Get

### Source Code
- `nurvex_node.py` — 800 lines of clean Python
- MIT licensed (use it however you want)
- No external dependencies except `cryptography`

### Working Testnet
- 3 nodes running live
- Public URL accessible now
- Faucet distributing 10 NVRX/hour

### Web Interfaces
- **Block Explorer** at `/explorer` — dark mode, live stats
- **Web Wallet** at `/wallet` — browser-based, Ed25519 signing

### REST API
12 endpoints:
- `/status`, `/health`, `/peers`, `/chain`
- `/blocks`, `/mempool`, `/tx/{id}`, `/faucet`
- POST `/transaction`, `/block`, `/peer`, `/faucet`

### Testing & CI
- 13 pytest tests (all passing)
- GitHub Actions: Python 3.10, 3.11, 3.12
- Automated on every push

### Documentation (8 files, ~1300 lines)
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/SETUP.md`
- `docs/API.md`
- `docs/MINING.md`
- `docs/DEPLOYMENT.md`
- `docs/ROADMAP.md`
- `BOOTSTRAP.md`

---

## Technical Features

### Consensus
- Proof-of-Work with 5-8 leading zeros
- Dynamic difficulty (adjusts every 10 blocks, target 60s/block)
- Longest-chain rule
- Cumulative-work fork resolution
- Timestamp tiebreaker for equal-work forks

### Cryptography
- Ed25519 transaction signatures
- SHA-256 block hashing
- Timestamp validation (±2h future, 10y past)

### Network
- HTTP peer-to-peer gossip
- Automatic peer discovery
- Block & transaction propagation
- No central server

### Security
- IP-based rate limiting (60/min tx, 10/min peer, 5/min faucet)
- Sequential nonce validation
- Double-spend prevention
- Mempool validation

### Economics
- 18,000,000 NVRX max supply
- 8.57142857 NVRX initial reward
- Halving every 1,050,000 blocks
- Faucet: 10 NVRX per hour per address

---

## What Is NOT Included

To be transparent — this is NOT:

- A mainnet with real-value tokens
- A project with users or revenue
- An audited codebase
- A registered company or legal entity
- A domain name (URL is temporary, free tier)

Buyer is responsible for:
- Legal compliance in their jurisdiction
- Security audit before mainnet
- Marketing and user acquisition
- Domain registration
- Any future liabilities

---

## Why This Is a Good Deal

**Cost to build from scratch:**
- Senior blockchain developer: $50,000 - $150,000
- Web UIs (Explorer + Wallet): $5,000 - $15,000
- Documentation: $3,000 - $8,000
- Testing & CI: $2,000 - $5,000
- **Total: $60,000 - $180,000+**

**Your price: $6,000**

That is **3-10% of the cost to build it**.

---

## Ideal Buyer

This project is ideal for:

- **A blockchain developer** wanting a Python reference implementation
- **A startup** needing a testnet foundation to build on
- **A university / research group** studying consensus mechanisms
- **A company** wanting to fork it for internal use (supply chain, voting, etc.)
- **A portfolio buyer** who wants a completed blockchain project

---

## How to Inspect Before Buying

1. **Visit GitHub:** https://github.com/7399795590/nurvex
2. **Read the docs:** `docs/` folder
3. **See it live:** `/explorer` and `/wallet` on any running node
4. **Check the code:** `nurvex_node.py` (~800 lines)
5. **Run the tests:** `python -m pytest tests/ -v`

Every claim in this listing is verifiable.

---

## Transfer Process

Upon payment:

1. You receive the GitHub repository (transfer or fork)
2. Full commit history included (30+ commits)
3. All documentation included
4. Optional: 1 hour of handover call / chat
5. Optional: Bootstrap URL updated to yours

Payment methods: PayPal, USDT, Bank Transfer.

---

## Contact

Open an issue at:
https://github.com/7399795590/nurvex/issues

Or DM on X.

Serious inquiries only.

---

**Reminder:** This is a testnet prototype. Any production use requires
additional work (audit, legal, infrastructure). Buyer accepts all risks.
