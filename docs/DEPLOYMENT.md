# NURVEX Deployment Guide

How to expose a NURVEX node to the internet for free, without a VPS or public IP.

## The Problem

NURVEX nodes listen on `127.0.0.1:8338` (or any port). To let others join:

1. Your node must be reachable from the internet.
2. You need a public IP (or a tunnel).
3. Most mobile networks use CGNAT (no public IP).

**Solution:** Cloudflare Tunnel (free, works behind CGNAT).

## Prerequisites

- NURVEX node installed and running (`serve` on port 8338 or 8765).
- `cloudflared` installed.
- Internet connection.

## Install cloudflared

### On Android (Termux)

    pkg install cloudflared

### On Linux

Download from https://github.com/cloudflare/cloudflared/releases

## Quick Tunnel (temporary URL)

**Step 1: Start your NURVEX node**

    NURVEX_DATA_DIR=~/nurvex_net/node1 python nurvex_node.py serve --host 127.0.0.1 --port 8338

**Step 2: In another terminal, start the tunnel**

    cloudflared tunnel --url http://127.0.0.1:8338

**Step 3: Copy the public URL**

cloudflared prints a URL like:

    https://random-words-1234.trycloudflare.com

This URL is now your public bootstrap endpoint.

**Step 4: Test it**

Open in a browser:

    https://random-words-1234.trycloudflare.com/status

You should see JSON with your node's height.

## Important Notes

### Temporary URL

The quick tunnel URL changes every time you restart cloudflared.
For a permanent URL, see "Named Tunnel" below.

### Two processes required

You must keep BOTH running:

- NURVEX `serve` (the actual node).
- `cloudflared` (the tunnel).

Use Termux sessions or `screen`/`tmux` for persistence.

### Security

- Quick tunnel exposes your node to the public.
- NURVEX has no peer authentication.
- Anyone can request `/faucet` (rate-limited).
- Do NOT run a faucet with real funds on a public tunnel.

## Sharing Your Bootstrap URL

Once your tunnel is up, share the URL:

    https://random-words-1234.trycloudflare.com

Others can then:

1. Add your node as a peer:

       python nurvex_node.py add-peer https://random-words-1234.trycloudflare.com

2. Sync the chain:

       python nurvex_node.py sync

3. Request NVRX from faucet (if enabled):

       curl -X POST https://random-words-1234.trycloudflare.com/faucet -H "Content-Type: application/json" -d '{"address": "YOUR_NVRX_ADDRESS"}'

## Named Tunnel (permanent URL)

For a stable URL that does not change:

**Step 1: Create a free Cloudflare account**

https://dash.cloudflare.com/sign-up

**Step 2: Authenticate cloudflared**

    cloudflared tunnel login

This opens a browser to authorize.

**Step 3: Create a named tunnel**

    cloudflared tunnel create nurvex-bootstrap

**Step 4: Route traffic to your tunnel**

    cloudflared tunnel route dns nurvex-bootstrap nurvex.yourdomain.com

(You need a domain on Cloudflare. Free with Cloudflare DNS.)

**Step 5: Create a config file**

    mkdir -p ~/.cloudflared
    cat > ~/.cloudflared/config.yml << 'EOF'
    tunnel: nurvex-bootstrap
    credentials-file: ~/.cloudflared/<tunnel-id>.json
    ingress:
      - hostname: nurvex.yourdomain.com
        service: http://127.0.0.1:8338
      - service: http_status:404
    EOF

**Step 6: Run**

    cloudflared tunnel run nurvex-bootstrap

Now `https://nurvex.yourdomain.com` always points to your node.

## Tips

1. **Battery:** Cloudflare tunnel + NURVEX serve drain battery. Keep phone plugged in.
2. **Network:** WiFi is more stable than LTE for tunnels.
3. **Bandwidth:** Each sync request is small (< 1MB), so mobile data is fine.
4. **Multiple nodes:** You can run multiple tunnels (one per node) on the same phone.
5. **Monitoring:** Add `/status` polling to check your node is online.

## Alternative: ngrok

If cloudflared is unavailable, try:

    pkg install ngrok  # if available
    ngrok http 8338

Or download ngrok from https://ngrok.com/download

ngrok gives a URL like `https://xxxx.ngrok.io`. Similar concept.

## Alternative: VPS

For maximum stability, use a VPS:

- DigitalOcean: $4/month
- Hetzner: 4 EUR/month
- Oracle Cloud Free: free tier available

Install NURVEX, open port 8338, and use the VPS's public IP directly.

## Troubleshooting

### 502 Bad Gateway

Your NURVEX serve is not running. Start it:

    NURVEX_DATA_DIR=~/nurvex_net/node1 python nurvex_node.py serve --host 127.0.0.1 --port 8338

### Tunnel disconnects

- Check internet.
- Restart cloudflared.
- URL changes on restart.

### "No such host" or DNS errors

Cloudflare may be blocked by your ISP. Try a different network.

### Slow response

- First request is slow (cold start).
- Subsequent requests are faster.
- If always slow, check your mobile data speed.
