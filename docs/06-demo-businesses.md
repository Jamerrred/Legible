# Demo businesses

*Last updated 4 November 2026. These are proposals. All names and details will be fictional.*

## How they were chosen

The four businesses aren't four versions of the same thing. Each one fails for different reasons, so together they exercise most of the [roadblock catalogue](05-roadblocks-and-queries.md).

Each is medium complexity: enough rules and options to defeat a quick read, but small enough for one person to check every fact.

| | 1. Mobile vehicle detailing | 2. HVAC and plumbing | 3. Pet grooming and boarding | 4. Custom cakes and catering |
|---|---|---|---|---|
| **How price works** | Size tier + add-ons + condition | Diagnostic fee, then a quote | Breed, weight and coat; staff level | Per serving, design tier, minimums |
| **Main question** | "What will it really cost, and when?" | "Can someone come, and what will I pay?" | "Will you take my pet?" | "Can you make this by then?" |
| **Main action** | Book | Dispatch or quote | Book after eligibility is met | Custom order with deposit |
| **How the site blocks agents** | Lead form before calendar | Phone first, JavaScript-only widget | Third-party iframe, rules in a PDF | Prices in images and a PDF, social-first |
| **What "unknown" looks like** | Surcharge for "excessive" hair | Repair cost before inspection | A dog that needs a temperament check | A design that needs a consultation |

## 1. Mobile vehicle detailing

**Why first:** the founder's real Muse run gives us a baseline to compare against. The queries go well beyond vans and pet hair, covering boats, fleets, odour, paint correction, apartment parking and gift cards.

**Roadblocks on the site:**

- Marketing tier names, with vehicle sizes that don't match customer words
- "Starting at" prices, with add-ons that require another service
- Undefined conditions, such as "excessive" hair or "heavily soiled"
- Water and power requirements buried in an FAQ
- Service area shown as a map image, with a travel fee mentioned elsewhere
- Calendar behind a name, address and phone form
- A mock third-party listing that shows a wrong, older price

## 2. HVAC and plumbing

**Why:** urgent, inspection-priced work, where a total can't be known up front. It tests whether an agent can report a range and a process honestly.

**Roadblocks on the site:**

- No prices at all on the service pages, and the diagnostic fee appears only in an FAQ
- Unclear whether that fee is credited toward the repair
- After-hours and weekend rates in a separate page
- Service area by ZIP code in a page that only renders with JavaScript
- "Call now" for emergencies, with no statement of response time
- A multi-step lead form asking for address, system age and photos, ending in "we'll call you"
- Brand and system limits unstated, along with licence details
- A maintenance plan discount with conditions

## 3. Pet grooming and boarding

**Why:** eligibility decides everything, with several independent rules and a third-party booking widget.

**Roadblocks on the site:**

- Booking inside a cross-origin iframe widget
- Vaccination rules in a PDF, including a waiting period after new shots
- Breed and weight limits in a pop-up or image
- Temperament policy, sedation and matting surcharges mentioned only in passing
- Prices by size, coat and groomer level
- Holiday blackout dates and minimum stays on boarding
- A client portal login needed to see boarding availability
- New-client requirements, such as a trial day

## 4. Custom cakes and catering

**Why:** a custom, lead-time business that runs on images and social media, which is common across the long tail.

**Roadblocks on the site:**

- Price sheet as an image and a scanned PDF
- Instagram as the main gallery, with key updates posted only there
- Lead times and order cut-offs in a long FAQ
- Per-serving pricing, minimum orders and design tiers
- Allergen handling stated vaguely
- Delivery zones and setup fees unclear
- Non-refundable deposit, with rush fees
- An embedded third-party form builder, ending in a manual reply
- Seasonal closure announced only in a banner image

## What these four don't cover

These can be added as variations or extra businesses later:

| Gap | Example business |
|---|---|
| Insurance-dependent pricing | Dentist, physical therapy |
| Class schedules, capacity and packages | Yoga studio, driving school |
| Professional conflicts and jurisdiction | Lawyer, notary, tax preparer |
| Multi-location or franchise pricing | National chain's local branch |
| Seasonal capacity and large-event minimums | Event venue |
| Regulated eligibility and waitlists | Childcare, home health care |

Insurance and health-related examples add real sensitivity, so they're a deliberate later choice.

## The facts file

Each business has one facts file, written before anything else. It's the single source of truth for the test.

| Used by | For |
|---|---|
| The "before" site | What gets published, partly hidden, or left out |
| The hand-written resource | What the resource states |
| The grader | The correct answer to each query |
| Demo accounts | Calendar and price sheet content for Composio |
| The back office agent's test | The answer key for what it should extract |

**It contains:** offerings, price rules, add-ons and their dependencies, defined conditions, eligibility, prerequisites, service area, staff differences, policies, hours, blackout dates and availability rules.

**Each fact also records:** where it appears on the "before" site (plain, hidden and how, or absent).

**Availability is generated, not written by hand.** Requests such as "in the next 2 days" depend on today's date, so slots need to roll forward. Otherwise the test goes stale.

**Some facts stay unknown on purpose.** The owner may not have decided, or the answer may truly depend on an inspection. These test whether an agent admits what it doesn't know, and they give the back office agent something real to ask about.

## Making a "before" site look real

- Build it the way a small business would: a template look, stock photos and uneven writing.
- Use the same third-party patterns real sites use. Where we can't embed a real platform, imitate the mechanics, such as a cross-origin iframe on another domain.
- Don't make it absurdly bad. A roadblock should be something a reasonable owner would do without thinking about agents.
- Use fictional names, and no real addresses or phone numbers.
