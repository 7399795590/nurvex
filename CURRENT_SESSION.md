# NURVEX — Current Session State

**Saved at:** 2026-10-11
**Session:** 5

## Status

- Public on GitHub: https://github.com/7399795590/nurvex
- 42+ commits
- CI passing (Python 3.10-3.12)
- 13 pytest tests
- Block Explorer: live
- Web Wallet: live (with transaction history)
- Faucet: working
- Rate limiting: active
- Fork resolution: complete

## Live Network

- Bootstrap URL: https://0fb7a2d5b371dc.lhr.life
- Note: URL changes each SSH restart (localhost.run limitation)
- Faucet address: nvrx1d109f6da8f2a98c0f83974e66bd7e77f76a60959

## Sale Channels

- GitHub README: FOR SALE badge
- X (Twitter): @M10Crypt
- SideProjectors: https://www.sideprojectors.com/project/99901/nurvex
- Price: $7,000 USD (negotiable)

## Payment Methods

- USDT (TRC20 or BEP20)
- Binance Pay

## To Stop Everything

    pkill -f nurvex_node.py; pkill -f ssh

## To Resume

Session A (SSH tunnel):

    pkill -f ssh; sleep 2; ssh -i ~/.ssh/id_ed25519 -R 80:localhost:8765 localhost.run

Session B (Node1 serve):

    NURVEX_DATA_DIR=~/nurvex_net/node1 python ~/NURVEX_NODE2/nurvex_node.py serve --host 127.0.0.1 --port 8765

## To Verify

    curl -s https://0fb7a2d5b371dc.lhr.life/status
    curl -s https://0fb7a2d5b371dc.lhr.life/wallet

## Next Steps

- Wait for SideProjectors approval (2-3 days)
- Monitor email: mhmdthbrh@gmail.com
- Monitor GitHub issues
- Monitor X: @M10Crypt
- When buyer arrives: contact via GitHub issue or X DM
