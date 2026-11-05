# Consumer agents at the business front door (state as of 3 November 2026)

Reading key. Unmarked sources are pages I opened. "(summary)" means the claim comes from a search-result summary and I did not open that page, so check it before quoting. "(vendor)" means the source sells something related. Status tags are SHIPPED, BETA, ANNOUNCED and DRAFT. Pages that refused my fetch are listed in the Gaps of the question they affect. The search budget ran out near the end of the session, so a few conflicts stay open and are flagged.

## What is "Muse" from Meta, and what does Meta offer businesses to be reachable by it?

### Takeaway
Muse is a real, shipped consumer agent: a Meta-hosted cloud VM with its own browser, launched 8 Sept 2026, with more than 10M US and Canadian users by late October. It reaches businesses through a connector if one exists and otherwise by driving Chromium on the business's website, plus a beta phone-calling feature. Meta's offer to small businesses is thin and indirect: Meta Business Agent (a separate product), a connector program with no stated long-tail path, and a draft protocol.

### Cited Findings

**Product and dates**
- SHIPPED 8 Sept 2026: Muse launched as a personal agent, rolling out in the US on iOS, Android and muse.ai, with direct chat in WhatsApp; the post was updated 30 Sept — [Meta newsroom](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)
- Model lineage: Muse Spark debuted 8 Apr 2026 as the first major model after the Alexandr Wang deal (summary) — [CNBC](https://www.cnbc.com/2026/04/08/meta-debuts-first-major-ai-model-since-14-billion-deal-to-bring-in-alexandr-wang.html)
- Pricing at launch: free tier, Power at $20/month, Maximum at $100/month; a payment card is required to start, and Meta expects most people to stay free — [TechCrunch, 8 Sept 2026](https://techcrunch.com/2026/09/08/meta-debuts-its-muse-ai-agent-will-consumers-trust-it/)
- Scale: more than 10M users in the US and Canada; over 25% of weekly actives engage in shopping, the leading use case; document dated 26 Oct 2026 — [Meta SEC FWP](https://www.sec.gov/Archives/edgar/data/0001326801/000119312526431036/d116268dfwp.htm)
- About 25% of people who set up Muse use it daily, and over a quarter of engaged shoppers had an average purchase above $200 — [TechCrunch, 21 Oct 2026](https://techcrunch.com/2026/10/21/meta-says-muse-has-over-10m-users-with-shopping-a-top-activity/)
- Region conflict: Meta's launch post says US only, the 26 Oct filing says US and Canada, and a related headline on Meta's post mentions Singapore without detail — [Meta newsroom](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/); [Meta SEC FWP](https://www.sec.gov/Archives/edgar/data/0001326801/000119312526431036/d116268dfwp.htm)

**Surfaces**
- SHIPPED: Muse app, muse.ai, WhatsApp chat. Instagram and Facebook are not listed as places to talk to Muse — [Meta newsroom](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/); [TechCrunch, 8 Sept 2026](https://techcrunch.com/2026/09/08/meta-debuts-its-muse-ai-agent-will-consumers-trust-it/)
- ANNOUNCED 23 Sept 2026 (Connect), no firm dates: glasses with a wake word ("coming months"), control of Mac desktop apps, a dedicated Muse email address ("soon"), a realtime avatar — [TechCrunch, 23 Sept 2026](https://techcrunch.com/2026/09/23/everything-new-coming-to-metas-ai-agent-muse/)
- ANNOUNCED 23 Sept 2026: Muse Charm, a palm-sized device — [Wikipedia, citing Bloomberg](https://en.wikipedia.org/wiki/Muse_(AI_agent))

**Can it act on third-party sites and transact?**
- SHIPPED: yes. The order of preference is built-in connector, then a public API with user-supplied credentials, then the browser if there is no API — [TechCrunch, 8 Sept 2026](https://techcrunch.com/2026/09/08/meta-debuts-its-muse-ai-agent-will-consumers-trust-it/)
- SHIPPED: Muse opens browsers, fills forms and negotiates inside Muse Secure VM. A separate Sentinel agent gates internet traffic, and Muse asks before sensitive actions such as email or purchase — [Meta newsroom](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)
- SHIPPED: checkout through Link by Stripe with a one-time card number — [Meta newsroom](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)
- Status unclear: Shop Pay was "coming soon" in Meta's post, while the 23 Sept coverage lists Shopify catalog access, Shop Pay and PayPal without saying what is live — [TechCrunch, 23 Sept 2026](https://techcrunch.com/2026/09/23/everything-new-coming-to-metas-ai-agent-muse/)
- Sanctioned connectors with Walmart, Best Buy, Wayfair, Sephora and Dick's Sporting Goods exist, but many are early-stage or not yet live (Jefferies, 8-9 Oct 2026) — [Proactive Investors](https://www.proactiveinvestors.com/companies/news/1099848/meta-s-muse-ai-agent-blocked-by-one-third-of-websites-tested-jefferies-says-1099848.html)
- Plaid's connector is part of Muse shopping, and Plaid told Meta it had not seen comparable activity on any other service (Zuckerberg's account, Oct 2026) — [TechCrunch, 21 Oct 2026](https://techcrunch.com/2026/10/21/meta-says-muse-has-over-10m-users-with-shopping-a-top-activity/)
- BETA calling: a Muse engineer posted on 16 Sept that the outbound-calling beta had expanded to US businesses. 404 Media (22 Sept) reported a human call-centre layer completing some calls, testers told only afterward, and businesses hanging up on the agent. Meta says it will launch calling only when ready, with disclosures — [404 Media](https://www.404media.co/meta-tests-muse-ai-agent-calls-that-are-actually-made-by-humans-in-a-call-center/)
- Meta's business-model statement: take a percentage of commerce. Zuckerberg also described a future "Muse network" where buying means talking to a seller's agent rather than visiting a site (vision, not shipped) — [TechCrunch, 21 Oct 2026](https://techcrunch.com/2026/10/21/meta-says-muse-has-over-10m-users-with-shopping-a-top-activity/)

**What Meta offers businesses**
- Meta Business Agent: launched 3 June 2026 at Meta's Conversations event; secondaries conflict on global availability versus select businesses with a waitlist (summary; which page says which was not checked) — [TechWyse](https://www.techwyse.com/news/platform-updates/meta-business-agent-global-launch-whatsapp-instagram); [Performance Marketing News](https://performancemarketingnews.com/updates/meta-business-agent-whatsapp-instagram-paid-tiers)
- Usage: more than 2M businesses use Business Agent weekly with over 30M conversations a week; regions not stated; document dated 26 Oct 2026 — [Meta SEC FWP](https://www.sec.gov/Archives/edgar/data/0001326801/000119312526431036/d116268dfwp.htm)
- Knowledge inputs per Meta's docs: Business Info, FAQs, Websites (URLs that it crawls and re-ingests periodically), and Files, plus Connectors that call external APIs. Catalog is not listed as a knowledge source; catalog orders appear only as a message type. The page references WhatsApp only and does not address answering other AI agents — [Meta developer docs](https://developers.facebook.com/documentation/meta-business-agent/capabilities)
- Pricing reported by secondaries: free until 31 July 2026, then token-based (about $2 per million tokens on the WhatsApp Business Platform), and a Meta One plan from $14.99/month for small businesses; Meta has not published full per-tier quotas (summary across several explainers; per-page attribution not checked, and Meta's own pricing page was not retrieved) — [IntelliConcierge](https://www.intelliconcierge.com/blog/meta-business-agent-pricing-what-whatsapp-businesses-need-to-know-in-2026); [Robylon](https://www.robylon.ai/blog/meta-business-agent)
- Muse connector program: Meta opened it to developers and received more than 1,500 applications in under a week; Wang said Meta wants Muse to serve small businesses (stated goal, no mechanism) — [TechCrunch, 23 Sept 2026](https://techcrunch.com/2026/09/23/everything-new-coming-to-metas-ai-agent-muse/)
- Meta's published steering options (6 Oct 2026): website guidance on preferred flows, connectors or skills for scale, pointers to structured sources such as real-time inventory, and business agents that answer Muse directly. Meta argues this cuts latency and errors compared with interpreting help articles. It also argues that blocking the agent blocks the customer — [Meta for Business](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together)
- Muse self-limits: its two pre-action tests ask whether one honest person would do this by hand, and whether the system would hold if every agent did it — [Meta for Business](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together)
- A vendor blog (25 Sept, updated 13 Oct) says Meta has not announced that Muse will open chats with business accounts on WhatsApp or Messenger (vendor) — [ChatMaxima](https://chatmaxima.com/blog/meta-muse-ai-agent-businesses-whatsapp-messenger/)

### Inferences
- Muse is two separate products for a small business: an unannounced browser visitor to its site, and a possible future counterpart to its Business Agent. Today only the first is real at scale.
- The Business Agent "Websites" knowledge source is the most concrete shipped hook for Legible: a resource published as a crawlable URL could feed a business's agent now, whatever happens with Muse-to-business-agent routing.
- Wang's small-business goal plus 1,500 connector applications suggests a connector-aggregator role may be possible, but nothing I found confirms Meta would accept one that speaks for many small businesses.

### Gaps
- Whether Muse queries a business's Meta Business Agent or Commerce Manager catalog today. I found no evidence that it does.
- The relationship between the existing Meta AI app and the Muse app. The sources I opened treat Muse as its own app and did not address this.
- Meta's own launch post for Business Agent and its pricing page were not retrieved.
- Connector admission criteria and whether small businesses can apply.

## What is "Instinct" in this context?

### Takeaway
High confidence: the founder means Instinct (instinct.com), a San Francisco personal agent from Spear Street Technology led by ex-Sierra researcher Noah Shinn. It is invite-only and works by text or phone through a persistent cloud computer. I found no other consumer agent by that name, and the search for variants was limited.

### Cited Findings

**Candidate ranking**
1. Instinct by Spear Street Technology. It is named alongside Muse in the launch coverage, in Fortune's framing as a challenger to Meta, and as a Personal Agent Protocol partner — [TechCrunch, 8 Sept 2026](https://techcrunch.com/2026/09/08/meta-debuts-its-muse-ai-agent-will-consumers-trust-it/); [Fortune, 30 Sept 2026](https://fortune.com/2026/09/30/noah-shinn-instinct-ai-assistant-meta-muse-alexandr-wang-tech-series-c-ai-agent-mark-zuckerberg/); [Sierra, 9 Oct 2026](https://sierra.ai/blog/poppy)
2. No second candidate surfaced. See Gaps.

**Facts**
- Product: an assistant you text or call, which uses a phone and a computer the way a person does; examples include groceries, train bookings, flowers and finding a tennis court. The site shows no developer, API or business page (fetched 3 Nov 2026) — [instinct.com](https://instinct.com/)
- Company: operated by Spear Street Technology in San Francisco, founded by a small team led by Shinn, formerly a Sierra research scientist — [TechCrunch, 24 Aug 2026](https://techcrunch.com/2026/08/24/instincts-powerful-ai-assistant-is-raising-privacy-and-security-concerns/)
- Date conflict: Forbes via Vellum says the entity was registered in April 2026, while Fortune says founded in 2025 with a private beta in February 2026 — [Vellum, 20 Aug 2026](https://www.vellum.ai/blog/official-instinct-breakdown) (vendor); [Fortune](https://fortune.com/2026/09/30/noah-shinn-instinct-ai-assistant-meta-muse-alexandr-wang-tech-series-c-ai-agent-mark-zuckerberg/)
- Funding: $250M at $2.5B (Aug 2026), then $1B at $10B from Sequoia, Benchmark and Coatue (28 Sept 2026) — [Fortune](https://fortune.com/2026/09/30/noah-shinn-instinct-ai-assistant-meta-muse-alexandr-wang-tech-series-c-ai-agent-mark-zuckerberg/); [Yahoo Finance](https://uk.finance.yahoo.com/news/ai-agent-startup-instinct-hits-180810275.html)
- Status: BETA, invite-only since Aug 2026, free, with each user given five invites; Shinn said it stays invite-only while compute is added — [Fortune](https://fortune.com/2026/09/30/noah-shinn-instinct-ai-assistant-meta-muse-alexandr-wang-tech-series-c-ai-agent-mark-zuckerberg/)
- Volume, self-reported: Shinn said on a podcast that Instinct is approaching $1B in annual transaction volume, about half of it travel. Fortune could not establish a user count — [Fortune](https://fortune.com/2026/09/30/noah-shinn-instinct-ai-assistant-meta-muse-alexandr-wang-tech-series-c-ai-agent-mark-zuckerberg/)

**Mechanics**
- Persistent cloud computer with browser access and cached credentials, reached by iMessage, WhatsApp or a call; it runs on Spear Street's infrastructure with no self-hosting (vendor) — [Vellum](https://www.vellum.ai/blog/official-instinct-breakdown)
- Terms let it receive screen captures, cursor movements and keyboard inputs, and allow it to enter binding agreements for the user — [TechCrunch, 24 Aug 2026](https://techcrunch.com/2026/08/24/instincts-powerful-ai-assistant-is-raising-privacy-and-security-concerns/)
- Email in practice: it pulled a sign-up code from a user's inbox to book a Resy table — [TechCrunch, 24 Aug 2026](https://techcrunch.com/2026/08/24/instincts-powerful-ai-assistant-is-raising-privacy-and-security-concerns/)
- SHIPPED to early users, Sept 2026: Concierge for high-touch phone calls and specialized bookings, a peer-to-peer protocol between Instinct agents, and location-aware features — [Yahoo Finance](https://uk.finance.yahoo.com/news/ai-agent-startup-instinct-hits-180810275.html)
- ANNOUNCED about 7 Oct 2026: agent-to-agent resolution with participating businesses on Sierra and Decagon, replacing a phone call; participating businesses not named (summary; direct fetch returned HTTP 402) — [Shinn on X](https://x.com/noahrshinn/status/2107875073038385546)
- Failures: testers hit CAPTCHAs and two-factor walls, a high-demand ticket purchase failed repeatedly, and an investor reported it reset a password on its own to finish a blocked purchase (vendor, relaying user accounts) — [Vellum](https://www.vellum.ai/blog/official-instinct-breakdown)

### Inferences
- Instinct's stated travel weighting and Concierge calling mean a long-tail business is more likely to meet it on the phone or by email than through any machine endpoint.
- With no developer surface, the only published way for a business to be reached deliberately by Instinct is through Sierra or Decagon, or eventually Poppy.

### Gaps
- Other uses of the name: only one query targeted this and it returned only this company. I did not run separate searches on spelling variants, so I cannot rule them out. No other candidate is verified, and I am not listing unverified ones.
- One explainer in the search results said Instinct has had its own email addresses since Sept 2026 for contacting businesses, and another claimed more than 100,000 users, attributed to The Information. I could not trace either to an opened source. Forbes and WSJ originals were not retrieved.
- Whether Instinct discloses itself as an AI on calls to businesses, and whether it identifies itself in browser traffic.

## Which other consumer agents matter, where are they live, and what can they do?

### Takeaway
The field consolidated in 2026 around cloud or browser agents plus closed partner checkouts. Most are US-first and paid. OpenAI's retreat from Instant Checkout is the clearest evidence that purchase-inside-the-assistant lagged expectations. Apple's Siri AI is live, but what I could verify covers app actions rather than autonomous web browsing.

### Cited Findings

| Agent | Status and date | Region and access | Actions | Source |
|---|---|---|---|---|
| ChatGPT agent | SHIPPED; agentic browsing now in desktop app, Chrome extension and Codex | Paid tiers; details not verified | Browses and acts on sites | [No Hacks, updated 31 Oct 2026](https://nohacks.co/blog/agentic-browser-landscape-2026) |
| ChatGPT Atlas | DISCONTINUED 9 Aug 2026 | n/a | Was the browser host for agent mode | [Wikipedia](https://en.wikipedia.org/wiki/ChatGPT_Atlas) |
| OpenAI dots | SHIPPED, rolling out 29 Sept 2026 | Pro and Business Premium; Pro rollout excludes EEA, Switzerland, UK | Always-on agent with its own cloud computer and browser, 4,000+ app connections (summary) | [TNW](https://thenextweb.com/news/openai-dots-always-on-ai-agents-cloud-computers-devday); [TechCrunch](https://techcrunch.com/2026/09/29/openai-launches-dots-its-bubbly-agentic-avatar/) |
| ChatGPT Instant Checkout | WITHDRAWN March 2026 | n/a | Checkout moved to merchant apps or sites; about 12 to 30 Shopify merchants had been live | [Forrester, 7 Mar 2026](https://www.forrester.com/blogs/what-it-means-that-the-leader-in-agentic-commerce-just-pulled-back/) |
| Chrome auto browse | SHIPPED 28 Jan 2026 | AI Pro and Ultra, US; a Google plan page adds India (summary) | Multi-step browsing; human confirms purchases | [9to5Google](https://9to5google.com/2026/01/28/chrome-gemini-auto-browse/); [Google One](https://one.google.com/about/google-ai-plans/) |
| Gemini Spark | ANNOUNCED 19 May 2026, since rolling out; plan and country claims conflict | Reported as US Ultra beta or Pro and Ultra in select countries (summary) | 24/7 agent on dedicated cloud VMs | [TechCrunch](https://techcrunch.com/2026/05/19/google-introduces-gemini-spark-a-24-7-agentic-assistant-with-gmail-integration/); [Gemini](https://gemini.google/overview/agent/spark/) |
| Google agentic checkout and UCP | ANNOUNCED 11 Jan 2026; staged rollout with select US retailers (summary) | US | Buy from eligible listings in AI Mode and Gemini via Google Pay; merchant stays merchant of record | [9to5Google](https://9to5google.com/2026/01/11/gemini-ai-mode-checkout/); [Google developers](https://developers.google.com/merchant/ucp/) |
| AI Mode booking | SHIPPED 17 Nov 2025 to US Search Labs | US Labs | Finds a slot and hands off to Booksy, Fresha or Vagaro; other calendars not supported | [Zoca](https://zoca.com/post/how-to-get-salon-booked-google-ai-mode-gemini) (vendor) |
| Google AI calling (Search) | SHIPPED July 2025 (summary) | US | Calls local businesses for price and availability | [TechCrunch](https://techcrunch.com/2025/07/16/google-rolls-out-ai-powered-business-calling-feature-brings-gemini-2-5-pro-to-ai-mode) |
| Gemini "Call for Me" | BETA test reported 9 Oct 2026 | Pixel 11, US, paid plan, Phone by Google beta, English | Hours, quotes, booking, phone menus, hold; no payments | [Local Falcon](https://www.localfalcon.com/blog/googles-gemini-is-starting-to-call-local-businesses-for-customers) |
| Alexa for Shopping | SHIPPED 13 May 2026 | US; no Prime or Echo required | Merges Rufus and Alexa+ for shopping; other tasks go to Alexa+ | [PPC Land](https://ppc.land/amazon-merges-rufus-and-alexa-into-one-shopping-assistant/) |
| Amazon Buy for Me and Shop Direct | SHIPPED, described by Amazon as a pilot (summary) | US | Buys on other retailers' sites; 500,000+ products by Nov 2025; feeds opened Mar 2026 with 100M+ products from 400,000+ merchants | [PPC Land](https://ppc.land/amazon-merges-rufus-and-alexa-into-one-shopping-assistant/) |
| Apple Siri AI | BETA from 14 Sept 2026 | English first; not initially in the EU on iOS, iPadOS, watchOS; not in China | App actions and on-screen content; no web navigation, calling or purchasing described | [Apple](https://www.apple.com/newsroom/2026/09/siri-ai-a-profoundly-more-capable-and-personal-assistant-is-here/) |
| Perplexity Comet | SHIPPED | Free; desktop, Android, iOS since Mar 2026 | Browser agent in the user's session | [No Hacks](https://nohacks.co/blog/agentic-browser-landscape-2026) |
| Microsoft Copilot Checkout | SHIPPED Jan 2026 (summary) | US; English-language merchants selling to US buyers; Shopify merchants auto-enrolled with opt-out | Purchase inside Copilot.com and mobile apps | [Microsoft](https://news.microsoft.com/source/2026/01/08/microsoft-propels-retail-forward-with-agentic-ai-capabilities-that-power-intelligent-automation-for-every-retail-function/); [Microsoft Ads](https://about.ads.microsoft.com/en/solutions/technology/agentic-commerce) |
| Copilot in Edge | SHIPPED; Copilot Mode brand retired 13 May 2026 | Free; desktop, Android, iOS | Partial agentic features | [No Hacks](https://nohacks.co/blog/agentic-browser-landscape-2026) |
| Claude in Chrome | GA on all paid plans since 26 Aug 2026 | Chrome desktop extension only; no free tier | Acts in the user's own browser | [No Hacks](https://nohacks.co/blog/agentic-browser-landscape-2026) |

- Legal backdrop: a federal judge enjoined Comet from password-protected Amazon areas in March 2026; the Ninth Circuit vacated on 4 Aug 2026, reasoning the user is the one accessing, and denied rehearing on 10 Sept. The underlying case continues (summary) — [CNBC](https://www.cnbc.com/2026/03/10/amazon-wins-court-order-to-block-perplexitys-ai-shopping-agent.html); [Engadget](https://www.engadget.com/2230471/perplexity-has-successfully-overturned-amazon-injunction-on-its-ai-shopping-bot/); [MediaPost](https://www.mediapost.com/publications/article/417007/appeals-court-sides-against-amazon-lifts-perplexi.html)
- The court left open whether sites can restrict access through terms of use — [i-SCOOP, Oct 2026](https://www.i-scoop.eu/websites-blocking-ai-agents/)
- Long-tail warning from Amazon Buy for Me: small businesses reported products listed without consent, including out-of-stock items, around Jan 2026. Amazon called it a pilot with an opt-out by email to branddirect@amazon.com, and a Modern Retail survey reportedly drew 145 brand responses (summary) — [ConsumerAffairs, 7 Jan 2026](https://www.consumeraffairs.com/news/small-business-owner-says-amazon-listed-its-products-without-consent-010726.html); [Modern Retail](https://www.modernretail.co/technology/brands-are-upset-that-buy-for-me-is-featuring-their-products-on-amazon-without-permission/)
- Google is also adding a Business Agent to Search, so a brand-run agent inside Google's surfaces is a parallel path to Meta's and Sierra's (summary, Jan 2026) — [9to5Google](https://9to5google.com/2026/01/11/gemini-ai-mode-checkout/)
- Share of observed agentic traffic, Sept 2026: Muse 40.3%, ChatGPT Agent 28.6%, Comet 9.4% (down from 40.7%), Codex Browser 7.7%, Claude Chrome extension 7.1% (down from 22%), Codex Chrome extension 3.4%. Muse had dedicated detection only from 22 Sept. Traffic is limited to HUMAN's customer base (vendor) — [HUMAN, Sept 2026](https://www.humansecurity.com/learn/blog/september-2026-agentic-traffic-triples-meta-muse-debuts-at-no-1/)
- Conflict on Google calling tiers: July 2025 coverage says free for all US Search users, while a current Google plan page lists it under Ultra (both summary) — [TechCrunch](https://techcrunch.com/2025/07/16/google-rolls-out-ai-powered-business-calling-feature-brings-gemini-2-5-pro-to-ai-mode); [Google One](https://one.google.com/about/google-ai-plans/)
- Pre-launch reports said iOS 27 would open Siri to third-party assistants through Extensions, but Apple's launch post does not mention third-party agents (report summary; Apple post opened) — [iClarified](https://www.iclarified.com/100360/apple-to-open-siri-to-thirdparty-ai-assistants-like-gemini-claude-in-ios-27); [Apple](https://www.apple.com/newsroom/2026/09/siri-ai-a-profoundly-more-capable-and-personal-assistant-is-here/)

### Inferences
- For a long-tail business, the agents most likely to appear in 2026 are browser-driven (Muse, ChatGPT agent, Comet, Claude in Chrome, auto browse) or phone-driven (Google, Muse, Instinct).
- HUMAN's Comet and Claude collapses in September look mostly like a share shift from Muse's arrival and detection coverage, though Comet's absolute decline of 28.3% shows it is not only that. Treat rankings as volatile.
- The EEA, UK and China are materially behind for most agents, so a US-first Legible pilot matches where the agents are.

### Gaps
- OpenAI's ChatGPT agent help page on identification returned HTTP 403, so its current tier, region and signing behaviour are unverified here.
- Microsoft's 25 Sept 2026 post on the new Copilot with Autopilot could not be opened, so that product's consumer scope is unverified: [Microsoft](https://blogs.microsoft.com/blog/2026/09/25/introducing-the-new-copilot-with-home-code-and-autopilot/). Copilot Actions current status not found.
- Alexa+ general availability and region beyond the shopping merge not verified. Google's Spark page returned generic plan content, so Spark's current eligibility remains unresolved.
- Current Perplexity Instant Buy status not verified.
- A search summary said a merchant-facing source states Buy for Me was not yet offered through the feed-powered beta, which would mean feed participation does not make a merchant eligible. I could not trace it to a page I opened.

## Mechanically, how does each agent read and act on a business? Do any look for llms.txt, /.well-known, MCP, or a social-bio link?

### Takeaway
Rendered-browser automation dominates observed agent traffic and is the only channel with broad evidence. HTTP fetch is secondary. Phone is a real channel for local services. Agent-to-agent is mostly announced. I found no measurement showing a consumer agent requesting an MCP endpoint or /.well-known file on a small-business site, and the best log study shows llms.txt is almost entirely unread by AI retrieval bots.

### Cited Findings

**Overall picture**
- Sierra's description of today, from the protocol's co-author: "Today most personal agents use websites and apps the way people do" (6 Oct 2026). If the site cannot finish the task, the agent may call the support line or open web chat, which is slow and may fail — [Sierra](https://sierra.ai/blog/introducing-personal-agent-protocol)
- Agentic browsers made up nearly three-quarters of agentic traffic in April 2026, with Comet and Atlas near 70% (summary; direct fetch returned 403) (vendor) — [HUMAN, Apr 2026](https://www.humansecurity.com/learn/blog/state-of-agentic-traffic-april-26/)
- What agents do when they arrive, Sept 2026: products and search 81% of agentic route traffic, user account 4%, authentication 3.1%, checkout and payment 2.4% (vendor) — [HUMAN, Sept 2026](https://www.humansecurity.com/learn/blog/september-2026-agentic-traffic-triples-meta-muse-debuts-at-no-1/)

**Muse specifically**
- Three observed paths: Chromium in the VM looking like desktop Chrome on Linux; Meta crawlers such as Meta-WebIndexer for simple static fetches; and scripts or curl through its egress proxy (vendor; test dates not stated) — [Vouched, 23 Oct 2026](https://www.vouched.id/learn/blog/muse-is-an-agent-but-it-doesnt-want-you-to-know?hs_amp=true)
- No custom user-agent; 99.3% of sampled requests came through Cloudflare (81.2%) or Fastly (18.1%), 0.6% from consumer ISPs (DataDome sample) — [PPC Land, reporting DataDome](https://ppc.land/metas-muse-agent-gains-a-signed-id-in-a-quiet-test-datadome-finds/)
- Shipping app hides automation signals including `navigator.webdriver` and checks pages for CAPTCHAs and block messages (Inc. analysis, as relayed) — [State of AI, 5 Oct 2026](https://www.thestateofai.com/news/meta-muse-bot-detection-blocked)
- Quiet Web Bot Auth test: Meta began signing a small share of Muse and Meta-WebIndexer requests around 12 Oct 2026 per DataDome (posted 30 Oct). Meta's crawler docs do not mention it as of 31 Oct and list only IP verification, which Cloudflare or Fastly addresses cannot pass. Vouched says Muse does not sign, which appears to predate or miss this test — [PPC Land](https://ppc.land/metas-muse-agent-gains-a-signed-id-in-a-quiet-test-datadome-finds/); [Vouched](https://www.vouched.id/learn/blog/muse-is-an-agent-but-it-doesnt-want-you-to-know?hs_amp=true)
- Only 2.3% of legitimate AI agent sessions carried a verified signature in Q3 2026 (Arkose Labs) — [PPC Land](https://ppc.land/metas-muse-agent-gains-a-signed-id-in-a-quiet-test-datadome-finds/)

**Mechanism by agent**

| Agent | Dominant mechanism | Evidence quality |
|---|---|---|
| Muse | Connector if available, otherwise cloud Chromium; crawler and curl for simple reads; phone beta | Good, multiple independent tests ([TechCrunch](https://techcrunch.com/2026/09/08/meta-debuts-its-muse-ai-agent-will-consumers-trust-it/), [Vouched](https://www.vouched.id/learn/blog/muse-is-an-agent-but-it-doesnt-want-you-to-know?hs_amp=true)) |
| Instinct | Cloud computer with browser and cached credentials, phone, email | Moderate, mostly user reports ([Vellum](https://www.vellum.ai/blog/official-instinct-breakdown), [TechCrunch](https://techcrunch.com/2026/08/24/instincts-powerful-ai-assistant-is-raising-privacy-and-security-concerns/)) |
| ChatGPT agent, Comet, Claude Computer Use | Rendered page, via structure, vision or a hybrid; perception differences change which element they click | Good for the split, version-specific ([Merj](https://merj.com/blog/agent-interaction-research)) |
| Chrome auto browse | Acts in the browser (scrolls, clicks, types). Separately, a Google-Agent user agent was added 20 Mar 2026 for agents on Google infrastructure, with Web Bot Auth testing as agent.bot.goog; the guide does not say auto browse uses either | Moderate, one guide ([No Hacks](https://nohacks.co/blog/agentic-browser-landscape-2026)) |
| Google Search and Gemini calling | Phone call, with AI disclosure at the start | Moderate ([Local Falcon](https://www.localfalcon.com/blog/googles-gemini-is-starting-to-call-local-businesses-for-customers)) |
| Google AI Mode booking | API-style partner handoff to Booksy, Fresha, Vagaro | Moderate ([Zoca](https://zoca.com/post/how-to-get-salon-booked-google-ai-mode-gemini)) |
| Amazon Buy for Me | Public product data taken without merchant integration, purchase on the merchant site; merchants' and analysts' description, not Amazon's (summary; per-page attribution not checked) | Low to moderate ([Cahoot](https://www.cahoot.ai/amazon-buy-for-me-agentic-commerce/), [Modern Retail](https://www.modernretail.co/technology/brands-are-upset-that-buy-for-me-is-featuring-their-products-on-amazon-without-permission/)) |
| Apple Siri AI | On-device App Toolbox and Spotlight, plus on-screen content | Good on what is stated, silent on the web ([Apple](https://www.apple.com/newsroom/2026/09/siri-ai-a-profoundly-more-capable-and-personal-assistant-is-here/)) |

**llms.txt: the best log evidence**
- Ahrefs, May 2026, 137,210 domains: 28% (about 38,000) published a valid file; 97% of those files received zero requests; about 22,000 requests in total and 96% from bots. AI retrieval bots were 1.1% (233 requests), AI assistants 2.5%, AI agents and infrastructure 10.5%, and SEO audit tools were the largest group at 21.7%. Limits: technical customer base, one month, and a fetch is not proof of use. Ahrefs sells the bot-analytics tool used (vendor) — [Ahrefs](https://ahrefs.com/blog/llmstxt-study/)
- Ahrefs' retrieval-bot section has an internal error: it states 1.1% of AI bot requests, but 233 is about 5.5% of the 4,273 AI-bot requests. The 1.1% applies to all requests — [Ahrefs](https://ahrefs.com/blog/llmstxt-study/)
- Small-business echo: among 163 working restaurant sites, llms.txt rose from 9 to 34 between July and September 2026, while 0 of 163 published a callable interface such as MCP or OpenAPI (vendor; single author) — [DEV Community, 17 Sept](https://dev.to/blondedevrules/how-do-you-test-whether-an-ai-agent-can-book-a-restaurant-121o)

**Supply of machine-readable endpoints**
- Cloudflare's scan of the top 200,000 domains (17 Apr 2026, modified 15 July): robots.txt 78%, Markdown content negotiation 3.9%, Content Signals 4%, and MCP Server Cards plus API Catalogs on fewer than 15 sites combined. Long-tail sites are outside this sample — [Cloudflare](https://blog.cloudflare.com/agent-readiness/)
- Of 7 agents tested in Feb 2026, only Claude Code, OpenCode and Cursor requested Markdown by default per a Checkly report. These are coding agents, not consumer agents — [Cloudflare](https://blog.cloudflare.com/agent-readiness/)
- Vendor benchmark, not field data: WebMCP configurations completed all 49 tasks, 2.5 to 7.5 times faster and 3 to 47 times cheaper than the median screenshot or DOM agent (nekuda WindTunnel, relayed) — [Merj](https://merj.com/blog/agent-interaction-research)

**Structured data**
- Live-retrieval tests mostly show JSON-LD does not reach the model: an Otterly test (Dec 2025 to Mar 2026) found 6 of 7 AI search platforms unable to fetch or correctly interpret schema when asked directly, with Gemini the exception (summary; vendor) — [Otterly](https://otterly.ai/blog/schema-markup-real-impact-ai-search/)
- Contrary evidence: a Feb 2026 Williams-Cook test had ChatGPT and Perplexity extracting an address from invalid JSON-LD, though it may have been treated as plain text; a later test found Gemini on a free plan said the block was absent (summary) — [Botpresso](https://botpresso.com/ai-assistants-schema-markup-test/); [SEO Técnico](https://seotecnico.dev.br/en/blog/structured-data-and-ai)
- Ahrefs (1,885 pages against 4,000 controls): adding schema changed AI Mode and ChatGPT citations within noise, and AI Overviews by -4.6% (relayed) — [LovedByAI](https://www.lovedby.ai/guide/state-of-ai-traffic-2026)
- All of these measured retrieval and citation by chat assistants, not a browser agent reading a page during a task — [Otterly](https://otterly.ai/blog/schema-markup-real-impact-ai-search/); [Merj](https://merj.com/blog/agent-interaction-research)

**/.well-known and MCP**
- The only consumer-agent discovery file I found is DRAFT: Poppy defines `/.well-known/poppy.json`, but no production implementer is stated — [Sierra, 9 Oct 2026](https://sierra.ai/blog/poppy); [Poppy GitHub](https://github.com/personal-agent-protocol/personal-agent-protocol)
- Searches for log data on `/.well-known/mcp` or `mcp.json` returned only tooling (Profound and Vercel log drains) and a 30-day study whose retrieved text did not cover these paths — [Profound docs](https://docs.tryprofound.com/agent-analytics/vercel_native); [Digital Applied](https://www.digitalapplied.com/blog/agentic-crawler-behavior-30-day-site-log-study)
- Log attribution is itself unreliable: Profound found requests using the meta-webindexer name in Muse sessions that did not come from Meta's IPs, and HUMAN found 16.7% of requests claiming to be ChatGPT-User were spoofed — [PPC Land](https://ppc.land/metas-muse-agent-gains-a-signed-id-in-a-quiet-test-datadome-finds/); [TechnologyChecker](https://technologychecker.io/blog/ai-crawler-statistics)

### Inferences
- A machine-facing resource reached only by a dedicated path has no demonstrated traffic source. The most defensible design has the resource reachable from a normal link in the rendered homepage DOM, with its key facts as server-rendered visible text, because that is what the dominant agent mode actually sees.
- Hidden JSON-LD should be a supplement, not the delivery vehicle. Visible text and real form controls are what browser agents act on.
- `/.well-known/poppy.json` is a cheap hedge worth publishing, since Muse and Instinct are named participants. It is not yet a traffic source, and its OAuth requirements suggest a hosted provider is needed for very small businesses.
- Legible cannot reliably measure this from user agents alone. Muse looks like Chrome from Cloudflare or Fastly addresses, so instrumented canary links are more trustworthy than log classification.
- Legible should run its own tests: put a resource link on a test site, send each live agent at it with real tasks, and record whether it is followed.

### Gaps
- No evidence found on any agent following a custom link in an Instagram, Facebook or TikTok bio as a discovery step. This is absence of evidence from limited searching, not proof it never happens.
- No published data on the split between connector use and browser use within Muse.
- No primary measurement of consumer agents requesting MCP endpoints. PostHog's 63M MCP tool calls measure a developer product and do not apply here: [PostHog](https://posthog.com/blog/how-ai-agents-behave).
- Search summaries also described an Ahrefs-cited test of ChatGPT, Claude, Perplexity, Gemini and AI Mode in which hidden structured data was ignored, and a searchVIU test in which none of five systems retrieved a price held only in JSON-LD. I could not trace either to a page I opened. Both point the same way as Otterly, so verify before citing.
- No fresh independent test of JavaScript execution by chat fetch bots. Whether Muse honours robots.txt was not tested in the sources I opened.
- Akamai's Sept 2026 report release surfaced no agent-traffic share (summary): [Akamai release](https://www.globenewswire.com/news-release/2026/09/22/3366103/0/en/akamai-report-securing-agentic-ai-requires-shift-to-behavioral-governance.html). Scrunch and Vercel surfaced no published discovery-file measurement.

## What is the single best evidence on agent failure at small-business sites?

### Takeaway
No rigorous multi-vertical study exists. The closest long-tail evidence is a 200-restaurant booking test in which only 8% of paths reached the final step, and it is small, vendor-authored and single-vertical. Merj's controlled tests are the best evidence on why agents fail, while Jefferies is the best evidence on access blocking at larger sites. Together they say access and interface friction, more than model quality, are the constraint.

### Cited Findings

**Best long-tail evidence**
- 200 restaurant booking paths (first run July, recheck Sept, post dated 17 Sept): a browser agent reached the final step on 16 of 200, and hit venue protection (anti-bot, CAPTCHA, device check) on 26 of 200. Other blocker classes included cookie walls, login walls, unparseable forms and no booking entry, without published counts. Two venues on the same booking system gave opposite outcomes. Limits: measures reach not completion, the detector changed between runs, no agents or vendors named, and the authors sell a booking product (vendor) — [DEV Community](https://dev.to/blondedevrules/how-do-you-test-whether-an-ai-agent-can-book-a-restaurant-121o)
- The same post's practical point: the CAPTCHA usually sits across the site, including read-only pages with hours and availability, when it only needs to guard the booking step (summary of the same post) — [DEV Community](https://dev.to/blondedevrules/how-do-you-test-whether-an-ai-agent-can-book-a-restaurant-121o)

**Best controlled evidence on why agents fail**
- Merj (published 29 Sept 2026; data Nov 2025 and Mar 2026; 100 purpose-built pages plus production pages; agents include ChatGPT Agent, Claude Computer Use, Comet): average success rose from about 30% to about 60%. Success counts even if it took more than one attempt. Full dataset unpublished, and the testing predates Muse (vendor consultancy) — [Merj](https://merj.com/blog/agent-interaction-research)
- March 2026 success averages from Merj, relevant to small-business sites: canvas with no DOM nodes about 34%; div-as-button with no role about 55%; icon-only button about 45%; transparent overlay about 41%; skeleton loaders mistaken for content about 58%; latency over 2s and stale DOM about 58%; full-screen consent banner about 64%; delayed newsletter popup about 58%; image and alt-text divergence about 55%; typing into pre-filled fields about 66% — [Merj](https://merj.com/blog/agent-interaction-research)
- Merj also observed CAPTCHA retry loops with no give-up condition and agents inventing email addresses to satisfy required fields (no rates given) — [Merj](https://merj.com/blog/agent-interaction-research)

**Best evidence on blocking**
- Jefferies (published 8-9 Oct 2026), Muse against several hundred leading US e-commerce, airline, OTA, hotel and reservation sites: about one-third blocked, one-third challenged or restricted, one-third easy. Jefferies said new restrictions were appearing almost daily and that access is a bigger bottleneck than model quality. Procedure not disclosed, and these are not long-tail sites — [Proactive Investors](https://www.proactiveinvestors.com/companies/news/1099848/meta-s-muse-ai-agent-blocked-by-one-third-of-websites-tested-jefferies-says-1099848.html)
- Amazon began blocking Muse on about 20-21 Sept 2026, saying Meta had not told it, the agent did not identify itself, and it appeared to capture credentials. Meta denies seeing passwords — [Wikipedia, citing GeekWire and Forbes](https://en.wikipedia.org/wiki/Muse_(AI_agent))
- Vouched got Muse past the Amazon block by having it run Firefox through its egress proxy (vendor) — [Vouched](https://www.vouched.id/learn/blog/muse-is-an-agent-but-it-doesnt-want-you-to-know?hs_amp=true)
- NBC News found some retailers blocked Muse, including Meta-named partners (summary; page not opened). An outlet's test at carrier Visible had Muse blocked with disabled chat, surviving even when the user took over (summary, low authority) — [NBC News](https://www.nbcnews.com/tech/tech-news/ai-agent-muse-shop-e-commerce-amazon-wal-mart-wayfair-buy-rcna599069); [BigGo Finance](https://finance.biggo.com/news/912f0e9e-a06f-48df-b8eb-1af774ed84b1)
- HUMAN's platform blocks Muse by default, and customers must opt to allow it (vendor) — [HUMAN, Sept 2026](https://www.humansecurity.com/learn/blog/september-2026-agentic-traffic-triples-meta-muse-debuts-at-no-1/)

**Web-wide barrier rates (popular sites, not the long tail)**
- Zyte, 11,100 popular landing pages (published 5 Aug 2026): WAF 92.4%, JavaScript barrier 40.6%, CAPTCHA 22.5%, rate limiting 22.1%, antibot 18.5%; only 18.5% with no barrier. Most defended: apparel, retail, sporting goods, real estate, travel. Least defended: farms, fishery, graphic design, public policy, performing arts. Local services not reported (vendor) — [Zyte](https://www.zyte.com/blog/the-state-of-web-access/)

**Cloudflare defaults: an unresolved conflict**
- Cloudflare's changelog (1 July 2026) says that from 15 Sept 2026, new domains get Training and Agent blocked on pages displaying ads, with Search allowed — [Cloudflare changelog](https://developers.cloudflare.com/changelog/product/bots/)
- Secondary reports go further: State of AI says zones with the older block-AI-bots setting were moved to the same default, and search summaries of other blogs add existing free-tier accounts (per-page attribution not checked). Neither is confirmed by the Cloudflare pages I opened — [State of AI](https://www.thestateofai.com/news/meta-muse-bot-detection-blocked); [Digital Applied](https://www.digitalapplied.com/blog/cloudflare-ad-page-ai-agent-block-bot-census)
- However, Cloudflare's docs (last updated 2 Nov 2026) state new domains default to Allow for Search, Agents and Training. Its Aug and Sept blog says new non-publisher customers start with no added blocks, while publishers who declare ad monetization get Training set to Disallow — [Cloudflare docs](https://developers.cloudflare.com/bots/additional-configurations/block-ai-bots/); [Cloudflare blog](https://blog.cloudflare.com/bot-preference-sync/)
- A changelog entry dated 4 Nov 2026, one day after this research date, adds per-agent controls for top Personal Agents and recommends Allow. No explicit reversal notice appears — [Cloudflare changelog](https://developers.cloudflare.com/changelog/product/bots/)

**Scraping and CAPTCHA proxies**
- An LLM scraping benchmark reported 5% success on dynamic CAPTCHA sites for one model; this is scraping rather than booking (summary) — [arXiv 2601.06301](https://arxiv.org/pdf/2601.06301)
- Booking widgets that load late can be missed entirely, and unlabeled form fields are common failure points, per a blog rather than a controlled study (summary) — [Elements AI](https://elementsai.net/blog/when-ai-agents-use-your-website/)

### Inferences
- For long-tail sites the likely failure order differs from big retail: less deliberate bot defence, more third-party widget, cookie-wall and form problems. The Zyte industry split and restaurant study point this way, but neither directly measures it.
- This favours Legible's premise: a clean, static, plainly labelled resource page sidesteps most failure classes that Merj and the restaurant study list, provided the agent actually gets there and the final booking step has a usable path.
- The final step remains the hard part. The resource can answer questions, but the restaurant test suggests booking widgets are where flows stop, so a resource should include a direct deep link and a phone or email fallback.
- If Legible onboards customers on Cloudflare or a host with bot defaults, checking agent access should be part of onboarding, since this setting could defeat the resource.

### Gaps
- No empirical study found on PDF or image menus specifically. The nearest proxies are Merj's image-related tests and a Business Agent limit that it cannot read documents in chat ([Meta docs](https://developers.facebook.com/documentation/meta-business-agent/capabilities)).
- No test found of live consumer agents on salons, trades or clinics, or across booking widgets (Calendly, Square, Vagaro, and so on) with per-vendor outcomes.
- No hands-on booking success rate for Muse or Instinct on small businesses. Whether Cloudflare's ad-page default took effect as described could not be settled before the search budget ended.

## What do agents do on social surfaces, and do any DM or phone businesses?

### Takeaway
Instagram and Facebook are not established as agent-readable business front doors. I found no direct test of third-party agents reading them, and only a thin Meta-side example. Phoning businesses is real and growing. Email is emerging. I found no confirmed agent DMing businesses at scale, including Muse.

### Cited Findings

**Instagram and Facebook**
- Muse's only stated Instagram example is turning a saved recipe reel into a grocery list, with no connector or access detail; Facebook is not mentioned — [Meta newsroom](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)
- Muse's app can show a feed built from connected Facebook and Instagram accounts (summary) — [CNBC, 8 Sept 2026](https://www.cnbc.com/2026/09/08/meta-personal-ai-agents-public-reckoning-privacy-safety.html)
- Since 10 July 2025, search engines index public content from professional Instagram accounts by default, for accounts that are public, 18+, and Business or Creator, with an opt-out (summary) — [afaqs](https://www.afaqs.com/news/digital/search-engines-can-now-index-public-content-from-instagram-9483796); [The Week](https://www.theweek.in/news/sci-tech/2025/07/12/social-media-instagram-posts-and-reels-will-now-pop-up-on-google-and-bing-searches-how-to-enable-disable-this-setting.amp.html)
- Meta's own crawlers differ by purpose: facebookexternalhit for previews, Meta-ExternalAgent for AI training. Meta's docs list five crawlers — [PPC Land](https://ppc.land/metas-muse-agent-gains-a-signed-id-in-a-quiet-test-datadome-finds/)

**Messaging and DM**
- Meta's WhatsApp Business Solution Terms bar general-purpose AI providers from the WhatsApp Business Platform from 15 Jan 2026, while support, sales and notification bots remain allowed; the scope applies to WhatsApp, not Instagram or Messenger (summary; vendor explainers) — [respond.io](https://respond.io/blog/whatsapp-general-purpose-chatbots-ban); [Alibaba Cloud](https://www.alibabacloud.com/help/en/chatapp/use-cases/whatsapp-ai-policy-2026-guide)
- Instinct users can reach their agent through WhatsApp, but the source does not describe how it connects or whether it messages businesses there — [TechCrunch, 24 Aug 2026](https://techcrunch.com/2026/08/24/instincts-powerful-ai-assistant-is-raising-privacy-and-security-concerns/)
- Meta has not announced that Muse will open business chats on WhatsApp or Messenger, per a vendor blog as of 13 Oct (vendor) — [ChatMaxima](https://chatmaxima.com/blog/meta-muse-ai-agent-businesses-whatsapp-messenger/)

**Phone**
- Google's business calling launched in the US in July 2025, with a robot self-identification and a Business Profile opt-out (summary) — [TechCrunch](https://techcrunch.com/2025/07/16/google-rolls-out-ai-powered-business-calling-feature-brings-gemini-2-5-pro-to-ai-mode); [Local Falcon](https://www.localfalcon.com/blog/googles-gemini-is-starting-to-call-local-businesses-for-customers)
- Best small-business phone data: Invoca (published 10 Dec 2025; Google AI pricing calls, July to Nov 2025; auto repair, salons, wellness, vets, pest control, plumbing): 26% unanswered, 49% of answered calls gave no price, and calls rose 324% in November over October. Relayed by a vendor; Invoca sells call analytics — [Zoca](https://zoca.com/post/how-to-get-salon-booked-google-ai-mode-gemini); [Invoca primary, not opened](https://www.invoca.com/blog/google-ai-pricing-calls-study)
- Gemini "Call for Me" (test reported 9 Oct 2026): identifies itself as a Google AI assistant on a recorded line and names the user, has daily limits, handles menus and hold, and takes no payments. Businesses can opt out at g.co/gemini/opt-out — [Local Falcon](https://www.localfalcon.com/blog/googles-gemini-is-starting-to-call-local-businesses-for-customers)
- Muse calling is in beta and Instinct Concierge is with early users — [404 Media](https://www.404media.co/meta-tests-muse-ai-agent-calls-that-are-actually-made-by-humans-in-a-call-center/); [Yahoo Finance](https://uk.finance.yahoo.com/news/ai-agent-startup-instinct-hits-180810275.html)
- Sierra says agents built on Sierra began calling other Sierra-built agents in healthcare in 2025, and shipped a speech-based detector, fleming-1, for AI callers (8 Oct 2026; no volumes given) — [Sierra](https://sierra.ai/blog/caller-id-in-the-age-of-agents)

### Inferences
- A social profile is best treated as a human-facing pointer, plus a possible input to Legible's ingestion. The evidence does not support an agent traversing bio to resource as a designed path.
- The phone is the proven small-business channel, and the failure there is informational: half of answered calls produced no price. The Legible resource could double as the script or knowledge source for answering these calls, which is a clearer near-term value than any endpoint.
- Google's opt-out and AI disclosure give a business some visibility on that channel. Muse's disclosure practice is still unsettled.

### Gaps
- No test found of ChatGPT agent, Comet, Claude in Chrome or auto browse reading an Instagram or Facebook business profile. Logged-in browser agents may technically see what the user sees, but I found no source testing it, and Meta's terms on agent access were not retrieved.
- Logged-out Instagram behaviour rests only on low-quality how-to guides in a search summary (photo, bio, counts and part of the grid before a login prompt; embedded posts rendering for everyone). No authoritative or dated source, so treat this as unverified.
- Current regulatory status of the WhatsApp general-purpose AI ban in the EU, Italy or Brazil not verified, and Meta's own terms page was not opened.
- No data on the share of Business Agent conversations that come from AI agents rather than people.

## What volume does a long-tail business actually see, and how do the forecasts compare with measurement?

### Takeaway
Measured AI referrals to small sites are low: a median of about 14 visits a month in one vendor's sample, and roughly 0.1% to 1.7% of sessions across panels. Agent sessions (not human click-throughs) on long-tail sites are essentially unmeasured because the leading agent doesn't identify itself. Forecasts of $190B to $5T are projections that do not rest on current transaction data, and observed agent traffic touches checkout about 2.4% of the time.

### Cited Findings

**Long-tail referrals (humans clicking from assistants)**
- LovedByAI first-party data (Aug 2026, sites active in July): median site 14 AI visits/month, 90th percentile 96, about 4 in 10 under 10, about 1 in 10 over 100; median doubled from March to August; top 10% of sites took 65.7% of visits. Customers of an AI-visibility product, so likely biased upward (vendor) — [LovedByAI](https://www.lovedby.ai/guide/state-of-ai-traffic-2026)
- Previsible: small-business sites rose from 0.4% to 1.71% of sessions from AI assistants between Dec 2024 and May 2026; 166 GA4 properties only (relayed) — [LovedByAI](https://www.lovedby.ai/guide/state-of-ai-traffic-2026)
- Broader panels: SE Ranking 0.33% (101,574 sites, Apr 2026), Ahrefs 0.28% (74,752 sites, Mar 2026), Semrush median 0.14%, enterprise-skewed Conductor 1.08% (relayed) — [LovedByAI](https://www.lovedby.ai/guide/state-of-ai-traffic-2026)
- Consumer intent is much higher than click behaviour: BrightLocal's March 2026 survey had 45% using AI for local recommendations, but its July study (1,227 respondents) found 8% started with AI and 18% were ready to contact the business recommended (relayed) — [LovedByAI](https://www.lovedby.ai/guide/state-of-ai-traffic-2026)

**Conversion (mostly not small-business specific)**
- Adobe, US retail, July 2026: AI referrals up 62% YoY, conversion 60% higher than non-AI, revenue per visit 53% higher, 11th straight month of outperformance. Base is more than 1 trillion visits. No absolute rates or shares given, and this is an analytics vendor's customer data — [Digital Commerce 360, 19 Aug 2026](https://www.digitalcommerce360.com/2026/08/19/adobe-ai-referral-traffic-data-july-2026/)
- Contradicting or tempering evidence: Marketing Science (peer-reviewed, Apr 2026; 973 ecommerce sites) found organic converted about 13% better than ChatGPT; Contentsquare found AI at 1.3% conversion and 0.2% of visits; Orbit Media (97 B2B lead-gen sites) found ChatGPT at 2.1% versus 0.5% for Google; Adobe's travel conversion was 28% worse in May 2026; a CRM study of 118 accounts had median 0% reaching closed-won (all relayed) — [LovedByAI](https://www.lovedby.ai/guide/state-of-ai-traffic-2026)

**Agent traffic specifically**
- HUMAN: agentic traffic up 209.7% from August to September 2026, the largest monthly rise it has recorded this year; Muse averaging millions of requests per day. No absolute totals (vendor) — [HUMAN, Sept 2026](https://www.humansecurity.com/learn/blog/september-2026-agentic-traffic-triples-meta-muse-debuts-at-no-1/)
- HUMAN's sector mix: ecommerce 60.4%, media 21.1%, travel 17.1%; SaaS, finance and gaming under 1% each. No local-services category; reflects HUMAN's customers (vendor) — [HUMAN, Sept 2026](https://www.humansecurity.com/learn/blog/september-2026-agentic-traffic-triples-meta-muse-debuts-at-no-1/)
- DataDome counted 29.1M Muse requests from 22 Sept to 3 Oct across its network (about 2.4M a day) and put Muse at 33% of agentic browser requests in September. Vouched relays that 8.9% of sampled requests hit logins, forms, payments or carts (vendor) — [PPC Land](https://ppc.land/metas-muse-agent-gains-a-signed-id-in-a-quiet-test-datadome-finds/); [Vouched](https://www.vouched.id/learn/blog/muse-is-an-agent-but-it-doesnt-want-you-to-know?hs_amp=true)
- Cloudflare Radar, Q3 2026: User Action was 3.66% of verified AI crawler requests (2.45% in Q2, 1.82% in Q3 2025), with training at 47.62%. Monthly: July 2.66%, August 4.80%, September 3.11% (provisional). Secondary pull of Radar, with a series relabelled in Oct — [TechnologyChecker](https://technologychecker.io/blog/ai-crawler-statistics)
- Meta's crawlers made 12.4B requests in Q3 on DataDome's network, against 51,000 Meta AI referrals reported in the same piece — [PPC Land](https://ppc.land/metas-muse-agent-gains-a-signed-id-in-a-quiet-test-datadome-finds/)
- Muse app downloads over 2.5M per Sensor Tower via Inc. in early Oct, then 10M+ users by late Oct — [State of AI](https://www.thestateofai.com/news/meta-muse-bot-detection-blocked); [TechCrunch, 21 Oct 2026](https://techcrunch.com/2026/10/21/meta-says-muse-has-over-10m-users-with-shopping-a-top-activity/)

**Forecasts (projections, not measurement)**
- Morgan Stanley: $190B to $385B of US e-commerce by 2030, or 10% to 20% share, with a stricter autonomy standard (summary; fetch timed out twice) — [Morgan Stanley](https://www.morganstanley.com/insights/articles/agentic-commerce-market-impact-outlook)
- McKinsey: $1T US B2C retail orchestrated by agents by 2030, and $3T to $5T globally; the figure varies by citation (summary; primary not opened) — [Investing.com PR](https://www.investing.com/news/press-releases/agentic-commerce-could-be-a-1-trillion-market--heres-how-to-read-the-projections-4596532)
- Gartner: agents intermediating over $15T of B2B purchases by 2028, alongside its prediction that over 40% of agentic AI projects are cancelled by 2027 (summary; primary not opened). B2B, so not comparable — [MetaRouter](https://www.metarouter.io/post/agentic-commerce-trends-statistics); [Software Strategies](https://softwarestrategiesblog.com/2026/02/26/roundup-of-agentic-ai-forecasts-and-market-estimates-2026/)
- eMarketer: AI-platform-driven ecommerce at $144B by 2029 (8.8%); Juniper: about $8B agentic transaction value in 2026 (both summary via aggregators; treat as low confidence) — [MarketSplash](https://marketsplash.com/agentic-commerce-statistics/); [Growth Centr](https://www.growthcentr.com/agentic-payments-statistics-2026/)
- Reality checks: Instant Checkout was withdrawn with about 12 to 30 Shopify merchants live, and purchasing inside the engine was the least-adopted answer-engine use case — [Forrester, 7 Mar 2026](https://www.forrester.com/blogs/what-it-means-that-the-leader-in-agentic-commerce-just-pulled-back/)

**Hype versus measurement**

| Claim type | Example | Grade |
|---|---|---|
| Measured, referrals | Adobe retail, SE Ranking, Ahrefs panels | Solid for direction; retail and panel-specific |
| Measured, small sample | Previsible 1.71%, LovedByAI median 14 visits | Useful; biased or small |
| Measured, vendor network | HUMAN, DataDome agent traffic | Real but customer-limited; enterprise skew |
| Self-reported | Instinct near $1B volume; Muse 10M users | Unaudited; Muse's number sits in an SEC filing |
| Projection | McKinsey, Morgan Stanley, Gartner | Scenario, not measurement |
| Headlines to reject | Claims that agents now out-traffic humans, which mix all bots with agents ([example](https://theaicareerlab.com/blog/ai-agents-majority-web-traffic-2026)) | Radar's user-action share of verified AI crawler requests is only 3.66% ([TechnologyChecker](https://technologychecker.io/blog/ai-crawler-statistics)) |

### Inferences
- Illustrative only, multiplying across studies that do not share samples: 14 AI visits a month at 1.3% to 2.1% conversion gives about 0.2 to 0.3 conversions a month, or 2 to 4 a year, for a median small site. That does not count agent sessions, which are unmeasured, or phone calls. A Legible ROI pitch based on today's site traffic alone would be weak.
- The 12.4B to 51,000 ratio on DataDome's network is about 243,000 crawler requests per referral. These are different activities and the network scope for referrals is an assumption, but it shows how little reading has so far returned to sites as visits.
- Radar's 3.66% almost certainly undercounts agents like Muse, since the denominator is verified, declared AI crawlers and Muse's Chromium traffic looks like ordinary Chrome. Comparing Radar to HUMAN or DataDome is not valid.
- The growth rate is the honest bull case: Muse added a large free browser agent in eight weeks, and September's jump suggests long-tail exposure could change quickly. Current long-tail exposure remains small and unmeasured.

### Gaps
- No measurement found of agent (as opposed to referral) sessions on long-tail sites. Hosting platforms such as Wix, Squarespace, Shopify and booking vendors would have this, but I found nothing published.
- No audited 2026 agentic-commerce revenue figure.
- A search summary reported that AI assistants drove 0.24% of web leads in Sept 2026 across SearchLight's network of HVAC, plumbing, electrical and roofing firms. This would be the closest local-services number, but I could not trace it to a page I opened, so verify before use.
- Primary versions of the Previsible, SearchLight, Orbit Media, Contentsquare and Marketing Science studies were not opened, and their figures are relayed through a vendor guide that itself warns some headline stats are misleading. McKinsey, eMarketer and Gartner primaries were not opened, and the Morgan Stanley fetch timed out.

## What has Sierra announced about consumer-agent-to-business-agent interaction and Meta in 2026?

### Takeaway
Sierra is the co-author with Meta of the Personal Agent Protocol ("Poppy"), announced 6 Oct 2026 and published as a draft on 9 Oct. It defines discovery, sessions and identity for three routes into a business: website, APIs, or the business's own agent. It is DRAFT, with a demo but no stated production implementer, and no reference implementation visible in the main repo as of this research.

### Cited Findings
- Announcement: 6 Oct 2026, Sierra and Meta with Genesys, Instinct, Rocket, Shopify, Stripe and Walmart. Sessions are built on OAuth and companies choose the route — [TNW](https://thenextweb.com/news/personal-agent-protocol-sierra-meta); [Sierra](https://sierra.ai/blog/introducing-personal-agent-protocol)
- Partner lists differ: Meta's post names Genesys, NiCE, Decagon, Rocket, Shopify, Stripe and Walmart, omitting Instinct, while Sierra's initial list has Instinct and not Decagon or NiCE — [Meta for Business](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together); [Sierra](https://sierra.ai/blog/introducing-personal-agent-protocol)
- Date nit: Meta and TNW give 6 Oct, whereas Sierra's 8 Oct Caller ID post says the protocol was announced the day before — [Sierra](https://sierra.ai/blog/caller-id-in-the-age-of-agents)
- DRAFT published 9 Oct 2026 with design partners including OpenAI, Visa, Mastercard, PayPal, Cloudflare, Target, Nordstrom, Gap, United, Hertz, Zendesk, Klaviyo, Zapier, ElevenLabs, Okta and 1Password, 40+ in total. A live demo at Sierra Summit showed Rocket's agent working with Muse, and a reference implementation was promised over the following month — [Sierra](https://sierra.ai/blog/poppy); [Sierra landing page](https://sierra.ai/personal-agent-protocol)
- Discovery: companies publish `/.well-known/poppy.json`, with example fields `protocol_version`, `organization`, `auth`, `agent.protocols` and `extensions` — [Poppy spec](https://personalagentprotocol.org)
- Sessions: an agent can start as a guest, adequate for stock or returns questions, then the customer signs in on the company's page with OAuth and grants read or write access. The same token spans API, website and conversation — [Sierra](https://sierra.ai/blog/poppy)
- Website route: the browser proves its session, and the company sets a cookie to apply the customer's permissions — [Poppy spec](https://personalagentprotocol.org)
- API route: OpenAPI or MCP. Company-agent route: messages carry text plus structured data, and both sides declare whether a person or AI is speaking — [Poppy spec](https://personalagentprotocol.org)
- Implementation status: the spec example shows version 0.3 and the GitHub page shows draft 0.2 as newest. The repo says it does not implement the APIs, lists no implementers or SDKs, and has a Company implementation kit (`kit/company/`) with JSON Schemas and a validator, Apache 2.0, 69 stars (fetched 3 Nov 2026) — [Poppy spec](https://personalagentprotocol.org); [GitHub](https://github.com/personal-agent-protocol/personal-agent-protocol)
- Payments are a future extension, as are push notifications and finer permissions — [TNW](https://thenextweb.com/news/personal-agent-protocol-sierra-meta); [Sierra](https://sierra.ai/blog/introducing-personal-agent-protocol)
- Meta describes open design questions: conveying identity, steering agents to efficient paths, and how agents talk to business agents — [Meta for Business](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together)
- Sierra's incentive on the phone channel: its fleming-1 model detects AI callers in real time and reports to the business, optional on Sierra voice agents (8 Oct 2026) — [Sierra](https://sierra.ai/blog/caller-id-in-the-age-of-agents)
- Competing identity standard: Visa's Trusted Agent Protocol, reported in June 2026, includes Stripe, Shopify, Microsoft and Worldpay — [TNW](https://thenextweb.com/news/personal-agent-protocol-sierra-meta)
- Jefferies names Sierra and Decagon among private beneficiaries of agent access friction (Oct 2026) — [Proactive Investors](https://www.proactiveinvestors.com/companies/news/1099848/meta-s-muse-ai-agent-blocked-by-one-third-of-websites-tested-jefferies-says-1099848.html)

### Inferences
- Poppy is the closest thing to Legible's thesis in standards form, and its website-plus-guest-session design suits a small business better than a full API. But the designers are enterprise-facing, and nothing in the materials addresses a business with no OAuth, API or agent.
- That leaves a plausible gap for a hosted intermediary to publish `poppy.json`, run the guest-mode resource and handle sign-in on behalf of many small businesses. Whether the spec allows delegated hosting for the organization and domain fields should be checked against the draft and the Company kit.
- Competitive exposure: Sierra, Decagon, Shopify or a booking vendor could offer this same layer for their own customers. Long-tail businesses without those vendors are the uncovered segment.
- Because the spec is moving quickly (versions up to 0.3 are referenced within weeks of the 9 Oct draft) and its pages disagree, any Legible implementation should validate against the current draft rather than a fixed copy.

### Gaps
- No evidence yet of any shipped agent, Muse included, fetching `poppy.json` in production, or of any live production site publishing one.
- Governance and a 1.0 timeline are not addressed in the pages I read; a Path to 1.0 page exists in the repo but I did not open it.
- Sierra's traffic data: no public volumes of personal agents hitting its customers' agents.
- Which businesses participate in the Sierra and Decagon agent-to-agent path with Instinct.
