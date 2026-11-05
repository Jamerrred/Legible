# Competitive landscape: getting small businesses ready to transact with consumer AI agents (state as of 3 Nov 2026)

Evidence tags used throughout: **[SHIPPED]** live per the vendor or a primary source. **[BETA]** live but labelled beta or preview. **[ANNOUNCED]** stated, not confirmed live. **[VENDOR CLAIM]** self-reported and unverified. **[SECONDARY]** third-party blog or trade summary, primary not seen. **[SNIPPET ONLY]** seen in a search result, page not opened or blocked, so lowest confidence.

Limits of this research: the shared web-search budget ran out partway through, so later work used only direct fetches of known URLs. Coverage is thinnest on Webflow, Mindbody, Parloa, Daydream, Crossmint, Thumbtack/Angi/Alexa+, and a systematic sweep of YC batches and Product Hunt. Each gap is listed in its section. Crunchbase was not checked, so "no funding found" does not mean unfunded. Absence of an announcement here is weak evidence of absence.

## Q1. Direct: who offers small businesses an agent-ready endpoint, MCP server or "agent storefront"?

### Takeaway
Yes, a long-tail "agent front door" category exists, but it is tiny, has no funding I could find, and is priced at $0-$5/month. Most players are directories or booking layers where the consumer still confirms. I found nobody combining connectors, adversarial simulation, an owner approval inbox and trace-driven improvement. Readiness scoring is already given away by Cloudflare and several others, and YC's "agent storefront" companies target D2C/e-commerce brands, not local services.

### Cited Findings

**Long-tail endpoint players**

| Company | What it actually ships | Price | Funding / traction found | Status | Source |
|---|---|---|---|---|---|
| Fugentic | No-code hosted MCP server from a guided intake (services, prices, areas, hours, policies, jobs declined). Hosting, registry listing, insights on which assistants arrive. Read-only: "It cannot act on them yet — no bookings, no orders, no payments." Admits registration cannot make an assistant choose you | First server free; paid plans not visible | None stated; no named customers | [SHIPPED] read-only, [VENDOR CLAIM] | [Fugentic](https://fugentic-website-dev.subgis.workers.dev/) (dev-domain site) |
| Lokuli / Local Service MCP (also BookingClaw) | 6 MCP tools over ~900 service types. `book_appointment` holds a slot 15 minutes and texts the customer, and nothing is booked until the customer confirms. `request_quotes` has Lokuli phone local pros and text back prices | Listing free; first 10 bookings free, then $5/mo; no commission; card payments 3.5% + 30c | Business count not stated; bookable businesses mostly in California | [SHIPPED], [VENDOR CLAIM] | [Local Service MCP](https://localservicemcp.com/) |
| Qasper | Hosted MCP at qasper.ai/mcp plus a consumer chat assistant. 7 tools including CheckAvailability and BookAppointment, which the README says creates a confirmed booking. Businesses self-list behind a login | Not stated | GitHub 0 stars; no counts, founders or funding on site | [SHIPPED], [VENDOR CLAIM] | [GitHub](https://github.com/QasperAI/mcp-server), [site](https://qasper.ai) |
| G-Guest (g-lab.studio) | Booking layer for restaurants, salons, studios and clinics. Public unauthenticated MCP (4 tools) in front of its human widget, returns a confirmation ID. Worked example uses a demo venue | Not stated | Founder post, 22 Aug (2026 per footer); no customer count | [SHIPPED], [VENDOR CLAIM] | [dev.to](https://dev.to/blondedevrules/i-put-a-public-mcp-server-online-that-books-real-restaurant-tables-4b3e) |
| ServeCounter | 5 MCP tools for barbers, hairdressers and nail salons on its own booking pages. `prepare_booking` returns a link, and the customer signs in and confirms | Connector price not stated | Listing showed Unhealthy, 90.2% uptime over 16 days | [SHIPPED] | [Glama](https://glama.ai/mcp/connectors/com.servecounter/booking) |
| anewera | Curated agent-readable directory: llms.txt, agent.json, agent.md and a live MCP/WebMCP endpoint per company. Agents trigger pre-approved actions (quote, meeting, callback) with recipient details hidden. German-language Swiss layer | Freemium | Listed 23 Jul 2026; no counts | [SHIPPED], [VENDOR CLAIM] | [PeerPush](https://peerpush.com/p/anewera) |
| agentready.ch | Verified Swiss company profiles with permissioned quote/callback/meeting functions | Not found | Not found | [SNIPPET ONLY], page returned 403 | [mcpservers.org](https://mcpservers.org/servers/agentready-ch-en-mcp) |
| Agent-Ready Bridge | Open-source Node MCP with one read-only tool over an exported JSON file, for legacy SMB systems | Free (MIT) | 1 star, 3 commits, no commercial offer | [SHIPPED] hobby-scale | [GitHub](https://github.com/doncelettabellamy-create/agent-ready-bridge) |
| Agentic Calendars | Email-native scheduling (Gmail/Outlook) marketed against Google's agentic booking. No agent endpoint described | From $12/mo | None stated | [SHIPPED], [VENDOR CLAIM] | [Blog, 3 Jun 2026](https://agenticcalendars.com/blog/what-is-agentic-booking/) |
| Agent Ready - Product Data Fix (Fast Commerce) | Shopify app: 17 product-data checks, 0-100 score, llms.txt, ACP/UCP support, ChatGPT app kit | $29.99 and $39.99/mo per listing (USD equivalents shown for Plus stores) | Launched 27 Jul 2026; 0 reviews | [SHIPPED] | [Shopify App Store](https://apps.shopify.com/agentready-4) |

**Evidence that the problem is real at the long tail**
- G-Guest's scan of 200 Amsterdam restaurants found 163 with working websites and none publishing an assistant-callable booking interface. [VENDOR CLAIM], Dutch sample — [dev.to](https://dev.to/blondedevrules/i-put-a-public-mcp-server-online-that-books-real-restaurant-tables-4b3e)
- Cloudflare's scan of the 200,000 most-visited domains (published 17 Apr 2026) found MCP Server Cards plus API Catalogs on fewer than 15 sites, and Markdown negotiation on 3.9%. Even the top of the web is not ready — [Cloudflare](https://blog.cloudflare.com/agent-readiness/)

**Readiness scoring (free and crowded)**
- Cloudflare's isitagentready.com [SHIPPED, 17 Apr 2026] scores Discoverability, Content, Bot Access Control and Capabilities, and gives a fix prompt for a coding agent. It checks x402, UCP and ACP but does not score them. No price is mentioned — [Cloudflare](https://blog.cloudflare.com/agent-readiness/)
- Other checkers: [Frase](https://www.frase.io/tools/agent-readiness), [Backlinko](https://backlinko.com/tools/agentic-browsing-readiness), [BuiltWith scores, 21 Jun 2026](https://blog.builtwith.com/2026/06/21/introducing-builtwith-ai-readiness-scores/), [IndexedAI](https://www.scriptbyai.com/indexedai-agent-readiness-score/), [GEO Toolbox](https://geotoolbox.ai/tools/ai-readiness), [Apify actor](https://apify.com/startuphub/agent-readiness-scanner.md), and an [AI Agent Readiness Scanner on Product Hunt](https://www.producthunt.com/products/ai-agent-readiness-scanner?page=2). [SNIPPET ONLY]

**YC 2025-2026**
- Kinect (P26): AI sales agents on brand sites plus structured brand data exposed through "agent storefronts", for D2C brands — [YC e-commerce list](https://www.ycombinator.com/companies/industry/e-commerce), [YC profile](https://www.ycombinator.com/companies/kinect)
- Wildcard (W25): AEO/GEO "command center" for e-commerce brands supporting ACP and UCP — [YC list](https://www.ycombinator.com/companies/industry/e-commerce). YC's standard $500K per one job-board article; no pricing found — [ZeroG](https://zerogtalent.com/blog/wildcard-s-500k-yc-bet-on-agentic-commerce-is-quietly-building-a-new-class-of-api-integration-engineers-and-it-reveals-what-happens-when-ai-agents-actually-buy-things) [SECONDARY]
- Channel3 (S25): product database for developers building shopping agents, paid by commission. Palisade (S26) and Pango (S26) are merchant-side and only borderline — [YC list](https://www.ycombinator.com/companies/industry/e-commerce)
- YC home-services companies from 2025-26 (Bernard S26, CentralComs P26, Cactus P25) answer human callers and dispatch. None is described as exposing a business to external agents — [YC list](https://www.ycombinator.com/companies/industry/Home%20Services)
- Async (S26) sells AI agents to law firms, clinics and real estate companies for internal work, not an agent-facing endpoint — [YC](https://www.ycombinator.com/companies/withasync) [SNIPPET ONLY]

**Near neighbours that are not long-tail**
- xpay turns a publisher URL or MCP server into a pay-per-use endpoint at about $0.001-$1.00 per call, claiming 5,000+ publishers. It targets content and API sellers, not service businesses. [VENDOR CLAIM] — [xpay](https://www.xpay.sh/merchants/wix/)
- AgenticPlug sells "agentic commerce optimization" pages for restaurants; not opened. [SNIPPET ONLY] — [AgenticPlug](https://agenticplug.ai/ai-search-optimization-for/restaurants)

### Inferences
- The Legible output artifact (machine-facing profile plus read-only MCP) is already free or nearly free. Price anchors here are $0-$5/month, so the artifact alone cannot carry a subscription.
- Most live "booking" endpoints route the final step to a consumer-confirm link (Lokuli, ServeCounter, and Fresha below). The market has not yet solved safe agent-completed writes for services, which is where an owner approval flow could matter.
- Every startup above needs businesses to adopt its booking system or join its directory. None was found sitting on top of a business's existing stack as an overlay, which is Legible's framing. That is differentiation, but it also means Legible inherits the vertical SaaS write-access problem in Q6.

### Gaps
- No systematic pass of YC W25-F26 batch lists or Product Hunt was possible after the search budget ran out; only two YC industry pages were opened.
- Funding for Fugentic, Lokuli, Qasper, G-Guest, ServeCounter and anewera: none found, Crunchbase not checked.
- Real booking volume through any of these endpoints: no data found anywhere.
- agentready.ch could not be opened. Whether it relates to anewera is unknown.

## Q2. Platform incumbents: what have they shipped, to whom, at what price?

### Takeaway
Commerce platforms have made product agent-readiness a free default, so that part is done for Shopify, Wix and Commerce.com merchants. For services, the path is being set by Google's free calling plus a few marketplaces wired into ChatGPT (OpenTable, Resy, Yelp, Fresha). Vertical SaaS (Toast, Vagaro, Housecall Pro, Jobber) has mostly not opened consumer-agent access. That leaves a real gap, but one these same platforms can close at will.

### Cited Findings

**Commerce and site platforms**

| Platform | Shipped | Announced / roadmap | Who, price |
|---|---|---|---|
| Shopify | [SHIPPED, 24 Mar 2026] Agentic Storefronts in ChatGPT (in-app browser, merchant checkout); thousands of merchants in Copilot; select brands in AI Mode/Gemini via UCP — [Shopify](https://www.shopify.com/news/agentic-commerce-momentum). Default-on for eligible stores, US buyers required, standard processing fees only, B2B not supported. Help page covers products, no mention of services or appointments — [Shopify Help](https://help.shopify.com/en/manual/online-sales-channels/agentic-storefronts/chatgpt) | Universal Cart API early access; Stripe agent-side private preview, as of 13 Oct 2026 — [ChatPal](https://chatpalbot.com/guides/agentic-commerce-for-small-stores) [SECONDARY] | Starter plan or higher for Catalog — [ChatPal](https://chatpalbot.com/guides/agentic-commerce-for-small-stores) [SECONDARY]. About 5.6M stores switched on by default — [Webhosting.today](https://webhosting.today/2026/06/12/woocommerce-10-9-ships-agent-abilities-the-hard-part-now-belongs-to-the-hosts/) [SECONDARY]. Agentic plan for non-Shopify brands: Shopify says publicly available, price undisclosed — [Shopify](https://www.shopify.com/news/agentic-commerce-momentum); one guide still says waitlist — [Ringly](https://ringly.io/blog/agentic-storefront-shopify) [SECONDARY, conflict] |
| Wix | Wix says Site MCP runs on every site (agents query products, business details, posts, services), plus automatic schema and an AI visibility view. Stripe ACS, PayPal sync, NLWeb and llms.txt are gradual and eligibility-based — [Wix blog, updated 26 Oct, year not shown](https://wix.com/blog/agentic-commerce-on-wix) [VENDOR CLAIM] | PayPal in-chat checkout expected. Agentic checkout for bookings not described — same source. UCP adoption not stated — [Wix Studio](https://www.wix.com/studio/ai-search-lab/agentic-ai-protocols) | Plans and fees not specified |
| Squarespace | No official MCP or agent announcement found; third-party connectors only — [Vinkius](https://vinkius.com/client/mastra-ai/connect/squarespace-commerce-mcp) [SNIPPET ONLY]. Listed as a Stripe Agentic Commerce Suite path — [Rye](https://rye.com/blog/agentic-commerce-startups) [SECONDARY]. Acuity: only third-party MCPs found — [Zapier](https://zapier.com/mcp/acuity-scheduling) [SNIPPET ONLY] | None found | Unknown |
| GoDaddy | Airo is the flagship website product, default in the domains path since late Q3. Annualized bookings run rate over $100M (from $50M, then $10M). Priced for broad adoption, no figures. "Agent-friendly" APIs for domains, hosting, email and commerce serve builders buying from GoDaddy, not consumer agents reaching SMBs. ANS demoed in a simulated purchase with Infoblox, Google and Cloudflare — [Q3 2026 remarks, created 29 Oct 2026](https://s23.q4cdn.com/406380394/files/content_files/GDDY-Q3-2026-Earnings-Prepared-Remarks.pdf) | New bundles in 2027; Investor Night 1 Dec — same. ANS contributed to Linux Foundation — [Q2 deck](https://s23.q4cdn.com/406380394/files/doc_financials/2026/q2/GDDY-Q2-2026-Earnings-Presentation.pdf) [SNIPPET ONLY]. LegalZoom partnership, Apr 2026 — [TechIntelPro](https://techintelpro.com/news/ai/agentic-ai/legalzoom-and-godaddy-partner-on-agent-name-service-for-ai-agents) [SNIPPET ONLY] | Micro and small businesses; stated strategy is to be their "agentic operating system". Airo prices not found |
| WordPress / WooCommerce | Abilities API in WP 6.9 (Dec 2025); MCP Adapter Feb 2026; WP 7.0 (20 May 2026). Woo 10.9 stable 23 Jun 2026 adds abilities via MCP, for store management only — [Webhosting.today](https://webhosting.today/2026/06/12/woocommerce-10-9-ships-agent-abilities-the-hard-part-now-belongs-to-the-hosts/) [SECONDARY] | Consumer-side agentic checkout on roadmap; native UCP unconfirmed | 4.3M+ live stores, no central switch. Owner must enable, provision credentials, choose abilities and secure a write endpoint. Hosts have not filled this. SiteGround force-installed an AI plugin on ~1M sites and drew a 1.1-star rating — same source |
| Commerce.com (BigCommerce) | [BETA] Cloudflare edge WebMCP (beta since Aug) turned on across almost 100,000 Commerce.com domains with no theme changes and per-merchant opt-out. WebMCP itself is experimental, behind a Chrome flag or Origin Trials — [Cloudflare, 21 Oct 2026](https://blog.cloudflare.com/webmcp-commerce/) | Usage data not given | Commerce.com merchants; price not stated |

**Service and booking platforms**

| Platform | Shipped | Gaps / roadmap | Who, price |
|---|---|---|---|
| Square | [BETA] Hosted MCP at mcp.squareup.com, seller OAuth login. Docs describe account-data and developer use; consumer-agent booking at sellers not mentioned — [Square docs](https://developer.squareup.com/docs/mcp) | No first-party ChatGPT or consumer-agent booking found | Appointments has a free tier plus Plus, Premium and Pro; dollar values not extracted — [Square](https://squareup.com/us/en/appointments/pricing) |
| Toast | Toast IQ Grow (website, SEO, ordering, marketing). Agentic products extending to scheduling, payroll, inventory; voice ordering flagged as potential — [MarketBeat, 9 Aug 2026](https://www.marketbeat.com/instant-alerts/toast-q2-earnings-call-highlights-2026-08-09/) [SNIPPET ONLY]. Sous Chef in pilot — [1Q26 transcript](https://transcripts.platformaeronaut.com/transcripts/TOST-1Q26-transcript) [SNIPPET ONLY] | No official ChatGPT app or consumer-agent MCP found. A community request asks for one — [Toast Community](https://community.toasttab.com/t5/restaurant-operations/feature-request-ai-agent-mcp-connector-for-toast-menu-and/m-p/18916) [SNIPPET ONLY, 403]. Supergood's connector works by reverse-engineering Toast's authenticated APIs — [Supergood](https://supergood.ai/docs/toast-mcp-server) [SNIPPET ONLY] | 100,000+ restaurants |
| Fresha | [SHIPPED, 4 Aug 2026] Native in ChatGPT and Claude through a public MCP. Live availability, then the user moves to Fresha's flow to confirm and pay — [press release via Webull](https://www.webull.ca/news-detail/15344919165084672). Availability, pricing and reviews in chat — [newsletter](https://buttondown.com/bizconvos/archive/quiet-day-for-launches-but-fresha-now-books/) [SECONDARY] | Agent-channel fees not disclosed | 140,000+ partners in 120+ countries (not all confirmed in the integration); US share unknown. [VENDOR CLAIM] |
| Booksy | Google AI Mode booking arrangement, API docs returning 401 — [Carly teaser, 19 Jul 2026](https://www.usecarly.com/blog/tags/salon-software/) [SECONDARY, competitor teaser, terms unverified] | Unknown | Unknown |
| Vagaro | REST API gated: paid tier using Vagaro card processing, request form, approval up to 7 business days. Employees, Locations, Appointments and Customers only — [Supergood, verified Nov 2026](https://supergood.ai/api-report-card/vagaro) [SECONDARY, sells unofficial API] | No consumer-agent integration found | Plans from $30/mo; webhooks $10/mo for 5,000 calls — same |
| Mindbody | Messenger AI inside the platform — [listing](https://preview.findailist.com/tools/mindbody) [SNIPPET ONLY] | No ChatGPT/MCP evidence found | Listed start prices inconsistent, $39-$99/mo — [Capterra](https://www.capterra.com/p/40229/MINDBODY/pricing/) [SNIPPET ONLY] |
| Yelp | [SHIPPED, 10 Aug 2026] Reservations and Waitlist in ChatGPT, US/Canada, Guest Manager restaurants only, changes route back to Yelp. Yelp licensed reviews, photos and business info to OpenAI, 24 Jul 2026 — [PPC Land](https://ppc.land/chatgpt-gains-yelp-table-booking-as-65-want-action-in-ai-local-search/) | Commercial terms undisclosed — same | Guest Manager $99-$299/mo, Yelp's own materials inconsistent — [FindSkill](https://findskill.ai/blog/chatgpt-reservations-restaurant-owner-checklist/) [SECONDARY] |
| OpenTable / Resy | [SHIPPED, 10 Aug 2026] ChatGPT reservations: OpenTable global, Resy US. No ChatGPT setup or per-cover fee published, no opt-out toggle, no attribution in owner dashboards. Restaurants not on OpenTable, Resy or Yelp Guest Manager have no path — [FindSkill](https://findskill.ai/blog/chatgpt-reservations-restaurant-owner-checklist/) [SECONDARY]. Google's US agentic booking has queried OpenTable, Resy and Tock since Nov 2025 — [PPC Land](https://ppc.land/chatgpt-gains-yelp-table-booking-as-65-want-action-in-ai-local-search/) | No self-serve public write API on OpenTable, Resy, Tock or SevenRooms as of 21 Oct 2026 — [Hyperleap](https://hyperleap.ai/blog/restaurant-booking-apis-ai-agents) [VENDOR] | Pricing page timed out; not captured |
| Calendly | [SHIPPED] Official hosted MCP, announced 11 Mar 2026 — [Calendly Community](https://community.calendly.com/developer-faq-62/announcing-the-calendly-mcp-server-5450) [SNIPPET ONLY]. GA 17 Feb 2026, no static-credential mode, browser consent required — [Scalekit](https://www.scalekit.com/blog/calendly-mcp-vs-api) [SNIPPET ONLY, date conflict] | Built for the account owner's assistant, per the consent model | Booking tools need a paid Calendly plan, per third-party guides [SNIPPET ONLY] |

**Google**
- Customer-request calling: Google may call on a customer's behalf to book, check wait times, or confirm prices and availability. Calls are recorded, free for businesses and customers, and available in all US states except IN, LA, MN, MT and NE. Verified owners can opt out in Advanced settings — [Google Help](https://support.google.com/business/answer/7690269?hl=en), [Google Help](https://support.google.com/business/answer/16190256). [SHIPPED]
- Answers from these conversations can be written back to the Business Profile as pending updates, and Google may post on the owner's behalf for verified profiles — [Google Help](https://support.google.com/business/answer/7690269?hl=en)
- [ANNOUNCED, 19 May 2026] Agentic booking expands to local experiences and services with direct links to book with a provider, and calling extends to select categories such as home repair, beauty and pet care. Stated rollout: everyone in the US, summer 2026. AI Mode has passed 1 billion monthly users — [Google](https://blog.google/products-and-platforms/products/search/search-io-2026/). I found no Google post confirming completion, though third parties describe it as deployed — [Mshahid, Oct 2026](https://mshahid.com/blog/google-ai-calling-local-businesses) [SECONDARY]
- Google's how-to page (updated 24 Jul 2026) documents product stock checks with a summary by text or email and covers no booking partners — [Google](https://blog.google/products-and-platforms/products/shopping/how-to-agentic-calling-let-google-call/)
- The AI targets top Map Pack businesses. One test returned results in about 10 minutes, and an Invoca study (Nov 2025) found 48% of human-answered calls gave the AI no price — [Sterling Sky, 11 Dec 2025](https://www.sterlingsky.ca/is-googles-ai-calling-your-business/) [SECONDARY]
- Business Agent [SHIPPED, 12 Jan 2026] is a retail chat agent activated in Merchant Center (Lowe's, Michaels, Poshmark, Reebok), for eligible US retailers. It is not a local-services product — [Google](https://blog.google/products/ads-commerce/agentic-commerce-ai-tools-protocol-retailers-platforms/)
- UCP currently supports direct buying, expanding to Lodging and Food via waitlists. Roadmap lists no booking features — [Google Developers](https://developers.google.com/merchant/ucp). AI Mode hotel booking rolled out 27 Aug 2026 with major chains and OTAs — [Skift](https://skift.com/2026/08/27/googles-agentic-hotel-booking-tool-comes-to-ai-mode/) [SNIPPET ONLY]

**Cloudflare and Microsoft**
- Cloudflare AI Index promised an MCP server, llms.txt and search API per customer domain "soon" (26 Sep 2025); I found no GA confirmation — [Cloudflare tag page](https://www.blog.cloudflare.com/tag/pay-per-crawl/)
- Pay Per Crawl was announced 1 Jul 2025 — [Cloudflare](https://www.blog.cloudflare.com/tag/pay-per-crawl/). It reportedly became Pay Per Use, with mixed-use crawlers blocked by default on ad-carrying pages from 15 Sep 2026 for free-tier and new accounts — [Beancount](https://beancount.io/blog/2026/08/05/cloudflare-pay-per-crawl-ai-bot-content-monetization-guide) [SECONDARY, no primary link]. These are publisher monetisation tools with little bearing on service SMBs.
- Microsoft: Copilot Checkout and Brand Agents, Jan 2026; Shopify merchants enrolled by default with opt-out, others apply, Brand Agents via Clarity waitlist — [Neowin](https://www.neowin.net/news/microsoft-launches-copilot-checkout-and-brand-agents-for-merchants/), [Search Engine Land](https://searchengineland.com/microsoft-launches-copilot-checkout-and-brand-agents-46717) [SNIPPET ONLY]
- NLWeb: open toolkit where each instance acts as an MCP server over Schema.org markup. About 6.3k stars, no formal releases listed, Microsoft support address — [GitHub](https://github.com/nlweb-ai/NLWeb)

### Inferences
- For product merchants on major platforms, "agent-ready" is now a default setting. Legible should not compete here.
- For services, Google's phone path needs no endpoint at all, while OpenTable/Resy/Yelp/Fresha act as walled gateways. The open question is who speaks for the independent service business with no marketplace, or with a marketplace that has not connected.
- Vertical SaaS's unopened consumer-agent access looks like a lag rather than a principled refusal. Fresha shows how quickly it can ship, so assume any overlay is on borrowed time in each vertical.

### Gaps
- Webflow: no findings, because the search budget ran out.
- Mindbody developer terms: portal page unreadable.
- Airo pricing and whether Airo exposes anything to consumer agents: not found.
- OpenTable and Resy pricing not captured.
- Confirmation of Google's summer rollout for services, and whether booking partners are tried before a call: not verified on a Google page.
- A search-result claim that Square supports AI voice ordering came from a vendor blog; not verified.

## Q3. Enterprise agent platforms moving down market; Sierra and Meta

### Takeaway
Sierra does not serve SMBs: no self-serve, no published price, reported six-figure floors. The Sierra-Meta news is a preview open standard, not an SMB product. Meta itself is the real down-market threat, with free-to-start Business Agent and Muse for Small Business. Fin is accessible at $0.99 per outcome but is a support product, not a route for long-tail businesses.

### Cited Findings

**Sierra**
- No published pricing, outcome-based contracts, no free plan or self-serve. Third-party estimates of about $150K+ annually plus $50K-$200K setup are unconfirmed, and an AWS Marketplace listing shows placeholder figures only. Named customers include WeightWatchers, Sonos, ADT, SiriusXM, Nordstrom and Wayfair. $950M Series E, May 2026, at a reported $15.8B post-money — [Macha](https://www.getmacha.com/blog/sierra-ai-complete-guide) [SECONDARY, competitor]. Estimates repeated by another competitor — [Fin](https://fin.ai/learn/sierra-ai-pricing). Competitor Lorikeet says no price list and describes a sales-led deployment model, with Sierra claiming about 40% of the Fortune 50 — [Lorikeet](https://www.lorikeetcx.ai/articles/sierra-ai-pricing-alternatives) [VENDOR CLAIM]

**Sierra and Meta: Personal Agent Protocol (PAP)**
- [ANNOUNCED, 6 Oct 2026] Sierra and Meta previewed an open standard for how personal agents interact with businesses. It covers discovery, guest and signed-in sessions over OAuth, customer-chosen read or write access, and channels via website, APIs (MCP, OpenAPI) or a company agent. v0.1 spec, workshops and a reference implementation were promised. Payments extensions are only possibilities. No mention of smaller businesses — [Sierra](https://sierra.ai/blog/introducing-personal-agent-protocol)
- Meta's framing: businesses steer agents to preferred web flows, give connectors for read/write API access, or run a business agent. Meta describes this as a preview with no launch date. Today Muse browses the web for one user and asks for explicit approval before sign-in or purchase — [Meta](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together)
- Partner lists differ. Meta names Sierra, Genesys, NiCE, Decagon, Rocket, Shopify, Stripe, Walmart — [Meta](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together). Sierra names Genesys, Instinct, Rocket, Shopify, Stripe, Walmart — [Sierra](https://sierra.ai/blog/introducing-personal-agent-protocol)
- [BETA / draft] The draft site specifies a discovery document at `/.well-known/poppy.json`, example protocol version 0.3, Apache 2.0, working toward 1.0 with unnamed design partners. It says any company can take part with what it has, and mentions neither small businesses nor hosted options — [personalagentprotocol.org](https://personalagentprotocol.org)
- A draft nicknamed Poppy on 9 Oct with 35 further partners including Visa, Mastercard, PayPal, OpenAI, Target, United and Cloudflare is single-sourced — [Relevant Audience](https://www.relevantaudience.com/meta/meta-sierra-personal-agent-protocol/) [SECONDARY]. At launch OpenAI, Anthropic, Amazon, Google, Zendesk and Salesforce were absent from launch posts — [eesel, 9 Oct 2026](https://www.eesel.ai/blog/personal-agent-protocol) [SECONDARY]
- [SHIPPED, 8 Oct 2026] Sierra's fleming-1 flags likely AI callers on voice agents built on Sierra. It is opt-in, businesses choose the handling, and PAP-identified agents can be recognised as authorised. No data on share of AI calls — [Sierra](https://sierra.ai/blog/caller-id-in-the-age-of-agents)
- [SHIPPED, 6 Oct 2026] Decagon open-sourced PACT, an agent identity and authority protocol built on A2A and OAuth 2.0, and joined the PAP working group — [Decagon](https://decagon.ai/blog/introducing-the-personal-agent-consent-trust-protocol-pact)

**Meta for SMBs**
- [SHIPPED, 3 Jun 2026] Meta Business Agent answers questions, recommends catalog items, books appointments, qualifies leads and hands off to humans. Free to start, paid tiers to follow, and Meta claims 1M+ businesses already on WhatsApp and Messenger. Calendar management is future work — [WhatsApp Business](https://whatsappbusiness.com/blog/introducing-meta-business-agent-ai/) [VENDOR CLAIM on count]. Paid access via WhatsApp Business Premium tiers, tokens for large businesses — [TechCrunch](https://www.techcrunch.com/2026/06/03/metas-ai-agent-for-whatsapp-business-is-now-available-globally/)
- [SHIPPED, 29 Sep 2026] Muse for Small Business: free with limits, paid plans for more. Connects to Instagram, Facebook Pages and ad accounts plus Shopify, Stripe, QuickBooks, HighLevel, Klaviyo, Slack and others. No named prices or country list — [TechCrunch](https://techcrunch.com/2026/09/29/meta-is-expanding-its-ai-agent-muse-to-small-businesses/)
- **Price conflict:** one tracker says free up to a refreshing limit, Meta One Essential $14.99/mo from 15 Sep 2026 (Advanced $49.99, Expert $149, Max $499), limited testing, token rate $2.00/M from 1 Aug 2026, and excludes finance, government, health, alcohol, gambling, OTC drugs and matrimony businesses. Verified 2 Nov 2026 — [AI Agent Index](https://theaiagentindex.com/agents/meta-business-agent) [SECONDARY]. A WhatsApp BSP says no free tier for API use — [Intelli](https://www.intelliconcierge.com/blog/meta-business-agent-pricing-explained-what-you-will-pay-in-2026) [SECONDARY, competitor]. Another source saw no public prices and guessed €50-100/mo — [Memacon](https://www.memacon.com/meta-business-agent-costs-prices-2026-what-can-businesses-expect/) [SECONDARY]. The likely reconciliation is app tier versus API platform, but that is my reading.

**Others**
- Intercom Fin: $0.99 per outcome, $9.99 per qualification, 50-outcome monthly minimum on another helpdesk; on Intercom plus $19/seat; 14-day trial; voice is custom. No general SMB plan — [Fin](https://fin.ai/pricing)
- Salesforce Agentforce: $2 per conversation or $500 per 100k Flex Credits (20 credits per standard action, 30 for voice); Foundations at $0; no Starter/SMB listing — [Salesforce](https://www.salesforce.com/agentforce/pricing/)

### Inferences
- PAP's design makes "start with what you have" a selling point, and its `/.well-known` discovery file is exactly what a long-tail business cannot author. A hosted PAP publisher is a real product gap, but it also shows the category is a thin compliance layer, and Meta Business Agent is likely to get native PAP support given its stated involvement.
- Meta's free agent is the closest overlap with Legible for businesses already run on WhatsApp and Instagram, and it now has the SMB's connected tools through Muse for Small Business.
- The apparent exclusion of health-related businesses from Meta's agent, if accurate, is a usable opening for clinics and possibly med spas, subject to compliance cost. It rests on one tracker.

### Gaps
- Parloa: nothing obtained before the search limit. Believed enterprise, not verified.
- Decagon pricing: not found.
- Sierra's "Ghostwriter" (a third-party guide suggested possible self-serve in March 2026): no primary source, and Macha's review does not mention it.
- Whether Meta Business Agent will be a native PAP endpoint: Meta's announcement names it as involved but gives no plan.

## Q4. Adjacent categories: GEO/AEO, agent commerce infra, AI receptionists

### Takeaway
GEO tools mostly do not serve agents; Scrunch's AXP (read-only, enterprise) is the exception. Commerce infra is real but crowded with payment rails and aimed at products, not service SMBs. AI receptionists already solve answer-and-book for humans at $49-$449/month with real budget, and they are the most credible competitor to absorb Legible's job, because a Google caller lands on them first.

### Cited Findings

**GEO/AEO** (prices read on vendor pages Aug 2026, page footer Nov 2026 — [Ryze](https://www.get-ryze.ai/blog/ai-visibility-tools-pricing-compared-2026) [SECONDARY, competitor])

| Tool | Price/mo | Readiness or agent-serving? |
|---|---|---|
| Profound | $99, $399 annual billing; self-serve tiers reportedly removed Sep 2026 — [eClincher](https://www.eclincher.com/articles/profound-alternatives-8-ai-visibility-tools-after-profounds-pricing-change) [SNIPPET ONLY, conflict] | Agent Analytics observes crawlers via server logs, no serving layer — [RankAI](https://rankai.ai/blog/scrunch-ai-alternatives) [SNIPPET ONLY] |
| Scrunch | $300, $500 ($250, $417 annual). AXP reportedly Enterprise. Acquired by Sitecore, announced 3 Jun 2026 | AXP serves a parallel LLM-optimised site at the edge via Cloudflare, Akamai or CloudFront, live for large enterprises. Help article does not address transactions — [Scrunch, 7 Jul 2026](https://intercom.help/scrunchai/en/articles/13656392-agent-experience-platform-axp) |
| Peec AI | $95, $245, $495 | Analytics and recommendations only |
| Otterly.AI | $29, $189, $489; Enterprise from $1,000 | GEO audits and recommendations |
| AthenaHQ | Free; $295; Enterprise custom | Content agent, human ships changes |

**Agent commerce infra**
- Dealroom (19 Oct 2026): 112 startups mapped, 81 founded in 2025-26, $115M raised 2026 YTD with Sapiom and Natural taking 70%. 48 in payment rails, 14 in checkout. An editorial cohort, not a census — [Dealroom](https://dealroom.co/charts/startup-stack-ai-spending)
- Rye's map: Rye (universal checkout), Henry Labs (one-click), Firmly (merchant-of-record preserving Buy Now across surfaces, $5.2M), Nekuda ($5M seed, May 2025), Skyfire ($9.5M), Basis Theory ($33M Series B, Oct 2025), and the Consortium. States every protocol requires merchant opt-in, leaving long-tail merchants on small platforms largely invisible — [Rye](https://rye.com/blog/agentic-commerce-startups) [VENDOR, Mar-Jun 2026]
- Rye's published reliability: Amazon 99% at 5 seconds, Shopify 96% at 20 seconds, non-integrated sites 65% at 5 minutes — [Stellagent, 4 Apr 2026](https://stellagent.ai/insights/agentic-commerce-infra-startups) [SECONDARY]. Rye $14M total per same source; Dealroom notes Rye and Crossmint raised partly for earlier products — [Dealroom](https://dealroom.co/charts/startup-stack-ai-spending)
- NewGen, Henry Labs, Crossmint appear as Consortium or map members; no funding found — [Trio](https://trio.dev/fintechs-building-agentic-commerce-infrastructure/) [SNIPPET ONLY]

**AI receptionists** (listing dated Nov 2026; confirm per vendor — [Trades With AI](https://tradeswithai.com/compare/ai-receptionist-pricing/) [SECONDARY])
- Rosie $49/mo; Goodcall from $79/mo; Smith.ai $300/mo for 30 calls; Upfirst from $24.95/mo, listing ChatGPT, Claude and MCP integrations; Dialzara from $29/mo; My AI Front Desk $99/mo; Ruby $250/mo; Sameday from $449/mo with Housecall Pro and ServiceTitan; NextPhone $199-$599/mo; Bland $299/mo plus $0.12/min; Retell $0.07-$0.31/min.
- Other roundups conflict on Smith.ai (per-call or $95/mo) and Goodcall (from $59) — [Target Dial](https://targetdial.co/blog/ai-receptionist-pricing), [Alm Corp](https://almcorp.com/blog/best-ai-receptionist-products-2026/) [SNIPPET ONLY, figure-to-page mapping unverified]
- Dialpad: Connect $15-$25/user/mo; Resolve AI agents custom, conversation-billed; no receptionist SKU — [Dialpad](https://www.dialpad.com/pricing/)
- Avoca: $125M+ across three rounds at $1B (27 Apr 2026), Kleiner, Meritech, General Catalyst, YC. Ships AI CSR, Simple Scheduler, Web Chat, Speed-to-Lead, Google LSA integration and call coaching, on ServiceTitan — [Avoca](https://www.avoca.ai/blog/avoca-raises-125m-series-b-1b-valuation). Quote-only, about $1,000-$3,000/mo estimated — [search roundup](https://www.stork.ai/blog/best-ai-receptionist-software-2026) [SNIPPET ONLY, mapping unverified]
- Vertical SaaS is bundling this: Housecall Pro sells Voice and CSR AI add-ons by demo — [Housecall Pro](https://www.housecallpro.com/pricing/). Jobber's AI is in-app with beta voice on every plan — [Truto](https://truto.one/blog/connect-jobber-to-chatgpt-manage-leads-requests-and-job-status.md) [SNIPPET ONLY]

### Inferences
- A consumer agent calling a business is, from the business's view, just another call. Receptionists already hold the policy knowledge, calendar connection, call transcripts and budget, so adding an agent-readable endpoint is a small extension for them. They also see the traces Legible needs.
- GEO vendors could add readiness cheaply (and already give away checks, per Q1), but their buyer is a marketer at a mid-size or larger brand, not a salon owner.
- Commerce infra is complementary to Legible rather than competitive, and mostly irrelevant until agents pay for services in-channel.

### Gaps
- Daydream: not researched. Crossmint, Henry Labs and New Generation funding: not found.
- Goodcall, Rosie, Sameday funding: not established; Sameday figures conflict ($125K-$750K) across trackers — [VCBacked](https://www.vcbacked.co/company/sameday) [SNIPPET ONLY].
- Share of receptionist calls coming from AI agents: no reliable number found. Sierra's post gives none.

## Q5. SMB willingness to pay, adoption, and channels

### Takeaway
Adoption depends heavily on definition, from 18-24% in hard data to 66-77% in opinion surveys. The actual spend is low: median about $28/month in bank data, $250/month among those who report paying. Legible has two plausible prices: under $50 for self-serve, or $100-$300 if bundled into answer-and-book or sold through agencies. Channel access is probably decisive, and it already belongs to HighLevel, GoDaddy, Wix, vcita-style white-label players and vertical SaaS.

### Cited Findings

**Adoption, ordered by evidence strength**
- JPMorganChase Institute (14 Apr 2026): 4.6M+ small business accounts, paid tools only, embedded AI excluded. 17.7% had adopted by end 2025. Information 39.3%, professional services 30.3%, education 29.5%, construction 8.9%, transport 5.4% — [JPMCI](https://www.jpmorganchase.com/institute/all-topics/business-growth-and-entrepreneurship/understanding-ai-use-by-small-businesses)
- Census BTOS: 19.8% of businesses as of 3 May 2026, flat in a 17-20% band. 250+ employees 37%; firms of four or fewer under 20%; Retail about 14% — [Census, 26 May 2026](https://census.gov/library/stories/2026/05/ai-use-businesses.html)
- NFIB (2025): 24% use AI; 75% of non-users have no plans in 12 months; only 9% use or plan AI for customer service. 82% of small businesses have a website (75% at 1-9 employees, 66% of non-employers), and only 19% of those accept payments on it — [NFIB](https://www.nfib.com/wp-content/uploads/2025/06/2025-NFIB-Technology-Survey.pdf)
- US Chamber (2026, n=3,732, under 250 employees): 66% use AI, up from 58%; 64% rely mostly or entirely on external tools — [US Chamber](https://www.uschamber.com/assets/documents/Empowering-Small-Business-The-Impact-of-Technology-on-U.S.-Small-Business-Small-Business-Report-2026.pdf). A blog's "89%" figure conflicts — [Small Biz Talks](https://smallbiztalks.com/small-business-ai-adoption-statistics/) [SECONDARY]; prefer the primary.
- Goldman Sachs 10KSB (2026, n=1,256, programme participants, not a random sample): 76% use AI, 14% fully integrated, 73% want training — [Mega Web Vision](https://megawebvision.com/insights/ai-adoption-statistics-small-business) [SECONDARY, Goldman page returned 403]. Barrier percentages differ between summaries.
- Intuit QuickBooks (2026, 34,000+ owners, four countries): 77% regular use in US. Vendor survey — [Mega Web Vision](https://megawebvision.com/insights/ai-adoption-statistics-small-business) [SECONDARY]
- SBA Office of Advocacy (Sep 2025): 77% of non-adopters see no applicable use, 82% among under-5-employee firms — [Small Biz Talks](https://smallbiztalks.com/small-business-ai-adoption-statistics/) [SECONDARY]
- Thryv (2026, vendor): nearly 70% say they lack skills to use AI effectively — [Thryv](https://www.thryv.com/blog/ai-for-small-business-2026-report/)

**Willingness to pay**
- Bank data: median paid AI spend about $28/month in 2025, down from about $78 in 2022; P25-P75 about $20-$90. 63% spend $1-$40, 22% spend $41-$150, 16% spend above $150 — [JPMCI](https://www.jpmorganchase.com/institute/all-topics/business-growth-and-entrepreneurship/understanding-ai-use-by-small-businesses)
- Survey data: 41% use free tools; median $250/month among those paying — [US Chamber](https://www.uschamber.com/assets/documents/Empowering-Small-Business-The-Impact-of-Technology-on-U.S.-Small-Business-Small-Business-Report-2026.pdf). SBE Council median about $2,200/year — [Mega Web Vision](https://megawebvision.com/insights/ai-adoption-statistics-small-business) [SECONDARY]

**Comparable price points**

| Tool type | Price/mo | Source |
|---|---|---|
| Agent endpoint | $0-$5 | [Fugentic](https://fugentic-website-dev.subgis.workers.dev/), [Lokuli](https://localservicemcp.com/) |
| Shopify readiness app | $29.99-$39.99 | [Shopify App Store](https://apps.shopify.com/agentready-4) |
| AI scheduling, chat | From $12; free to $20 | [Agentic Calendars](https://agenticcalendars.com/blog/what-is-agentic-booking/), [ChatPal](https://chatpalbot.com/guides/agentic-commerce-for-small-stores) |
| GEO entry | $29-$295 | [Ryze](https://www.get-ryze.ai/blog/ai-visibility-tools-pricing-compared-2026) |
| AI receptionist | $25-$449; quote-only above | [Trades With AI](https://tradeswithai.com/compare/ai-receptionist-pricing/) |
| Salon software | Vagaro from $30, many pay $200+ after add-ons | [Supergood](https://supergood.ai/api-report-card/vagaro) [SECONDARY] |
| Field service | Housecall Pro $59, $149, $299 annual; API only on Max | [Housecall Pro](https://www.housecallpro.com/pricing/) |
| Restaurant guest mgmt | Yelp Guest Manager $99-$299 | [FindSkill](https://findskill.ai/blog/chatgpt-reservations-restaurant-owner-checklist/) [SECONDARY] |
| Agency platform | HighLevel $97, $297, $497; AI Employee $50-$97 per sub-account | [HighLevel](https://www.gohighlevel.com/pricing) |

**Channels**
- HighLevel: unlimited sub-accounts at $297, SaaS Mode resale at $497, white-labelling, rebilling with markup — [HighLevel](https://www.gohighlevel.com/pricing). AI Agent action with MCP tool support in workflows, Apr 2026 — [NetPartners](https://netpartners.marketing/gohighlevel-april-2026-releases-the-agentic-ai-month/) [SNIPPET ONLY]. Named as a Muse for Small Business integration — [TechCrunch](https://techcrunch.com/2026/09/29/meta-is-expanding-its-ai-agent-muse-to-small-businesses/)
- vcita inTandem: every agent available white-label to telcos, SaaS firms, publishers and marketing firms, pitched as reducing churn. No prices (13 Oct 2026) — [vcita](https://intandem.vcita.com/blog/partners/top-10-ai-agents-for-your-small-business-clients)
- Vendasta: official MCP gateway "planned" for H2 2026 with no committed date; customers asking for an ETA through 2 Oct 2026 — [Vendasta feedback](https://feedback.vendasta.com/ai-workforce/p/official-vendasta-mcp-model-context-protocol)
- Yext: MCP, API, desktop and mobile access for paying Scout customers from 17 Jun 2026 (12M locations, enterprise and multi-location brands) — [Yext](https://www.yext.com/about/news-media/yext-opens-full-platform-for-trusted-agentic-marketing-execution). Scout MCP and API for partners, 18 May 2026 — [Business Wire](https://www.businesswire.com/news/home/20260518413611/en/Yext-Opens-Scout-Visibility-Intelligence-to-Partners-with-the-Launch-of-MCP-and-API) [SNIPPET ONLY]
- Birdeye: 30-tool MCP (3 Aug 2026) is owner-facing analytics for reputation and listings, not for consumer agents — [Birdeye](https://birdeye.com/blog/?p=72193)

### Inferences
- The 41%-free plus $28 median pattern suggests self-serve Legible competes with "free default from my platform". Pricing near a receptionist needs a booked-job ROI story, and that story is hard because attribution is weak (see Q7).
- With 64% relying on external tools and low skill confidence, the buyer who understands "adversarial agent simulation" is more likely to be an agency than an owner. Sell the simulation report as an agency audit deliverable, and let the agency own the recurring relationship.
- Vendasta's unshipped MCP and customer pressure suggest reseller platforms want this but have not built it, making a white-label partner a realistic early route.

### Gaps
- Franchise groups and local chambers as a channel: no direct evidence found. Treat as hypothesis.
- Web agency share of SMB site management: no data obtained.
- Direct survey of WTP for "agent readiness": none exists that I could find.
- A search roundup cited BTOS at 23.8% through 4 Oct 2026; not confirmed on Census.
- BTOS, JPMCI and NFIB splits for personal services, repair and restaurants were not obtained, so vertical adoption is unknown.

## Q6. Where is the wedge? Which verticals are underserved and which are locked?

### Takeaway
Restaurants and boutique retail are effectively closed. Salons are contested, and pet care plus independent home-service trades look like the best wedge: named in Google's calling categories, weak endpoint options, and the valuable answers are unstructured context rather than a calendar slot. The defensible wedge is the context-and-approval layer rather than the endpoint, and the wedge should be tested as a feature for agencies or receptionist vendors before being treated as a standalone company.

### Cited Findings

| Vertical | Clear agent intents | Who controls the path today | API accessibility | Read |
|---|---|---|---|---|
| Restaurants | Reserve, waitlist, order | OpenTable, Resy, Yelp in ChatGPT — [FindSkill](https://findskill.ai/blog/chatgpt-reservations-restaurant-owner-checklist/); OpenTable, Resy, Tock on Google — [PPC Land](https://ppc.land/chatgpt-gains-yelp-table-booking-as-65-want-action-in-ai-local-search/); UCP "Food" waitlist — [Google](https://developers.google.com/merchant/ucp) | No self-serve write access — [Hyperleap](https://hyperleap.ai/blog/restaurant-booking-apis-ai-agents) [VENDOR]. Toast access reverse-engineered by third parties — [Supergood](https://supergood.ai/docs/toast-mcp-server) [SNIPPET ONLY] | Locked for reservations. Takeout/ordering less settled, but UCP Food is coming |
| Salons, beauty | Book, price, stylist choice | Fresha live in ChatGPT and Claude — [press release](https://www.webull.ca/news-detail/15344919165084672); Booksy with Google [unverified] — [Carly](https://www.usecarly.com/blog/tags/salon-software/); Google calling names beauty — [Google](https://blog.google/products-and-platforms/products/search/search-io-2026/) | Vagaro gated, tied to its card processing — [Supergood](https://supergood.ai/api-report-card/vagaro) [SECONDARY]; Square MCP beta — [Square](https://developer.squareup.com/docs/mcp) | Contested and closing. Open only for independents on non-connected tools |
| Med spas | Book, eligibility, pricing | Fresha lists med spas — [press release](https://www.webull.ca/news-detail/15344919165084672); Agentic Calendars files them under Google's beauty — [blog](https://agenticcalendars.com/blog/what-is-agentic-booking/) [VENDOR] | Zenoti, Boulevard API terms not found | High ticket, consult-heavy, but unverified; compliance risk |
| Home services | Quote, availability, emergency, scope fit | Google calling names home repair — [Google](https://blog.google/products-and-platforms/products/search/search-io-2026/); Avoca, Sameday and vendor AI on the phone | No first-party ChatGPT app or MCP from Housecall Pro per a competitor — [Carly, 19 Sep 2026](https://www.usecarly.com/blog/tags/housecall-pro/); none from ServiceTitan per same vendor — [Carly](https://www.usecarly.com/blog/tags/ai-field-service-assistant/) [SNIPPET ONLY]; Jobber via Truto bridge — [Truto](https://truto.one/blog/connect-jobber-to-chatgpt-manage-leads-requests-and-job-status.md) [SNIPPET ONLY]. Housecall Pro API only on $299 Max — [Housecall Pro](https://www.housecallpro.com/pricing/) | Larger shops locked by ServiceTitan and Avoca. Independents on Jobber-level tools are the opening |
| Pet care | Book, price, vaccination and breed policy | Google calling names pet care — [Google](https://blog.google/products-and-platforms/products/search/search-io-2026/) | Vertical SaaS not researched | Candidate wedge, thin evidence |
| Clinics | Book, insurance, availability | Google's help lists booking calls generally — [Google](https://support.google.com/business/answer/7690269?hl=en); health reportedly excluded from Meta's agent — [AI Agent Index](https://theaiagentindex.com/agents/meta-business-agent) [SECONDARY]; Async (YC S26) sells to clinics internally — [YC](https://www.ycombinator.com/companies/withasync) [SNIPPET ONLY] | Not researched | Possible gap, but HIPAA cost makes it a poor first wedge for a prototype (my judgement) |
| Tutors, coaches | Fit, availability, trial | Calendly official MCP — [Calendly](https://community.calendly.com/developer-faq-62/announcing-the-calendly-mcp-server-5450) [SNIPPET ONLY]; Calendly and Cal.com open APIs — [Hyperleap](https://hyperleap.ai/blog/restaurant-booking-apis-ai-agents) [VENDOR] | Open | Easy integration; low ticket; agent demand unevidenced |
| Boutique retail | Stock, buy | Shopify default-on, Wix, Commerce.com, and Google's stock calls — [Google](https://blog.google/products-and-platforms/products/shopping/how-to-agentic-calling-let-google-call/) | Open via platforms | Commoditised |

**Data point supporting a context-first wedge**
- 48% of human-answered calls gave Google's AI no price per Invoca, Nov 2025 — [Sterling Sky](https://www.sterlingsky.ca/is-googles-ai-calling-your-business/) [SECONDARY]. Readiness checkers test technical standards — [Cloudflare](https://blog.cloudflare.com/agent-readiness/) — or product data fields — [Agent Ready](https://apps.shopify.com/agentready-4) — rather than whether a business can answer what an agent asks.

### Inferences

**Piece-by-piece verdict for Legible**

| Piece | Verdict | Why |
|---|---|---|
| Machine-facing resource (profile, llms.txt, read-only MCP) | **Commoditised** | Free from Wix (claimed), Fugentic, Lokuli, anewera; Cloudflare's promised AI Index would cover the rest if shipped |
| Readiness score | **Commoditised** | Free from Cloudflare and others |
| Connecting website, socials, calendar, catalog | **Commoditising fast** | Muse for Small Business, Zapier, Truto and Composio bridges, official Calendly and Square MCPs. Write access still gated by vertical SaaS |
| Booking transaction for vertical SaaS users | **Locked or closing** | OpenTable, Resy, Yelp, Fresha, Vagaro gating |
| Standards publishing across ACP, UCP, PAP, WebMCP, ARD for a non-technical owner | **Open but thin** | Real pain, moving target; only valuable if agents consult it, and likely absorbed by platforms |
| Adversarial simulation for missing business context | **White space, feature-sized** | I found no one offering it for SMBs. Easy to copy; strongest as a sales wedge or agency audit |
| Owner approval inbox for agent-originated requests | **Mostly white space** | Consumer confirm links dominate; anewera has pre-approved actions; Yext's Action Center concerns marketing fixes. WTP unproven; receptionists and Meta can add it |
| Self-improvement from agent traces | **White space with a data problem** | Traces only exist on channels Legible hosts, and Google-call, ChatGPT and Muse browsing traffic will largely bypass it |

**Recommended wedge hypothesis:** independent, phone-first home-service trades and pet care businesses on light tools, sold through agencies or receptionist vendors, with the promise "answer what Google's caller and other agents ask, correctly, with approval on anything binding". Start with the simulation as an audit, then publish the outcome across Business Profile, phone agent script, Meta and a PAP/MCP endpoint. The aim is to win on accurate quotes and policies, not on being an endpoint. This is inference and needs customer validation.

### Gaps
- Pet-care and med-spa vertical SaaS (for example Zenoti, Boulevard, Gingr, MoeGo) API terms and agent integrations: not researched.
- Whether answering Google's caller better actually leads to selection: no data.
- Vertical-level agent traffic volumes: no public US source found. Fresha's figure below is APAC only.

## Q7. Disintermediation and the strongest bear case

### Takeaway
The bear case is strong. Consumer agents can already reach long-tail businesses by phone or browser without any endpoint, platforms give away the structured layer, and the demand signal for protocol-based transactions is mixed. Legible's surviving thesis depends on accurate business context and owner control being scarce once agents arrive, and neither has yet been shown to be something small businesses pay for separately.

### Cited Findings

**Agents do not need an endpoint**
- Google calls on the consumer's behalf for free, in 45 US states, with Business Profile as its store of what it learned — [Google Help](https://support.google.com/business/answer/7690269?hl=en). The stated expansion to services was for all US users in summer 2026 — [Google](https://blog.google/products-and-platforms/products/search/search-io-2026/). AI Mode: 1B+ monthly users, same source.
- Lokuli itself phones pros when no bookable business exists, showing even endpoint vendors fall back to the phone — [Local Service MCP](https://localservicemcp.com/)
- Muse is live and transacting by browsing the web with user approval, with no protocol needed — [Meta](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together). About 25% of users shop with it, average purchase about $200, ~10M US/Canada sign-ups. Stripe's president said agentic activity surged from September. All company statements — [Payments Dive, 23 Oct 2026](https://www.paymentsdive.com/news/shopping-is-muses-top-task-meta/833817/)
- Rye reports 65% reliability on non-integrated sites at 5 minutes per order — [Stellagent](https://stellagent.ai/insights/agentic-commerce-infra-startups) [SECONDARY]. If this improves, the case for structured endpoints weakens.

**Platforms give it away**
- Shopify default-on — [Shopify Help](https://help.shopify.com/en/manual/online-sales-channels/agentic-storefronts/chatgpt); Wix on every site — [Wix](https://wix.com/blog/agentic-commerce-on-wix) [VENDOR CLAIM]; Commerce.com on almost 100k domains without merchant work — [Cloudflare](https://blog.cloudflare.com/webmcp-commerce/); Meta free to start — [WhatsApp Business](https://whatsappbusiness.com/blog/introducing-meta-business-agent-ai/); Google calling free — [Google Help](https://support.google.com/business/answer/7690269?hl=en)

**Being reachable does not mean being chosen, and discovery is out of scope**
- Google's AI typically targets top Map Pack businesses — [Sterling Sky](https://www.sterlingsky.ca/is-googles-ai-calling-your-business/) [SECONDARY]. Fugentic says registration cannot make an assistant choose you — [Fugentic](https://fugentic-website-dev.subgis.workers.dev/). ChatGPT restaurant selection depends on availability inside partner platforms, with no published ranking — [FindSkill](https://findskill.ai/blog/chatgpt-reservations-restaurant-owner-checklist/) [SECONDARY]

**Protocol-transaction demand is mixed, and the standards are unsettled**
- Instant Checkout launched Sep 2025 and was scaled back. OpenAI said 24 Mar 2026 it would let retailers use their own checkout and focus on discovery. Walmart's EVP reportedly told Wired conversion was one-third of its own site. The Shopify pilot reached about 12 merchants, and Etsy said sales volume was low — [Stellagent](https://stellagent.ai/insights/chatgpt-instant-checkout-failure-lessons) [SECONDARY]; about 12 live also — [EcomCrew](https://www.ecomcrew.com/openai-pulls-back-on-chatgpt-instant-checkout/) [SECONDARY]. A competing figure of ~30 Shopify merchants (attributed to Forrester) appeared in search results only [SNIPPET ONLY].
- Standards in flight: PAP draft, 0.3 in example — [PAP site](https://personalagentprotocol.org); PACT — [Decagon](https://decagon.ai/blog/introducing-the-personal-agent-consent-trust-protocol-pact); WebMCP experimental — [Cloudflare](https://blog.cloudflare.com/webmcp-commerce/); ACP moved toward discovery — [ChatPal](https://chatpalbot.com/guides/agentic-commerce-for-small-stores) [SECONDARY]; UCP adding verticals — [Google](https://developers.google.com/merchant/ucp); ANS and ARD — [GoDaddy](https://s23.q4cdn.com/406380394/files/content_files/GDDY-Q3-2026-Earnings-Prepared-Remarks.pdf). Fugentic says assistant support for registry lookups is still new — [Fugentic](https://fugentic-website-dev.subgis.workers.dev/)

**ROI cannot yet be shown to the buyer**
- No ChatGPT attribution in Yelp, OpenTable or Resy owner dashboards — [FindSkill](https://findskill.ai/blog/chatgpt-reservations-restaurant-owner-checklist/) [SECONDARY]. Median paid AI spend ~$28/mo — [JPMCI](https://www.jpmorganchase.com/institute/all-topics/business-growth-and-entrepreneurship/understanding-ai-use-by-small-businesses). 75% of non-users plan nothing — [NFIB](https://www.nfib.com/wp-content/uploads/2025/06/2025-NFIB-Technology-Survey.pdf)

**Counter-evidence: why the idea is not dead**
- Businesses bear real costs from phone agents: 48% gave no price — [Sterling Sky](https://www.sterlingsky.ca/is-googles-ai-calling-your-business/) [SECONDARY]. Sierra built caller detection, implying AI calls are seen as a concern and that identified agents get better treatment — [Sierra](https://sierra.ai/blog/caller-id-in-the-age-of-agents)
- Meta says connectors beat browser automation in many cases — [Meta](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together). Sierra says PAP lets companies set what agents may do and see when an agent acts for a customer — [Sierra](https://sierra.ai/blog/introducing-personal-agent-protocol)
- Fresha reported Gemini and other LLMs at 25% of online booking referrals in APAC (up from about one in seven two years earlier), though undefined and with no methodology, and only in some regions — [BriefGlance, Feb 2026](https://briefglance.com/articles/ai-now-drives-1-in-4-selfcare-bookings-yielding-9x-roi-for-salons) [VENDOR CLAIM]. Fresha also claims 1.2M monthly appointments via Google across 30,000+ businesses — same source.
- 65% of US adults in a Yelp-commissioned Morning Consult survey (n=2,202, Feb 2026) said action-taking on trusted platforms matters when using AI for local discovery. This supports demand but also the platform-led view — [PPC Land](https://ppc.land/chatgpt-gains-yelp-table-booking-as-65-want-action-in-ai-local-search/)

### Inferences

**Strongest bear case against Legible, in one argument**
1. The consumer agent already has three free paths to a long-tail business: Google's phone call, its own browser, and marketplace gateways. None requires Legible.
2. The business's structured layer is being generated for free by Wix, Shopify, Google Business Profile, Meta and vertical SaaS, using data they already hold.
3. The traffic Legible would see is the residue the free paths miss. A long-tail business may see too few agent interactions on a hosted endpoint for traces to self-improve, or for an owner to justify payment. I have no measured volumes, so this is a reasoned estimate, but no vendor publishes contrary evidence.
4. Businesses cannot see the benefit: no attribution, no discovery claim (explicitly out of scope), and a median budget nearer $30 than $300.
5. Well-funded adjacent players can add the remaining pieces: Avoca with $125M+, Meta with distribution, GoDaddy with $100M+ Airo run rate and a stated "agentic OS" goal.
6. Approval inboxes add work for owners whose stated problem is time, and Meta already markets to that exact shortage. Consumers can also approve at the agent side, reducing the owner's role.
7. Therefore Legible risks being a feature with no distribution, in a category whose standards are still moving.

**What would have to be true for Legible to win**
- Agent-originated requests reach high enough frequency in a specific vertical that errors are costly (mis-quotes, policy violations, double bookings).
- Owners or agencies pay for accuracy and control across several surfaces, because no single platform wants to be neutral across Google, Meta, ChatGPT and vertical SaaS.
- Legible gets traces via a partner that sees real traffic, such as a receptionist vendor or agency platform, rather than relying on its own endpoint.
- Cheap kill tests: run the adversarial simulation on 20 local businesses in one vertical, then measure whether owners or agencies pay for the fix. Separately, ask receptionist vendors whether AI callers are appearing in their logs.

**Disintermediation assessment:** phone-based agents do not fully eliminate the need, since someone still has to supply answers at the moment of the call. But the supplier of those answers is likely to be whoever already answers the phone or holds the Business Profile. Legible's most realistic position is upstream of those systems as a context source, not in front of them as a gateway.

### Gaps
- Measured share of local-business calls or bookings coming from AI agents in the US: no reliable figure found.
- Whether Google favours businesses with structured booking over phone calling: not verified. A vendor search result claimed partner routing occurs first, unconfirmed by Google.
- Thumbtack, Angi, Alexa+ and similar marketplace routes for home services: not researched, because the search budget ran out. These could further strengthen the bear case.
- Whether ChatGPT or other consumer agents place outbound calls: searched once with no confirmation.
- OpenAI's restaurant release notes were not opened directly; the facts come from secondary reports.
