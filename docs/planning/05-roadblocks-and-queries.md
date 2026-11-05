# Roadblocks and the long tail of queries

*Last updated 5 November 2026.*

This is the catalogue used to design mock sites and test queries. The Muse van cleaning query is one data point in it, not its model. What stays constant across service types is the question the agent can't answer, so the catalogue is organised around those questions.

## The ten questions an agent can't answer

| # | The agent can't tell... | Typical cause |
|---|---|---|
| A | How to get in | Bot checks, logins, social-only presence |
| B | What the page says | JavaScript, images, PDFs, widgets |
| C | Where the fact is | Buried in FAQs, split across pages |
| D | What the words mean | The customer's words don't match the business's |
| E | What it will really cost | "Starting at", hidden fees, inspection first |
| F | Whether this case qualifies | Service area, eligibility, requirements, silence |
| G | When it can happen | No calendar, lead-time rules, staff schedules |
| H | How to make it happen | Phone only, lead forms, verification |
| I | What's true | Contradictions, stale data, third-party errors |
| J | What happened next | No confirmation, replies it can't see |

## Evidence labels

Each row says how much we actually know:

- **T:** seen in the founder's own test of Muse, summarised in [the Muse findings](02-muse-findings.md).
- **S:** stated by a source we read, linked in the [research](07-consumer-agent-research.md) or the raw notes in `research_notes/Consumer agents/`.
- **I:** our inference from general knowledge. It's plausible, but unchecked.

The agent profiles are defined in the [consumer agent design](08-consumer-agent-design.md#profiles). **Index** reads cached copies, **Fetch** does a plain request without JavaScript, and **Browser** runs a full browser.

**How strong this is:** treat rows marked I as design input, not findings.

- **Best evidenced:** blocking cookie banners, CAPTCHAs, cross-origin booking widgets and the failures seen with Muse.
- **Sourced so far, some only from search summaries:** HVAC and plumbing, movers, pet care, custom cakes, dentists, house cleaning, event venues, driving schools, vets, family lawyers and notaries.
- **Not yet researched:** auto repair, landscaping, pest control, roofing, locksmiths, physical therapy, salons, tutoring, fitness, photographers, catering, tax preparers, childcare and home health care.

## What's been measured

These are the few measured results we found. The BrowserArena figures come from a summary of the paper, not its tables.

| Finding | Source | Weight |
|---|---|---|
| On 80 tasks with a blocking cookie banner, Claude 3.7 detected it every time but closed it in only 7.5%. DeepSeek R1 never detected it, yet marked 53.75% of tasks complete | [BrowserArena](https://arxiv.org/abs/2510.02418), via its [HTML version](https://arxiv.org/html/2510.02418) | arXiv paper, one site per test |
| On 220 tasks with CAPTCHAs, agents got stuck because puzzle parts often aren't clickable page elements, and they tried workarounds such as direct links or other sites | BrowserArena | As above |
| Most of 163 working restaurant sites embedded booking in a cross-origin iframe. Only 9 had structured data, and none offered a callable booking action | [One author's test](https://dev.to/blondedevrules/why-ai-agents-cant-use-your-booking-widget-4j27) | Single author, restaurants only |
| Acuity's and Square's availability APIs need the owner's credentials, so a visiting agent has to use the widget itself | [Acuity](https://developers.acuityscheduling.com/reference/get-availability-dates), [Square](https://developer.squareup.com/reference/square/bookings-api/search-availability) | Vendor docs |
| Claude web fetch doesn't support JavaScript-rendered pages and obeys `robots.txt` | [Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) | Vendor docs |

How the other booking platforms embed, and when each asks for personal details, isn't confirmed. We'll need to check before imitating any specific one.

## A. Can't get in

*The resource clears these with a public page that needs no login. It can't remove a block on the owner's own site, only give agents another way in.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| A1 | Bot check or CAPTCHA | On page load, or on a contact form | Fetch, Browser | S |
| A2 | Crawler blocked | `robots.txt` block, or an anti-bot firewall returning degraded data | Index, Fetch | S |
| A3 | Login or client portal | Boarding dates, class schedules, member prices | All | I |
| A4 | Social-only business | Instagram or Facebook with a link page and no website | All | I |
| A5 | Pop-ups in the way | Cookie banner, newsletter modal, chat bubble covering a button | Browser | S |
| A6 | Location or age gate | "Choose your city" before prices show | All | I |
| A7 | Broken or changed site | Expired certificate, redirect loop, dead pages | All | S |
| A8 | Not in the index | New site, or a blocked crawler means it's simply absent | Index | S |

## B. Can't read it

*The resource clears these with facts in plain HTML text.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| B1 | JavaScript-only content | Empty HTML until scripts run | Index, Fetch | S |
| B2 | Prices in images | Canva flyers, menu photos, price boards | Index, Fetch | I |
| B3 | Information in PDFs | Price sheets, vaccination policies, scanned forms | Fetch, Browser | I |
| B4 | Cross-origin booking widget | A third-party iframe the page can't read into, loading its data late | All | S |
| B5 | Hidden until clicked | Accordions, tabs, "load more", hover text | Fetch | I |
| B6 | Service area as a picture | A map image with no ZIP list | All | I |
| B7 | Custom controls | Shadow DOM, canvas UI, unusual date pickers | Browser | I |
| B8 | Video-only explanation | "Watch how it works", Reels | All | I |
| B9 | Another language, or mixed | Key rules in one language only | All | I |

## C. Can't find it

*The resource clears these with one place for everything and one page per offering.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| C1 | Buried in prose | Deal-breaking requirement in an FAQ, blog or terms page | All | T |
| C2 | Unhelpful navigation | "Experiences", "Our Story", "Packages" hiding the prices | Browser | I |
| C3 | Split across pages | Base price on one, fee on another, tax at checkout | All | T |
| C4 | Cut off by the tool | A long page truncated before the fact appears | Fetch | S |
| C5 | Excerpt without context | A snippet says "$99" without saying what for | Index | S |
| C6 | Duplicate pages | Old and new service pages, location pages with copied text | All | I |

## D. Can't work out what the words mean

*The resource clears these with plain synonyms and definitions.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| D1 | Vocabulary mismatch | Customer says "AC's dead", "just a trim" or "van"; the site says "cooling diagnostic", "tidy" or "oversized" | All | T |
| D2 | Marketing tier names | "Gold", "Signature", with contents listed elsewhere | All | I |
| D3 | Unclear units | Per hour, per person, per room, per serving, per truck | All | I |
| D4 | Undefined conditions | "Heavy", "excessive", "matted", "standard home", "large dog" | All | T |
| D5 | Implicit exclusions | "Deep clean" that doesn't cover the oven or windows | All | I |
| D6 | Similar service names | "Consultation" and "evaluation" at different prices | All | I |

## E. Can't work out the real cost

*The resource clears these with stated price rules and full totals, or a range plus what's still needed.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| E1 | "Starting at" | Any service with a floor price and no drivers | All | T |
| E2 | Range without drivers | "$150–600" with no explanation | All | T |
| E3 | Quote only | "Call for pricing", "contact us" | All | T |
| E4 | Inspection first | Repair priced only after a diagnostic, and that fee may or may not be credited | All | S |
| E5 | Hidden fees | Travel, trip, disposal, fuel, materials, tax, gratuity | All | T |
| E6 | Dependent add-ons | An add-on that requires another service | All | T |
| E7 | Minimums | Minimum hours, order size, guests or spend | All | S |
| E8 | Price changes with time | After-hours, weekends, holidays, peak season | All | I |
| E9 | Price changes with staff | Senior stylist, lead groomer, partner vs associate | All | I |
| E10 | Conditional discounts | First visit, membership, seniors, multi-pet, bundles | All | I |
| E11 | Deposit vs total | Non-refundable deposits, rush fees, full payment on short notice | All | S |
| E12 | Depends on a third party | Insurance copay, or what a plan covers | All | S |
| E13 | Type of estimate | Binding, non-binding or not-to-exceed | All | S |
| E14 | First-time pricing | A first house clean priced as a deep clean, a deposit on a first vet visit | All | S |
| E15 | Fees revealed in stages | Venue fee vs food and drink minimum, catering rates after the contract, a legal retainer set after the consultation | All | S |

## F. Can't tell whether this case qualifies

*The resource clears these with explicit rules, including what isn't offered.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| F1 | Service area | ZIP limits, distance fees, "greater metro area" | All | T |
| F2 | Customer eligibility | New patients, referrals, age limits, memberships, permits | All | S |
| F3 | Subject eligibility | Breed, weight, vaccines, vehicle class, building type | All | S |
| F4 | Size limits | Largest group, height, weight, square footage | All | I |
| F5 | Prerequisites | Water and power, parking, clear access, patch test, a consultation first | All | T |
| F6 | Silence on an offering | Can't distinguish "we don't do that" from "we didn't list it" | All | T |
| F7 | Special needs | Allergies, accessibility, language, anxious pets, sedation | All | S |
| F8 | Credentials | Licence, insurance, bonding, certifications | All | I |
| F9 | Outside rules | HOA, landlord permission, permits, local regulations | All | I |
| F10 | A document the customer must hold | Learner's permit, rabies record, valid photo ID | All | S |

## G. Can't tell when

*The resource clears these with availability or lead-time rules visible without personal details.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| G1 | No calendar | A free-text "preferred date" box | All | T |
| G2 | Calendar behind a lead form | Name, address and phone before any dates appear | Browser | T |
| G3 | Widget-only availability | Data from an internal API, needing a session or token | All | S |
| G4 | Lead time unstated | Two weeks' notice, or order cut-offs, only in an FAQ | All | S |
| G5 | Stale or scattered hours | Holiday closure only in a banner image or social post | All | I |
| G6 | Staff-specific schedule | Only one person does this service, on set days | All | I |
| G7 | Seasonal limits | Blackout dates, waitlists, "booked until March" | All | I |
| G8 | Urgency unstated | "Call for emergencies", with no response time or same-day rule | All | I |
| G9 | Windows and duration | "Between 8 and 12", or how long the job takes | All | I |
| G10 | Capacity | A class full, or a waitlist | Browser | I |
| G11 | Date and timezone | Relative dates, or a service in another timezone | All | T |

## H. Can't make it happen

*The resource clears these with a structured request that needs personal details only at booking, and a prefilled link for agents that can't submit forms. Phone-only businesses still need the owner to accept requests another way.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| H1 | Phone only | "Call to book" with no other option | All | T |
| H2 | Contact form only | No promise of what happens or when | Browser | T |
| H3 | Long lead form | Many steps of personal details before any value | Browser | T |
| H4 | Fields an agent can't fill | Photos, exact measurements, or a signature | Browser | I |
| H5 | Card to hold | Payment details needed to reserve | Browser | I |
| H6 | Fragile forms | Dynamic fields, odd validation, custom date pickers | Browser | S |
| H7 | Submission unclear | A silent failure, or confirmation inside a widget | Browser | S |
| H8 | Verification | SMS or email code | Browser | I |
| H9 | Account required | Sign up before booking | Browser | I |
| H10 | Redirect to a marketplace | Thumbtack or Yelp handles the lead | Browser | I |
| H11 | Tool can't submit | The agent can read but can't make a POST request | Index, Fetch | S |
| H12 | Needs the person | A waiver, consent or terms to accept | Browser | I |

## I. Can't tell what's true

*The resource helps with a single dated source. It can't fix other sites, so a wrong listing elsewhere stays wrong.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| I1 | Third-party contradiction | A directory lists a service or price the business doesn't offer | All | T |
| I2 | Site contradicts itself | Home page and FAQ disagree, or an old blog post lingers | All | I |
| I3 | No date | No way to tell if a price is current | All | T |
| I4 | Expired offers | A promotion banner from last year | All | I |
| I5 | Stale index | The agent's copy is days or weeks old | Index | T |
| I6 | Chain vs local | National pricing on a franchise's local page | All | I |
| I7 | Business status | Moved, renamed, closed or under new owners | All | I |

## J. Can't close the loop

*The resource clears these with a status page per request and a clear statement of what happens next.*

| ID | Roadblock | Examples | Hits | Evidence |
|---|---|---|---|---|
| J1 | "We'll call you" | The answer arrives by phone, and the agent never sees it | All | I |
| J2 | Unclear commitment | "Request received", where nothing says if it's booked | All | I |
| J3 | Slot not held | The slot may be gone by the time the person approves | All | S |
| J4 | No way to change | Rescheduling or cancelling means a phone call | All | I |
| J5 | Policy unclear | Cancellation windows that differ by booking type, emergency exemptions, refunds, or what happens if it rains | All | S |
| J6 | Agent invisible to owner | The owner can't tell an agent sent it, or who for | All | T |

## Limits on the agent's side

These aren't roadblocks on the site, but they shape what a fair test looks like. Each has a counterpart in the [consumer agent's rules](08-consumer-agent-design.md).

| Limit | Why it matters |
|---|---|
| Won't share personal details without approval | Stops at lead forms by design, so availability has to come before personal details |
| Step, token and time budgets | A hard site can run out the clock without any single failure |
| Wary of instructions on pages | Text that gives orders may be ignored or treated as an injection |
| Trusts the merchant over listings | Only if it can tell which is the merchant's own site |
| Can be overconfident | May report something that didn't happen, such as closing a banner, so results need checking |
| Sees only part of the page | browser-use lists only interactive elements in the visible viewport by default, so facts lower down need scrolling or a page search |

## The long tail of queries

The queries have to be as wide as the roadblocks. A resource that only works for questions seen in advance proves nothing.

### Query types

The examples here are illustrative, not real customer wording. See [Real customer questions](#real-customer-questions) for what we have on that.

| Type | What it tests | Examples |
|---|---|---|
| Direct fact | Basic legibility | "Are you open Saturday?" |
| Messy description | Vocabulary mapping | "The thing on my wall is blinking and the house is 85 degrees" |
| Total under a cap | Price arithmetic | "All-in, under $300?" |
| Many constraints at once | Combining facts | "Nut-free cake for 40, Saturday pickup, under $200" |
| Eligibility | Rules applied to a case | "Will you board a 90 lb dog who had shots yesterday?" |
| Missing document | Rules tied to something the customer must hold | "My ID expired last month. Can you still notarize this?" |
| First-time status | Rules that differ for new customers | "Why does my first clean cost more?" |
| Not offered | Correct "no" | "Do you repair commercial freezers?" |
| Unknown | Admitting gaps | Anything the facts file marks as undecided |
| Urgent | Time rules | "Water's coming through the ceiling, can someone come tonight?" |
| Edge of a rule | Exceptions | "I'm 2 miles outside your area, can you still come?" |
| Choosing | Recommending within one business | "Which package fits a one-bedroom, moving out Friday?" |
| Policy | Rules on change | "What if I cancel the day before?" |
| Credentials | Trust facts | "Are you licensed and insured in this county?" |
| Logistics | Prerequisites | "I'm in an apartment with no driveway. Does that work?" |
| Recurring | Repeat service | "Every two weeks, and is there a discount?" |
| More than one | Group or multi-item | "Three dogs, same day. What's the total?" |
| Personal circumstance | Special needs | "My dog is terrified of dryers" |
| Wrong premise | Correcting a false belief | "Yelp says it's $50. Can I get that?" |
| Payment | Methods and timing | "Cash? Financing? Is the deposit refundable?" |
| Conditional | Logic the agent must keep | "Add it only if the total stays under $200" |
| What's needed | Discovering the requirements | "What do you need from me to quote this?" |
| Take the action | Completing a request | "Book the earliest slot, and check with me first" |
| Follow up | The status page | "Did they confirm my request?" |
| Another language | Language handling | The same request written in Spanish |

### Real customer questions

**We don't have verbatim customer questions yet.** Our searches didn't surface usable text from Reddit, Yelp, Thumbtack or Angi. What we have are topics paraphrased from business policy pages, FAQs and forum threads, mostly seen only as search summaries:

| Service | Question topic (paraphrased) |
|---|---|
| House cleaning | Why is the first visit more expensive? Can I skip a one-time clean without a fee? Do I need to restrain my dog? |
| Event venues | Does the food and drink minimum include tax and service? Can I see catering rates before signing? |
| Driving schools | Can a 15-year-old start before holding a permit for 6 months? What if I forget my permit on lesson day? |
| Vets | Will you see my cat without earlier vaccine records? Is the reservation fee refundable in an emergency? |
| Plumbing | How much is a visit? Is a quote fee normal? |
| Custom cakes | How far in advance should I order? |
| Dog grooming | Do you handle aggressive or anxious pets? |
| Lawyers and notaries | Is the retainer refundable if I stop mid-case? Is the travel fee capped? |

**Before finalising the query bank,** we need one of: a proper pass through real Q&A sources, or real queries the founder runs on Muse.

**Patterns so far (our inference):**

- Many rules depend on whether the customer is new.
- Fees come in parts, and each part is disclosed at a different time.
- Eligibility is often tied to a document the customer has to hold.
- Cancellation windows differ by booking type, and emergencies are often exempt.
- A good test combines a customer fact with a gate: "She's 15 and a half and has had her permit for 4 months."

### How a query bank is built

- **Per business:** about 30 queries to start, across all the types above. Anthropic's guidance suggests 20–50 tasks as a starting point.
- **Each query records:** its type, the roadblock IDs it touches, the correct answer from the facts file, and how it's graded.
- **Written separately:** whoever writes queries sees only the facts file and the customer's point of view, never the resource.
- **Real wording:** use real customer questions as a base wherever we have them.
- **Held-out set:** keep about a third of the queries unseen until the final test, so a fix can't simply target known questions.
- **Include "no" and "unknown":** so an agent isn't rewarded for guessing.

**First demo:** the benchmark is 12 queries in `bench/queries.json`, written by a fresh subagent from the facts file with its site placement data removed. All 12 act as held-out queries. The founder's sample detailing queries are in `bench/discovery_seeds.json`. They seed the discovery set and were used only to check the agent on the control page, and the query writer never saw them.

### How answers are graded

| Outcome | Meaning | Counts as |
|---|---|---|
| Verified correct | Matches the facts file, with a source | Pass |
| Honest unknown | Correctly says the fact isn't available, and says what to do next | Pass |
| Correct but unsourced | Right answer, but no evidence | Partial |
| Gave up | Tells the person to call although the answer was available | Fail |
| Wrong | A confident answer that doesn't match | Fail |
| Invented | States something with no source at all | Fail, and flagged |
| Unsafe | Shared personal details or took an action without approval | Fail, and flagged |

Grade in code wherever possible, by exact match on the answer or a check of the form submission. Use a model as judge only for free text, with "unknown" as an option, and check a sample by hand.

The first demo's grader (`bench/grade.py`) works in code only and reports two rates, because "I can't tell" is honest on a site that hides a fact but doesn't help the customer:

- **Correct:** the right answer with a source from the merchant's own pages.
- **Acceptable:** correct, or an honest unknown where the fact really wasn't reachable on that version of the site.

### How much to run

Every query, profile, site version and repeat multiplies quickly. Thirty queries, three profiles, two versions and three repeats is 540 runs per business. A proposed way to keep it manageable:

- **Wide pass:** all queries, once per profile and version, to find what breaks.
- **Deep pass:** the 5–10 demo queries, 10 times each, for the pass rates we quote.

Report pass@k (any of k runs succeeds) and pass^k (all k succeed), since a 75% success rate means only about 42% of sets of three all pass.

## Coverage by demo business

| Category | Detailing | HVAC and plumbing | Pet care | Cakes and catering |
|---|---|---|---|---|
| A. Get in | Pop-ups | Bot check on form | Client portal | Social-first |
| B. Read | Map image | JavaScript-only | Iframe, PDF | Images, scanned PDF |
| C. Find | FAQ | Separate pages | Pop-up rules | Long FAQ |
| D. Meaning | Size tiers | Symptoms to services | Coat and size terms | Design tiers |
| E. Cost | Add-ons, conditions | Diagnostic, after-hours | Staff level, matting | Per serving, minimums, rush |
| F. Qualifies | Prerequisites, area | ZIP, brands, licence | Vaccines, breed, temperament | Allergens, delivery zone |
| G. When | Lead form gate | Urgency, windows | Blackouts, minimum stays | Lead time, closures |
| H. Act | Lead form | Phone, lead form | Widget, account | Form builder, deposit |
| I. True | Wrong listing | Old blog post | PDF vs page conflict | Instagram vs site |
| J. Next | No status | "We'll call you" | Unclear booking state | Manual reply |
