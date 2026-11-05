#!/usr/bin/env bash
# Deploy the site and resource to Cloudflare. Usage: ./deploy.sh YOUR_WORKERS_SUBDOMAIN
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: ./deploy.sh YOUR_WORKERS_SUBDOMAIN" >&2
  exit 1
fi

cd "$(dirname "$0")"
resource_url="https://cormorant-agents.$1.workers.dev"

uv sync --quiet
export PATH="$PWD/.venv/bin:$PATH"

for version in resource before after; do
  python build.py "$version" "$resource_url"
  pywrangler deploy --env "$version"
done
