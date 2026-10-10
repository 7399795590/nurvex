# NURVEX — Current Session State

**Saved at:** 2026-10-10 (end of session)
**Session:** 3

## Status

- Public on GitHub: https://github.com/7399795590/nurvex
- 24 commits
- 8 docs files
- CI passing (Python 3.10-3.12)
- 9 pytest tests
- MIT License
- Live testnet on internet
- Faucet working

## Repository Structure

NURVEX_NODE2/
  nurvex_node.py               (main program)
  requirements.txt             (runtime deps)
  requirements-dev.txt         (dev deps: pytest)
  README.md                    (with badges)
  LICENSE                      (MIT)
  BOOTSTRAP.md                 (current bootstrap URL)
  CURRENT_SESSION.md           (this file)
  .gitignore
  .github/workflows/test.yml   (CI)
  docs/
    ARCHITECTURE.md
    SETUP.md
    API.md
    MINING.md
    DEPLOYMENT.md
    ROADMAP.md
  tests/
    __init__.py
    test_basic.py              (9 tests)
  scripts:
    start_network.sh
    stop_network.sh
    test_network.sh
    monitor.sh

## Live Network

- Bootstrap URL: https://452f440293c541.lhr.life
- Tunnel: localhost.run (SSH-based, permanent)
- Faucet address: nvrx1d109f6da8f2a98c0f83974e66bd7e77f76a60959
- Faucet balance: ~32.85 NVRX
- Chain height: 6

## Node Addresses

- Node1: nvrx1c6ef3c7871269bb0c4997a8599fd4c7381156636
- Node2: nvrx12794457b6b35cf2a4533ce356a55b8cfc987b224
- Node3: nvrx1773b3b9ad226dad11ebcb9caf0a65408a2df9330

## Running Processes

Check with:

    pgrep -af "ssh|nurvex"

Expected:
- ssh ... localhost.run (tunnel)
- python nurvex_node.py serve :8765 (Node1)
- python nurvex_node.py serve :8766 (Node2)
- python nurvex_node.py serve :8767 (Node3)

## To Stop Everything

    pkill -f nurvex_node.py; pkill -f ssh

## To Resume

Session A (SSH tunnel):

    ssh -i ~/.ssh/id_ed25519 -R 80:localhost:8765 localhost.run

Session B (Node1 serve):

    NURVEX_DATA_DIR=~/nurvex_net/node1 python ~/NURVEX_NODE2/nurvex_node.py serve --host 127.0.0.1 --port 8765

## To Verify

    curl -s https://452f440293c541.lhr.life/status
    curl -s https://452f440293c541.lhr.life/faucet

## Git Remote

- origin: https://github.com/7399795590/nurvex.git
- branch: main
- token stored in ~/.git-credentials

## Next Steps

See docs/ROADMAP.md for the full plan.

Priority:
1. Block Explorer (web UI)
2. Web Wallet
3. More tests (>50)
4. Rate limiting

## Milestones Achieved Today

- Fork resolution + tiebreaker
- Faucet on permanent URL
- GitHub public repo
- LICENSE (MIT)
- CI/CD (GitHub Actions)
- pytest suite (9 tests)
- Badges in README
- Description + Topics
- ROADMAP
- Testing section in README
