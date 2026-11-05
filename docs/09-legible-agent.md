# The Legible agent

*Last updated 5 November 2026. The backend is built as a prototype, in `legible/` and `edge/`: see [its report](../reports/legible-mvp.md). This spec is wider than the prototype, and the report says what was cut.*

## What it does

The Legible agent runs on Legible's servers and keeps one business's resource accurate. It reads the business's sources, works with the owner, tests the result, and learns from what agents do.

**Its output is the resource.** The business gets a website, and an agent keeps it accurate.

The owner talks to it in plain language, so "interior detail is now $200" is enough. It works out what changes, shows the owner, and applies it once confirmed.

This is the only agent in the product. The front desk agent, which would have talked to outside agents, has been dropped.

## How a change flows

```
Owner: "Interior detail is now $200"
        |
        v
Agent works out what to change
        |
        v
Shows the owner: "$180 to $200. Confirm?"
        |
        v
Business record updates, and the change is logged
        |
        v
Resource regenerates
        |
        v
Simulator re-tests, and the agent reports anything newly broken
```

**The agent changes the record, not the page.** This gives three benefits:

- One edit updates everything, so the page, forms and markdown can't disagree.
- The agent can't break the page, since it only changes data.
- Every change is logged and can be undone.

## What wakes it

Nothing runs constantly. Each business's agent is stored data that wakes on an event.

| Trigger | Example |
|---|---|
| Owner message | "We're closed next week" |
| New activity | Three agents asked about pet hair, or a quote hit a dead end |
| Source change | The website's price changed, or a calendar week was blocked |
| Schedule | Time to check stale facts or re-run the simulator |
| A new request | An agent submitted a booking that needs approval |

## What it does, end to end

| Stage | What happens | Built on |
|---|---|---|
| Ingestion | Crawl the site and read price images | Exa, with a plain crawl as backup |
| Connectors | Read connected accounts such as a calendar or price sheet | Composio |
| Interview | Ask only what's missing: "Do you go to customers' homes?" | Agent and owner chat |
| Record | Store confirmed facts, offerings, actions and rules | Our database |
| Generation | Build the resource from the record | Our code, not the model |
| Simulation | One check at onboarding: send consumer agents at the website and find what fails. The owner can run it again | [The consumer agent](08-consumer-agent-design.md) |
| Inbox | Ask for confirmations and answers, and handle requests | Owner app |
| Learning | Turn dead ends, questions and failures into owner questions | Activity log |

## Use cases

**Core:**

| Use case | Example |
|---|---|
| Plain-language updates | "Interior detail is now $200" |
| Learning from new questions | An owner's answer becomes a fact on the page |
| Guided onboarding | Reads the crawl, then asks only what's missing |
| Watching sources | Sees a new website price or a blocked calendar week and asks the owner to confirm |
| Catching contradictions | "Your website says $180, but your record says $200" |
| Checking stale facts | "Still open Sundays? You last confirmed this six months ago" |
| Preparing approvals | Checks the calendar and suggests a reply, so the owner only has to tap |
| Completing requests | After approval, creates the event and sends the confirmation and reminders |
| Drafting rules | "Ask me about anything over $500" becomes a rule |
| Running the simulator | Re-tests after each change and ranks gaps by importance |
| Demand insights | "12 agents asked for ceramic coating, which you don't offer." Moved to core after the Muse findings |

**Later:**

| Use case | Example |
|---|---|
| Fixing the owner's own site | Drafts exact wording to paste into the owner's website |
| Improving wording | Rewrites text so one snippet carries the answer, and keeps the version that tests better |

## How it learns without a front desk agent

Since no agent talks to outside agents, learning comes only from what's recorded:

| Signal | What it tells us | Limit |
|---|---|---|
| Quote inputs and dead ends | What people wanted and where it failed | Only agents that use the form |
| "Ask the business" questions | Direct gaps in the facts | Agents may not use the form. This needs testing |
| Abandoned requests | Where a request stalled | The reason is unknown |
| Page hits | What was read | Doesn't show what the agent wanted |
| Simulator failures | Gaps found before real agents hit them | Only as wide as the query bank |

For the demo, the simulator gives most of the learning. A wide [query bank](05-roadblocks-and-queries.md) is what makes it useful.

## What it can and can't do

| It can | It can't |
|---|---|
| Read sources and activity | Serve a fact the owner hasn't confirmed |
| Propose changes to the record | Change the record based on anything an outside agent says |
| Ask the owner questions | Edit the page or layout |
| Run the simulator | Run arbitrary code or use a shell |
| Complete approved requests | Approve requests itself, unless the owner has set a rule allowing it |
| Draft rules for the owner | Change a rule without the owner confirming |

The model can reason and phrase things, but code enforces the rules. Coding harnesses assume a trusted developer with a shell, so this agent gets a much narrower set of tools.

**Outside text is data.** A caller's question could try to instruct the agent that updates the record, so all caller text is treated as data, and any change requires the owner's confirmation.

## Issues to settle before building

The first two change the data model.

| Issue | Why it matters | Proposed fix |
|---|---|---|
| One-off versus permanent answers | "Yes, I can fit him in Saturday" isn't true for everyone | Owner picks "just this once" or "use for everyone" |
| Temporary facts | "Closed next week" has to end by itself | Start and end dates on facts |
| Conflicting sources | A re-crawl could overwrite what the owner said | Priority order: owner, then connected systems, then crawl |
| Late answers | The asking agent may be gone when the owner replies | Questions return a status link, just as requests do |
| Too many interruptions | Owners start ignoring questions or approving without reading | Batch and rank questions, with a daily limit |
| Owner's channel | Someone working with their hands won't open a dashboard | Let them instruct and reply by chat, text or email |
| Testing the agent itself | The simulator only tests the outward-facing side | A test set of owner instructions and the changes each should produce |

## How we'll know it works

Three tests, all from work done earlier in the plan:

1. **Answer key:** given only a mock business's website and owner data, does it produce a resource with the same facts as the hand-written one?
2. **Regression:** does the consumer agent pass the same queries on the generated resource as on the hand-written one?
3. **Instruction test:** given a set of owner instructions, does it propose the right changes, ask when something's unclear, and refuse to apply anything unconfirmed?

## What the mock data needs

Connectors need something to connect to, so each mock business needs real demo accounts, such as a Google Calendar with bookings and a price sheet. These come from the same [facts file](06-demo-businesses.md#the-facts-file) as the site and resource. We still need to check that Composio covers the services we choose.

## Harness

The harness choice is covered in [the research](07-consumer-agent-research.md) and [the design](08-consumer-agent-design.md). This agent's needs differ from the consumer agent's in three ways: it runs on events, it writes to a record, and it has strict permissions. The choice can be made separately when we get here.
