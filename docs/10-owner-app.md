# The owner app

*Last updated 5 November 2026. The backend is built, and this is the map a frontend builds on. The visual design comes later from the founder. Nothing here is final design.*

## The feel

Very minimal, smooth and polished. Take Cursor's restraint and its always-available prompt bar, but not its density or developer vocabulary, because owners aren't developers.

- Almost no colour: one accent, used only for what needs the owner.
- Hairline borders rather than shadows, with plenty of space.
- Plain words. "Your resource is live", not "Deployment succeeded".
- The inbox has to work at phone width, since owners often work with their hands.

## The four screens

A thin icon sidebar on the left holds these, and the inbox opens first.

| Screen | What it holds | Main action |
|---|---|---|
| Inbox | What needs the owner: fact confirmations, interview questions, proposed changes and booking requests. A second view shows minimal activity | One text bar to tell MuseFront anything |
| Resource | The fact sheet, reading like a clean document. Each line shows where it came from | Click a line to edit it, and copy the link |
| Simulations | Each check with its score, and what agents couldn't answer | Run a check |
| Websites | Each linked website, whether the link is on the site, and its connected accounts | Add a website, connect an account |

The owner's accounts live under Websites, because a connection belongs to one website.

## Screens to API

Run the API with `uv run uvicorn back_office.api:app --port 8200`. Interactive docs are at `/docs`. There's no login yet.

**Websites**

| Call | What it does |
|---|---|
| `POST /websites` | Starts onboarding from a URL, in the background |
| `GET /websites`, `GET /websites/{id}` | List or read, with `stage`, `stage_note`, `link`, `link_line`, `live` and `open_inbox`. Poll `stage` during onboarding |
| `POST /websites/{id}/check-link` | Checks whether the owner's home page carries the link |
| `POST /websites/{id}/connections` | Returns a connect link for `googlecalendar` or `googlesheets` |
| `POST /websites/{id}/connections/{toolkit}/sync` | Reads the account and puts any changes in the inbox |

**Inbox**

| Call | What it does |
|---|---|
| `GET /websites/{id}/inbox` | Open items. Each `kind` is `review`, `question`, `proposal`, `request`, `agent_question` or `insight` |
| `POST /websites/{id}/instructions` | Plain language in, a proposal out, or a clarifying question |
| `POST /inbox/{item}/answer` | Answers a question. `scope` is `everyone`, which adds it to the record, or `once`, which only replies |
| `POST /inbox/{item}/confirm` | Applies a proposal, or confirms crawled facts. `exclude_ids` leaves some out |
| `POST /inbox/{item}/dismiss` | Dismisses an item |
| `POST /inbox/{item}/reply` | Answers a booking request. The reply shows on its public status page |
| `GET /websites/{id}/activity` | Counts, agents, dead ends, unmet demand and a feed |
| `POST /websites/{id}/revise` | Runs the periodic review now |

**Resource**

| Call | What it does |
|---|---|
| `GET /websites/{id}/resource` | The record, with link, version, counts and what's not stated yet |
| `PATCH /websites/{id}/resource` | Direct or programmatic edits, as ops. These apply and publish at once |
| `POST /websites/{id}/resource/undo` | Restores the previous version and republishes |
| `GET /websites/{id}/resource/versions` | Version history |

**Simulations**

| Call | What it does |
|---|---|
| `POST /websites/{id}/simulations` | Runs a check on `resource` or `storefront`, reusing the first check's queries so scores compare |
| `GET /websites/{id}/simulations` | Each check and its summary |
| `GET /simulations/{id}` | Every query, answer and outcome in one check |

## Who can change what

| Who | How it applies |
|---|---|
| Owner, editing directly | At once, logged and undoable |
| Owner, in plain language | The agent proposes it, and the owner confirms |
| Owner, answering a question | At once, because the words are the owner's own |
| Crawl and connected accounts | Proposed, and never served until confirmed |
| Outside agents | Never. Their text is data, and it can only become a question for the owner |
