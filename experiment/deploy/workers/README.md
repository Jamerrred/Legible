# Deploying to Cloudflare

The site and resource run on [Cloudflare Python Workers](https://developers.cloudflare.com/workers/languages/python/). It needs no Docker or containers, and the app code is the same as it is locally.

You need `uv`, Node and a Wrangler login, which `npx wrangler login` sets up. Then deploy, using your subdomain from **Workers & Pages** in the Cloudflare dashboard:

```bash
./deploy.sh YOUR_WORKERS_SUBDOMAIN
```

## What it creates

| Worker | What it is | Live at |
|---|---|---|
| `sunrise-auto-detailers` | The site, "before" | https://sunrise-auto-detailers.jamerrred-audiobooks.workers.dev |
| `sunrise-detailers` | The site, "after", which adds one link line | https://sunrise-detailers.jamerrred-audiobooks.workers.dev |
| `sunrise-agents` | The resource | https://sunrise-agents.jamerrred-audiobooks.workers.dev |

The names don't reveal which version is which, so a test doesn't give it away.

## How it works

`build.py` copies the app code into `src/` and the static files into `public/`, then records which version this is in `src/version.py`. `src/main.py` serves that version, and Cloudflare serves static files directly.

## Limits

- **Forms and status pages don't last:** a Worker can only write to `/tmp`, which clears when it restarts, so a status link can stop working.
- **Cloudflare's logs are the lasting record:** each event is printed there and kept for a few days, including form contents such as contact details. Watch them live with `npx wrangler tail sunrise-agents`.
- **Hidden from search:** every app page sends `X-Robots-Tag: noindex`, because these are mock businesses. Search tools, including Exa, may not find them, so give agents the address directly.
