// Resource: the fact sheet, the lens onto what agents read, the quote console and the prompt bar.
import { $, $$, actions, api, app, copyButton, currency, domain, esc, forms, icon, isBusy, money as moneyText, morph, plural, post, screens, shortDate, state, toast, withTransition } from "../core.js";
import { showLiveMoment } from "./moment.js";

const CATEGORIES = { vocabulary: "In the customer's words", dependencies: "What depends on what", conditions: "Conditions that change the price", eligibility: "Who and what can be served", prerequisites: "What the customer needs to provide", availability: "Availability", staff: "Staff", policies: "Policies", timing: "Timing rules", credentials: "Credentials", next_step: "What happens after a request", other: "Other facts" };

const srcLabel = (item) => (item.status === "draft" ? '<span class="tag-draft">Not public yet</span>' : item.source === "crawl" ? "Your website" : item.source === "connector" ? "Connected account" : item.confirmed_on ? `You, ${shortDate(item.confirmed_on)}` : "You");
const flashed = (id) => (state.flash && state.flash === id ? "flash" : "");

const cellFor = (rec) => (collection, id, field, variant, value) => `<span class="cell num" data-do="editNumber" data-collection="${collection}" data-id="${esc(id)}" data-field="${field}" data-variant="${esc(variant || "")}" data-value="${esc(value ?? "")}">${moneyText(currency(rec), value)}</span>`;
const factLine = (collection, item, text) => `<div class="fact editable" data-do="editFact" data-collection="${collection}" data-id="${esc(item.id)}" data-text="${esc(text)}" id="fact-${esc(item.id)}"><span class="text ${flashed(item.id)}">${esc(text)}</span><span class="src">${srcLabel(item)}</span></div>`;
const section = (title, body, note = "") => (body ? `<section class="doc-section"><div class="doc-section-head"><h2>${title}</h2>${note ? `<span class="tiny muted">${note}</span>` : ""}</div>${body}</section>` : "");

function priceSection(rec, title, collection, items) {
  if (!items.length) return "";
  const cell = cellFor(rec);
  const labels = items[0].variants?.map((v) => v.label) || [];
  const uniform = labels.length && items.every((o) => (o.variants || []).map((v) => v.label).join() === labels.join());
  if (uniform) {
    const head = `<tr><th>${collection === "addons" ? "Add-on" : "Service"}</th>${labels.map((l) => `<th>${esc(l)}</th>`).join("")}</tr>`;
    const body = items.map((o) => `<tr id="fact-${esc(o.id)}"><td><span class="strong">${esc(o.name)}</span><span class="small muted clamp-2">${esc([o.description, o.duration].filter(Boolean).join(". ").replace(/\.\.+/g, "."))}</span></td>${o.variants.map((v) => `<td>${cell(collection, o.id, "variants", v.id, v.price)}</td>`).join("")}</tr>`).join("");
    return section(title, `<table class="prices">${head}${body}</table>`, "Prices before tax");
  }
  const rows = items.map((o) => {
    const price = (o.variants || []).length ? o.variants.map((v) => `${esc(v.label)} ${cell(collection, o.id, "variants", v.id, v.price)}`).join(" · ") : o.price_type === "quote_only" ? "Quoted after details" : cell(collection, o.id, "price", "", o.price);
    return `<div class="fact" id="fact-${esc(o.id)}"><span class="text"><span class="strong">${esc(o.name)}</span>${o.requires ? `<span class="small muted"> Requires ${esc(o.requires)}</span>` : ""}</span><span class="small">${price}</span></div>`;
  }).join("");
  return section(title, rows, "Prices before tax");
}

function docHtml(rec, unknowns) {
  const biz = rec.business || {};
  const facts = rec.facts || [];
  const cell = cellFor(rec);
  const closures = facts.filter((f) => f.category === "closure").map((f) => factLine("facts", f, f.statement)).join("");
  const fees = (rec.fees || []).map((f) => `<div class="fact" id="fact-${esc(f.id)}"><span class="text ${flashed(f.id)}">${esc(f.label)}${f.applies_when ? `<span class="small muted"> · ${esc(String(f.applies_when).replace(/\.+$/, ""))}</span>` : ""}</span><span class="num">${f.percent ? `${esc(f.percent)}%` : cell("fees", f.id, "amount", "", f.amount)}</span><span class="src">${srcLabel(f)}</span></div>`).join("");
  const tax = rec.tax?.rate !== undefined && rec.tax?.rate !== null ? `<div class="fact"><span class="text">Sales tax is ${Math.round(Number(rec.tax.rate) * 100000) / 1000}%${rec.tax.applies_to ? `, on ${esc(rec.tax.applies_to)}` : ""}</span></div>` : "";
  const zones = (rec.zones || []).map((z) => `<div class="fact" id="fact-${esc(z.id)}"><span class="text">${esc(z.label)}${(z.zips || []).length ? `<span class="small muted"> · ${z.zips.length} ZIP codes</span>` : ""}</span><span class="num">${z.fee ? cell("zones", z.id, "fee", "", z.fee) : z.fee === 0 ? "No travel fee" : "Fee not stated"}</span><span class="src">${srcLabel(z)}</span></div>`).join("") + facts.filter((f) => f.category === "service_area").map((f) => factLine("facts", f, f.statement)).join("");
  const groups = Object.entries(CATEGORIES).map(([cat, title]) => section(title, facts.filter((f) => f.category === cat || (cat === "other" && !CATEGORIES[f.category] && !["closure", "service_area"].includes(f.category))).map((f) => factLine("facts", f, f.statement)).join(""))).join("");
  const refused = (rec.not_offered || []).map((n) => factLine("not_offered", n, n.statement)).join("");
  const unknown = unknowns.map((u) => `<div class="fact"><span class="dot dot--pen" style="align-self:center"></span><span class="text soft">${esc(u)}</span><a class="small pen strong" href="#/simulations">Answer this</a></div>`).join("");
  return `<h1 class="doc-title">${esc(biz.name || "Your business")}</h1>${biz.summary ? `<p class="doc-summary">${esc(biz.summary)}</p>` : ""}
    ${section("Closures and notices", closures)}${priceSection(rec, "What's offered", "offerings", rec.offerings || [])}${priceSection(rec, "Add-ons", "addons", rec.addons || [])}${section("Fees and tax", fees + tax)}${section("Where the service goes", zones)}${groups}${section("Not offered", refused)}${section("Not stated yet", unknown, "Agents are told plainly that this isn't known")}`;
}

function agentHtml(site, agent) {
  if (!agent?.live) return `<div class="agent-page"><h2 class="t-1">Agents can't read anything yet</h2><p style="margin-top:10px;color:var(--agent-soft)">Confirm your facts, and this is where you'll see your page exactly as they read it.</p></div>`;
  const base = domain(site.link).replace(/^[^/]+/, "");
  const verbs = [["Read", "Your facts, in plain text", base], ["Quote", "A total, worked out live", `${base}/quote`], ["Request", "A booking for you to accept", `${base}/request`], ["Ask", "A question, sent to you", `${base}/ask`]];
  return `<div class="agent-page"><div class="agent-actions">${verbs.map(([verb, what, path]) => `<div class="agent-action"><b>${verb}</b>${what}<code>${esc(path)}</code></div>`).join("")}</div><pre class="agent-md">${esc(agent.text)}</pre></div>`;
}

// ---- Quote console: the live page answers, exactly as an agent would be answered

const dayOptions = () => Array.from({ length: 9 }, (_, i) => {
  const d = new Date();
  d.setDate(d.getDate() + i + 1);
  const iso = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  return [iso, d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })];
});

function defaultQuote(rec) {
  const service = (rec.offerings || []).find((o) => o.price_type !== "quote_only") || rec.offerings?.[0];
  const zone = (rec.zones || []).find((z) => (z.zips || []).length && z.fee) || (rec.zones || []).find((z) => (z.zips || []).length);
  const saturday = dayOptions().find(([iso]) => new Date(`${iso}T12:00:00`).getDay() === 6);
  return { service: service?.id || "", variant: service?.variants?.[1]?.id || service?.variants?.[0]?.id || "", zip: zone?.zips?.[0] || "", when: saturday?.[0] || "", addons: [] };
}

function receiptHtml(rec, result) {
  if (!result) return `<div class="receipt"><div class="row"><span class="ring"></span><span class="shimmer">Asking your page</span></div></div>`;
  const q = result.quote || {};
  const sym = currency(rec);
  const lines = (q.lines || []).map((l) => `<li><span>${esc(l.label)}</span><span>${moneyText(sym, l.amount)}</span></li>`).join("");
  const tax = q.tax ? `<li><span>Tax</span><span>${moneyText(sym, q.tax)}</span></li>` : "";
  const end = q.total !== null && q.total !== undefined && q.status === "ok" ? `<div class="receipt-total"><span class="small">Total</span><b>${moneyText(sym, q.total)}</b></div>` : `<p class="receipt-stop">${esc(q.summary || q.reason || "This can't be priced as entered.")}</p>`;
  return `<div class="receipt"><div class="receipt-call">GET ${esc(domain(result.address))}</div>${lines || tax ? `<ul class="receipt-lines">${lines}${tax}</ul>` : ""}${end}</div>`;
}

function consoleHtml(site, rec) {
  if (!site.live) return `<aside class="console"><h2>Try it like an agent</h2><p class="small soft">Once your page is live, you can ask it for a quote here, exactly as an agent would.</p></aside>`;
  state.quote = state.quote && (rec.offerings || []).some((o) => o.id === state.quote.service) ? state.quote : defaultQuote(rec);
  const q = state.quote;
  const service = (rec.offerings || []).find((o) => o.id === q.service);
  const options = (rows, value) => rows.map(([v, label]) => `<option value="${esc(v)}" ${v === value ? "selected" : ""}>${esc(label)}</option>`).join("");
  const variants = (service?.variants || []).map((v) => [v.id, v.label]);
  const addons = (rec.addons || []).slice(0, 6).map((a) => `<button type="button" class="addon-chip ${q.addons.includes(a.id) ? "on" : ""}" data-do="toggleAddon" data-id="${esc(a.id)}">${esc(a.name)}</button>`).join("");
  return `<aside class="console" id="console">
    <div><h2>Try it like an agent</h2><p class="small soft" style="margin-top:3px">Your page works this out itself, with no AI, so the same question always gets the same answer.</p></div>
    <form class="console-fields" data-form="quote">
      <label class="full">Service<select name="service" data-change="quote">${options((rec.offerings || []).map((o) => [o.id, o.name]), q.service)}</select></label>
      ${variants.length ? `<label>Size<select name="variant" data-change="quote">${options(variants, q.variant)}</select></label>` : ""}
      <label>ZIP code<input name="zip" inputmode="numeric" maxlength="5" value="${esc(q.zip)}" data-change="quote" autocomplete="off"></label>
      <label class="full">Day<select name="when" data-change="quote">${options(dayOptions(), q.when)}</select></label>
    </form>
    ${addons ? `<div class="addon-chips">${addons}</div>` : ""}
    <div id="quote-out">${receiptHtml(rec, state.quote.result)}</div>
  </aside>`;
}

let quoteTimer;
function runQuote(rec, delay = 160) {
  clearTimeout(quoteTimer);
  quoteTimer = setTimeout(async () => {
    const q = state.quote;
    if (!q || !state.site?.live) return;
    const params = new URLSearchParams();
    for (const key of ["service", "variant", "zip", "when"]) if (q[key]) params.set(key, q[key]);
    for (const addon of q.addons) params.append("addon", addon);
    try {
      q.result = await api(`/websites/${state.site.id}/resource/quote?${params}`);
    } catch (error) {
      q.result = { quote: { summary: error.message }, address: "" };
    }
    const out = $("#quote-out");
    if (out && state.quote === q) morph(out, receiptHtml(rec, q.result));
  }, delay);
}

// ---- The prompt bar

function composerHtml(pending) {
  const cards = pending.map((p) => {
    const ops = (p.payload?.ops || []).map((op) => op.item?.statement || op.item?.label || op.item?.name).filter(Boolean);
    return `<div class="proposal" id="prop-${p.id}"><span class="eyebrow">Proposed change. Nothing is public until you confirm.</span><div class="proposal-title">${esc(p.title)}</div>${ops.length ? `<div class="proposal-ops">${ops.map((o) => `<div>+ ${esc(o)}</div>`).join("")}</div>` : ""}<div class="row"><button class="btn btn--primary btn--sm" data-do="confirmChange" data-id="${p.id}">${icon("check")} Confirm and publish</button><button class="btn btn--ghost btn--sm" data-do="discardChange" data-id="${p.id}">Discard</button></div></div>`;
  }).join("");
  const clarify = state.clarify ? `<div class="proposal"><div class="proposal-title">${esc(state.clarify)}</div></div>` : "";
  const working = state.working ? `<div class="proposal"><div class="row small"><span class="ring"></span><span class="shimmer">Working out the change</span></div></div>` : "";
  const hints = !pending.length && !state.working ? `<div class="composer-hints"><button type="button" class="composer-hint" data-do="useHint" data-text="Closed for the next 2 days">Closed for the next 2 days</button><button type="button" class="composer-hint" data-do="useHint" data-text="We now take Apple Pay">We now take Apple Pay</button></div>` : "";
  return `<div class="composer">${cards}${clarify}${working}${hints}<form data-form="instruct"><div class="field"><input name="text" required autocomplete="off" aria-label="Tell Legible what changed" placeholder="Tell Legible what changed, in plain words" ${state.working ? "disabled" : ""}><button class="send" aria-label="Send" ${state.working ? "disabled" : ""}>${icon("arrow-up")}</button></div></form></div>`;
}

async function refreshComposer() {
  const changes = await api(`/websites/${state.site.id}/resource/changes`);
  const el = $("#composer");
  if (el) morph(el, composerHtml(changes.filter((c) => c.status === "open")));
}

// ---- The lens

function setLens(wrap, percent, { snap = true } = {}) {
  wrap.style.setProperty("--split", `${percent}%`);
  if (!snap) return;
  wrap.classList.toggle("is-owner", percent >= 99);
  wrap.classList.toggle("is-agent", percent <= 1);
  wrap.classList.toggle("is-mid", percent > 1 && percent < 99);
}

function syncSeg() {
  const seg = $("#lens-seg");
  if (!seg) return;
  const on = $("button.on", seg);
  seg.style.setProperty("--x", `${on.offsetLeft - 3}px`);
  seg.style.setProperty("--w", `${on.offsetWidth}px`);
  seg.classList.toggle("agent", state.agentView);
}

function setAgentView(next) {
  state.agentView = next;
  const seg = $("#lens-seg");
  if (seg) for (const b of seg.querySelectorAll("button")) b.classList.toggle("on", (b.dataset.do === "viewAgent") === next);
  syncSeg();
  const wrap = $("#lens");
  if (wrap) setLens(wrap, next ? 0 : 100);
}

function bindLensHandle() {
  const wrap = $("#lens");
  const handle = $("#lens-handle");
  if (!wrap || !handle) return;
  handle.addEventListener("pointerdown", (start) => {
    start.preventDefault();
    handle.setPointerCapture(start.pointerId);
    wrap.classList.add("dragging");
    wrap.classList.remove("is-owner", "is-agent");
    wrap.classList.add("is-mid");
    const box = wrap.getBoundingClientRect();
    const move = (event) => setLens(wrap, Math.min(100, Math.max(0, ((event.clientX - box.left) / box.width) * 100)), { snap: false });
    const up = (event) => {
      handle.removeEventListener("pointermove", move);
      wrap.classList.remove("dragging");
      const at = ((event.clientX - box.left) / box.width) * 100;
      if (at < 12 || at > 88) setAgentView(at < 50);
      else setLens(wrap, at);
    };
    handle.addEventListener("pointermove", move);
    handle.addEventListener("pointerup", up, { once: true });
  });
}

screens.resource = {
  async load() {
    const id = state.site.id;
    if (isBusy(state.site) && state.site.facts.draft + state.site.facts.confirmed === 0) return { waiting: true };
    const [res, changes, reviews] = await Promise.all([api(`/websites/${id}/resource`), api(`/websites/${id}/resource/changes`), api(`/websites/${id}/inbox?kinds=review`)]);
    const agent = state.site.live ? await api(`/websites/${id}/resource/agent-view`) : null;
    return { res, agent, pending: changes.filter((c) => c.status === "open"), review: reviews[0] };
  },
  view({ waiting, res, agent, pending, review }) {
    if (waiting) return `<div class="blank"><div class="blank-inner"><span class="ring"></span><h1 class="t-1">Your fact sheet is on its way</h1><p class="soft">${esc(state.site.stage_note || "Legible is reading your website.")}</p><a class="btn" href="#/websites">Watch it work</a></div></div>`;
    const site = state.site;
    const banner = review ? `<div class="confirm-bar"><div><b>Confirm ${plural(site.facts.draft, "fact")} read from your website</b><small>Nothing is public until you do. Click any line to fix it first.</small></div><button class="btn btn--on-agent" data-do="confirmReview" data-id="${review.id}" id="confirm-all">${icon("check")} Confirm and publish</button></div>` : "";
    return `<div class="res">
      <header class="res-bar">
        <div class="row" style="min-width:0"><span class="dot ${site.live ? "dot--live" : ""}"></span><span class="small strong ${site.live ? "ok" : "muted"}">${site.live ? "Live" : "Not public yet"}</span><span class="small muted">${plural(res.counts.confirmed + res.counts.draft, "fact")}, version ${res.version}</span></div>
        <div class="seg" id="lens-seg"><span class="seg-ind"></span><button class="${state.agentView ? "" : "on"}" data-do="viewOwner">Your view</button><button class="${state.agentView ? "on" : ""}" data-do="viewAgent">What agents see</button></div>
        <div class="row"><button class="btn btn--ghost btn--sm" data-do="undo">${icon("undo-2")} Undo last change</button>${site.live ? copyButton(res.link, "Link", { cls: "btn--sm" }) : ""}</div>
      </header>
      <div class="res-main">
        <div class="lens-wrap ${state.agentView ? "is-agent" : "is-owner"}" id="lens" style="--split:${state.agentView ? 0 : 100}%">
          <div class="lens-scroll" id="docScroll"><div class="lens-stack">
            <div class="lens-owner"><div class="doc">${banner}${docHtml(res.record, res.not_stated_yet)}</div></div>
            <div class="lens-agent agent-surface">${agentHtml(site, agent)}</div>
          </div></div>
          <div class="lens-handle" id="lens-handle" aria-hidden="true"><b></b></div>
          <div class="composer-wrap" id="composer">${composerHtml(pending)}</div>
        </div>
        ${consoleHtml(site, res.record)}
      </div>
    </div>`;
  },
  after({ waiting, res }) {
    if (waiting) return;
    syncSeg();
    bindLensHandle();
    screens.resource.record = res.record;
    if (state.quote) runQuote(res.record, state.quote.result ? 200 : 40);
    if (state.flash) {
      const target = document.getElementById(`fact-${state.flash}`);
      target?.scrollIntoView({ block: "center", behavior: "smooth" });
      setTimeout(() => { state.flash = null; }, 3400);
    }
  },
};

// The quote console re-asks on every change.
document.addEventListener("change", (event) => {
  const el = event.target.closest("[data-change=quote]");
  if (!el || !state.quote) return;
  state.quote[el.name] = el.value;
  if (el.name === "service") {
    const service = (screens.resource.record?.offerings || []).find((o) => o.id === el.value);
    state.quote.variant = service?.variants?.[1]?.id || service?.variants?.[0]?.id || "";
    app.render();
    return;
  }
  runQuote(screens.resource.record);
});
document.addEventListener("input", (event) => {
  const el = event.target.closest("input[data-change=quote]");
  if (el && state.quote && el.value.length === 5) {
    state.quote[el.name] = el.value;
    runQuote(screens.resource.record);
  }
});

Object.assign(actions, {
  viewOwner: () => setAgentView(false),
  viewAgent: () => setAgentView(true),
  toggleAddon: (el) => {
    const q = state.quote;
    const id = el.dataset.id;
    q.addons = q.addons.includes(id) ? q.addons.filter((a) => a !== id) : [...q.addons, id];
    el.classList.toggle("on");
    runQuote(screens.resource.record);
  },
  useHint: (el) => {
    const input = $("#composer input[name=text]");
    input.value = el.dataset.text;
    input.focus();
  },
  undo: async () => {
    await post(`/websites/${state.site.id}/resource/undo`);
    state.lastAnswer = null;
    toast("Went back to the previous version");
    app.render();
  },
  confirmReview: async (el) => {
    const rect = el.getBoundingClientRect();
    const count = state.site.facts.draft;
    await post(`/inbox/${el.dataset.id}/confirm`);
    await app.render();
    showLiveMoment(state.site, count, rect);
  },
  confirmChange: async (el) => {
    state.clarify = null;
    const change = await api(`/websites/${state.site.id}/resource/changes`).then((rows) => rows.find((c) => c.id === el.dataset.id));
    await post(`/inbox/${el.dataset.id}/confirm`);
    state.flash = change?.payload?.ops?.[0]?.item?.id || null;
    toast("Published", { do: "undo", label: "Undo" });
    await app.render();
  },
  discardChange: async (el) => {
    await post(`/inbox/${el.dataset.id}/dismiss`);
    refreshComposer();
  },
  editFact: (el) => {
    const { collection, id, text } = el.dataset;
    el.outerHTML = `<form class="editing" data-form="saveFact" data-collection="${esc(collection)}" data-id="${esc(id)}"><input name="text" value="${esc(text)}" autocomplete="off" aria-label="Edit this fact"><button class="btn btn--primary btn--sm">Save</button><button class="btn btn--ghost btn--sm" type="button" data-do="reload">Cancel</button></form>`;
    const input = $(".editing input");
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
  },
  editNumber: (el) => {
    const d = el.dataset;
    el.outerHTML = `<form data-form="saveNumber" data-collection="${esc(d.collection)}" data-id="${esc(d.id)}" data-field="${esc(d.field)}" data-variant="${esc(d.variant)}" style="display:inline"><input class="cell-input" name="value" type="number" step="any" value="${esc(d.value)}" aria-label="Edit this price"></form>`;
    const input = $(".cell-input");
    input.focus();
    input.select();
    input.addEventListener("blur", () => app.render());
  },
  reload: () => app.render(),
});

Object.assign(forms, {
  instruct: async (form) => {
    const text = form.text.value.trim();
    state.working = true;
    state.clarify = null;
    await refreshComposer();
    try {
      const result = await post(`/websites/${state.site.id}/instructions`, { text });
      if (result.needs_clarifying) state.clarify = result.question;
    } finally {
      state.working = false;
    }
    await refreshComposer();
  },
  saveFact: async (form) => {
    await api(`/websites/${state.site.id}/resource`, { method: "PATCH", body: { reason: "Edited by the owner", ops: [{ op: "upsert", collection: form.dataset.collection, item: { id: form.dataset.id, statement: form.text.value.trim() } }] } });
    state.flash = form.dataset.id;
    toast("Saved and published", { do: "undo", label: "Undo" });
    app.render();
  },
  saveNumber: async (form) => {
    const { collection, id, field, variant } = form.dataset;
    const value = Number(form.value.value);
    const res = await api(`/websites/${state.site.id}/resource`);
    const item = res.record[collection].find((i) => i.id === id);
    const patch = field === "variants" ? { id, variants: item.variants.map((v) => (v.id === variant ? { ...v, price: value } : v)) } : { id, [field]: value };
    await api(`/websites/${state.site.id}/resource`, { method: "PATCH", body: { reason: "Edited by the owner", ops: [{ op: "upsert", collection, item: patch }] } });
    toast("Saved and published", { do: "undo", label: "Undo" });
    app.render();
  },
  quote: async () => {},
});

window.addEventListener("resize", syncSeg);
export { $$, withTransition };
