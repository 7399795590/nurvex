# NURVEX Roadmap

This document outlines what has been built, what's in progress, and what's planned.

## Completed ✅

### Core Blockchain
- [x] PoW with dynamic difficulty (5-8 zeros, target 60s/block)
- [x] Ed25519 transaction signatures
- [x] Timestamp validation (±2h)
- [x] Halving (every 1,050,000 blocks)
- [x] Max supply cap (18,000,000 NVRX)
- [x] Mempool with sequential validation
- [x] Nonce management

### Consensus
- [x] Longest-chain rule
- [x] Cumulative work (chain_work)
- [x] Fork resolution
- [x] Timestamp tiebreaker

### Network
- [x] HTTP peer-to-peer gossip
- [x] Peer discovery (automatic)
- [x] Block propagation
- [x] Transaction relay
- [x] Bootstrap via Cloudflare Tunnel
- [x] Bootstrap via localhost.run (permanent URL)

### Services
- [x] Faucet (10 NVRX/hour/address)
- [x] REST API (12 endpoints)
- [x] CLI (13 commands)

### Quality
- [x] 9 pytest tests
- [x] GitHub Actions CI (Python 3.10-3.12)
- [x] MIT License
- [x] Documentation (~1300 lines)

## In Progress 🚧

### Block Explorer
- [ ] Web UI to browse blocks
- [ ] Transaction search
- [ ] Address lookup
- [ ] Real-time updates

### Web Wallet
- [ ] Browser-based wallet
- [ ] Create/import wallets
- [ ] Send/receive NVRX
- [ ] Transaction history

## Planned 📋

### Short Term (1-2 months)
- [ ] More tests (>50)
- [ ] Rate limiting on API
- [ ] Docker support
- [ ] Metrics endpoint (/metrics)
- [ ] Peer authentication

### Mid Term (3-6 months)
- [ ] TLS for P2P
- [ ] Light client (SPV)
- [ ] Multiple transaction types
- [ ] Multi-signature wallets
- [ ] Address book

### Long Term (6-12 months)
- [ ] Smart contract support
- [ ] Privacy features (zk-proofs)
- [ ] Mobile app (Android/iOS)
- [ ] Cross-chain bridges
- [ ] Governance system

## Won't Do ❌

- Premined tokens (fair launch only)
- ICO/presale
- Centralized servers

## Contributing

See [SETUP.md](SETUP.md) for how to run a node.
See [API.md](API.md) for the HTTP API.

All contributions welcome. Please:
1. Fork the repo
2. Create a feature branch
3. Add tests
4. Submit a PR

## Milestones

### v0.3 (Current)
- Working testnet
- Faucet
- REST API
- Fork resolution

### v0.4 (Next)
- Block explorer
- Web wallet
- 50+ tests

### v1.0
- Production-ready mainnet
- Full audit
- Mobile app
- Wide adoption
