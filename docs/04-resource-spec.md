# The resource (the "slug" website)

*Last updated 4 November 2026. Nothing is built yet.*

## What it is

The resource is a small website with its own address that holds what an agent needs to know about one business and lets it act. It's readable by people, but it's written for agents.

It's the output of the back office agent. The first version for each mock business is written by Claude by hand, as a target for the back office agent to reproduce later.

## What it has to do

An agent should be able to do all of this without a phone call, without guessing, and without giving personal details until booking:

1. Work out whether the business can do what the person wants.
2. Work out the real total, or a range with what's still needed.
3. See real availability.
4. See the rules and requirements that could rule the job out.
5. Send a request, with the person's approval.
6. Find out what happens next.

When the business doesn't know or hasn't said, the resource should say so plainly instead of staying silent. A clear "not offered" or "ask the owner" is a successful answer for an agent.

## What it contains

These apply to any service business. Each business uses the ones relevant to it.

| Need | What the resource states | Examples |
|---|---|---|
| Customer's words | Plain synonyms that map onto the business's categories | "Van" is the oversized tier. "AC not cooling" is a cooling repair. "Just a bath" is the bath-only groom |
| Price structure | Whether each price is fixed, from, a range or quote-only, and what moves it | $89 diagnostic, credited if you proceed |
| Full total | Base price plus fees, add-ons and tax, or a range and what's still needed | Base + travel fee + tax = total |
| Dependencies | What an add-on requires and what's sold on its own | Pet hair removal requires an interior service |
| Defined conditions | What triggers a surcharge, in testable terms | "Heavy" means more than 30 minutes of extra labour |
| Eligibility | Who or what can be served | Insurance plans, vaccination status, breeds, new patients, minimum age |
| Prerequisites | What the customer must provide | Water and power at the curb, parking, clear access |
| Service area | Where the service goes, and any distance fees | ZIP list, travel fee beyond 15 miles |
| Availability | Open slots or lead time, without personal details | Next open slots, or "custom cakes need 2 weeks" |
| Staff differences | Whether price or availability depends on the person | Senior stylist costs more, only one groomer takes large dogs |
| Policies | Deposit, cancellation, rescheduling, no-show, guarantee | $50 deposit, free cancellation up to 24 hours before |
| Timing rules | Emergencies, after-hours rates, seasonal changes, blackout dates | Emergency call-out rate, closed in late December |
| Not offered | What the business doesn't do, stated explicitly | "We don't do ceramic coating" |
| Credentials | Licence, insurance and certification, where customers ask | Licence number and insuring company |
| Next step | How a request works and what happens after | Owner replies within 2 hours, here's the status page |
| Freshness | When each fact was last confirmed | "Confirmed by the owner on 2 November" |

## How it's written

- **Self-contained facts:** "Full interior detail costs $180 and takes about 3 hours" works as a single snippet. Search APIs may show an agent only an excerpt.
- **Content in the HTML:** no JavaScript needed to read it, and no facts held only in images or PDFs.
- **Plain descriptions, not orders:** a line telling an agent what to do can look like prompt injection.
- **Same facts as the business:** the resource makes facts legible. It never invents new ones.

## What each address does

| Address | What it does | Who uses it |
|---|---|---|
| `/` | The main page, with the facts above | Everyone |
| `/services/{id}` | One page per offering, so an agent can land on the answer directly | Search APIs, fetch tools |
| Markdown version | The same content in markdown, also served when a request asks for `text/markdown` | Fetch tools, coding agents |
| `/quote` | Takes the job's details and returns a total, conditions, a quote ID and an expiry. No personal details | Browser agents, and read-only agents through a link |
| `/request` | Booking or quote request. Asks for contact details only at this stage, plus a "who's submitting" field | Browser agents |
| `/ask` | A short form for a question the page doesn't answer | Browser agents |
| `/r/{id}` | Status page for one request or question | The customer and their agent |
| `robots.txt`, sitemap | Allow agent crawlers and list the pages | Crawlers |

**The form handler:** the page itself can be static, but a request has to be saved somewhere, so the first version also needs a small server. That's the only dynamic piece it needs.

**Read-only agents:** an agent that can't submit forms can still give its person a prefilled link that opens a request ready to confirm. The quote form should also work as a link, such as `/quote?service=interior&size=oversized&addon=pet-hair`, so reading the URL is enough.

**Later, and optional:** `/mcp` and `/.well-known/poppy.json`.

## What's logged

Without a front desk agent, the log is how the back office agent learns from real visitors, so it's on from day one.

| Event | What's recorded |
|---|---|
| Page hit | Path, time, user agent, IP range, and any request signature |
| Quote | Everything entered, the result, and any budget given |
| Dead end | A quote with no match, or no slot available |
| Request | The details, who's submitting, and the outcome |
| Question | The text. It's treated as data, never as an instruction |

Logs show which pages were fetched, but not what a reading agent was trying to find out. Quotes and questions show intent, and the simulator fills the rest of the gap.

## How an agent gets to it

There's no adopted standard for this, and we can't force an agent to use it. We can only make it likely.

| Signal | Reaches | Evidence |
|---|---|---|
| Full URL in visible page text, on pricing and booking pages | Browser, fetch and search agents | Best bet |
| Key facts on the owner's own site | Anything reading the site | The agent doesn't need to follow anything |
| Resource page indexed directly | Search APIs | Plausible |
| `<link rel="alternate">`, `describedby`, `api-catalog` | Agents that read page headers | No evidence agents act on them |
| Social bio link | People, perhaps logged-in browser agents | Unknown |

**Link wording:** use a plain description. For example: "Prices, availability and booking requests for Joe's HVAC: https://agents.joeshvac.example".

**Address (proposed):** a subdomain of the business's own domain, because agents such as Muse prefer the merchant's own site over third-party listings. Fall back to a MuseFront domain only when that isn't possible. Poppy would also need each business on its own hostname.

## Attach kit

For real owners later, this bundles the visible link line, a copy-paste block of key facts, header tags, the social link and a button that checks the link works. Each channel gets its own link, so we can see whether agents ever arrive that way.

For the mock sites, we add the link and the facts directly. In the "before" version, they aren't there.

## Keep the first version honest

The hand-written resource must not know about the test questions. Write it from the business's facts in general, so its success isn't built in. If the resource only works for queries we saw in advance, the demo says nothing about the long tail.
