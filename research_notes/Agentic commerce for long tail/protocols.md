# Agent-to-business protocol landscape and the "Poppy" protocol (state as of 2026-11-03)

Status labels used below: **[LIVE]** = shipped and observed in real use. **[DRAFT]** = public spec, no confirmed consumer-agent use. **[ANNOUNCED]** = stated intent only. **[DORMANT]** = archived or no meaningful recent activity. "Probe" = my own HTTP GET on 2026-11-03 from one IP with a browser user agent. A 404 is suggestive, not proof, and a 403, 429 or unfollowed redirect is inconclusive.

## 1. What is "Poppy"?

### Takeaway
Verified. "Poppy" is the official short name of the **Personal Agent Protocol** (press shorthand: PAP), announced by Sierra and Meta on 2026-10-06, with a first public draft on 2026-10-09. It is a real, public, Apache-2.0 draft (0.1 and 0.2 frozen, 0.3 in progress), still pre-1.0 and changing fast. I found no evidence that any shipping consumer agent speaks it natively.

### Cited Findings

**Identity and dates**
- Exact name is "Personal Agent Protocol", self-described as `"poppy" for short`; tagline "An open protocol for every company and every personal agent" — [personalagentprotocol.org](https://personalagentprotocol.org); [GitHub repo description](https://github.com/personal-agent-protocol/personal-agent-protocol)
- 2026-10-06: "Introducing Personal Agent Protocol" by Bret Taylor and Clay Bavor, published around Sierra Summit, promising a v0.1 spec "later this month" — [Sierra](https://sierra.ai/blog/introducing-personal-agent-protocol); summit context from [Cellcog (secondary)](https://cellcog.ai/blog/personal-agent-protocol/)
- 2026-10-06: Meta's own post, "A New Way for Businesses and Personal Agents to Work Together", says the protocol "will be open for anyone to implement" — [Meta for Business](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together)
- 2026-10-09: "Sharing a draft of Personal Agent Protocol" says the draft is "known as Poppy". This is the first use of the name that I found. Neither site explains where the name comes from — [Sierra](https://sierra.ai/blog/poppy)
- Version history: 0.1 published 2026-10-09 (frozen); 0.2 published 2026-10-24 (frozen, breaking); 0.3 marked "In progress" on the changelog, while docs already present "Draft 0.3" — [changelog](https://personalagentprotocol.org/docs/changelog); [Path to 1.0](https://personalagentprotocol.org/docs/path-to-1)
- The third-party SDK dates Draft 0.3 at 2026-10-30, and commits were still landing on 2026-11-02 and 11-03 (including the UCP extension) — [PyPI](https://pypi.org/project/personal-agent-protocol/); [commits via GitHub API](https://api.github.com/repos/personal-agent-protocol/personal-agent-protocol/commits?per_page=5)
- Conflict: [Yellow](https://yellow.com/news/meta-muse-5m-downloads-websites-blocking) dates the announcement Oct 7. The Sierra and Meta primaries say Oct 6.

**Backers (conflict between lists)**
- Sierra, Oct 6: Meta plus Genesys, Instinct, Rocket, Shopify, Stripe, Walmart — [Sierra](https://sierra.ai/blog/introducing-personal-agent-protocol)
- Meta, Oct 6: Sierra, Genesys, NiCE, Decagon, Rocket, Shopify, Stripe, Walmart. Instinct is absent — [Meta](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together)
- Sierra, Oct 9, adds 35 design partners: Adyen, Atomic, Bank of America, BBVA, Chime, Cigna, Cloudflare, Comcast, DIRECTV, ElevenLabs, FOX, Gap Inc., GEICO, Hertz, Insurify, Klaviyo, Liberty Mutual, Mastercard, Nordstrom, Notion, Okta, OneSignal, OpenAI, PayPal, Plaid, SiriusXM, Synchrony, Target, United Airlines, Venmo, Visa, Wells Fargo, Zapier, Zendesk, 1Password. Decagon does not appear in the list as I extracted it — [Sierra](https://sierra.ai/blog/poppy)
- Personal-agent partners are named as Instinct, Meta and OpenAI; company and technology partner groups are also listed — [Path to 1.0](https://personalagentprotocol.org/docs/path-to-1)
- "Design partner" is not adoption. No neutral foundation or formal governance model is stated on the Path to 1.0 page — [Path to 1.0](https://personalagentprotocol.org/docs/path-to-1)
- Stripe and Shopify also back Visa's Trusted Agent Protocol, which TNW calls "a rival protocol"; it says "Stripe and Shopify are now in both" — [TNW, 2026-10-06](https://thenextweb.com/news/personal-agent-protocol-sierra-meta)

**Repo, licence, maturity**
- Spec repo: `personal-agent-protocol/personal-agent-protocol`, created 2026-10-14, last push 2026-11-03, 69 stars, 12 forks, 35 open issues/PRs, Apache-2.0 — [GitHub API](https://api.github.com/repos/personal-agent-protocol/personal-agent-protocol)
- The licence covers spec and docs but not the names "Personal Agent Protocol" and "Poppy", the logo or the site design — [repo README](https://github.com/personal-agent-protocol/personal-agent-protocol)
- Contributors are concentrated: `arya` 81 commits, `ToddKerpelman` 7, `shopdave` 1 — [GitHub API](https://api.github.com/repos/personal-agent-protocol/personal-agent-protocol/contributors)
- Stability: "Each 0.x version can break the one before it"; backward compatibility starts at 1.0. No 1.0 date is published — [changelog](https://personalagentprotocol.org/docs/changelog); [Path to 1.0](https://personalagentprotocol.org/docs/path-to-1)
- Churn example: 0.3 replaced the 0.2 session model with a per-request `Poppy-Session` JWT and delegated keys, and removed `poppy:read`/`poppy:write` scopes — [changelog](https://personalagentprotocol.org/docs/changelog)
- Issue #60 (2026-10-29, from Authlete) reports the live site ahead of `main`; #64 reports home-page walkthroughs still showing the 0.2 wire format — [#60](https://github.com/personal-agent-protocol/personal-agent-protocol/issues/60); [#64](https://github.com/personal-agent-protocol/personal-agent-protocol/issues/64)

**What Draft 0.3 specifies** (all from [spec](https://personalagentprotocol.org/docs/0.3/spec) unless noted)
- *Transport:* HTTPS and JSON. Conversation events use long polling with `cursor` and `wait`; SSE is optional.
- *Discovery:* `https://{domain}/.well-known/poppy.json`. Required: `protocol_version` (`major.minor`) and `organization` (`name`, `domain`). At least one of `agent`, `apis`, `web` must be present. Other fields: `auth`, `feedback`, `excluded_tasks`, `extensions`, `skill_index`.
- *Agent identity:* `client_id` is an HTTPS URL returning client metadata (`jwks_uri`, `redirect_uris`, `token_endpoint_auth_method: private_key_jwt`). A `jwks_uri` key signs a delegation (`poppy-delegation+jwt`, max 24 hours), and the delegated key signs a per-request `Poppy-Session` JWT (`ES256`, claims `iss`, `aud`, `sid`, `sub`, `htm`, `htu`, `iat`, `jti`, optional `agent_id`, `ath`). Companies must accept ES256 and should accept PS384.
- *User privacy:* before sign-in the company sees only a non-personal ID that is stable over time and different at each company — [introduction](https://personalagentprotocol.org/docs/introduction)
- *Auth:* standard OAuth. Direct Sign-In (authorization code + PKCE) and Device Sign-In (RFC 8628), with issuer found through RFC 9728 and RFC 8414 metadata. Scopes are company-defined, with `scope_hints` for reversibility and personal data. "The Session JWT never grants account access" — [foundation milestone](https://raw.githubusercontent.com/personal-agent-protocol/personal-agent-protocol/main/kit/company/milestones/foundation.md)
- *Channels:* `apis[]` of type `openapi` (3.0/3.1) or `mcp` (Streamable HTTP, MCP 2025-06-18 or later); `web.browser_session_endpoint` for joining a browser to the session; `agent.protocols` for conversations.
- *Message schema:* `POST {endpoint}` (start), `POST {endpoint}/{id}/messages`, `GET {endpoint}/{id}/events`, `POST {endpoint}/{id}/handoff`, `POST {endpoint}/{id}/close`. Messages carry `id`, `author`, `text`, `data`, `context`, `extensions`.
- *Human handoff:* first-class. `author.type` and `responder` distinguish `agent` from `human`; `/handoff` returns 202 and status moves to `queued`. "Direct Conversations" let the user talk to the company, started by a `user_requested` event, but "the User decides when they're brought in".
- *Transactions:* no core payments. The `operations` extension v2 has the user approve exact terms, then the agent retries; "Retries never perform the action twice" — [extensions](https://personalagentprotocol.org/docs/0.3/extensions)
- *Other extensions:* `disclosures` (e.g. allergens), `links`, `mediated-sign-in` (transitional, planned for removal at 1.0), `ucp` — [extensions](https://personalagentprotocol.org/docs/0.3/extensions); [changelog](https://personalagentprotocol.org/docs/changelog)
- *Open topics:* payments, push notifications, version compatibility, signed approvals with user-held keys, attachments, self-hosted agents — [Path to 1.0](https://personalagentprotocol.org/docs/path-to-1)

**Confusables, ruled out**
- **PACT** (Personal Agent Consent & Trust), Decagon + Instinct, 2026-10-06: separate protocol built on A2A + OAuth device flow, Apache-2.0, 114 stars. Decagon says it is joining the Poppy working group, but the post does not say how the two relate — [Decagon](https://decagon.ai/blog/introducing-the-personal-agent-consent-trust-protocol-pact); [GitHub API](https://api.github.com/repos/openpactprotocol/openpactprotocol)
- PACT's contents (reference provider, demo agent, conformance tests) come from a secondary source — [eesel](https://www.eesel.ai/blog/personal-agent-protocol)
- **fleming-1** (Sierra, 2026-10-08) is a voice model that flags likely-AI callers, not a protocol. Sierra positions it for calls where Poppy is not used — [Sierra](https://sierra.ai/blog/caller-id-in-the-age-of-agents)

### Inferences
- The user's memory was accurate. The confusion likely comes from press using "PAP" while the wire format uses "poppy".
- Early coverage saying no spec or licence exists (e.g. [eesel, as of Oct 9](https://www.eesel.ai/blog/personal-agent-protocol)) is now stale and should not be quoted.

### Gaps
- "POPI" and "Poppi": no matching protocol surfaced in my search, so they appear to be mishearings only.
- Meta's Q3 2026 earnings remarks: a tweet title suggests "bot-to-bot" discussion, but the [X post](https://x.com/TheValueist/status/2113053581418885271) returned 402, the [Bullfincher transcript](https://bullfincher.io/companies/meta-platforms/earnings-call/fy2026-q3) was truncated and my guessed prepared-remarks PDF URL returned 404. Unverified.
- The Information and Stratechery coverage was not read.

## 2. What must a resource do to be Poppy-compatible? Conformance, SDKs, adopters

### Takeaway
A signed-out Poppy presence is cheap: one JSON file plus an existing stateless MCP or OpenAPI endpoint, with no OAuth. The hard constraint for MuseFront is identity. Each business must be its own hostname, and path-based tenants on a shared host cannot be expressed today. There is an official validator but no certification and no official reference server yet, and adoption is demos plus design-partner work.

### Cited Findings

**Implementation tiers**
- *Tier A, static.* Publish `poppy.json` with `protocol_version`, `organization`, and at least one interface. A website-only company "stops after publishing `poppy.json` without `auth`" and without a browser-session endpoint — [Company kit SKILL](https://raw.githubusercontent.com/personal-agent-protocol/personal-agent-protocol/main/kit/company/SKILL.md)
- *No OAuth needed for signed-out work.* Return 404 from the protected-resource metadata URL (or publish metadata with no authorization servers), omit `auth.issuer`, and use `https://{organization.domain}` as the session audience. Limit abuse with rate limits per `client_id` — [guides](https://personalagentprotocol.org/docs/0.3/guides)
- *Existing MCP servers work.* An unchanged server can ignore the Session header and serve signed-out calls that need no session identity or state. Its calls simply do not join the Session — [kit MCP pattern](https://raw.githubusercontent.com/personal-agent-protocol/personal-agent-protocol/main/kit/company/patterns/mcp.md)
- *Tier B, attribution.* Verify the Session header: fetch client metadata without following redirects, fetch `jwks_uri`, verify delegation (≤24h) and the ES256 JWT, check `aud`, `htm`, `htu`, `iat`. Return `invalid_session` as a 400 on failure — [foundation milestone](https://raw.githubusercontent.com/personal-agent-protocol/personal-agent-protocol/main/kit/company/milestones/foundation.md)
- *Tier C, conversation.* Five conversation routes including handoff — [spec](https://personalagentprotocol.org/docs/0.3/spec)
- *Tier D, account access.* Per-company OAuth issuer, `protected_resources` listing the domain, enforced scopes, optional `operations` — [spec](https://personalagentprotocol.org/docs/0.3/spec)
- *Useful for honest small businesses:* `excluded_tasks` tells agents what not to look for, written "the way a customer would ask for it" with an alternative where one exists — [guides](https://personalagentprotocol.org/docs/0.3/guides)
- Agents are told "Don't phone a company that publishes a `poppy.json`", though DIRECTV (design partner, 2026-10-27) points out this is only guide-level advice — [guides](https://personalagentprotocol.org/docs/0.3/guides); [#48](https://github.com/personal-agent-protocol/personal-agent-protocol/issues/48)

**The multi-tenant constraint (critical for MuseFront)**
- "A provider, such as a commerce platform, can run the protocol for several independent companies", but: "Serve each storefront's `poppy.json` on the storefront's own domain", and "A document redirected to the platform's domain speaks for the platform, not the storefront" — [guides](https://personalagentprotocol.org/docs/0.3/guides)
- `organization.domain` must be the host serving the document after redirects; since 0.2 a leading `www.` is not ignored — [spec](https://personalagentprotocol.org/docs/0.3/spec); [changelog](https://personalagentprotocol.org/docs/changelog)
- Open issue #57 (2026-10-28, from a "large scheduling product"): tenants at a path on a shared host "can't be identified", which is "common for scheduling and booking tools, link-in-bio and creator pages, and marketplaces", and "often the business has no domain of its own". Same issue confirms the current model "covers platforms where each tenant has its own hostname". Proposal not accepted as of 2026-11-03 — [#57](https://github.com/personal-agent-protocol/personal-agent-protocol/issues/57)
- Endpoints listed in the document "can be on any host" (spec §10.3), so a business-domain `poppy.json` can point at MuseFront-hosted APIs — [spec](https://personalagentprotocol.org/docs/0.3/spec)
- A company can use another provider for its agent endpoint, though "Publishing metadata alone doesn't configure the issuer or establish trust between the providers" — [guides](https://personalagentprotocol.org/docs/0.3/guides)
- Open issue #58 (2026-10-28) comes from a vendor running assistants for 300+ merchants and raises token audience and operator-disclosure gaps for that setup — [#58](https://github.com/personal-agent-protocol/personal-agent-protocol/issues/58)

**Conformance and tooling**
- **Official validator [LIVE]:** `kit/company/validate` acts as a test personal agent. Commands: `survey`, `check [url]`, `keygen`, `report`; offline `--file poppy.json`; exit 1 on a MUST failure; needs Node ≥22.18. It describes no certification — [validator README](https://raw.githubusercontent.com/personal-agent-protocol/personal-agent-protocol/main/kit/company/validate/README.md)
- **Official Company kit [LIVE]:** instructions, JSON Schemas, milestones (foundation, interfaces, sign-in, extensions), and a generated agent skill — [repo](https://github.com/personal-agent-protocol/personal-agent-protocol)
- **Official reference implementation [ANNOUNCED]:** Sierra promised one "over the next month" on Oct 9. The repo "does not implement the APIs", and it is the only repo in the org as of 2026-11-03 — [Sierra](https://sierra.ai/blog/poppy); [repo](https://github.com/personal-agent-protocol/personal-agent-protocol); [GitHub org](https://api.github.com/orgs/personal-agent-protocol/repos)
- **Third-party SDK [LIVE, unofficial]:** Datalayer's Python and TypeScript SDK, BSD-3, v0.30.0 (2026-10-31), 4 stars, `pap` CLI, reference company "Manzanita". Listed gaps include no KMS/HSM signer, no durable token store, no rate limiting in reference companies — [PyPI](https://pypi.org/project/personal-agent-protocol/); [GitHub API](https://api.github.com/repos/datalayer/personal-agent-protocol)
- Datalayer's self-run report shows 99 of 99 cases passing per pairing across four pairings, against profile 0.3 dated 2026-10-26, with no independent verifier named. It cites Operations v1 while the spec is now at v2, so it lags — [report](https://personal-agent-protocol.datalayer.tech/protocol/conformance-report/)

**Adoption evidence**
- **Real deployment found: one.** `printwithpoppy.com/.well-known/poppy.json` serves `protocol_version` 0.3, an `openapi` API, `operations` v2 and `mediated-sign-in`. It is a community demo that charges, prints and ships real orders. Its own description tells "Agents without native Poppy support" to use a separate compatibility API — [Probe](https://printwithpoppy.com/.well-known/poppy.json); [demos page](https://personalagentprotocol.org/docs/demos)
- The demos page lists four community demos (Cliffside Retail, Poppy Demo Agent with public validator, Print with Poppy, Poppy on Cloudflare Workers), notes they are not reviewed or endorsed, and names no adopters — [demos](https://personalagentprotocol.org/docs/demos)
- Probe: no `poppy.json` (HTTP 404) at walmart.com, shopify.com, target.com, hertz.com, nordstrom.com, zendesk.com, stripe.com, sierra.ai, gap.com or meta.com (apex and/or `www`). geico.com returned 403, and united.com was inconclusive. Instinct's domain was not confirmed, so Instinct is untested — e.g. [walmart probe](https://www.walmart.com/.well-known/poppy.json)
- Implementers in the open: Authlete reports testing draft 0.3 — [#60](https://github.com/personal-agent-protocol/personal-agent-protocol/issues/60). The merchant-assistant vendor in #58 says it is building the signed-out path — [#58](https://github.com/personal-agent-protocol/personal-agent-protocol/issues/58)
- Shopify stores are structurally close: 5 of 6 stores I probed as likely Shopify serve `/.well-known/ucp`, `oauth-authorization-server` and `oauth-protected-resource` (bombas.com rate-limited; allbirds, gymshark and beardbrand confirmed as Shopify by their `myshopify.com` endpoints, tentree and rothys by status code only). None of this is Poppy yet — e.g. [beardbrand probe](https://www.beardbrand.com/.well-known/oauth-protected-resource)

### Inferences
- Valid hosting shapes for MuseFront, in order of identity strength: (1) file on the business's own apex or `www`; (2) business subdomain (`agents.example-salon.com`) via CNAME, with an optional redirect from the apex well-known; (3) per-tenant MuseFront hostname, which is valid but makes the MuseFront host the identity the agent shows the user. The third is the only option for businesses with no domain.
- A signed-out profile needs no per-tenant OAuth issuer, which removes the most expensive multi-tenant requirement. Adding OAuth later can change the company identifier ("Users get new IDs and Sessions", [guides](https://personalagentprotocol.org/docs/0.3/guides)), so pick the hostname model carefully at the start.
- Generate `poppy.json` from a template and run the validator in CI, because 0.x breaks are the norm.

### Gaps
- Whether website builders (Wix, Squarespace, GoDaddy) let an owner serve arbitrary `/.well-known/` paths. Not researched, and it decides how many pilot tenants can do option 1.
- No source confirms what Muse or ChatGPT will do when they find a `poppy.json`, or when.
- The GitHub README text I saw listed 0.1 and 0.2 as the versions while the site shows 0.3, so it may lag.

## 3. Status of general agent protocols and how a small business would expose each

### Takeaway
MCP is the only general protocol with real consumer hosts, and it is the shared substrate beneath Poppy and UCP. A2A is real but enterprise-centred. WebMCP is an origin trial, and NLWeb and llms.txt have no demonstrated consumer-agent consumption. AGNTCY, ANP and IBM ACP are irrelevant to a small-business pilot.

### Cited Findings

**MCP [LIVE]**
- Governance: an Agentic AI Foundation project alongside AGENTS.md, goose, agentgateway and A2A — [AAIF, 2026-08-17](https://aaif.io/blog/a2a-joins-aaif)
- Current spec 2026-07-28: stateless core (`initialize` and `Mcp-Session-Id` removed), mandatory `server/discover`, `ttlMs`/`cacheScope` on list results, Tasks moved to an extension — [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- Elicitation: server-initiated requests replaced by Multi Round-Trip Requests (`resultType: "input_required"`, client retries with `inputResponses`); URL-mode completion notification removed — [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- Auth: Client ID Metadata Documents preferred, Dynamic Client Registration deprecated, `iss` validation (RFC 9207), credentials bound to issuer — [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- Roadmap (2026-08-22) gives no dates and lists agent identity/delegation, DPoP and progressive discovery as priorities — [roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/)
- Registry: "currently in preview. Breaking changes or data resets may occur", and "not intended to be directly consumed by host applications". It is a discovery tool — [docs](https://modelcontextprotocol.io/registry/about)
- Server Cards: conflicting signals. SEP-2127 shows closed and merged, updated 2026-10-06, still labelled `in-review`, with `.well-known/ai-catalog.json` in its description — [PR](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127). The tracking repo says "not an accepted or official MCP extension" and recommends `GET <streamable-http-url>/server-card` — [ext-server-card](https://github.com/modelcontextprotocol/ext-server-card). The August roadmap says the WG is still working on `.well-known` conventions — [roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/)
- Cards plus API catalogs appeared on fewer than 15 of about 200,000 top domains — [Cloudflare, published 2026-04-17, modified 2026-07-15](https://blog.cloudflare.com/agent-readiness/). Probe: github.com serves `/.well-known/ai-catalog.json` with type `application/ai-catalog+json` — [probe](https://github.com/.well-known/ai-catalog.json)
- Tool annotations are advisory; the MCP blog treats hints as a risk vocabulary with limits — [MCP blog index](https://blog.modelcontextprotocol.io/)
- *Small-business exposure:* one remote Streamable HTTP server per tenant, or a tenant path on a shared server. Tools like `get_services`, `check_availability`, `request_quote`. Support both pre- and post-2026-07-28 clients, since Poppy's floor is 2025-06-18 — [kit MCP pattern](https://raw.githubusercontent.com/personal-agent-protocol/personal-agent-protocol/main/kit/company/patterns/mcp.md)

**Google A2A / agent cards [LIVE in enterprise; no consumer evidence]**
- v1.0.0 released 2026-03-12, v1.0.1 2026-05-28; Apache-2.0; 26.4k stars — [releases](https://github.com/a2aproject/A2A/releases); [GitHub API](https://api.github.com/repos/a2aproject/A2A)
- Joined AAIF 2026-08-17. AAIF claims 150+ organizations, and production use in supply chain, financial services, HarmonyOS, WeChat and cloud AI platforms (self-reported) — [AAIF](https://aaif.io/blog/a2a-joins-aaif)
- Card at `https://{server_domain}/.well-known/agent-card.json`; JWS signing optional; bindings JSON-RPC, gRPC, HTTP+JSON — [spec](https://a2a-protocol.org/latest/specification/)
- Probes: no agent card at google.com or walmart.com — [probe](https://www.walmart.com/.well-known/agent-card.json). Shopify's live UCP profile advertises `mcp` and `embedded` transports, not A2A — [allbirds probe](https://allbirds.com/.well-known/ucp)
- *Small-business exposure:* static agent card plus a task endpoint fronting the business's agent. Poppy conversations use their own `type: poppy`, not A2A — [spec](https://personalagentprotocol.org/docs/0.3/spec)

**WebMCP / browser agent standards [DRAFT, origin trial]**
- Draft Community Group Report dated 2026-11-02; "not a W3C Standard nor is it on the W3C Standards Track"; editors from Microsoft and Google; API is `document.modelContext.registerTool()` — [spec](https://webmachinelearning.github.io/webmcp/)
- Chrome origin trial from Chrome 149 — [Chrome, 2026-06-09](https://developer.chrome.com/blog/ai-webmcp-origin-trial)
- As of 2026-10-29: Edge 150 trial expiring 2027-03-30; Firefox "neutral", WebKit "oppose", neither supports it; Chrome Status lists milestone 156 as last. Secondary guide; another search result (not opened) said the trial may run through Chrome 162, so the Chrome end date is unconfirmed — [MCPBundles](https://www.mcpbundles.com/guides/webmcp-browser-support)
- Consumption: Google's docs do not say Gemini in Chrome calls WebMCP tools. A community list shows Brave Leo experimental and ChatGPT Desktop "supported", which are not vendor statements — [MCPBundles](https://www.mcpbundles.com/guides/webmcp-browser-support)
- *Small-business exposure:* JavaScript on the site registering tools, plus per-browser origin-trial tokens. It needs code on the business's site, unlike a hosted resource.

**NLWeb [DORMANT-leaning]**
- Repo moved to `nlweb-ai/NLWeb`, MIT, 6.3k stars, no releases, last push 2026-08-11. Each instance is an MCP server with an `ask` method; A2A "coming soon" — [repo](https://github.com/nlweb-ai/NLWeb); [GitHub API](https://api.github.com/repos/nlweb-ai/NLWeb)
- No primary evidence of consumer-agent use found. UCP `ask` covers the same need (see question 4).
- *Small-business exposure:* index schema.org content and run the service. MuseFront could offer the same via an `ask` tool on its MCP server without adopting NLWeb.

**llms.txt [widely published, rarely read]**
- 137,210 domains, May 2026: 28% publish it (upper bound, SEO-skewed sample) and 97% of those files got zero requests. AI assistants were 2.5% of requests, retrieval bots 1.1%; Claude-Code led assistant bots — [Ahrefs, 2026-06-15](https://ahrefs.com/blog/llmstxt-study/)
- Google: "You don't need to create new machine readable files, AI text files, or markup" for AI features — [Google Search docs](https://developers.google.com/search/docs/appearance/ai-features)
- Developer docs do use it: MCP's own docs point agents to `/llms.txt` — [MCP docs](https://modelcontextprotocol.io/community/working-groups/server-card)
- *Small-business exposure:* a static file generated from the resource. Zero marginal cost, no demonstrated benefit with consumer agents.

**schema.org / JSON-LD actions [LIVE as data; actions unproven]**
- Google: "no special schema.org structured data" is needed for AI features, and structured data should match visible text — [Google Search docs](https://developers.google.com/search/docs/appearance/ai-features)
- I found no controlled evidence that any consumer agent executes `potentialAction`/`ReserveAction`. What surfaced was vendor advice, e.g. [Hitches, 2026-05-05](https://lawrencehitches.pages.dev/agent-action-schema/)
- OpenAI's reservation and quote flows use a dedicated business feed rather than schema.org actions — [restaurant spec](https://developers.openai.com/plugins/guides/restaurant-reservation-conversion-spec.md)
- *Small-business exposure:* JSON-LD `LocalBusiness`, `Service`, `Offer`, `OpeningHoursSpecification` in the page head.

**OpenAPI / ai-plugin manifests**
- OpenAPI 3.0/3.1 is a first-class Poppy API type, used by the one live Poppy store found — [spec](https://personalagentprotocol.org/docs/0.3/spec); [probe](https://printwithpoppy.com/.well-known/poppy.json)
- OpenAI's current "plugins" are skills + MCP servers + optional UI, submitted to the ChatGPT Directory. The docs I read describe no OpenAPI manifest route — [OpenAI docs](https://developers.openai.com/apps-sdk)
- RFC 9727 API catalogs: fewer than 15 sites, counted together with server cards — [Cloudflare](https://blog.cloudflare.com/agent-readiness/)
- *Small-business exposure:* generate an OpenAPI document from the same operations as the MCP tools.

**AGNTCY [enterprise infrastructure]**
- `agntcy/acp-spec` archived (last push 2025-05-23), which settles conflicting blog claims about its Agent Connect Protocol. `agntcy/dir`, `slim` and `identity` remain active — [acp-spec API](https://api.github.com/repos/agntcy/acp-spec); [org repos](https://api.github.com/orgs/agntcy/repos?sort=pushed)
- *Small-business exposure:* none sensible.

**ANP [DRAFT, marginal]**
- 1,464 stars, last commit 2026-10-22 (CIMD and DID binding docs), Apache-2.0 — [GitHub API](https://api.github.com/repos/agent-network-protocol/AgentNetworkProtocol). Linked to the W3C AI Agent Protocol Community Group, whose page shows 283 participants and drafts last dated 2025-08-19 — [W3C CG](https://www.w3.org/community/agentprotocol/)
- *Small-business exposure:* none sensible. No consumer-agent evidence found.

**IBM ACP [DORMANT, merged]**
- Merged into A2A in August 2025; repo `i-am-bee/acp` archived — [AAIF](https://aaif.io/blog/a2a-joins-aaif); [GitHub API](https://api.github.com/repos/i-am-bee/acp). Do not confuse it with OpenAI/Stripe ACP or AGNTCY's ACP.

**W3C / IETF / Linux Foundation**
- AAIF (Linux Foundation) is the main neutral home; Poppy, UCP and ACP are not listed among its projects in that post — [AAIF](https://aaif.io/blog/a2a-joins-aaif)
- IETF `webbotauth` WG is active (question 5). MCP's roadmap references the IETF OAuth and WIMSE WGs — [roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/)
- W3C's WebMCP remains outside the Standards Track, as above.

### Inferences
- MCP is the best single investment because it feeds three paths: direct connectors, Poppy `apis[]`, and the transport Shopify chose for UCP.
- Server Cards should be treated as unsettled. A hosted resource can add one later cheaply.

### Gaps
- The most widely repeated MCP download figures appear only in secondary articles, so I omitted them.
- NLWeb's 2026 Build announcements could not be checked.

## 4. Commerce protocols: discovery, catalog and checkout interface only

### Takeaway
UCP is the live one, and on Shopify it is already served for the merchant. ACP remains published, but ChatGPT's in-chat checkout has been deprioritised. Neither has a general services or appointments vertical; UCP's vertical-neutral `ask` and `location` capabilities and OpenAI's beta local-services flows are the nearest fits for long-tail service businesses.

### Cited Findings

**UCP [LIVE]**
- Released 2026-01-11 and now at v2026-08-25; Apache-2.0; 3.5k stars — [releases](https://github.com/Universal-Commerce-Protocol/ucp/releases); [GitHub API](https://api.github.com/repos/Universal-Commerce-Protocol/ucp)
- Governing Council: Google and Shopify (permanent), Stripe (2026-04-28). Tech Council added Amazon, Meta, Microsoft, Stripe, Salesforce representatives (2026-04-24) — [announcements](https://ucp.dev/documentation/announcements/)
- Discovery `/.well-known/ucp`; platforms identify through the `UCP-Agent` header. Transports REST, MCP, A2A, Embedded; auth API key, OAuth 2.0, mTLS or RFC 9421 signatures — [spec](https://ucp.dev/2026-08-25/specification/overview/)
- Capabilities in a live profile: checkout, cart, order, catalog search/lookup, fulfillment, discount, buyer consent, `common.ask`, `common.location.search`/`lookup`, identity linking; transports `mcp` and `embedded` only; endpoint `https://{shop}.myshopify.com/api/ucp/mcp` — [allbirds probe](https://allbirds.com/.well-known/ucp); [beardbrand probe](https://www.beardbrand.com/.well-known/ucp)
- Surfaces: AI Mode and Gemini with Etsy and Wayfair from 2026-02-11; main Search Buy button from 2026-05-05; Australian trial mid-June; eligible US Shopify products auto-opted-in to Google native checkout 2026-09-22 — [Wiegold, 2026-10-23, secondary with citations](https://thomas-wiegold.com/blog/agentic-commerce-ucp/)
- Wiegold found valid profiles at 9 of 14 stores checked — [Wiegold](https://thomas-wiegold.com/blog/agentic-commerce-ucp/)
- Shopify: "UCP-compliant MCP servers"; Checkout MCP hands buyers to the storefront for payment, trusted agents may complete directly, access set by agent trust tiers. Whether UCP is on for every store and plan is not stated — [Shopify docs](https://shopify.dev/docs/agents)
- Verticals: Food TC formed 2026-07-16 (Block/Square, DoorDash, Google, Toast, Uber Eats); Lodging TC 2026-08-11; draft `dev.ucp.lodging.booking` merged 2026-09-25; grocery readiness in v2026-08-25. No appointments or home-services group is listed — [announcements](https://ucp.dev/documentation/announcements/)
- **`dev.ucp.common.ask`** is natural-language Q&A on a business's "resources, policies, and services": REST `POST /ask`, MCP tool `ask_business`. Public tier available; "`ask` answers; it does not act"; "An answer is indicative, not authoritative" — [spec](https://ucp.dev/2026-08-25/specification/common/ask/)
- **`dev.ucp.common.location.*`**: hours, `exception_hours`, IANA timezone, amenities, and a `serves` relation for whether a location can serve an address. Absent hours means unknown, not closed — [spec](https://ucp.dev/2026-08-25/specification/common/location/)
- Poppy bridge: `extensions.ucp`, profile on the same host, "Complete Checkout" is the commit, and payment runs through UCP handlers. A `ucp` entry in `agent.protocols` requires `dev.ucp.common.ask` — [Poppy UCP extension](https://personalagentprotocol.org/docs/0.3/extensions/ucp)
- *Small-business exposure:* Shopify merchants already have it, so do nothing except verify. Non-Shopify: a host-level profile plus catalog and checkout endpoints is substantial work, while a profile with `ask` and `location` alone is light.

**OpenAI/Stripe ACP [DRAFT as checkout; feed use continues]**
- Apache-2.0 spec with dated versions through 2026-04-17; last push 2026-07-18; 1.6k stars. The 2026-04-17 release adds a Feed API where merchants push catalog data to agents — [changelog](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/blob/main/changelog/2026-04-17.md); [GitHub API](https://api.github.com/repos/agentic-commerce-protocol/agentic-commerce-protocol)
- The site still names ChatGPT as first implementer and Stripe as first PSP, and allows publishing via API or MCP — [agenticcommerce.dev](https://www.agenticcommerce.dev/)
- Retreat: launched 2025-09-29; OpenAI deprioritised Instant Checkout on 2026-03-24; "ACP now mainly carries product feeds for discovery" — [Wiegold](https://thomas-wiegold.com/blog/agentic-commerce-ucp/)
- Forrester counted about 30 live Shopify merchants by February 2026 (via a secondary) — [Naturaily, 2026-08-24](https://naturaily.com/blog/agentic-commerce-shopify-guide)
- `/.well-known/acp.json` added 2026-04-17; 0 of 13 stores served it — [Wiegold](https://thomas-wiegold.com/blog/agentic-commerce-ucp/). Probes: 404 at etsy.com and walmart.com — [probe](https://www.etsy.com/.well-known/acp.json)
- I could not open OpenAI's own post (HTTP 403), so the retreat rests on secondary sources: [OpenAI post](https://openai.com/index/powering-product-discovery-in-chatgpt/).
- *Small-business exposure:* product feed only, for product sellers, and via a platform.

**OpenAI plugin conversion specs [Beta, approved partners only]**
- Local services "Get Quote": required tool `request_service`, widget `ui://widget/request-service.html`, partner feed `GET /v1/businesses`, `action_type: request_a_quote`. Apply through the ChatGPT merchants form — [spec](https://developers.openai.com/plugins/guides/local-services-request-quote-conversion-spec.md)
- Restaurant "Reserve": required tool `restaurant_reservation`; recommended later `refresh_availability`, `make_reservation`, `reservation_confirmation` — [spec](https://developers.openai.com/plugins/guides/restaurant-reservation-conversion-spec.md)
- Guidelines: verified organization; explicit annotations on every tool; "Plugins may conduct commerce only for physical goods"; external checkout on your own domain; "Separate tenants on a shared hosting service count as different domains" for iframes — [guidelines](https://developers.openai.com/plugins/plugin-guidelines.md)
- *Small-business exposure:* not directly. It is a provider-level integration, so MuseFront would be the applicant.

**Others (interface level only)**
- Microsoft Copilot Checkout (2026-01-08, with PayPal, Shopify, Stripe) and Perplexity Instant Buy with PayPal (2025-11-25, no 2026 update found) — [Wiegold](https://thomas-wiegold.com/blog/agentic-commerce-ucp/). Wire protocols are not clearly documented in what I read; a [commercetools post, 2026-02-24](https://commercetools.com/blog/understanding-mcp-acp-ucp-in-agentic-commerce) associates Copilot with ACP but is marketing.

### Inferences
- OpenAI's `GET /v1/businesses` + `request_service` shape is the closest published schema for what a MuseFront resource does. It is worth mirroring in tool design even without partner approval.
- Implementing UCP `ask` and `location` for service businesses is spec-legal in structure, but I found no surface calling them on a non-merchant. Treat it as a later option.
- The Toast and Block seats on the Food TC suggest restaurant tenants may get coverage through their POS vendor rather than MuseFront.

### Gaps
- No evidence on whether Square, Toast, Mindbody, Vagaro, Calendly or similar expose agent endpoints. Searching was cut off by the session's web-search limit, and this is the largest remaining gap for a services-heavy pilot.
- The Shopify plan and eligibility rules for UCP were not found. My probes cover 6 stores and none is confirmed as long-tail.

## 5. Agent identity: how can a server tell which agent is calling?

### Takeaway
There is no universal answer today. ChatGPT's cloud browser signs with Web Bot Auth and Google-Agent signs a subset, while Muse, the agent MuseFront most cares about, reportedly looks like ordinary Chrome. A pilot should use signatures for recognition and analytics, never as a gate.

### Cited Findings

**Web Bot Auth [LIVE on the wire; standard unfinished]**
- IETF `webbotauth` WG: charter covers crawlers and AI agents acting for users, on sites mainly serving humans. HTTP APIs and end-user authentication are out of scope. The Apr 30 and Aug 31 2026 milestones have passed — [charter](https://datatracker.ietf.org/wg/webbotauth/about/)
- `draft-ietf-webbotauth-httpsig-protocol-01` dated 2026-10-29 is still a WG draft, with related drafts on registry, signed-agent metadata and anonymous auth — [documents](https://datatracker.ietf.org/wg/webbotauth/documents/)
- Mechanism: RFC 9421 `Signature`, `Signature-Input`, `Signature-Agent`; keys at `/.well-known/http-message-signatures-directory` — [Cloudflare docs](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/)
- **ChatGPT cloud browser:** OpenAI's help article reportedly says it "uses Web Bot Auth to sign outbound HTTP requests" with `Signature-Agent` of `https://chatgpt.com` — [WorkOS, 2026-10-19](https://workos.com/blog/web-bot-auth-identify-ai-agents) (the [OpenAI page](https://help.openai.com/en/articles/11845367-chatgpt-works-cloud-browser-allowlisting) returned 403). Probe: key directory live — [chatgpt.com directory](https://chatgpt.com/.well-known/http-message-signatures-directory)
- **Google-Agent:** subset of requests only, `Signature-Agent: g="https://agent.bot.goog"`. "We don't sign every request", so keep IP and reverse-DNS checks — [Google, updated 2026-10-13](https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth). Probe: directory live — [agent.bot.goog](https://agent.bot.goog/.well-known/http-message-signatures-directory)
- **Meta Muse:** "presents itself as an ordinary Chrome browser" and does not uniquely identify itself; detected behaviourally at "more than half of the customers it studied" — [Cequence, 2026-10-07, vendor, no methodology](https://www.cequence.ai/blog/cequence-agent-trust-metas-muse-is-a-bot-and-a-customer-now-what)
- A secondary says the Muse report also cites consumer VPN routing and a Sept 1 to 24 window; I did not see those in the Cequence post — [RPLCED](https://rplced.com/blog/meta-and-sierra-propose-a-personal-agent-protocol-what-to-do-while-muse-is-alrea). Probe: no directory at meta.ai — [probe](https://meta.ai/.well-known/http-message-signatures-directory)
- Poppy says personal agents should send an operator signature using RFC 9421 and Web Bot Auth, warns "current products do not all implement the same revision", and says a signature does not replace the delegated Session JWT — [guides](https://personalagentprotocol.org/docs/0.3/guides)

**Cloudflare signed agents [LIVE]**
- Launched 2025-08-28 with ChatGPT agent, Goose, Browserbase, Anchor Browser — [Cloudflare blog](https://blog.cloudflare.com/signed-agents/)
- Since 2026-07-01 the distinction is a BotBase field, Direct vs Intermediary. Customers can use AI Crawler and Agent access policies; a `Forwarded` header experiment could expose the end user behind an intermediary — [Cloudflare docs](https://developers.cloudflare.com/bots/concepts/bot/signed-agents/)
- *Small-business exposure:* a site behind Cloudflare gets verification at the edge. Plan availability is not stated on the [docs page](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/). A MuseFront-hosted resource can verify itself and need no action from the business.

**Visa Trusted Agent Protocol [ANNOUNCED/limited evidence]**
- Launched 2025-10-14 with Cloudflare on Web Bot Auth; "minimal changes"; interoperability work with x402; engagement with Google, OpenAI, Stripe. No live volumes reported — [Digital Transactions](https://www.digitaltransactions.net/visa-launches-trusted-agent-an-agentic-commerce-protocol/)
- Repo is sample code (agent registry, CDN proxy, merchant demo), 6 commits, last push 2025-10-28 — [repo](https://github.com/visa/trusted-agent-protocol); [GitHub API](https://api.github.com/repos/visa/trusted-agent-protocol)
- Visa joined Poppy's design partners 2026-10-09 — [Sierra](https://sierra.ai/blog/poppy)
- *Small-business exposure:* via CDN or processor, not directly.

**Know Your Agent**
- I found KYA used as a vetting programme or marketing term, not a formal open spec; one vendor describes it as underpinning TAP registration (search snippet, unopened) — [ATXP](https://atxp.ai/blog/visa-trusted-agent-protocol-explained)
- Nothing in it is implementable by a small business.

**Other identification signals**
- Poppy: `iss` = HTTPS `client_id` URL with signed delegation, the strongest signal specified, when present — [spec](https://personalagentprotocol.org/docs/0.3/spec)
- UCP: `UCP-Agent` header with platform profile URI, optional RFC 9421 signature — [spec](https://ucp.dev/2026-08-25/specification/overview/)
- MCP: `clientInfo` in `_meta` is a SHOULD and is self-declared; OAuth client identity via CIMD is stronger — [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- Phone: Sierra's fleming-1 scores speech for AI generation, with no accuracy figures published — [Sierra, 2026-10-08](https://sierra.ai/blog/caller-id-in-the-age-of-agents)

### Inferences
- Layered recognition for the pilot: Poppy session if present, then a verified Web Bot Auth signature, then OAuth client or `clientInfo`, then user agent and IP, then "unknown browser, assume possibly Muse".
- Rejecting unsigned traffic would exclude Muse on current evidence, which defeats the product's purpose.

### Gaps
- No independent measurement of Muse's wire identity. Evidence is vendor-sourced, and Muse could change.
- Anthropic's and Perplexity's signing status is unverified: secondary claims only, and my probes at claude.ai (404), anthropic.com and perplexity.ai (redirects) were inconclusive.

## 6. What do real consumer agents consume today, versus what is only announced?

### Takeaway
Consumer agents today mostly consume rendered websites, user-connected or directory-approved MCP servers, and Google's and Shopify's UCP pipeline. Poppy, WebMCP, A2A, NLWeb, llms.txt and JSON-LD actions have no demonstrated consumer-agent use at meaningful scale in what I could open.

### Cited Findings

**Consumed today (evidence)**
- **Muse** (US launch 2026-09-08; estimated 5M downloads by 2026-09-30, Sensor Tower via a secondary) — [Yellow](https://yellow.com/news/meta-muse-5m-downloads-websites-blocking)
- Muse transacts "through a business's connector or directly on its website", with user approval for sign-in, reservation or purchase. Meta's stated sequence: now, guide agents to preferred flows or connectors; next, connector APIs; longer term, business agents with "lower latency, fewer errors" (no measurements) — [Meta, 2026-10-06](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together)
- Muse drives a real browser and checks out with Link by Stripe; MCP is not mentioned — [eesel, 2026-09-09, secondary](https://www.eesel.ai/blog/meta-muse-agent)
- **Friction:** Amazon has blocked Muse since 2026-09-20; Walmart called its blocks unintentional; Yelp bars non-human traffic without paid licensing — [Yellow, secondary](https://yellow.com/news/meta-muse-5m-downloads-websites-blocking)
- **ChatGPT:** cloud browser with signatures (question 5); MCP-based plugins through the Directory — [OpenAI docs](https://developers.openai.com/apps-sdk); product data through Shopify Catalog — [Wiegold](https://thomas-wiegold.com/blog/agentic-commerce-ucp/)
- **Claude:** remote MCP custom connectors on Free through Enterprise, with "No sign in" as an option; connections come from Anthropic's cloud, and Free is limited to one custom connector. User-added, not automatic on arrival — [Anthropic support, undated](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp)
- **Google AI Mode, Gemini, Search:** UCP checkout for eligible merchants (question 4); Google-Agent signed in part (question 5).
- **Copilot and Perplexity:** checkout integrations through partners (question 4).
- **Coding agents, not consumer agents:** Claude Code, OpenCode and Cursor send `Accept: text/markdown` by default (Feb 2026 study via Cloudflare), and Claude-Code leads assistant fetches of llms.txt — [Cloudflare](https://blog.cloudflare.com/agent-readiness/); [Ahrefs](https://ahrefs.com/blog/llmstxt-study/)

**Announced or draft only**
- Poppy: partners listed, but one store and demos are the only deployments I found (question 2). The one live store's own file tells non-native agents to use a compatibility API — [probe](https://printwithpoppy.com/.well-known/poppy.json)
- A secondary reading of Meta's post also concludes no protocol feature is live — [Relevant Audience](https://www.relevantaudience.com/meta/meta-sierra-personal-agent-protocol/)
- WebMCP: origin trial, no vendor-confirmed consumer agent — [MCPBundles](https://www.mcpbundles.com/guides/webmcp-browser-support)
- MCP Server Cards and API catalogs: under 15 of about 200k domains as of the 2026 Cloudflare data — [Cloudflare](https://blog.cloudflare.com/agent-readiness/)
- OpenAI local-services and reservations: beta with approved partners — [spec](https://developers.openai.com/plugins/guides/local-services-request-quote-conversion-spec.md)

### Inferences
- For an agent that "arrives at a business" with no prior connector, the realistic path in November 2026 is the web page. MCP mostly requires a prior install or directory step, and that is the gap Poppy's `poppy.json` is designed to close by making `apis[]` discoverable from a domain.
- MuseFront's practical near-term value is therefore (a) a page Muse can use, and (b) a ready MCP endpoint and `poppy.json` for when agents start reading them. The second is a bet on Meta and OpenAI following through, not a current traffic source.

### Gaps
- No independent, cross-agent measurement of which protocols consumer agents call. Most data comes from vendors with a commercial interest.
- I could not confirm what protocol Muse "connectors" use.
- Whether Muse, ChatGPT or Gemini fetch `/.well-known/` files on arrival is unknown. MuseFront's own logs during a pilot could answer this.

## 7. Smallest protocol set for a pilot of about two dozen small businesses

### Takeaway
Ship three things: an agent-legible web page per business with JSON-LD, one multi-tenant remote MCP server, and a signed-out `poppy.json` per business hostname. Add passive Web Bot Auth logging. Treat UCP as "already handled" for Shopify tenants and defer everything else.

### Cited Findings
Each choice rests on evidence above; key anchors:
- Web page first, because Muse acts "directly on its website" — [Meta](https://www.facebook.com/business/news/a-new-way-for-businesses-and-personal-agents-to-work-together)
- MCP, because it is what ChatGPT plugins and Claude connectors consume — [OpenAI](https://developers.openai.com/apps-sdk); [Anthropic](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp). It is also a Poppy API type and Shopify's UCP transport — [Poppy spec](https://personalagentprotocol.org/docs/0.3/spec); [allbirds probe](https://allbirds.com/.well-known/ucp)
- Signed-out Poppy, because no OAuth issuer is needed and an existing MCP server can be listed unchanged — [guides](https://personalagentprotocol.org/docs/0.3/guides); [MCP pattern](https://raw.githubusercontent.com/personal-agent-protocol/personal-agent-protocol/main/kit/company/patterns/mcp.md)
- Web Bot Auth as logging only, because signing is partial — [Google](https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth)

### Inferences

**Build now (recommendation, my judgment)**
1. **Web page per business.** Server-rendered HTML with real prices, hours, services, a working contact or booking flow, no CAPTCHA on read paths, and JSON-LD `LocalBusiness`/`Service`. JSON-LD's benefit is unproven, but its cost is near zero.
2. **One remote MCP server** (Streamable HTTP, supporting 2025-06-18 through 2026-07-28 clients). Read tools plus one or two request tools such as `request_quote` and `request_booking`, modelled on OpenAI's `request_service` and on UCP's `ask` and `location` semantics, including "indicative" answers and "unknown, not closed" hours. Explicit annotations on every tool. No sign-in. Actions that commit the business go through as requests that a human confirms.
3. **Signed-out `poppy.json`** on each business's own host where possible, else a per-tenant MuseFront hostname. Include `apis` to the MCP server, `web`, `excluded_tasks`, and `feedback`. Run the official validator in CI, pin `protocol_version`, and accept regeneration on each draft. Cost is low, and payoff depends on Meta, OpenAI or Instinct shipping clients.
4. **Passive identity logging.** Verify Web Bot Auth signatures and, if present, Poppy Session JWTs. Record agent, tool and outcome. Never gate on it. These logs also fill the biggest evidence gap in this research.

**Conditional**
- Shopify tenants: verify `/.well-known/ucp` and reference it. Do not rebuild it. Note the Poppy `ucp` extension requires the profile on the same host as `poppy.json`, so these tenants need their `poppy.json` on the storefront host or should skip Poppy for now.
- Restaurant tenants: check Toast and Block/Square status before building ordering.
- MuseFront as a provider: apply to OpenAI's merchant form for "Get Quote" as a parallel business-development action, not an engineering dependency.

**Defer, with what would change the call**
| Item | Why defer | Revisit when |
|---|---|---|
| Poppy conversation endpoint and handoff | Needs staffed or agent-backed responses; Meta itself calls business agents "longer term" | A consumer agent ships Poppy client support |
| Poppy OAuth and Operations | Per-tenant issuer; spec churn | Pilot tenants need account actions |
| UCP checkout for non-Shopify | Heavy, retail-centred | A services vertical appears |
| A2A / agent card | No consumer evidence; Poppy uses its own conversation type | A named consumer agent requires it |
| WebMCP | Origin trial, needs site code, WebKit opposed | Chrome ships by default and a consumer agent is confirmed |
| MCP Server Card / Registry | Unsettled, and discovery is out of scope | SEP status clears |
| ACP checkout, Visa TAP | Retreat and payment-layer concerns | Other researcher's payments findings suggest otherwise |
| NLWeb, AGNTCY, ANP, IBM ACP | No consumer use; ACP (IBM) is merged | Not expected |
| llms.txt | No demonstrated consumer value | Generate only if free |

**Watch list:** Poppy #57 (path tenants), reference implementation, a 1.0 date, any Meta or OpenAI statement that their agents read `poppy.json`, UCP services vertical, MCP Server Card resolution.

### Gaps
- The recommendation is a judgment made without measured conversion or traffic data for any protocol, and with no cost estimates validated against a real build.
- Web search budget for this session ran out before covering small-business platform support (booking, POS, website builders). Those would be the first follow-ups and could change the hosting and tenant-mix assumptions.
- Spec details here were read through a summarising fetch tool, not line by line. Check exact field names and MUST/SHOULD wording against the [Draft 0.3 spec](https://personalagentprotocol.org/docs/0.3/spec) and the validator before implementing.
