# NURVEX Mining Guide

How mining works, expected times, and how to optimize.

## What is Mining?

Mining is finding a `nonce` value such that:

\`\`\`
sha256(block_without_hash_field) starts with N zeros
\`\`\`

Where `N` = current difficulty (starts at 5, adjusts every 10 blocks).

Each attempt is one SHA-256 hash. The miner tries nonces sequentially until one matches.

## Expected Time

The probability of a hash starting with `N` zeros is `1 / 16^N`.

| Difficulty | Probability | Avg hashes | Avg time (100k H/s) |
|---|---|---|---|
| 5 zeros | 1 / 1,048,576 | ~1 million | ~10 s |
| 6 zeros | 1 / 16,777,216 | ~16 million | ~2.7 min |
| 7 zeros | 1 / 268,435,456 | ~268 million | ~45 min |
| 8 zeros | 1 / 4,294,967,296 | ~4.3 billion | ~12 hours |

**Note:** These are averages. Actual time varies widely (Poisson distribution):
- Some blocks: 1 second.
- Some blocks: 5 minutes.
- All at the same difficulty.

## Dynamic Difficulty

Every 10 blocks, the network recalculates difficulty:

- If the last 10 blocks took **< 5 minutes** (fast): difficulty increases by 1.
- If they took **> 20 minutes** (slow): difficulty decreases by 1.
- Otherwise: stays the same.

Clamped between `MIN_DIFFICULTY = 5` and `MAX_DIFFICULTY = 8`.

**Target:** 60 seconds per block = 10 minutes per 10-block window.

## How to Mine

\`\`\`bash
NURVEX_DATA_DIR=~/nurvex_net/node1 python nurvex_node.py mine YOUR_ADDRESS
\`\`\`

Example output:
\`\`\`
Mined block #42: 000001a2b3c4d5e6...
Reward: 8.57142857 NVRX
Transactions: 2
Time: 23.79s
\`\`\`

**Field breakdown:**
- `Mined block #N`: height of the new block.
- `Hash`: starts with required zeros.
- `Reward`: NVRX earned (current subsidy).
- `Transactions`: how many mempool transactions were included.
- `Time`: seconds spent searching for nonce.

## Halving

Rewards halve every `HALVING_INTERVAL = 1,050,000` blocks.

| Block range | Reward |
|---|---|
| 0 – 1,049,999 | 8.57142857 NVRX |
| 1,050,000 – 2,099,999 | 4.28571428 NVRX |
| 2,100,000 – 3,149,999 | 2.14285714 NVRX |
| ... | (halves each interval) |

Total supply cap: **18,000,000 NVRX** (across all halvings).

## Reward Maturity

**Important:** Mining rewards are **not spendable** until the block is:
1. Mined.
2. Accepted by the network.
3. Included in the current chain (not on a fork).

If you mine a block and it gets replaced by a longer chain, your reward disappears.

## Mempool Inclusion

When you mine, your node:
1. Loads the mempool.
2. Validates each transaction against a temporary ledger (to prevent double-spends).
3. Picks valid transactions in order.
4. Adds them to the block.
5. After mining, removes those transactions from the mempool.

**You can't include more transactions than fit in the block.** Currently, there is no explicit block size limit, but the protocol may add one in the future.

## Optimizing Mining

### On a phone (Termux)

- Close other apps.
- Keep the phone plugged in (mining drains battery).
- Avoid running multiple miners on the same device.

### On a computer

- Python's `hashlib` uses CPU only. No GPU acceleration yet.
- Multiple cores don't help (single-threaded miner).
- For faster mining, run multiple nodes on different cores.

### On a VPS

- Small VPS (1 vCPU): similar to phone.
- Bigger VPS (4+ vCPUs): run multiple miners, one per core.

## Common Issues

### "Insufficient proof of work"

Your hash doesn't start with enough zeros. Check:
- Are you using the latest `nurvex_node.py`?
- Is `required_prefix(chain)` returning the correct value?

### "Chain validation failed"

The block you mined doesn't validate. Common causes:
- Bad timestamp.
- Invalid mempool transaction.
- Wrong previous_hash.

Run \`validate\` to diagnose:
\`\`\`bash
python nurvex_node.py validate
\`\`\`

### Mining takes hours

Check difficulty:
\`\`\`bash
curl http://127.0.0.1:8338/status
\`\`\`

If the chain has been fast, difficulty may have risen to 7 or 8. Wait for it to drop.

### "Maximum supply exceeded"

The network has issued all 18M NVRX. No more mining rewards are possible.

## Tips

1. **Mine with a stable connection.** If your node loses sync, it may lose rewards.
2. **Don't mine on an outdated chain.** Always `sync` first.
3. **Check status before mining.** Confirm height and validity.
4. **Run 24/7 for consistent rewards.** PoW favors continuous mining.
5. **Join a pool** (not yet implemented). Currently, solo mining only.
