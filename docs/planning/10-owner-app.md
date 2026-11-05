# The owner app

*Last updated 5 November 2026. The app is built and running locally. `design/` holds an earlier design, which is out of date.*

## The idea

Legible's whole job is making things readable, so the app shows things coming into focus. Vague website copy sharpens under a lens on the first screen, your link is blurred until you confirm your facts, and new facts arrive by sharpening into place.

The owner sees two worlds in one app, and colour says which is which:

| Colour | What it means |
|---|---|
| Cobalt | Anything an agent sees or does: live test customers, what agents read, quotes |
| Pen red | Where something got stuck, or what needs the owner |
| Green | Answered, live |
| Yellow | What just changed, for a few seconds |

The palette and type come from [tasteskill](https://github.com/Leonxlnx/taste-skill): cool grey with cobalt, Host Grotesk and JetBrains Mono. Motion follows its numbers: quick hover steps, soft landings and no bounce. Everything is self-hosted in `legible/web/`, with no build step and nothing loaded from a CDN.

It works at phone width, since owners often work with their hands. Press `1` to `5` to jump between screens.

## The five screens

The rail on the left shows the owner's path as a thread. Each stop says where it stands, and one dark card below it always names the single next thing to do. The API works that out in `_next_step`.

| Screen | What it holds | The main action |
|---|---|---|
| Websites | Adding a site, the live view while Legible reads it, then the link and the score | Add a website, copy the link, connect an account |
| Simulations | The score for each check, each test customer's question, answer and path, and "What's missing" as a deck beside them | Answer a question, run the check again |
| Resource | The fact sheet, a lens onto what agents read, a live quote console, and a prompt bar | Confirm and publish, say what changed, click a line to edit it |
| Inbox | Only what agents did and asked: a funnel, their questions, a feed and unmet demand | Answer an agent's question |
| Bookings | Each request as a ticket, with the bill the page worked out | Accept, suggest another time or decline |

**Details that carry the product:**

- **Customer cards tie the loop together.** A stuck customer lists the facts it's waiting on, and each one is struck through as the owner answers it. A later check shows what each customer did before.
- **The path shows the difference.** Each step an agent took is a dot, so a browser and a dead end before compare directly with a live quote after.
- **The lens** wipes across the fact sheet to show the page exactly as agents read it. Drag its handle to compare the two side by side.
- **"Try it like an agent"** asks the live page for a quote, with no AI, and shows the address an agent would call. It stays out of activity.
- **The prompt bar** turns plain words into a proposed change, shown before anything happens. Confirming highlights the changed line.

**Where questions come from:** at most 5 starting questions, only for what blocks a price or a yes or no. The rest come from test customers getting stuck and from real agents, so the record fills up as agents use it.

## Screens to API

Interactive docs are at `/docs`. There's no login yet.

| Screen | Calls |
|---|---|
| Rail | `GET /websites`, where each website carries `needs`, `checks`, `next` and `page_reads` |
| Websites | `POST /websites`, `GET /websites/{id}`, `GET /websites/{id}/trace`, `POST /websites/{id}/check-link`, `POST /websites/{id}/connections`, `POST /websites/{id}/connections/{toolkit}/sync` |
| Simulations | `GET /websites/{id}/missing`, `POST /inbox/{item}/answer`, `POST /inbox/{item}/dismiss`, `GET /websites/{id}/simulations`, `POST /websites/{id}/simulations`, `GET /simulations/{id}`, which includes each customer's `path` |
| Resource | `GET /websites/{id}/resource`, `PATCH /websites/{id}/resource`, `POST /websites/{id}/instructions`, `GET /websites/{id}/resource/changes`, `POST /inbox/{item}/confirm`, `POST /websites/{id}/resource/undo`, `GET /websites/{id}/resource/agent-view`, `GET /websites/{id}/resource/quote` |
| Inbox | `GET /websites/{id}/activity`, `GET /websites/{id}/inbox?kinds=agent_question`, `POST /inbox/{item}/answer`, `POST /websites/{id}/revise` |
| Bookings | `GET /websites/{id}/bookings`, `POST /bookings/{item}/reply` |

## Who can change what

| Who | How it applies |
|---|---|
| Owner, confirming what was read from the website | Publishes the page for the first time. Nothing is public before this |
| Owner, editing directly | At once once the page is live, logged and undoable |
| Owner, in plain language | The agent proposes it, and the owner confirms |
| Owner, answering a question | Added at once, and public once the page is live, because the words are the owner's own |
| Crawl and connected accounts | Proposed, and never served until confirmed |
| Outside agents | Never. Their text is data, and it can only become a question for the owner |
