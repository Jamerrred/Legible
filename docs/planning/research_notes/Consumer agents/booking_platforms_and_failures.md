# Booking platforms and agent failures (time-boxed, partial)

Only Calendly, Acuity and Square were read, and only partly. Everything else is "not confirmed".
"Stated" = in the fetched page text. "Inference" = mine.

## Platforms

| Platform | Placement on business site | Availability w/o personal details | Card/account required | Public availability API | Sources |
|---|---|---|---|---|---|
| Calendly | Stated: three embed styles (inline, popup text, popup widget), made via "Add to website" and a pasted snippet; plain link if plan lacks HTML embeds. Script vs iframe not stated on the page (a related article reportedly covers iframe; not read). | Not confirmed | Not confirmed | REST API stated to "book meetings and read and write Scheduling, Contacts..." data. Whether it has availability endpoints, and its auth, are not confirmed. The page links OAuth (inference: OAuth). | https://calendly.com/help/embed-options-overview ; https://developer.calendly.com/api-docs/ |
| Acuity Scheduling | Not confirmed (help page returned 403) | Not confirmed | Not confirmed | Stated: GET /availability/dates (dates with availability for a month and appointment type) and /availability/times (needs date + appointmentTypeID). HTTP Basic auth with user ID + API key, i.e. owner credentials, not open to the public. | https://developers.acuityscheduling.com/reference/get-availability-dates ; https://developers.acuityscheduling.com/reference/get-availability-times |
| Square Appointments | Not confirmed | Not confirmed | Not confirmed | Stated: SearchAvailability endpoint needs OAuth bearer token with APPOINTMENTS_READ (seller-level: APPOINTMENTS_ALL_READ too). Not anonymous. | https://developer.squareup.com/reference/square/bookings-api/search-availability |
| OpenTable | Not confirmed | Not confirmed | Not confirmed | Docs landing page had no readable content. Not confirmed. | https://docs.opentable.com/ |
| Mindbody, Vagaro, Booksy, Housecall Pro, Jobber, ServiceTitan, Toast | Not confirmed (not reached) | Not confirmed | Not confirmed | Not confirmed | - |

Inference: owner-authenticated APIs mean an agent visiting a customer-facing site cannot use them. It must go through the widget UI.

## Reported agent failure modes

### BrowserArena (arXiv 2510.02418; read via arxiv HTML, https://arxiv.org/html/2510.02418)
Stated setup: live-web arena, BrowserUse on Playwright Chromium, 5 models (DeepSeek R1, Claude 3.7 Sonnet Thinking, Llama-4-Maverick, o4-mini, Gemini 2.5 Pro Preview). Prolific users, 109 valid battles, 218 step-level feedback examples. Failure modes were found by clustering step labels. Three were studied:
- Captcha: agents get stuck because puzzle parts are often not clickable DOM elements. Tested on 220 Expedia tasks. Models used avoidance strategies (direct link, Google search, new tab 60.45% for o4-mini, mobile site 58.64%, cache 45.45%, switching websites 60% for Claude 3.7).
- Blocking cookie/privacy pop-up banner (80 BBC tasks):
  - R1 never detected it (0%) yet marked tasks complete 53.75% of the time.
  - o4-mini detected it in 91.25% of tasks and closed 17.81% of those detected.
  - Llama-4 closed 17.72% of those detected.
  - Claude 3.7 detected it in 100% of tasks and closed 7.5%.
- Direct navigation: agents go straight to a start URL instead of searching (TriviaQA, 100 qs). Gemini had 50 failed runs.
Note: the wording on whether the percentages are per-task or per-detection is from the summarizer; I did not read the tables directly.
The full PDF could not be text-extracted, so the above relies on a fetch-tool summary of the HTML.

### Dev.to blog, "we tested browser agents on 20 real websites" (weak, non-peer-reviewed)
https://dev.to/osaka2077/we-tested-browser-agents-on-20-real-websites-heres-where-they-break-4pen
Stated miss rates for identifying interactive elements (not executing actions): cookie consent ~50%, e-commerce (cart/add to cart) ~40%, login/auth ~30%, search ~25%, navigation ~20%. Overall F1 66%. No sample sizes and no per-agent results. Uses the authors' own library.

Inference for mock sites: cookie banners that block interaction, non-DOM captchas, and floating or overlay widgets are the best-evidenced obstacles. Booking-widget-specific failure data was not found.

## Not confirmed
- Embed method, anonymous availability visibility, and the step where personal details/card are demanded: for all 11 vendors.
- Any availability API for Calendly (endpoint list), Mindbody, Vagaro, Booksy, Housecall Pro, Jobber, ServiceTitan, OpenTable, Toast.
- Square Bookings overview page and the Acuity help page (404/403).
- Full-text reading of BrowserArena PDF.
- Online-Mind2Web / WebVoyager error breakdowns (search did not surface them).
