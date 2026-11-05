# MuseFront

AI agents already shop for people, but they often can't finish the job on a small business's website. Prices are in images, rules are buried, and the agent gives up or guesses.

MuseFront fixes that. Give it a website, and it builds a small page that any AI agent can read and act on, works out what's missing, and keeps the page accurate. The owner runs it all from one simple app.

## Run it

This takes about 5 minutes. Everything runs on your own computer, and you don't need a Cloudflare account.

### 1. Install what you need

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)**, which runs the Python code and installs its dependencies.
- **[Node.js](https://nodejs.org)**, version 20 or newer, which runs the public agent page locally.

### 2. Download the code and install

```bash
git clone https://github.com/Jamerrred/Musefront.git
```

```bash
cd Musefront
```

```bash
uv sync
```

The test customers sometimes need a real browser, so install one:

```bash
uv run --with playwright playwright install chromium
```

### 3. Add your API keys

Make your settings file:

```bash
cp .env.example .env
```

Then open `.env` and fill in these two:

| Key | What it's for | Where to get it |
|---|---|---|
| `OPENROUTER_API_KEY` | The AI model behind every agent. About $3 of credit is plenty to try everything | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `EXA_API_KEY` | Reads websites and runs the test customers' searches | [dashboard.exa.ai](https://dashboard.exa.ai) |

`COMPOSIO_API_KEY` is optional: see [Connect accounts](#optional-connect-accounts). Leave the other values alone, because the next step fills them in.

### 4. Start it

```bash
uv run python scripts/start.py
```

The first start takes a minute. It opens the app at **http://127.0.0.1:8200**. Keep that terminal window open while you use it, and press `Ctrl+C` to stop.

## Try it

The sidebar follows the order an owner works in, so go through it from top to bottom.

**1. Websites: connect a website.** Paste an address and press the arrow. You can use your own, or this fictional demo business, which has prices hidden in images and missing rules on purpose:

```text
https://cormorant-detailing.jamerrred-audiobooks.workers.dev
```

Leave "Also test it with 5 customer agents" ticked to see the full flow. That takes about 5 minutes and costs about $1.50. Untick it for a quick try, which takes about a minute and costs a few cents.

**2. Resource: confirm the facts.** Check what MuseFront read from the site and press **Confirm all**. Nothing is public until you do. Your page is now live, and **What agents see** shows it exactly as agents read it.

**3. Simulations: fill in what's missing.** Answer the questions. Each answer goes straight onto your page. Then press **Run check** to see how test customers do now.

**4. Resource: change something.** Use the text box at the bottom, and type:

```text
We're closed for the next 2 days
```

MuseFront works out the exact dates and asks you to confirm. It ends by itself when the dates pass. You can also click any line or price to edit it, and undo with the version button at the top.

**5. Websites: copy your link.** This is the link a real business would put on its website.

**6. Inbox and Bookings: act like an agent.** Open your link and use its **Ask** and **Request** pages, as an agent would. The question shows up in **Inbox**, and the request shows up in **Bookings**. Answer or accept them, then open the status link to see your reply.

## Test it

These need no keys and cost nothing:

```bash
uv run pytest
```

```bash
uv run ruff check .
```

To watch the whole product run by itself, with a script playing the business owner, start MuseFront in one terminal and run this in another. It costs a few cents, and it only makes sense with the demo business above:

```bash
uv run python scripts/mvp_demo.py --url https://cormorant-detailing.jamerrred-audiobooks.workers.dev
```

## Record a demo

A private demo copy plays the whole flow back in about a minute, with no AI credit. Crawling, questions and test customers are scripted from a real crawl and the demo business's facts. Publishing is real, so the public page and its quote, request and ask forms work. It needs a Cloudflare Worker to publish to, so set `MF_EDGE_URL` and `MF_ADMIN_TOKEN` first, or run `scripts/start.py` alongside it.

```bash
MF_DEMO=1 MF_DB_PATH=back_office/demo.db uv run uvicorn back_office.api:app --port 8300
```

Open `http://127.0.0.1:8300`. To start a new take, open `http://127.0.0.1:8300/demo/reset`. If you show this to others, say it's sped up with sample data.

## Optional: connect accounts

MuseFront works without this. To let owners connect accounts such as Google Calendar and Google Sheets through [Composio](https://composio.dev):

1. Get an API key from [composio.dev](https://composio.dev).
2. Add it to `.env` as `COMPOSIO_API_KEY`.
3. Restart MuseFront.
4. Go to **Websites**, press **Connect a resource**, and follow the popup.

MuseFront reads what you connect and proposes changes for you to confirm. This part hasn't been tested with a real key yet.

## If something goes wrong

| What you see | What to do |
|---|---|
| `Add OPENROUTER_API_KEY...` when starting | Fill in your keys in `.env`, then start again |
| `Is another program using that port?` | Close the other program, or use another port: `MF_PORT=8300 uv run python scripts/start.py` |
| The website shows "couldn't be read" | Check your Exa key, or try another address. Sites that block automated visitors can fail |
| A test customer says "Agent crashed" | The AI provider returned an error. It doesn't count against the business, so run the check again |
| You want to start over | Stop MuseFront and delete `back_office/musefront.db` |

## How it works

| Part | What it does | Where |
|---|---|---|
| Owner app | The five screens | `back_office/web/` |
| Back office agent | Reads the site, builds the fact sheet, asks the owner, runs checks and reviews what agents did | `back_office/` |
| Public resource | The page, quote and booking forms that agents use. It's built from the fact sheet and needs no AI to serve | `edge/` |
| Test customers | A general-purpose AI agent that acts like a customer's assistant | `consumer_agent/` |

The agent changes the fact sheet and never the page, so every part of the page stays consistent. Only facts the owner has confirmed are ever public, and nothing an outside agent says can change them.

**Good to know:**

- The app has no login, so keep it on your own computer.
- Agent pages run on your computer too, so real outside agents can't reach them. To put them online, deploy `edge/` to Cloudflare with `npx wrangler deploy`, then set `MF_EDGE_URL` and the Worker's `ADMIN_TOKEN` secret.
- The businesses in the demo are fictional.

[docs/](docs/README.md) has the full decisions and research, and [reports/](reports/back-office-mvp.md) has the build notes and test results.

## For contributors

- **`consumer_agent/` is frozen** at the tag `first-demo-agent-freeze`, so test results stay comparable. If you change it, rerun the benchmark and move the tag.
- **Work** happens on short-lived branches, merged by pull request with a merge commit. See [CLAUDE.md](CLAUDE.md).
- **`docs/reference/muse-transcript.md`** names real businesses, so replace those names before making this repo public.
