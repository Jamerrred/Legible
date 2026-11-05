# Roadblock evidence: what stops agents on small service-business sites

Research was time-boxed (about 5 minutes, a handful of searches and 4 page fetches). Tags: [SOURCE] = stated by a page I read or by search-result text; [INFERENCE] = my reasoning. Much of the search output was low-quality SEO content; I flag that where it matters.

## Technical roadblocks (with evidence)

1. Cross-origin iframe booking widgets. [SOURCE] Dev.to post by one author (single-author account, method details external): a browser agent was pointed at 200 Amsterdam restaurant venues (163 working sites) with the task "check availability for a real date and party size and reach the final booking step" (no bookings submitted). Most venues embedded booking as a cross-origin iframe. Same-origin policy blocked the parent page from the widget's DOM; fields loaded asynchronously; availability came from an internal API the agent had no token for; confirmations appeared inside the iframe or as redirects. Clicking through sometimes works only if elements are stable and no CAPTCHA or automation detection fires; the author gave no rate.
   https://dev.to/blondedevrules/why-ai-agents-cant-use-your-booking-widget-4j27
2. No machine-readable booking action. [SOURCE, same post] Only 9 of 163 sites had structured data, all Restaurant/LocalBusiness schema from SEO plugins describing the venue, not how to book. No site published a callable booking action (schema.org ReserveAction exists). In a ChatGPT test, ChatGPT read and understood prose API docs on a plain HTML page but said its web tool could not make a POST request. (One anecdote.) A reader comment (not author) noted availability is effectively a quote, so booking APIs need hold/confirm/idempotency.
3. JavaScript-rendered content and async state. [SOURCE, search summary of practitioner posts; I did not open the Tian Pan page, it returned HTTP 503] Load events fire before React data arrives, so agents act on unloaded content or time out. Treat as practitioner opinion, not measurement.
4. Bot detection, CAPTCHA, fingerprinting. [SOURCE] TinyFish dev.to post (vendor marketing, self-reported numbers): protection checks IP reputation (datacenter ranges flagged), TLS fingerprint, HTTP/2 header ordering, headless-browser signals, timing (e.g. click 40ms after navigation), then CAPTCHAs. Says some systems silently return degraded data. No failure rates for unmanaged agents given.
   https://dev.to/tinyfishie/why-web-agents-fail-on-protected-sites-and-how-to-fix-it-at-the-infrastructure-level-12oe
5. CAPTCHAs and pop-up banners. [SOURCE] BrowserArena abstract (arXiv 2510.02418), a live open-web agent evaluation, names three failure modes: CAPTCHA resolution (o4-mini tries more strategies than others), pop-up banner removal (DeepSeek-R1 misleads users about whether a banner was closed), and direct URL navigation. Abstract gives no numbers. https://arxiv.org/abs/2510.02418
6. Brittle selectors, scripted clicks failing. [SOURCE, search summary of a Webfuse blog, not opened] Framework-generated IDs/classes change; programmatic clicks can fail even when the element is found.
7. Benchmark-vs-reality gap. [SOURCE, secondhand, unverified] Blogs claim 20-30% success on unseen sites and 50-60% real-world vs 90%+ on curated benchmarks; I could not trace the primary sources. Do not cite without checking.
8. Not found / not verified: shadow DOM, PDFs, prices in images, Instagram/Facebook-only businesses, login walls, phone-only flows. No evidence gathered. [INFERENCE] These are plausible blockers for a text-reading agent (a PDF menu or price list embedded as an image yields no text; a phone-only quote yields nothing an agent can complete), and are easy to mock, but I have no source here.

## Booking and lead-form systems

- Searched for OpenTable, Toast, Square Appointments, Calendly, Acuity, Mindbody, Vagaro, Booksy, Housecall Pro, Jobber, ServiceTitan agent accessibility. [SOURCE] Found no vendor documentation or independent test on whether these embeds are agent-readable. Only evidence is the Amsterdam restaurant iframe write-up above (vendors there not named in what I read).
- [SOURCE] Chatbot vendor guides (socialintents, chatling) show Calendly and Cal.com embedded inside chat via iframe; these describe human UX, not agent access.
- [SOURCE] Serviceform markets an API that returns an embed snippet plus iframe fallback (vendor claim).
- [INFERENCE] Most of the named platforms are widgets loaded by a script tag into an iframe or injected DOM, so the same-origin and async problems likely apply, but this is untested by me. Multi-step lead forms (name, address, photos, then "we'll call you") are a distinct mock: agent can fill but cannot get a price or confirmation.

## Information gaps by vertical cluster

Tags: [S] = I read a source saying this; [I] = my inference from general knowledge, unsourced.

| Cluster | What buyers need that sites often omit | Evidence |
|---|---|---|
| HVAC, plumbing, electrical, appliance repair | Diagnostic or trip fee amount; whether fee is credited toward repair; hourly vs flat; after-hours/emergency surcharge; service area; licence number | [S] ServiceTitan blog: fee commonly credited if repair approved, typical ~$75-150; ServiceExperts: some charge diagnostic regardless of whether you proceed; some firms advertise $0 diagnosis. Roto-Rooter blog argues plumbers should not quote by phone without inspection (company self-interest). Reddit threads (via search summary, not opened): quote fees $25-$100, sometimes credited, fine "if disclosed". Cost guides on low-authority sites conflicted, not usable. Surcharge/licence/area: [I] |
| Movers | Binding vs non-binding vs not-to-exceed estimate; hourly minimum; travel/stairs/long-carry fees; inventory-based pricing | [S] Multiple moving-industry pages: non-binding is approximate and final cost often higher; binding is guaranteed if inventory unchanged; some charge to prepare binding estimate; FMCSA expects written estimates. Hourly minimums/travel fees: not found |
| Locksmiths | Total price vs "service fee"; licensing; real local address | Not sourced (search returned nothing). [I] common pattern of low phone quote then higher bill |
| Dog grooming, boarding | Vaccines (rabies, DHPP, Bordetella, sometimes canine flu), waiting period after shots, breed limits, temperament/aggression policy, sedation, size-based pricing | [S] Boarding facility pages: vaccine lists, 48-72h wait after new vaccination at some; breed restrictions vary (one FL resort none, one UT facility excludes several bully breeds and Cane Corso, wolf hybrids commonly excluded); one groomer FAQ says accepts biters but some dogs too risky; another notes sedation sometimes needed |
| Custom cakes, bakeries | Lead time, rush fee, deposit, allergen handling, pickup vs delivery, order cut-offs | [S] Bakery FAQs: 2-4 weeks typical, rush fee ~$20-35 at one shop, 50% non-refundable deposit common, some require full payment for short notice, one bakery advertises same-day (so varies). Note: these were FAQ pages, i.e. info exists as prose on the page |
| Dentists, medical | Which insurance plans, new-patient acceptance, emergency slots | [S] Many sites say "call to confirm" insurance; some say accepting new patients without naming plans; directory pages say "accepts insurance" with no plan names |
| Auto repair, detailing, house cleaning, landscaping, pest control, roofing | Quote-after-inspection, size/condition tiers, add-ons (pet hair), recurring vs one-off, seasonal availability, materials not included | [I] only, no sources gathered |
| Vets, PT, salons, barbers, tutoring, driving schools, yoga, photographers, venues, catering, restaurants, tax, lawyers, notaries, childcare, home health | Staff-specific pricing/availability, new-patient/referral rules, cancellation windows, minimum guest counts, deposits, age/eligibility, language, insurance | [I] only, no sources gathered |

[I] Cross-cutting pattern worth mocking: price as a range with conditions ("starting at"), price that depends on an inspection, eligibility gates (vaccines, insurance, age), lead time and deposit rules, and "call us" for anything non-standard.

## Real long-tail question examples

Thin. Searches for Yelp "Ask the community", Thumbtack and Reddit questions returned no actual user questions I could quote (results were mostly SEO pages). What I did get:
- [S, paraphrased] "How much do you get charged for a plumber visit?" (r/Chambana thread title seen in results, not opened). "Is a quote fee normal?" (Reddit, via search summary).
- [S, paraphrased] FAQ-style questions on pages I saw in results: "How far in advance should I place my order?" (cake shops); "Do groomers handle aggressive or anxious pets?" (vetpi FAQ); vaccination and breed restriction FAQs on boarding sites.
- [I] Illustrative long-tail form for the demo (not sourced): "can you groom a 90 lb dog that bites", "do you do same-day cake pickup with nut-free", "is the callout fee waived if I hire you", "do you take Delta Dental for a new patient on Saturday".

## Gaps in this research

- No primary evidence on shadow DOM, PDFs, image-only prices, social-only businesses, login walls, cookie banners (beyond BrowserArena naming pop-ups), or phone-only flows.
- No vendor-level evidence for Square, Calendly, Acuity, Mindbody, Vagaro, Booksy, Housecall Pro, Jobber, ServiceTitan, Toast, OpenTable.
- Tian Pan and WebGym pages not read; "20-30% / 50-60%" success figures unverified.
- Most vertical rows (and every cluster beyond HVAC/plumbing, movers, pets, cakes, dentists) are inference.
- No actual Yelp/Thumbtack/Angi/Reddit question text retrieved; Reddit threads seen only in search summaries.
- Time limit was applied; next step would be targeted fetches of the BrowserArena PDF, vendor embed docs, and Reddit/Thumbtack Q&A pages.
