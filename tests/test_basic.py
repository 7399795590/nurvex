"""Basic tests for NURVEX core functions."""
import sys
import os
import tempfile
from pathlib import Path

# Setup test environment BEFORE importing nurvex_node
_tmpdir = tempfile.mkdtemp(prefix="nurvex_test_")
os.environ["NURVEX_DATA_DIR"] = _tmpdir

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nurvex_node import (
    address_for, canonical, sha256, block_hash, tx_id,
    fmt, reward_for_height, count_leading_zeros, chain_work,
)


def test_canonical_is_deterministic():
    """Same dict should produce same canonical bytes."""
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert canonical(a) == canonical(b)


def test_sha256_known_value():
    """SHA256 of empty string is well-known."""
    assert sha256(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_address_for_format():
    """Address must start with nvrx1 and be 45 chars."""
    pub_hex = "00" * 32
    addr = address_for(pub_hex)
    assert addr.startswith("nvrx1")
    assert len(addr) == 45


def test_fmt_trims_zeros():
    """fmt() should trim trailing zeros."""
    assert fmt(100_000_000) == "1"
    assert fmt(50_000_000) == "0.5"
    assert fmt(0) == "0"


def test_reward_halving():
    """Reward should halve at intervals."""
    assert reward_for_height(0) == 857_142_857
    assert reward_for_height(1_050_000) == 428_571_428
    assert reward_for_height(2_100_000) == 214_285_714


def test_count_leading_zeros():
    """Count leading zeros in hex string."""
    assert count_leading_zeros("00000abc") == 5
    assert count_leading_zeros("0000abcd") == 4
    assert count_leading_zeros("1234") == 0
    assert count_leading_zeros("00000012") == 6
    assert count_leading_zeros("") == 0


def test_chain_work_calculation():
    """chain_work = sum of 16^zeros per block."""
    fake_chain = [
        {"height": 0, "hash": "0" * 64},   # genesis, skipped
        {"height": 1, "hash": "0" * 5 + "abc"},
        {"height": 2, "hash": "0" * 6 + "xyz"},
    ]
    expected = (16 ** 5) + (16 ** 6)
    assert chain_work(fake_chain) == expected


def test_block_hash_deterministic():
    """Same block should produce same hash."""
    block = {"height": 1, "timestamp": 1000, "nonce": 42, "transactions": []}
    h1 = block_hash(block)
    h2 = block_hash(block)
    assert h1 == h2
    assert len(h1) == 64


def test_tx_id_deterministic():
    """Same tx should produce same id."""
    tx = {"type": "transfer", "sender": "a", "recipient": "b", "amount": 100}
    assert tx_id(tx) == tx_id(tx)
    assert len(tx_id(tx)) == 64


# ===== Rate Limiter Tests =====

def test_rate_limiter_allows_up_to_limit():
    """RateLimiter allows up to limit requests."""
    from nurvex_node import RateLimiter
    rl = RateLimiter(window_seconds=60)
    for i in range(5):
        ok, retry = rl.check("1.1.1.1", 5)
        assert ok, f"Request {i+1} should be allowed"
        assert retry == 0


def test_rate_limiter_blocks_over_limit():
    """RateLimiter blocks requests over limit."""
    from nurvex_node import RateLimiter
    rl = RateLimiter(window_seconds=60)
    for i in range(3):
        rl.check("1.1.1.1", 3)
    ok, retry = rl.check("1.1.1.1", 3)
    assert not ok, "4th request should be blocked"
    assert retry > 0, "retry_after should be positive"


def test_rate_limiter_different_ips_independent():
    """Different IPs have independent buckets."""
    from nurvex_node import RateLimiter
    rl = RateLimiter(window_seconds=60)
    for i in range(3):
        rl.check("1.1.1.1", 3)
    # IP 1 is blocked
    ok1, _ = rl.check("1.1.1.1", 3)
    assert not ok1
    # IP 2 is fine
    ok2, _ = rl.check("2.2.2.2", 3)
    assert ok2


def test_rate_limits_config_exists():
    """RATE_LIMITS dict should contain all endpoints."""
    from nurvex_node import RATE_LIMITS
    assert "/transaction" in RATE_LIMITS
    assert "/peer" in RATE_LIMITS
    assert "/faucet" in RATE_LIMITS
    assert "/block" in RATE_LIMITS
    assert RATE_LIMITS["/peer"] == 10
    assert RATE_LIMITS["/faucet"] == 5
