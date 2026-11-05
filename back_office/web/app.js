// The MuseFront owner app. Plain JS: each screen fetches its data and renders into #view.
const $ = (s) => document.querySelector(s);
const view = $("#view");
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const icon = (name, cls = "") => `<i data-lucide="${name}" class="${cls}"></i>`;
const NAV = [["websites", "globe", "Websites"], ["simulations", "flask-conical", "Simulations"], ["resource", "file-text", "Resource"], ["inbox", "inbox", "Inbox"], ["bookings", "calendar-check", "Bookings"]];
const SOURCE = { simulation: "A test customer got stuck", agent_activity: "Real agents hit this", interview: "Missing from your website" };
const CATEGORIES = { vocabulary: "In the customer's words", dependencies: "What depends on what", conditions: "Conditions that change the price", eligibility: "Who and what can be served", prerequisites: "What the customer needs to provide", availability: "Availability", staff: "Staff", policies: "Policies", timing: "Timing rules", credentials: "Credentials", next_step: "What happens after a request", other: "Other facts" };
const ACCOUNTS = [["googlecalendar", "calendar", "Google Calendar", "Keeps closures and blocked dates current"], ["googlesheets", "table", "Google Sheets", "Keep your price list in a sheet"]];
const STEPS = [["crawling", "Read your website"], ["extracting", "Build your fact sheet"], ["interviewing", "Work out what's missing"], ["checking", "Test it with customer agents"]];

const state = { sites: [], site: null, selectedSim: null, selectedBooking: null, agentView: false, working: false, clarify: null };
let poll = null;

async function api(path, options = {}) {
  const init = { ...options };
  if (options.body !== undefined) { init.body = JSON.stringify(options.body); init.headers = { "content-type": "application/json" }; }
  const response = await fetch(path, init);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "That didn't work. Try again.");
  return data;
}
const post = (path, body = {}) => api(path, { method: "POST", body });

let toastTimer;
function toast(message, action) {
  const el = $("#toast");
  el.innerHTML = `<span>${esc(message)}</span>${action ? `<button data-do="${action.do}">${esc(action.label)}</button>` : ""}`;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), action ? 7000 : 3500);
}
const fail = (error) => toast(error.message || "That didn't work. Try again.");
const copy = (text, label) => navigator.clipboard.writeText(text).then(() => toast(`${label} copied`), () => toast("Couldn't copy. Select it and copy by hand."));
const when = (iso) => { const d = new Date(iso); return Number.isNaN(+d) ? "" : d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }); };
const shortDate = (iso) => { const d = new Date(`${iso}T12:00:00`); return Number.isNaN(+d) ? iso : d.toLocaleDateString(undefined, { month: "short", day: "numeric" }); };
const route = () => (location.hash.replace(/^#\/?/, "") || "websites").split("/")[0];

async function loadSites() {
  state.sites = await api("/websites");
  const wanted = localStorage.getItem("mf.site");
  state.site = state.sites.find((s) => s.id === wanted) || state.sites[0] || null;
}
function selectSite(id) { localStorage.setItem("mf.site", id); state.site = state.sites.find((s) => s.id === id) || null; state.selectedSim = null; state.selectedBooking = null; state.agentView = false; }

function renderRail() {
  const n = state.site?.needs || {};
  const dots = { simulations: n.missing, resource: (n.review || 0) + (n.proposals || 0), inbox: n.agent_questions, bookings: n.bookings };
  $("#rail").innerHTML = `<div class="logo">M</div>` + NAV.map(([id, ic, label]) => `<a class="nav ${route() === id ? "on" : ""}" href="#/${id}">${icon(ic)}<span>${label}</span>${dots[id] ? '<span class="dot"></span>' : ""}</a>`).join("") + (state.site ? `<a class="switcher" href="#/websites" title="${esc(state.site.name)}">${esc((state.site.name || "?")[0])}</a>` : "");
}
const paint = (html) => { view.innerHTML = html; if (window.lucide) lucide.createIcons(); };
const needSite = () => `<div class="center-pane"><div class="stack" style="max-width:420px;text-align:center"><h1 class="headline">Add a website first</h1><p class="soft">MuseFront starts by reading your website.</p><div><a class="btn primary" href="#/websites">Add a website</a></div></div></div>`;

async function render() {
  clearTimeout(poll);
  try {
    await loadSites();
    renderRail();
    if (window.lucide) lucide.createIcons();
    const r = route();
    if (r === "websites") return await renderWebsites();
    if (!state.site) return paint(needSite());
    if (r === "simulations") return await renderSimulations();
    if (r === "resource") return await renderResource();
    if (r === "inbox") return await renderInbox();
    if (r === "bookings") return await renderBookings();
    location.hash = "#/websites";
  } catch (error) {
    paint(`<div class="center-pane"><div class="stack" style="max-width:420px;text-align:center"><h1 class="headline">Couldn't load this</h1><p class="soft">${esc(error.message)}</p><div><button class="btn" data-do="reload">Try again</button></div></div></div>`);
  }
}

// ------------------------------------------------------------ Websites

const isBusy = (s) => s && !["ready", "failed"].includes(s.stage);

function addForm() {
  return `<div class="center-pane"><form class="stack" data-form="addSite" style="width:min(600px,100%)">
    <h1 class="headline">Which website should agents be able to read?</h1>
    <p class="soft" style="margin:0;font-size:15.5px">MuseFront reads it, works out what's missing, and nothing goes public until you've confirmed it.</p>
    <div class="field"><input name="url" type="url" required placeholder="https://yourbusiness.com" autofocus><button class="send" aria-label="Add website">${icon("arrow-up")}</button></div>
    <label class="row-flex small soft"><input type="checkbox" name="check" checked> Also test it with 5 customer agents, about 5 minutes</label>
  </form></div>`;
}

function stepsPanel(site) {
  const at = STEPS.findIndex(([id]) => id === site.stage);
  const rows = STEPS.map(([id, label], i) => {
    const done = site.stage === "ready" || (at >= 0 && i < at);
    const now = i === at || (site.stage === "queued" && i === 0);
    const mark = done ? icon("check", "ok") : now ? icon("loader", "spin accent") : '<span class="status-dot" style="margin:0 5px;opacity:.4"></span>';
    return `<div class="line-row">${mark}<span class="grow ${now ? "" : done ? "" : "muted"}" style="font-weight:${now ? 500 : 400}">${label}</span></div>`;
  }).join("");
  return `<div class="stack"><h1 class="headline">Getting to know ${esc(site.name || site.slug)}</h1><p class="soft" style="margin:0;font-size:15.5px">${esc(site.stage_note || "Starting")}. You can leave this page while it works.</p><div class="step-list">${rows}</div></div>`;
}

async function renderWebsites() {
  const adding = location.hash.includes("/new") || !state.sites.length;
  const site = adding ? null : state.site && (await api(`/websites/${state.site.id}`));
  const list = state.sites.map((s) => `<button class="list-item ${site && s.id === site.id ? "on" : ""}" data-do="pickSite" data-id="${s.id}">
    <div class="name">${esc(s.name || s.slug)}</div><div class="tiny muted" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(s.url.replace(/^https?:\/\//, ""))}</div>
    <div class="row-flex tiny" style="gap:6px;margin-top:3px"><span class="status-dot ${s.live ? "live" : ""}"></span><span class="${s.live ? "ok" : "muted"}" style="font-weight:500">${s.live ? "Live" : isBusy(s) ? "Setting up" : s.stage === "failed" ? "Failed" : "Not public yet"}</span></div></button>`).join("");
  const side = `<aside class="pane-list"><div class="list-head"><h1 class="page-title">Websites</h1><a class="btn icon-btn" href="#/websites/new" aria-label="Add a website">${icon("plus")}</a></div><div class="list">${list}</div></aside>`;
  if (adding) return paint(side + addForm());
  if (isBusy(site)) { poll = setTimeout(render, 3000); return paint(side + `<div class="center-pane"><div style="width:min(600px,100%)">${stepsPanel(site)}</div></div>`); }
  if (site.stage === "failed") return paint(side + `<div class="center-pane"><div class="stack" style="width:min(600px,100%)"><h1 class="headline">This website couldn't be read</h1><p class="soft">${esc(site.stage_note)}</p><div><a class="btn" href="#/websites/new">Try another address</a></div></div></div>`);
  const linked = (site.connections || []).filter((c) => c.status === "connected");
  const accounts = linked.length ? linked.map((c) => { const a = ACCOUNTS.find(([id]) => id === c.toolkit) || [c.toolkit, "plug", c.toolkit]; return `<div class="line-row">${icon(a[1], "soft")}<div class="grow" style="font-weight:500;font-size:14.5px">${esc(a[2])}</div><span class="row-flex small ok" style="gap:6px;font-weight:500">${icon("check")} Connected</span></div>`; }).join("") : "";
  const n = site.needs;
  const next = n.review ? ["resource", `Confirm ${site.facts.draft} facts read from your website`] : n.missing ? ["simulations", `Answer ${n.missing} question${n.missing > 1 ? "s" : ""} about what's missing`] : null;
  paint(side + `<section class="pane-main"><div class="column">
    <h1 class="headline">${esc(site.name || site.slug)}</h1><p class="muted" style="margin:10px 0 0;overflow-wrap:anywhere">${esc(site.url.replace(/^https?:\/\//, ""))}</p>
    ${next ? `<a class="banner" href="#/${next[0]}" style="margin:24px 0 0;text-decoration:none"><span class="accent" style="font-weight:500">${esc(next[1])}</span>${icon("arrow-right", "accent")}</a>` : ""}
    <div class="stack section-gap"><div class="between"><h2 class="section">Your link</h2><button class="btn ghost small" data-do="checkLink">${icon("search-check")} Check it's on your site</button></div>
      ${site.live ? `<div class="link-box"><span class="mono">${esc(site.link)}</span><button class="btn primary" data-do="copy" data-text="${esc(site.link)}" data-label="Link">${icon("copy")} Copy</button></div>
      <div class="small soft">Paste this line on your pricing or booking page, where any agent reading it will see it:</div>
      <div class="paste-line"><span>${esc(site.link_line)}</span><button class="btn ghost icon-btn" data-do="copy" data-text="${esc(site.link_line)}" data-label="Line" aria-label="Copy line">${icon("copy")}</button></div>` : `<div class="empty" style="border:0;padding:0"><b>Your link appears once you've confirmed your facts</b>Nothing is public until then.</div>`}
    </div>
    <div class="section-gap"><div class="between"><div><h2 class="section">Connected accounts</h2><p class="small soft" style="margin:4px 0 14px">Optional. MuseFront reads these and asks you before anything changes.</p></div><button class="btn" data-do="openConnect">${icon("plug")} Connect a resource</button></div>${accounts}</div>
  </div></section>`);
}

// ------------------------------------------------------------ Connect popup

const connectState = { configured: false, rows: {} };
function renderConnect() {
  const notice = connectState.configured ? "" : `<div class="modal-note">Connecting accounts is optional, and MuseFront works without it. To turn it on, add <code>COMPOSIO_API_KEY</code> to your <code>.env</code> file and restart MuseFront.</div>`;
  const rows = ACCOUNTS.map(([id, ic, name, help]) => {
    const r = connectState.rows[id] || {};
    const isConnected = r.step === "done" || (state.site.connections || []).some((c) => c.toolkit === id && c.status === "connected");
    const right = isConnected ? `<span class="done-check">${icon("check")}</span>` : r.step === "waiting" ? icon("loader", "spin accent") : `<button class="btn" data-do="startConnect" data-id="${id}" ${connectState.configured ? "" : "disabled"}>Connect</button>`;
    const waiting = r.step === "waiting" ? `<div class="small soft">Finish signing in in the new window, then come back here.</div>${id === "googlesheets" ? `<input class="sheet" id="sheet-id" placeholder="Paste your spreadsheet's ID">` : ""}<div><button class="btn primary" data-do="finishConnect" data-id="${id}">I've connected it</button></div>` : "";
    return `<div class="modal-row"><div class="top">${icon(ic, "soft")}<div class="grow" style="flex:1;min-width:0"><div style="font-weight:500;font-size:14.5px">${name}</div><div class="small muted">${help}</div></div>${right}</div>${waiting}${r.error ? `<div class="err-text">${esc(r.error)}</div>` : ""}</div>`;
  }).join("");
  $("#modal").innerHTML = `<div class="modal-back" data-do="closeConnect" data-self="1"><div class="modal" role="dialog" aria-modal="true" aria-label="Connect a resource"><div class="between"><h2 class="section">Connect a resource</h2><button class="btn ghost icon-btn" data-do="closeConnect" aria-label="Close">${icon("x")}</button></div><p class="small soft" style="margin:6px 0 0">MuseFront reads what you connect and proposes changes for you to confirm. Connections run through Composio.</p>${notice}<div style="margin-top:14px">${rows}</div></div></div>`;
  if (window.lucide) lucide.createIcons();
}

// ------------------------------------------------------------ Simulations

function questionBlock(q) {
  return `<article class="question"><div class="source-tag">${esc(SOURCE[q.source] || "Missing")}</div><h3>${esc(q.title)}</h3>${q.body ? `<div class="soft small">${esc(q.body)}</div>` : ""}
    <form data-form="answer" data-id="${q.id}" style="margin-top:6px"><div class="field"><input name="text" required placeholder="Type your answer" autocomplete="off"><button class="send" aria-label="Send answer">${icon("arrow-up")}</button></div></form>
    <div><button class="btn ghost small" data-do="dismiss" data-id="${q.id}" style="padding:4px 8px;margin-left:-8px">Doesn't apply</button></div></article>`;
}

async function renderSimulations() {
  const id = state.site.id;
  const [missing, sims] = await Promise.all([api(`/websites/${id}/missing`), api(`/websites/${id}/simulations`)]);
  if (!sims.some((s) => s.id === state.selectedSim)) state.selectedSim = sims[0]?.id || null;
  const current = state.selectedSim ? await api(`/simulations/${state.selectedSim}`) : null;
  const running = sims.some((s) => s.status === "running") || isBusy(state.site);
  if (running) poll = setTimeout(render, 5000);
  const score = (s) => (s.status === "running" ? "…" : `${s.summary.answered} of ${s.summary.queries}`);
  const list = sims.map((s) => `<button class="list-item ${s.id === state.selectedSim ? "on" : ""}" data-do="pickSim" data-id="${s.id}"><div class="between"><div style="min-width:0"><div class="name">${esc(s.label)}</div><div class="tiny muted">${esc(when(s.created_at))}</div></div><span style="font:400 18px var(--voice);flex:none">${score(s)}</span></div></button>`).join("");
  let detail = `<div class="empty"><b>No check has run yet</b>A check sends test customers at your website to find what they can't answer.</div>`;
  if (current) {
    const runs = current.runs || [];
    const broke = (r) => r.result?.error || (r.result?.answer || "").startsWith("The model stopped responding");
    const segs = runs.map((r) => `<i class="${r.settled ? "ok" : broke(r) ? "" : "stuck"}"></i>`).join("");
    const rows = runs.map((r) => {
      const label = r.settled ? "Answered" : broke(r) ? "Agent crashed" : "Stuck";
      const mark = r.settled ? icon("check", "ok") : broke(r) ? icon("minus", "muted") : icon("x", "accent");
      const asked = r.query.replace(/\s*\(?https?:\/\/\S+\)?/g, "");
      return `<details class="run"><summary>${mark}<span class="request">“${esc(asked)}”</span><span class="small ${label === "Stuck" ? "accent" : "muted"}" style="flex:none">${label}</span></summary><div class="run-body">${esc(broke(r) ? "The test agent crashed before it finished. This doesn't count against you." : r.result?.answer || "No answer.")}</div></details>`;
    }).join("");
    detail = current.status === "running"
      ? `<div class="row-flex soft" style="padding:16px 0">${icon("loader", "spin")} Test customers are working through this now. It takes about 5 minutes.</div>`
      : `<div class="stack"><div class="small muted" style="font-weight:500">${esc(current.label)}</div><h2 class="headline" style="font-size:30px">${current.summary.answered} of ${current.summary.queries} test customers got an answer</h2><div class="meter">${segs}</div></div><div style="margin-top:22px">${rows}</div>`;
  }
  const open = missing.open;
  const answered = missing.answered.filter((q) => q.status === "done").slice(0, 8).map((q) => `<details class="run"><summary>${icon("check", "ok")}<span class="request" style="font-size:15.5px">${esc(q.title)}</span></summary><div class="run-body">${esc(q.resolution)}</div></details>`).join("");
  paint(`<aside class="pane-list"><div class="list-head"><h1 class="page-title">Simulations</h1></div><div class="list">${list}</div><div class="spacer"></div>
    <div class="stack" style="padding:16px 20px 22px 24px;gap:10px"><div class="small muted">Sends the same test customers again, so you can see the score change. About 5 minutes.</div><button class="btn primary wide" data-do="runCheck" ${running ? "disabled" : ""}>${icon("play")} ${running ? "Running" : "Run check"}</button></div></aside>
    <section class="pane-main"><div class="column">
      <h1 class="headline" style="font-size:30px">What's missing${open.length ? `<span class="count-pill">${open.length}</span>` : ""}</h1>
      <p class="soft" style="margin:8px 0 18px">Your answers go live on your page. New questions appear here as test customers and real agents get stuck.</p>
      ${open.length ? open.map(questionBlock).join("") : `<div class="empty"><b>Nothing's missing right now</b>When a test customer or a real agent gets stuck, the question lands here.</div>`}
      <div class="section-gap">${detail}</div>
      ${answered ? `<div class="section-gap"><h2 class="section" style="margin-bottom:12px">Already answered</h2>${answered}</div>` : ""}
    </div></section>`);
}

// ------------------------------------------------------------ Resource

const srcLabel = (i) => (i.status === "draft" ? '<span class="draft-tag">Not public yet</span>' : i.source === "crawl" ? "Your website" : i.source === "connector" ? "Connected account" : i.confirmed_on ? `You, ${shortDate(i.confirmed_on)}` : "You");
const money = (rec, n) => (n === null || n === undefined || n === "" ? "Not stated" : `${{ USD: "$", EUR: "€", GBP: "£", INR: "₹" }[rec.currency || "USD"] ?? ""}${Number(n).toLocaleString()}`);
const editCell = (collection, id, field, variant, value, rec) => `<span class="cell" data-do="editNumber" data-collection="${collection}" data-id="${esc(id)}" data-field="${field}" data-variant="${esc(variant || "")}" data-value="${esc(value ?? "")}">${money(rec, value)}</span>`;
const factLine = (collection, item, text) => `<div class="fact editable" data-do="editFact" data-collection="${collection}" data-id="${esc(item.id)}" data-text="${esc(text)}"><span class="text">${esc(text)}</span><span class="src">${srcLabel(item)}</span></div>`;

function priceSection(rec, title, collection, items) {
  if (!items.length) return "";
  const labels = items[0].variants?.map((v) => v.label) || [];
  const uniform = labels.length && items.every((o) => (o.variants || []).map((v) => v.label).join() === labels.join());
  if (uniform) {
    const head = `<tr><th>Service</th>${labels.map((l) => `<th>${esc(l)}</th>`).join("")}</tr>`;
    const body = items.map((o) => `<tr><td><div style="font-weight:500">${esc(o.name)}</div><div class="small muted">${esc([o.description, o.duration].filter(Boolean).join(". ")).slice(0, 150)}</div></td>${o.variants.map((v) => `<td>${editCell(collection, o.id, "variants", v.id, v.price, rec)}</td>`).join("")}</tr>`).join("");
    return `<section class="doc-section"><div class="between"><h2 class="section">${title}</h2><span class="small muted">Prices before tax</span></div><table class="prices">${head}${body}</table></section>`;
  }
  const rows = items.map((o) => {
    const price = (o.variants || []).length ? o.variants.map((v) => `${esc(v.label)} ${editCell(collection, o.id, "variants", v.id, v.price, rec)}`).join(" · ") : o.price_type === "quote_only" ? "Quoted after details" : editCell(collection, o.id, "price", "", o.price, rec);
    return `<div class="fact"><span class="text"><span style="font-weight:500">${esc(o.name)}</span>${o.requires ? `<span class="small muted"> Requires ${esc(o.requires)}</span>` : ""}</span><span>${price}</span></div>`;
  }).join("");
  return `<section class="doc-section"><div class="between"><h2 class="section">${title}</h2><span class="small muted">Prices before tax</span></div>${rows}</section>`;
}

function renderDoc(rec, unknowns) {
  const b = rec.business || {};
  const facts = rec.facts || [];
  const section = (title, body, note = "") => (body ? `<section class="doc-section"><div class="between"><h2 class="section">${title}</h2>${note ? `<span class="small muted">${note}</span>` : ""}</div>${body}</section>` : "");
  const closures = facts.filter((f) => f.category === "closure").map((f) => factLine("facts", f, f.statement)).join("");
  const fees = (rec.fees || []).map((f) => `<div class="fact"><span class="text">${esc(f.label)}${f.applies_when ? `<span class="small muted"> · ${esc(String(f.applies_when).replace(/\.+$/, ""))}</span>` : ""}</span><span>${f.percent ? `${esc(f.percent)}%` : editCell("fees", f.id, "amount", "", f.amount, rec)}</span><span class="src">${srcLabel(f)}</span></div>`).join("");
  const tax = rec.tax?.rate !== undefined && rec.tax?.rate !== null ? `<div class="fact"><span class="text">Sales tax is ${Math.round(Number(rec.tax.rate) * 100000) / 1000}%${rec.tax.applies_to ? `, on ${esc(rec.tax.applies_to)}` : ""}</span></div>` : "";
  const zones = (rec.zones || []).map((z) => `<div class="fact"><span class="text">${esc(z.label)}${(z.zips || []).length ? `<span class="small muted"> · ${z.zips.length} ZIP codes</span>` : ""}</span><span>${z.fee ? editCell("zones", z.id, "fee", "", z.fee, rec) : "No travel fee"}</span><span class="src">${srcLabel(z)}</span></div>`).join("") + facts.filter((f) => f.category === "service_area").map((f) => factLine("facts", f, f.statement)).join("");
  const groups = Object.entries(CATEGORIES).map(([cat, title]) => section(title, facts.filter((f) => f.category === cat || (cat === "other" && !CATEGORIES[f.category] && !["closure", "service_area"].includes(f.category))).map((f) => factLine("facts", f, f.statement)).join(""))).join("");
  const not = (rec.not_offered || []).map((n) => factLine("not_offered", n, n.statement)).join("");
  const unknown = unknowns.map((u) => `<div class="fact"><span class="status-dot" style="background:var(--accent)"></span><span class="text soft">${esc(u)}</span><a class="small accent" style="font-weight:500;text-decoration:none" href="#/simulations">Answer</a></div>`).join("");
  return `<h1 class="headline" style="font-size:44px;letter-spacing:-.8px">${esc(b.name || "Your business")}</h1>${b.summary ? `<p class="soft" style="font-size:16px;margin:12px 0 0">${esc(b.summary)}</p>` : ""}
    ${section("Closures and notices", closures)}${priceSection(rec, "What's offered", "offerings", rec.offerings || [])}${priceSection(rec, "Add-ons", "addons", rec.addons || [])}${section("Fees and tax", fees + tax)}${section("Where the service goes", zones)}${groups}${section("Not offered", not)}${section("Not stated yet", unknown, "Agents are told plainly that this isn't known")}`;
}

function composerHtml(pending) {
  const cards = pending.map((p) => `<div class="proposal"><div class="title">${esc(p.title)}</div>${p.body ? `<div class="small muted">You said: “${esc(p.body)}”</div>` : ""}<div class="row-flex"><button class="btn primary" data-do="confirmChange" data-id="${p.id}">Confirm</button><button class="btn ghost" data-do="discardChange" data-id="${p.id}">Discard</button></div></div>`).join("");
  const clarify = state.clarify ? `<div class="proposal"><div class="title">${esc(state.clarify)}</div></div>` : "";
  const working = state.working ? `<div class="row-flex small soft" style="padding:0 4px">${icon("loader", "spin")} Working out the change</div>` : "";
  return `<div class="composer">${cards}${clarify}${working}<form data-form="instruct"><div class="field"><input name="text" required autocomplete="off" placeholder="Tell MuseFront what to change, like “closed for the next 2 days”" ${state.working ? "disabled" : ""}><button class="send" aria-label="Send" ${state.working ? "disabled" : ""}>${icon("arrow-up")}</button></div></form></div>`;
}

async function renderResource() {
  const id = state.site.id;
  if (isBusy(state.site) && state.site.facts.draft + state.site.facts.confirmed === 0) { poll = setTimeout(render, 3000); return paint(`<div class="center-pane"><div style="width:min(600px,100%)">${stepsPanel(state.site)}</div></div>`); }
  const [res, changes, reviews] = await Promise.all([api(`/websites/${id}/resource`), api(`/websites/${id}/resource/changes`), api(`/websites/${id}/inbox?kinds=review`)]);
  const pending = changes.filter((c) => c.status === "open");
  const review = reviews[0];
  const banner = review ? `<div class="banner"><div><div style="font-weight:500">${esc(review.title)}</div><div class="small soft">Nothing is public until you do. Click any line to fix it first.</div></div><button class="btn primary" data-do="confirmReview" data-id="${review.id}">Confirm all</button></div>` : "";
  let body = banner + renderDoc(res.record, res.not_stated_yet);
  if (state.agentView) { const a = await api(`/websites/${id}/resource/agent-view`); body = a.live ? `<pre class="agent-view">${esc(a.text)}</pre>` : `<div class="empty" style="border:0"><b>Agents can't see anything yet</b>Confirm your facts to publish your page.</div>`; }
  paint(`<div class="res-wrap"><header class="res-bar"><div class="row-flex" style="min-width:0"><span class="status-dot ${state.site.live ? "live" : ""}"></span><span class="${state.site.live ? "ok" : "muted"}" style="font-weight:500">${state.site.live ? "Live" : "Not public yet"}</span>${state.site.live ? `<span class="mono soft" style="font-size:12.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(res.link.replace(/^https?:\/\//, ""))}</span>` : ""}</div>
      <div class="row-flex"><div class="seg"><button class="${state.agentView ? "" : "on"}" data-do="viewOwner">Your view</button><button class="${state.agentView ? "on" : ""}" data-do="viewAgent">What agents see</button></div><button class="btn ghost small" data-do="undo" title="Go back to the previous version">${icon("undo-2")} Version ${res.version}</button><button class="btn primary" data-do="copy" data-text="${esc(res.link)}" data-label="Link" ${state.site.live ? "" : "disabled"}>${icon("copy")} Copy link</button></div></header>
    <div class="res-scroll" id="docScroll"><div class="doc">${body}</div></div><div class="composer-wrap" id="composer">${composerHtml(pending)}</div></div>`);
}

function refreshComposer() {
  return api(`/websites/${state.site.id}/resource/changes`).then((changes) => { $("#composer").innerHTML = composerHtml(changes.filter((c) => c.status === "open")); if (window.lucide) lucide.createIcons(); const input = $("#composer input"); if (input && !state.working) input.focus(); });
}

// ------------------------------------------------------------ Inbox: what agents did and asked

function feedLine(e) {
  const job = e.inputs || {};
  const what = [job.service, job.variant, job.zip].filter(Boolean).join(", ");
  switch (e.event) {
    case "page_hit": return ["file-text", `Read ${e.path === "/" ? "your main page" : e.path}`, e.agent || "", false];
    case "quote": return ["calculator", `Worked out a quote${what ? `: ${what}` : ""}`, typeof e.total === "number" ? `$${e.total.toFixed(2)}` : e.status === "needs_info" ? "Needed more details" : "", false];
    case "dead_end": return ["circle-slash", `Dead end${what ? `: ${what}` : ""}`, String(e.reason || "").replaceAll("_", " "), true];
    case "request": return ["calendar-check", `Sent a booking request${what ? `: ${what}` : ""}`, String(e.outcome || "").replaceAll("_", " "), false];
    case "question": return ["message-circle", `Asked: “${e.text}”`, "", false];
    default: return ["circle", e.event, "", false];
  }
}

async function renderInbox() {
  const id = state.site.id;
  const [activity, items] = await Promise.all([api(`/websites/${id}/activity`), api(`/websites/${id}/inbox?kinds=agent_question`)]);
  const c = activity.counts;
  const stats = [[c.page_reads, "Pages read"], [c.quotes, "Quotes worked out"], [c.dead_ends, "Dead ends"], [c.questions, "Questions"]].map(([n, l]) => `<div class="stat"><b class="${l === "Dead ends" && n ? "accent" : ""}">${n}</b><span class="small muted">${l}</span></div>`).join("");
  const asked = items.map((q) => `<article class="question"><h3>${esc(q.title)}</h3><div class="soft small">An agent asked this for a customer. Your answer shows on its status page.</div>
    <form data-form="answer" data-id="${q.id}"><div class="field"><input name="text" required placeholder="Type your answer" autocomplete="off"><button class="send" aria-label="Send answer">${icon("arrow-up")}</button></div>
    <label class="row-flex small soft" style="margin-top:8px"><input type="checkbox" name="once"> Just this once, don't add it to my page</label></form></article>`).join("");
  const feed = activity.feed.slice(0, 30).map((e) => { const [ic, text, detail, dead] = feedLine(e); return `<div class="line-row">${icon(ic, dead ? "accent" : "muted")}<span class="grow" style="overflow-wrap:anywhere">${esc(text)}</span><span class="small muted" style="flex:none">${esc(detail)}</span><span class="tiny muted" style="flex:none;width:96px;text-align:right">${esc(when(e.ts))}</span></div>`; }).join("");
  const wanted = activity.unmet_demand.map((d) => `<div class="line-row"><span class="grow" style="font:400 16px/1.3 var(--voice)">${esc(d.title)}</span></div>`).join("");
  paint(`<section class="pane-main"><div class="wide-column"><div class="between"><h1 class="page-title">Inbox</h1><button class="btn ghost small" data-do="review">${icon("refresh-cw")} Review activity now</button></div>
    <div class="stats">${stats}</div>
    ${asked ? `<div style="margin-bottom:40px"><h2 class="section" style="margin-bottom:6px">Agents are asking</h2>${asked}</div>` : ""}
    <div class="zones"><div><h2 class="section" style="margin-bottom:12px">What agents did</h2>${feed || `<div class="empty"><b>No agents yet</b>Put your link on your website, and what agents do will show up here.</div>`}</div>
    <aside><h2 class="section" style="margin-bottom:12px;font-size:19px">Wanted, but not offered</h2>${wanted || `<div class="empty small">Nothing yet.</div>`}<p class="small muted" style="margin-top:16px">You can only see agents that reach your MuseFront page. An agent that stops at your own website stays invisible.</p></aside></div>
  </div></section>`);
}

// ------------------------------------------------------------ Bookings

const words = (t) => { const w = String(t || "").replace(/[-_]+/g, " ").trim(); return w ? w[0].toUpperCase() + w.slice(1) : ""; };
const bookingTitle = (b) => { const job = b.payload?.details?.inputs || {}; const name = words(job.service) || "A job"; return job.when ? `${name} on ${shortDate(job.when)}` : name; };
const replyText = (r) => { const m = String(r || "").match(/^(\w+): ([\s\S]*)$/); return m ? `${words(m[1])}. ${m[2]}` : r; };

async function renderBookings() {
  const rows = await api(`/websites/${state.site.id}/bookings`);
  if (!rows.some((b) => b.id === state.selectedBooking)) state.selectedBooking = rows[0]?.id || null;
  const b = rows.find((x) => x.id === state.selectedBooking);
  const list = rows.map((x) => `<button class="list-item ${x.id === state.selectedBooking ? "on" : ""}" data-do="pickBooking" data-id="${x.id}"><div class="between tiny" style="margin-bottom:3px"><span class="row-flex" style="gap:6px;font-weight:500;color:var(--ink-2)">${x.status === "open" ? '<span class="status-dot" style="background:var(--accent)"></span>Needs a reply' : "Replied"}</span><span class="muted">${esc(when(x.created_at))}</span></div><div class="name">${esc(bookingTitle(x))}</div><div class="tiny muted">${esc(x.payload?.details?.name || "")}</div></button>`).join("");
  let detail = `<div class="center-pane"><div class="stack" style="max-width:440px;text-align:center"><h1 class="headline" style="font-size:30px">No booking requests yet</h1><p class="soft" style="margin:0">When an agent sends one for a customer, it lands here for you to accept or decline.</p></div></div>`;
  if (b) {
    const d = b.payload?.details || {};
    const job = d.inputs || {};
    const kv = (k, v) => (v ? `<div class="kv"><span class="k">${k}</span><span class="v">${esc(v)}</span></div>` : "");
    const reply = b.status === "open" ? `<form class="stack section-gap" data-form="bookingReply" data-id="${b.id}" style="gap:10px"><textarea class="reply" name="message" placeholder="Add a note to your reply. It shows on the status page the agent checks."></textarea><div class="row-flex" style="flex-wrap:wrap"><button class="btn primary" name="status" value="accepted">Accept</button><button class="btn" name="status" value="suggested">Suggest another time</button><button class="btn ghost" name="status" value="declined">Decline</button></div></form>` : `<div class="section-gap"><div class="small muted" style="margin-bottom:4px">Your reply</div><div style="font:400 19px/1.35 var(--voice)">${esc(replyText(b.resolution))}</div></div>`;
    detail = `<section class="pane-main"><div class="column"><div class="small muted" style="font-weight:500;margin-bottom:12px">${d.submitted_by === "agent" ? `Sent by ${esc(d.agent_name || "an agent")}` : "Sent by the customer"}, ${esc(when(b.created_at))}</div><h1 class="headline">${esc(bookingTitle(b))}</h1>
      <div style="margin-top:28px">${kv("Customer", d.name)}${kv("Email", d.email)}${kv("Phone", d.phone)}${kv("Size or type", words(job.variant))}${kv("Add-ons", (job.addons || []).join(", "))}${kv("ZIP code", job.zip)}${kv("Date", job.when ? shortDate(job.when) : "")}${kv("Notes", d.notes)}${typeof d.total === "number" ? kv("Quoted total", `$${d.total.toFixed(2)}`) : ""}</div>${reply}
      <p class="small section-gap"><a class="muted" href="${esc(b.status_url)}" target="_blank" rel="noopener">See the public status page</a></p></div></section>`;
  }
  paint(`<aside class="pane-list"><div class="list-head"><h1 class="page-title">Bookings</h1></div><div class="list">${list}</div></aside>${detail}`);
}

// ------------------------------------------------------------ Actions

const actions = {
  reload: () => render(),
  openConnect: async () => { const a = await api("/connections/available"); connectState.configured = a.configured; connectState.rows = {}; renderConnect(); },
  closeConnect: () => { $("#modal").innerHTML = ""; render(); },
  startConnect: async (el) => {
    const id = el.dataset.id;
    connectState.rows[id] = { step: "waiting" };
    renderConnect();
    try {
      const r = await post(`/websites/${state.site.id}/connections`, { toolkit: id });
      window.open(r.connect_link, "_blank", "noopener,width=520,height=680");
    } catch (error) { connectState.rows[id] = { error: error.message }; renderConnect(); }
  },
  finishConnect: async (el) => {
    const id = el.dataset.id;
    const sheet = $("#sheet-id")?.value.trim();
    try {
      const r = await post(`/websites/${state.site.id}/connections/${id}/sync`, sheet ? { spreadsheet_id: sheet } : {});
      connectState.rows[id] = { step: "done" };
      renderConnect();
      toast(r.proposal ? "Connected. Proposed changes are waiting on your Resource page" : "Connected. Nothing new to change");
    } catch (error) { connectState.rows[id] = { step: "waiting", error: error.message }; renderConnect(); }
  },
  copy: (el) => copy(el.dataset.text, el.dataset.label),
  pickSite: (el) => { selectSite(el.dataset.id); location.hash = "#/websites"; render(); },
  pickSim: (el) => { state.selectedSim = el.dataset.id; render(); },
  pickBooking: (el) => { state.selectedBooking = el.dataset.id; render(); },
  viewOwner: () => { state.agentView = false; render(); },
  viewAgent: () => { state.agentView = true; render(); },
  checkLink: async () => { const r = await post(`/websites/${state.site.id}/check-link`); toast(r.found ? "Found on your website" : "Not on your website's home page yet"); },
  dismiss: async (el) => { await post(`/inbox/${el.dataset.id}/dismiss`); render(); },
  runCheck: async () => { await post(`/websites/${state.site.id}/simulations`, { target: state.site.live ? "resource" : "storefront" }); toast("Check started"); setTimeout(render, 600); },
  review: async () => { const r = await post(`/websites/${state.site.id}/revise`); toast(r.signals ? `Reviewed ${r.signals} signals: ${r.questions} new questions, ${r.insights} insights` : "Nothing new to review"); render(); },
  undo: async () => { await post(`/websites/${state.site.id}/resource/undo`); toast("Went back to the previous version"); render(); },
  confirmReview: async (el) => { await post(`/inbox/${el.dataset.id}/confirm`); toast("Your page is live"); render(); },
  confirmChange: async (el) => { state.clarify = null; await post(`/inbox/${el.dataset.id}/confirm`); toast("Published", { do: "undo", label: "Undo" }); render(); },
  discardChange: async (el) => { await post(`/inbox/${el.dataset.id}/dismiss`); refreshComposer(); },
  editFact: (el) => {
    const { collection, id, text } = el.dataset;
    el.outerHTML = `<form class="editing" data-form="saveFact" data-collection="${esc(collection)}" data-id="${esc(id)}"><input name="text" value="${esc(text)}" autocomplete="off"><button class="btn primary" style="padding:5px 12px">Save</button><button class="btn ghost" type="button" data-do="reload" style="padding:5px 8px">Cancel</button></form>`;
    const input = $(".editing input"); input.focus(); input.setSelectionRange(input.value.length, input.value.length);
  },
  editNumber: (el) => {
    const d = el.dataset;
    el.outerHTML = `<form data-form="saveNumber" data-collection="${esc(d.collection)}" data-id="${esc(d.id)}" data-field="${esc(d.field)}" data-variant="${esc(d.variant)}" style="display:inline"><input class="cell-input" name="value" type="number" step="any" value="${esc(d.value)}"></form>`;
    const input = $(".cell-input"); input.focus(); input.select(); input.addEventListener("blur", () => render());
  },
};

const forms = {
  addSite: async (form) => {
    const site = await post("/websites", { url: form.url.value.trim(), run_check: form.check.checked });
    localStorage.setItem("mf.site", site.id);
    location.hash = "#/websites"; render();
  },
  answer: async (form) => {
    const r = await post(`/inbox/${form.dataset.id}/answer`, { text: form.text.value.trim(), scope: form.once?.checked ? "once" : "everyone" });
    toast(r.summary || "Saved", { do: "undo", label: "Undo" });
    render();
  },
  instruct: async (form) => {
    const text = form.text.value.trim();
    state.working = true; state.clarify = null;
    await refreshComposer();
    try {
      const r = await post(`/websites/${state.site.id}/instructions`, { text });
      if (r.needs_clarifying) state.clarify = r.question;
    } finally { state.working = false; }
    await refreshComposer();
  },
  saveFact: async (form) => {
    const field = "statement";
    await api(`/websites/${state.site.id}/resource`, { method: "PATCH", body: { reason: "Edited by the owner", ops: [{ op: "upsert", collection: form.dataset.collection, item: { id: form.dataset.id, [field]: form.text.value.trim() } }] } });
    toast("Saved and published", { do: "undo", label: "Undo" }); render();
  },
  saveNumber: async (form) => {
    const { collection, id, field, variant } = form.dataset;
    const value = Number(form.value.value);
    const res = await api(`/websites/${state.site.id}/resource`);
    const item = res.record[collection].find((i) => i.id === id);
    const patch = field === "variants" ? { id, variants: item.variants.map((v) => (v.id === variant ? { ...v, price: value } : v)) } : { id, [field]: value };
    await api(`/websites/${state.site.id}/resource`, { method: "PATCH", body: { reason: "Edited by the owner", ops: [{ op: "upsert", collection, item: patch }] } });
    toast("Saved and published", { do: "undo", label: "Undo" }); render();
  },
  bookingReply: async (form, submitter) => {
    const status = submitter?.value || "accepted";
    const defaults = { accepted: "Yes, that works. We'll be in touch to confirm.", suggested: "That time doesn't work. Please suggest another.", declined: "Sorry, we can't take this one." };
    await post(`/bookings/${form.dataset.id}/reply`, { status, message: form.message.value.trim() || defaults[status] });
    toast("Reply sent"); render();
  },
};

document.addEventListener("click", async (event) => {
  const el = event.target.closest("[data-do]");
  if (!el || el.disabled) return;
  if (el.dataset.self && event.target !== el) return; // Clicks inside the popup don't close it.
  try { await actions[el.dataset.do](el); } catch (error) { fail(error); }
});
document.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target.closest("[data-form]");
  if (!form) return;
  const buttons = [...form.querySelectorAll("button")];
  buttons.forEach((b) => (b.disabled = true));
  try { await forms[form.dataset.form](form, event.submitter); } catch (error) { fail(error); state.working = false; buttons.forEach((b) => (b.disabled = false)); }
});
document.addEventListener("keydown", (event) => { if (event.key === "Escape" && (document.querySelector(".editing") || document.querySelector(".cell-input"))) render(); });
window.addEventListener("hashchange", render);
render();
