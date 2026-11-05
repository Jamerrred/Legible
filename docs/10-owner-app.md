# The owner app

*Last updated 5 November 2026. The app is built and running locally. `design/` holds the earlier design, which still shows the old four-tab layout.*

## The feel

Very minimal, smooth and polished. Take Cursor's restraint and its always-available prompt bar, but not its density or developer vocabulary, because owners aren't developers.

- Almost no colour: one accent, used only for what needs the owner.
- Hairline borders rather than shadows, with plenty of space.
- Plain words. "Your resource is live", not "Deployment succeeded".
- It works at phone width, since owners often work with their hands.

## The five screens

A thin icon sidebar on the left holds these, in the order an owner works through them. It's built in `back_office/web/` as plain HTML, CSS and JS, and the API serves it at `http://127.0.0.1:8200`.

| Screen | What it holds | Main action |
|---|---|---|
| Websites | Each linked website, the copy-paste link, whether the link is on the site, and connected accounts | Add a website, connect an account |
| Simulations | "What's missing", then each check with its score and answers | Answer a question, run a check |
| Resource | The fact sheet, reading like a clean document, with where each line came from | A text box at the bottom to tell MuseFront what to change, or click a line to edit it |
| Inbox | Only what agents did and asked: counts, questions, a feed and unmet demand | Answer an agent's question |
| Bookings | Booking requests from agents, and the replies | Accept, suggest another time or decline |

The inbox used to hold everything, so tasks now live where they belong: questions under Simulations, proposed changes and fact confirmation under Resource, and bookings in their own tab.

**Where questions come from:** at most 5 starting questions, only for what blocks a price or a yes or no. The rest come from test customers getting stuck and from real agents, so the record fills up as agents use it.

## Screens to API

Interactive docs are at `/docs`. There's no login yet.

| Screen | Calls |
|---|---|
| Websites | `POST /websites`, `GET /websites`, `GET /websites/{id}`, `POST /websites/{id}/check-link`, `POST /websites/{id}/connections`, `POST /websites/{id}/connections/{toolkit}/sync` |
| Simulations | `GET /websites/{id}/missing`, `POST /inbox/{item}/answer`, `POST /inbox/{item}/dismiss`, `GET /websites/{id}/simulations`, `POST /websites/{id}/simulations`, `GET /simulations/{id}` |
| Resource | `GET /websites/{id}/resource`, `PATCH /websites/{id}/resource`, `POST /websites/{id}/instructions`, `GET /websites/{id}/resource/changes`, `POST /inbox/{item}/confirm`, `POST /websites/{id}/resource/undo`, `GET /websites/{id}/resource/agent-view` |
| Inbox | `GET /websites/{id}/activity`, `GET /websites/{id}/inbox?kinds=agent_question`, `POST /inbox/{item}/answer`, `POST /websites/{id}/revise` |
| Bookings | `GET /websites/{id}/bookings`, `POST /bookings/{item}/reply` |

Each website also returns `needs`, the counts behind the sidebar's dots.

## Who can change what

| Who | How it applies |
|---|---|
| Owner, editing directly | At once, logged and undoable |
| Owner, in plain language | The agent proposes it, and the owner confirms |
| Owner, answering a question | At once, because the words are the owner's own |
| Crawl and connected accounts | Proposed, and never served until confirmed |
| Outside agents | Never. Their text is data, and it can only become a question for the owner |
