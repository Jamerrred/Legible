// The public resource for every business. Each page is built from the published record
// when it's requested, so the link needs no model and no Legible app, and dated facts
// such as "closed for 2 days" start and end by themselves.

const CATEGORY_TITLES = {
  vocabulary: "In the customer's words",
  dependencies: "What depends on what",
  conditions: "Conditions that change the price",
  eligibility: "Who and what can be served",
  prerequisites: "What the customer needs to provide",
  service_area: "Where the service goes",
  availability: "Availability",
  staff: "Staff",
  policies: "Policies",
  timing: "Timing rules",
  credentials: "Credentials",
  next_step: "What happens after a request",
  other: "Other facts",
};
const DEAD = new Set(["not_offered", "out_of_area", "closed", "unknown_service"]);

const esc = (v) =>
  String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json; charset=utf-8" } });
const now = () => new Date().toISOString();
const newId = (prefix) => `${prefix}-${crypto.randomUUID().replaceAll("-", "").slice(0, 16)}`;
const norm = (t) => String(t ?? "").toLowerCase().replace(/[_-]+/g, " ").replace(/\s+/g, " ").trim();
const list = (v) => (Array.isArray(v) ? v : []);

function todayIn(tz) {
  try {
    return new Intl.DateTimeFormat("en-CA", { timeZone: tz || "UTC" }).format(new Date());
  } catch {
    return new Date().toISOString().slice(0, 10);
  }
}

const inWindow = (item, day) => (!item.valid_from || item.valid_from <= day) && (!item.valid_to || day <= item.valid_to);
const upcoming = (item, day) => Boolean(item.valid_from && item.valid_from > day);
const servable = (items, day) => list(items).filter((i) => inWindow(i, day));

function money(rec, value) {
  const symbol = { USD: "$", EUR: "€", GBP: "£", INR: "₹", CAD: "$", AUD: "$" }[rec.currency || "USD"] ?? `${rec.currency} `;
  const n = Number(value);
  return `${symbol}${n.toLocaleString("en-US", { minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2 })}`;
}

function priceText(rec, o) {
  if (list(o.variants).length) return list(o.variants).map((v) => `${money(rec, v.price)} for ${v.label}`).join(", ");
  switch (o.price_type) {
    case "quote_only":
      return "a price quoted after the details are given";
    case "range":
      return `${money(rec, o.price)} to ${money(rec, o.price_high)}`;
    case "from":
      return `from ${money(rec, o.price)}`;
    default:
      return o.price === null || o.price === undefined ? "a price the owner hasn't stated" : money(rec, o.price);
  }
}

function confirmed(item) {
  const from = item.source === "crawl" ? "From the business's website" : item.source === "connector" ? "From the business's connected accounts" : "From the owner";
  return item.confirmed_on ? ` (${from}, confirmed ${item.confirmed_on})` : "";
}

function offeringLine(rec, o, base) {
  const name = rec.business?.name || "this business";
  const parts = [`[${o.name}](${base}/services/${o.id}) at ${name} costs ${priceText(rec, o)}.`];
  if (o.duration) parts.push(`Time on site: ${String(o.duration).replace(/\.+$/, "")}.`);
  if (o.description) parts.push(o.description);
  if (list(o.aliases).length) parts.push(`Customers also call it ${list(o.aliases).join(", ")}.`);
  if (o.notes) parts.push(o.notes);
  return parts.join(" ") + confirmed(o);
}

function addonLine(rec, a, base) {
  const name = rec.business?.name || "this business";
  const parts = [`[${a.name}](${base}/services/${a.id}) at ${name} is an add-on costing ${priceText(rec, a)}.`];
  if (a.requires) parts.push(`It requires ${a.requires}.`);
  if (a.notes) parts.push(a.notes);
  return parts.join(" ") + confirmed(a);
}

function feeLine(rec, f) {
  const amount = f.percent ? `${f.percent}%` : f.amount === null || f.amount === undefined ? "amount varies" : money(rec, f.amount);
  const when = String(f.applies_when || "").replace(/\.+$/, "");
  return `${f.label}: ${amount}.${when ? ` Applies: ${when}.` : ""}` + confirmed(f);
}

function sections(rec, base, day) {
  const name = rec.business?.name || "This business";
  const out = [];
  const add = (id, title, lines) => lines.length && out.push({ id, title, lines });
  const facts = servable(rec.facts, day);
  const allFacts = list(rec.facts);

  const notices = [
    ...facts.filter((f) => f.category === "closure"),
    ...allFacts.filter((f) => f.category === "closure" && upcoming(f, day)),
  ];
  add("notices", "Closures and notices", notices.map((f) => f.statement + confirmed(f)));
  add("offerings", "What's offered", servable(rec.offerings, day).map((o) => offeringLine(rec, o, base)));
  add("addons", "Add-ons", servable(rec.addons, day).map((a) => addonLine(rec, a, base)));

  const totals = servable(rec.fees, day).map((f) => feeLine(rec, f));
  if (rec.tax?.rate !== undefined && rec.tax?.rate !== null) {
    totals.push(`Sales tax at ${name} is ${Math.round(Number(rec.tax.rate) * 100000) / 1000}%${rec.tax.applies_to ? `, applied to ${rec.tax.applies_to}` : ""}.`);
  }
  add("fees", "Fees and tax", totals);

  const zones = servable(rec.zones, day).map((z) => {
    const zips = list(z.zips).join(", ");
    const fee = z.fee ? `a ${money(rec, z.fee)} travel fee` : z.fee === 0 ? "no travel fee" : "a travel fee the owner hasn't stated";
    return `${z.label}${zips ? ` (ZIP ${zips})` : ""}: ${fee}.` + confirmed(z);
  });
  add("area", CATEGORY_TITLES.service_area, [...zones, ...facts.filter((f) => f.category === "service_area").map((f) => f.statement + confirmed(f))]);

  for (const [category, title] of Object.entries(CATEGORY_TITLES)) {
    if (category === "service_area" || category === "other") continue;
    add(category, title, facts.filter((f) => f.category === category).map((f) => f.statement + confirmed(f)));
  }
  const known = new Set([...Object.keys(CATEGORY_TITLES), "closure"]);
  add("other", CATEGORY_TITLES.other, facts.filter((f) => !known.has(f.category) || f.category === "other").map((f) => f.statement + confirmed(f)));
  add("not-offered", "Not offered", servable(rec.not_offered, day).map((n) => n.statement + confirmed(n)));
  add("unknown", "Not stated by the owner yet", list(rec.unknowns).map((u) => u.statement || u));

  const b = rec.business || {};
  const contact = [b.phone && `Phone: ${b.phone}.`, b.email && `Email: ${b.email}.`, b.address && `Address: ${b.address}.`, b.website && `Website: ${b.website}.`].filter(Boolean);
  add("contact", "Contact", contact);
  add("addresses", "Addresses on this site", [
    `Work out a total, with no personal details: [${base}/quote](${base}/quote). It also works as a plain link, such as ${base}/quote?service=SERVICE&variant=SIZE&addon=ADDON&zip=ZIP&when=YYYY-MM-DD. Add format=json for JSON.`,
    `Send a request, which asks for contact details: [${base}/request](${base}/request).`,
    `Ask the owner a question this page doesn't answer: [${base}/ask](${base}/ask).`,
    `This page as markdown: [${base}/index.md](${base}/index.md).`,
  ]);
  return out;
}

function inlineHtml(text) {
  return esc(text).replace(/\[([^\]]+)\]\(((?:https?:\/\/|\/)[^)\s]+)\)/g, '<a href="$2">$1</a>');
}

const renderHtmlSections = (secs) =>
  secs.map((s) => `<section id="${esc(s.id)}"><h2>${esc(s.title)}</h2><ul>${s.lines.map((l) => `<li>${inlineHtml(l)}</li>`).join("")}</ul></section>`).join("");
const renderMdSections = (secs) => secs.map((s) => `## ${s.title}\n\n${s.lines.map((l) => `- ${l}`).join("\n")}`).join("\n\n");

function shell(title, body, base, biz, status = 200, noindex = true, mdPath = null) {
  const alt = mdPath ? `<link rel="alternate" type="text/markdown" href="${esc(mdPath)}">` : "";
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(title)}</title>${alt}
<style>body{font:16px/1.6 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem;color:#1c1c1a}h1{font-size:1.6rem;font-weight:600}h2{font-size:1.1rem;font-weight:600;margin-top:2rem}li{margin:.4rem 0}label{display:block;margin:.7rem 0 .2rem}input,select,textarea{width:100%;padding:.45rem;font:inherit;box-sizing:border-box}input[type=checkbox]{width:auto}button{margin-top:1rem;padding:.5rem 1rem;font:inherit}.answer{font-size:1.1rem;font-weight:600}.err{color:#a32d2d}nav a{margin-right:1rem}</style></head><body>
<nav><a href="${esc(base)}">${esc(biz)}</a><a href="${esc(base)}/quote">Quote</a><a href="${esc(base)}/request">Request</a><a href="${esc(base)}/ask">Ask</a></nav>${body}</body></html>`;
  return new Response(html, { status, headers: { "content-type": "text/html; charset=utf-8", ...(noindex ? { "x-robots-tag": "noindex" } : {}) } });
}

function markdown(text, noindex = true) {
  return new Response(text, { headers: { "content-type": "text/markdown; charset=utf-8", ...(noindex ? { "x-robots-tag": "noindex" } : {}) } });
}

// ------------------------------------------------------------ quoting

function matchIn(items, text) {
  const wanted = norm(text);
  if (!wanted) return null;
  const terms = [];
  for (const item of items) {
    for (const t of [item.id, item.name, item.label, ...list(item.aliases)]) if (t) terms.push([norm(t), item]);
  }
  const exact = terms.find(([t]) => t === wanted);
  if (exact) return exact[1];
  terms.sort((a, b) => b[0].length - a[0].length);
  const hit = terms.find(([t]) => t.length > 2 && (wanted.includes(t) || t.includes(wanted)));
  return hit ? hit[1] : null;
}

function parseWhen(text, day) {
  const value = norm(text);
  if (!value) return null;
  if (value === "today") return day;
  if (value === "tomorrow") return new Date(Date.parse(`${day}T12:00:00Z`) + 86400000).toISOString().slice(0, 10);
  const match = String(text).match(/\d{4}-\d{2}-\d{2}/);
  return match ? match[0] : null;
}

const weekdayOf = (iso) => new Date(`${iso}T12:00:00Z`).toLocaleDateString("en-US", { weekday: "long", timeZone: "UTC" });
const round2 = (n) => Math.round(n * 100) / 100;

function unitPrice(item, variant) {
  if (variant) return { low: Number(variant.price), high: Number(variant.price) };
  if (item.price_type === "range") return { low: Number(item.price), high: Number(item.price_high) };
  if (item.price === null || item.price === undefined) return null;
  return { low: Number(item.price), high: Number(item.price) };
}

function evaluate(rec, job, day) {
  const r = { status: "ok", lines: [], subtotal: null, tax: null, total: null, still_needed: [], notes: [], dead_end: null };
  const offerings = servable(rec.offerings, day);
  const addons = servable(rec.addons, day);
  const fees = servable(rec.fees, day);
  const zones = servable(rec.zones, day);
  const stop = (status, note) => {
    r.status = status;
    r.dead_end = status;
    r.reason = note;
    r.notes.unshift(note);
    return r;
  };

  // A listed service, add-on or fee is never refused, so only unlisted words are checked.
  const unlisted = [
    ...(job.service && !matchIn(offerings, job.service) && !matchIn(addons, job.service) ? [job.service] : []),
    ...job.addons.filter((a) => !matchIn(addons, a)),
    ...job.conditions.filter((c) => !matchIn(fees, c)),
  ];
  const words = unlisted.map(norm).filter(Boolean);
  for (const n of servable(rec.not_offered, day)) {
    const terms = [n.name, ...list(n.terms)].map(norm).filter(Boolean);
    if (words.some((w) => terms.some((t) => w.includes(t) || t.includes(w)))) return stop("not_offered", n.statement);
  }

  const when = parseWhen(job.when, day);
  if (when) {
    // Only a dated closure rules out a date. "Closed Sundays" has no dates, and closed_weekdays covers it.
    const closure = list(rec.facts).find((f) => f.category === "closure" && (f.valid_from || f.valid_to) && inWindow(f, when));
    if (closure) return stop("closed", closure.statement);
    const closedDays = list(rec.business?.closed_weekdays).map(norm);
    if (closedDays.includes(norm(weekdayOf(when)))) return stop("closed", `${rec.business?.name} is closed on ${weekdayOf(when)}s.`);
  }

  const offering = job.service ? matchIn(offerings, job.service) : null;
  if (job.service && !offering) {
    const addonAsService = matchIn(addons, job.service);
    if (addonAsService) job.addons.push(job.service);
    else return stop("unknown_service", `"${job.service}" isn't listed. The offerings are: ${offerings.map((o) => o.name).join(", ")}. A question for the owner can go through /ask.`);
  }
  if (!job.service) r.still_needed.push("service");

  let variant = null;
  if (offering && list(offering.variants).length) {
    variant = matchIn(offering.variants, job.variant);
    if (!variant) r.still_needed.push(`variant: one of ${offering.variants.map((v) => v.label).join(", ")}`);
  }
  if (offering?.price_type === "quote_only") {
    r.status = "quote_only";
    r.notes.push(`${offering.name} is priced after the details are given, so a request is the next step.`);
  }

  const quantity = Math.max(Number(job.quantity) || 1, 1);
  const items = [];
  const push = (label, price, taxable = true) => price && items.push({ label, low: price.low, high: price.high, taxable });
  if (offering && (variant || !list(offering.variants).length)) {
    const price = unitPrice(offering, variant);
    if (!price && offering.price_type !== "quote_only") r.still_needed.push("a price for this service, which the owner hasn't stated");
    if (price) push(`${offering.name}${variant ? `, ${variant.label}` : ""}${quantity > 1 ? ` x ${quantity}` : ""}`, { low: price.low * quantity, high: price.high * quantity });
  }

  for (const text of job.addons) {
    const addon = matchIn(addons, text);
    if (!addon) {
      r.notes.push(`"${text}" isn't one of the add-ons.`);
      r.dead_end = r.dead_end || "unknown_addon";
      continue;
    }
    if (addon.requires) r.notes.push(`${addon.name} requires ${addon.requires}.`);
    const addonVariant = list(addon.variants).length ? matchIn(addon.variants, job.variant) : null;
    if (list(addon.variants).length && !addonVariant) {
      r.still_needed.push(`variant for ${addon.name}: one of ${addon.variants.map((v) => v.label).join(", ")}`);
      continue;
    }
    const price = unitPrice(addon, addonVariant);
    if (price) push(`${addon.name}${quantity > 1 ? ` x ${quantity}` : ""}`, { low: price.low * quantity, high: price.high * quantity });
  }

  const applied = new Set();
  const applyFee = (fee) => {
    if (applied.has(fee.id)) return;
    applied.add(fee.id);
    if (fee.percent) {
      const low = items.reduce((s, i) => s + i.low, 0) * (Number(fee.percent) / 100);
      const high = items.reduce((s, i) => s + i.high, 0) * (Number(fee.percent) / 100);
      push(fee.label, { low, high }, fee.taxable !== false);
    } else if (fee.amount === null || fee.amount === undefined) r.notes.push(`${fee.label} applies, but its amount varies.`);
    else push(fee.label, { low: Number(fee.amount), high: Number(fee.amount) }, fee.taxable !== false);
  };
  for (const text of job.conditions) {
    const fee = matchIn(fees, text);
    if (fee) applyFee(fee);
    else r.notes.push(`"${text}" isn't a defined condition, so nothing was charged for it.`);
  }
  if (when) for (const fee of fees) if (list(fee.weekdays).map(norm).includes(norm(weekdayOf(when)))) applyFee(fee);
  for (const fee of fees) {
    if (!applied.has(fee.id)) r.notes.push(`May also apply: ${fee.label}${fee.applies_when ? ` (${String(fee.applies_when).replace(/\.+$/, "")})` : ""}. Pass condition=${fee.id} to include it.`);
  }

  if (zones.length) {
    const code = String(job.zip || "").replace(/\D/g, "").slice(0, 5);
    if (!code) r.still_needed.push("zip");
    else {
      let zone = zones.find((z) => list(z.zips).map(String).includes(code));
      if (!zone) {
        // A zone with no ZIP list can't rule a ZIP out, so say what's being assumed instead of refusing.
        const unlisted = zones.filter((z) => !list(z.zips).length);
        if (!unlisted.length) return stop("out_of_area", `ZIP ${code} isn't in the service area.`);
        zone = unlisted[0];
        r.notes.push(`ZIP ${code} isn't on a list, so this assumes it's in ${unlisted.map((z) => z.label).join(" or ")}. The owner can confirm.`);
      }
      if (zone.fee) push(`Travel fee (${zone.label})`, { low: Number(zone.fee), high: Number(zone.fee) }, false);
      else if (zone.fee !== 0) r.notes.push(`The owner hasn't stated the travel fee for ${zone.label}, so this total leaves it out.`);
    }
  }

  r.lines = items.map((i) => ({ label: i.label, amount: i.low === i.high ? round2(i.low) : { low: round2(i.low), high: round2(i.high) } }));
  if (r.still_needed.length && r.status === "ok") r.status = "needs_info";
  if (r.status === "ok" && items.length) {
    const rate = Number(rec.tax?.rate);
    const hasTax = rec.tax?.rate !== null && rec.tax?.rate !== undefined && !Number.isNaN(rate);
    if (!hasTax) r.notes.push("The owner hasn't stated whether tax applies, so this total leaves it out.");
    const sum = (key, taxableOnly) => items.filter((i) => !taxableOnly || i.taxable).reduce((s, i) => s + i[key], 0);
    const low = round2(sum("low"));
    const high = round2(sum("high"));
    const taxLow = hasTax ? round2(sum("low", true) * rate) : 0;
    const taxHigh = hasTax ? round2(sum("high", true) * rate) : 0;
    r.subtotal = low === high ? low : { low, high };
    r.tax = taxLow === taxHigh ? taxLow : { low: taxLow, high: taxHigh };
    r.total = low === high ? round2(low + taxLow) : { low: round2(low + taxLow), high: round2(high + taxHigh) };
    const budget = Number(job.budget);
    if (budget && typeof r.total === "number") r.notes.push(r.total <= budget ? `This fits a budget of ${money(rec, budget)}.` : `This is over a budget of ${money(rec, budget)} by ${money(rec, round2(r.total - budget))}.`);
  }
  return r;
}

function headline(rec, o) {
  if (o.status === "ok" && o.total !== null) {
    const total = typeof o.total === "number" ? money(rec, o.total) : `${money(rec, o.total.low)} to ${money(rec, o.total.high)}`;
    return `The total comes to ${total}, including tax and fees that apply.`;
  }
  if (o.status === "needs_info") return `A total needs more details: ${o.still_needed.join("; ")}.`;
  if (o.status === "quote_only") return "This is priced after the details are given.";
  return o.reason || o.notes[0] || "This can't be priced as entered.";
}

function outcomeHtml(rec, o) {
  const rows = o.lines.map((l) => `<li>${esc(l.label)}: ${typeof l.amount === "number" ? esc(money(rec, l.amount)) : `${esc(money(rec, l.amount.low))} to ${esc(money(rec, l.amount.high))}`}</li>`).join("");
  const tax = o.tax !== null && o.status === "ok" ? `<li>Tax: ${typeof o.tax === "number" ? esc(money(rec, o.tax)) : `${esc(money(rec, o.tax.low))} to ${esc(money(rec, o.tax.high))}`}</li>` : "";
  const notes = o.notes.length ? `<h2>Notes</h2><ul>${o.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>` : "";
  return `<p class="answer">${esc(headline(rec, o))}</p>${rows || tax ? `<ul>${rows}${tax}</ul>` : ""}${notes}`;
}

// ------------------------------------------------------------ forms

function readJob(p) {
  const get = (...keys) => keys.map((k) => p.get(k)).find((v) => v) || "";
  return {
    service: get("service", "offering"),
    variant: get("variant", "size"),
    addons: [...p.getAll("addon"), ...p.getAll("addons")].flatMap((v) => v.split(",")).map((v) => v.trim()).filter(Boolean),
    zip: get("zip", "zip_code"),
    conditions: [...p.getAll("condition"), ...p.getAll("conditions"), ...p.getAll("fee")].flatMap((v) => v.split(",")).map((v) => v.trim()).filter(Boolean),
    when: get("when", "date"),
    quantity: get("quantity"),
    budget: get("budget"),
  };
}

function quoteForm(rec, base, job, day) {
  const options = servable(rec.offerings, day).map((o) => `<option value="${esc(o.id)}"${matchIn([o], job.service) ? " selected" : ""}>${esc(o.name)}</option>`).join("");
  const addons = servable(rec.addons, day).map((a) => `<label><input type="checkbox" name="addon" value="${esc(a.id)}"${job.addons.includes(a.id) ? " checked" : ""}> ${esc(a.name)}</label>`).join("");
  const fees = servable(rec.fees, day).map((f) => `<label><input type="checkbox" name="condition" value="${esc(f.id)}"${job.conditions.includes(f.id) ? " checked" : ""}> ${esc(f.label)}</label>`).join("");
  return `<form method="get" action="${esc(base)}/quote"><label for="service">Service</label><select id="service" name="service"><option value="">Choose one</option>${options}</select>
<label for="variant">Size or type, if the service has them</label><input id="variant" name="variant" value="${esc(job.variant)}">
${addons && `<h2>Add-ons</h2>${addons}`}${fees && `<h2>Conditions</h2>${fees}`}
<label for="zip">ZIP code</label><input id="zip" name="zip" value="${esc(job.zip)}"><label for="when">Date (YYYY-MM-DD)</label><input id="when" name="when" value="${esc(job.when)}">
<label for="budget">Budget, if any</label><input id="budget" name="budget" value="${esc(job.budget)}"><button type="submit">Work out the total</button></form>`;
}

function requestForm(base, job, p, errors = []) {
  const val = (k) => esc(p.get(k) || "");
  const hidden = job.addons.map((a) => `<input type="hidden" name="addon" value="${esc(a)}">`).join("") + job.conditions.map((c) => `<input type="hidden" name="condition" value="${esc(c)}">`).join("");
  return `${errors.map((e) => `<p class="err">${esc(e)}</p>`).join("")}<form method="post" action="${esc(base)}/request">${hidden}
<label for="service">Service</label><input id="service" name="service" value="${esc(job.service)}"><label for="variant">Size or type</label><input id="variant" name="variant" value="${esc(job.variant)}">
<label for="zip">ZIP code</label><input id="zip" name="zip" value="${esc(job.zip)}"><label for="when">Preferred date</label><input id="when" name="when" value="${esc(job.when)}">
<label for="name">Name</label><input id="name" name="name" value="${val("name")}"><label for="email">Email</label><input id="email" name="email" value="${val("email")}"><label for="phone">Phone</label><input id="phone" name="phone" value="${val("phone")}">
<label for="submitted_by">Who's submitting</label><select id="submitted_by" name="submitted_by"><option value="customer">The customer</option><option value="agent"${p.get("submitted_by") === "agent" ? " selected" : ""}>An agent acting for the customer</option></select>
<label for="agent_name">Agent name, if any</label><input id="agent_name" name="agent_name" value="${val("agent_name")}"><label for="notes">Notes</label><textarea id="notes" name="notes" rows="3">${val("notes")}</textarea>
<button type="submit">Send the request</button></form>`;
}

async function readParams(request, url) {
  const params = new URLSearchParams(url.search);
  if (request.method === "POST") {
    const type = request.headers.get("content-type") || "";
    if (type.includes("json")) {
      const body = await request.json().catch(() => ({}));
      for (const [k, v] of Object.entries(body)) for (const one of Array.isArray(v) ? v : [v]) params.append(k, String(one));
    } else {
      const form = await request.formData().catch(() => null);
      if (form) for (const [k, v] of form.entries()) params.append(k, String(v));
    }
  }
  return params;
}

// ------------------------------------------------------------ storage

// The owner app's own reads and quote console aren't agent activity.
const quiet = new WeakSet();

function log(env, ctx, slug, event, payload) {
  if (quiet.has(ctx)) return;
  ctx.waitUntil(env.DB.prepare("INSERT INTO event (slug, ts, event, payload) VALUES (?, ?, ?, ?)").bind(slug, now(), event, JSON.stringify(payload)).run());
}

async function loadBusiness(env, slug) {
  const row = await env.DB.prepare("SELECT * FROM business WHERE slug = ?").bind(slug).first();
  return row ? { ...row, record: JSON.parse(row.record) } : null;
}

const wantsMarkdown = (request) => (request.headers.get("accept") || "").toLowerCase().includes("text/markdown");

// ------------------------------------------------------------ public routes

async function publicRoute(request, env, ctx, url, slug, rest) {
  if ((request.headers.get("user-agent") || "").startsWith("legible-")) quiet.add(ctx);
  const biz = await loadBusiness(env, slug);
  if (!biz) return new Response("No business is published at this address.", { status: 404 });
  const rec = biz.record;
  const name = rec.business?.name || slug;
  const day = todayIn(rec.business?.timezone);
  const origin = url.origin;
  const base = `/b/${slug}`;
  const abs = `${origin}${base}`;
  const noindex = biz.noindex !== 0;
  const page = (title, body, status = 200, md = null) => shell(title, body, base, name, status, noindex, md);
  const asJson = (url.searchParams.get("format") || "").toLowerCase() === "json";

  const h = request.headers;
  log(env, ctx, slug, "page_hit", {
    path: rest || "/",
    method: request.method,
    user_agent: h.get("user-agent") || "",
    referer: h.get("referer") || "",
    accept: h.get("accept") || "",
    signature: h.get("signature-agent") || h.get("signature-input") || "",
    country: request.cf?.country || "",
  });

  if (rest === "" || rest === "/" || rest === "/index.md") {
    const secs = sections(rec, abs, day);
    const stamp = `Information confirmed by the owner. Last updated ${rec.updated_at || biz.updated_at}.`;
    const intro = rec.business?.summary ? `${rec.business.summary}` : "";
    if (rest === "/index.md" || wantsMarkdown(request)) return markdown(`# ${name}\n\n${intro}\n\n${renderMdSections(secs)}\n\n${stamp}\n`, noindex);
    return page(`${name}: prices, availability and booking requests`, `<h1>${esc(name)}</h1><p>${esc(intro)}</p>${renderHtmlSections(sections(rec, base, day))}<p>${esc(stamp)}</p>`, 200, `${base}/index.md`);
  }

  if (rest === "/services" || rest.startsWith("/services/")) {
    const id = rest.replace("/services", "").replace(/^\//, "").replace(/\.md$/, "");
    const asMd = rest.endsWith(".md") || wantsMarkdown(request);
    const all = [...servable(rec.offerings, day), ...servable(rec.addons, day)];
    if (!id) {
      const lines = all.map((o) => `[${o.name}](${base}/services/${o.id}): ${priceText(rec, o)}.`);
      if (asMd) return markdown(`# Offerings at ${name}\n\n${lines.map((l) => `- ${l}`).join("\n")}\n`, noindex);
      return page(`Offerings at ${name}`, `<h1>Offerings at ${esc(name)}</h1><ul>${lines.map((l) => `<li>${inlineHtml(l)}</li>`).join("")}</ul>`);
    }
    const item = all.find((o) => o.id === id);
    if (!item) return page("Not found", `<h1>Not an offering on this site</h1><p><a href="${esc(base)}/services">See the offerings</a></p>`, 404);
    const isAddon = list(rec.addons).some((a) => a.id === id);
    const lines = [isAddon ? addonLine(rec, item, abs) : offeringLine(rec, item, abs)];
    if (asMd) return markdown(`# ${item.name} at ${name}\n\n${lines[0]}\n`, noindex);
    return page(`${item.name} at ${name}`, `<h1>${esc(item.name)} at ${esc(name)}</h1><p>${inlineHtml(isAddon ? addonLine(rec, item, base) : offeringLine(rec, item, base))}</p><p><a href="${esc(base)}/quote?service=${encodeURIComponent(id)}">Work out a total</a></p>`, 200, `${base}/services/${id}.md`);
  }

  if (rest === "/quote") {
    const params = await readParams(request, url);
    const job = readJob(params);
    if (!job.service && !job.addons.length && !job.zip) {
      if (asJson) return json({ status: "needs_info", still_needed: ["service"], services: servable(rec.offerings, day).map((o) => ({ id: o.id, name: o.name })) });
      return page(`Quote: ${name}`, `<h1>Work out a total for ${esc(name)}</h1><p>This takes a job's details and returns a total or range. It takes no personal details, and it also works as a plain link.</p>${quoteForm(rec, base, job, day)}`);
    }
    const outcome = evaluate(rec, job, day);
    const quoteId = newId("quote");
    log(env, ctx, slug, "quote", { quote_id: quoteId, inputs: job, status: outcome.status, total: outcome.total, still_needed: outcome.still_needed });
    if (outcome.dead_end) log(env, ctx, slug, "dead_end", { source: "quote", reason: outcome.dead_end, quote_id: quoteId, inputs: job, notes: outcome.notes });
    const q = new URLSearchParams({ service: job.service, variant: job.variant, zip: job.zip, when: job.when, quote_id: quoteId });
    for (const a of job.addons) q.append("addon", a);
    for (const c of job.conditions) q.append("condition", c);
    const requestUrl = DEAD.has(outcome.status) ? null : `${base}/request?${q}`;
    if (asJson) {
      const { dead_end, ...rest_ } = outcome;
      return json({ quote_id: quoteId, business: name, inputs: job, summary: headline(rec, outcome), ...rest_, request_url: requestUrl ? `${origin}${requestUrl}` : null, ask_url: `${abs}/ask` });
    }
    const next = requestUrl
      ? `<p><a href="${esc(requestUrl)}">Open the request form with these details</a>. Contact details are asked for only there.</p>`
      : `<p>This can't go ahead as a request as entered. A question for the owner can go through <a href="${esc(base)}/ask">/ask</a>.</p>`;
    return page(`Quote ${quoteId}: ${name}`, `<h1>Quote from ${esc(name)}</h1>${outcomeHtml(rec, outcome)}${next}<h2>Change the details</h2>${quoteForm(rec, base, job, day)}`);
  }

  if (rest === "/request") {
    const params = await readParams(request, url);
    const job = readJob(params);
    if (request.method !== "POST") return page(`Request: ${name}`, `<h1>Send a request to ${esc(name)}</h1>${requestForm(base, job, params)}`);
    const wantsJson = asJson || (params.get("format") || "").toLowerCase() === "json";
    const errors = [];
    if (!params.get("name")) errors.push("A name is needed.");
    if (!params.get("email") && !params.get("phone")) errors.push("An email address or phone number is needed, because the owner replies by text or email.");
    if (errors.length) {
      log(env, ctx, slug, "request", { id: null, inputs: job, outcome: "rejected_missing_details" });
      return wantsJson ? json({ outcome: "rejected_missing_details", errors }, 422) : page(`Request: ${name}`, `<h1>Send a request to ${esc(name)}</h1>${requestForm(base, job, params, errors)}`, 422);
    }
    const outcome = evaluate(rec, job, day);
    if (DEAD.has(outcome.status)) {
      log(env, ctx, slug, "request", { id: null, inputs: job, outcome: `refused_${outcome.status}` });
      log(env, ctx, slug, "dead_end", { source: "request", reason: outcome.status, inputs: job, notes: outcome.notes });
      return wantsJson ? json({ outcome: `refused_${outcome.status}`, summary: headline(rec, outcome), notes: outcome.notes }, 422) : page(`Request not sent: ${name}`, `<h1>This request wasn't sent</h1>${outcomeHtml(rec, outcome)}${requestForm(base, job, params)}`, 422);
    }
    const id = newId("req");
    const data = { inputs: job, name: params.get("name"), email: params.get("email") || "", phone: params.get("phone") || "", submitted_by: params.get("submitted_by") || "customer", agent_name: params.get("agent_name") || "", notes: params.get("notes") || "", quote_id: params.get("quote_id") || "", lines: outcome.lines, tax: outcome.tax, total: outcome.total, still_needed: outcome.still_needed };
    await env.DB.prepare("INSERT INTO item (id, slug, kind, created_at, data) VALUES (?, ?, 'request', ?, ?)").bind(id, slug, now(), JSON.stringify(data)).run();
    log(env, ctx, slug, "request", { id, inputs: job, outcome: "received", submitted_by: data.submitted_by, agent_name: data.agent_name, total: outcome.total });
    const status = `${abs}/r/${id}`;
    if (wantsJson) return json({ id, outcome: "received", status_url: status, slot_held: false, summary: headline(rec, outcome), total: outcome.total });
    return page(`Request received: ${name}`, `<h1>Request received by ${esc(name)}</h1><p class="answer">Request ${esc(id)} was received, and no slot is held yet.</p><p>Status page: <a href="${esc(`${base}/r/${id}`)}">${esc(status)}</a></p>${outcomeHtml(rec, outcome)}`);
  }

  if (rest === "/ask") {
    const params = await readParams(request, url);
    const text = params.get("question") || params.get("q") || "";
    const form = `<form method="post" action="${esc(base)}/ask"><label for="question">Question</label><textarea id="question" name="question" rows="3">${esc(text)}</textarea><button type="submit">Pass it to the owner</button></form>`;
    if (request.method !== "POST") return page(`Ask: ${name}`, `<h1>Ask ${esc(name)} a question</h1><p>This passes a question to the owner and returns a status page. It needs no contact details.</p>${form}`);
    if (!text) return asJson ? json({ outcome: "rejected_empty", errors: ["A question is needed."] }, 422) : page(`Ask: ${name}`, `<h1>Ask ${esc(name)} a question</h1><p class="err">A question is needed.</p>${form}`, 422);
    const id = newId("ask");
    await env.DB.prepare("INSERT INTO item (id, slug, kind, created_at, data) VALUES (?, ?, 'question', ?, ?)").bind(id, slug, now(), JSON.stringify({ text })).run();
    log(env, ctx, slug, "question", { id, text });
    const status = `${abs}/r/${id}`;
    if (asJson || (params.get("format") || "").toLowerCase() === "json") return json({ id, outcome: "passed_to_owner", status_url: status });
    return page(`Question received: ${name}`, `<h1>Question passed to the owner</h1><p class="answer">Question ${esc(id)} was passed to the owner.</p><p>Status page: <a href="${esc(`${base}/r/${id}`)}">${esc(status)}</a></p>`);
  }

  if (rest.startsWith("/r/")) {
    const id = rest.slice(3);
    const row = await env.DB.prepare("SELECT * FROM item WHERE id = ? AND slug = ?").bind(id, slug).first();
    if (!row) return page("Not found", "<h1>No request or question has this ID</h1>", 404);
    const data = JSON.parse(row.data);
    const label = row.kind === "request" ? "Request" : "Question";
    const subject = row.kind === "request" ? `${data.inputs?.service || "A job"}${data.inputs?.when ? ` on ${data.inputs.when}` : ""}` : data.text;
    const replied = row.reply ? `<h2>The owner's reply</h2><p>${esc(row.reply)}</p>` : "<p>The owner hasn't replied yet.</p>";
    return page(`Status ${id}: ${name}`, `<h1>${label} status</h1><p class="answer">Status: ${esc(row.status)}</p><p>${esc(subject)}</p>${replied}<p>Received ${esc(row.created_at)}.</p>`);
  }

  if (rest === "/sitemap.xml") {
    const paths = ["", "/index.md", "/services", ...[...servable(rec.offerings, day), ...servable(rec.addons, day)].map((o) => `/services/${o.id}`), "/quote", "/request", "/ask"];
    const entries = paths.map((p) => `<url><loc>${esc(`${abs}${p}`)}</loc></url>`).join("");
    return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${entries}</urlset>`, { headers: { "content-type": "application/xml" } });
  }

  return page("Not found", "<h1>Nothing here</h1>", 404);
}

// ------------------------------------------------------------ admin routes, for the Legible app

async function adminRoute(request, env, url, path) {
  const auth = request.headers.get("authorization") || "";
  if (!env.ADMIN_TOKEN || auth !== `Bearer ${env.ADMIN_TOKEN}`) return json({ error: "unauthorized" }, 401);
  const parts = path.split("/").filter(Boolean); // admin, businesses, slug, ...
  if (parts[1] === "businesses" && parts[2]) {
    const slug = parts[2];
    if (parts.length === 3 && request.method === "PUT") {
      const body = await request.json();
      const old = await env.DB.prepare("SELECT version FROM business WHERE slug = ?").bind(slug).first();
      const version = (old?.version || 0) + 1;
      await env.DB.prepare("INSERT OR REPLACE INTO business (slug, record, version, noindex, updated_at) VALUES (?, ?, ?, ?, ?)").bind(slug, JSON.stringify(body.record), version, body.noindex === false ? 0 : 1, now()).run();
      return json({ slug, version, url: `${url.origin}/b/${slug}` });
    }
    if (parts.length === 3 && request.method === "DELETE") {
      await env.DB.prepare("DELETE FROM business WHERE slug = ?").bind(slug).run();
      return json({ slug, deleted: true });
    }
    if (parts[3] === "events") {
      const after = Number(url.searchParams.get("after") || 0);
      const limit = Math.min(Number(url.searchParams.get("limit") || 500), 2000);
      const { results } = await env.DB.prepare("SELECT * FROM event WHERE slug = ? AND id > ? ORDER BY id LIMIT ?").bind(slug, after, limit).all();
      return json({ events: results.map((e) => ({ ...e, payload: JSON.parse(e.payload) })) });
    }
    if (parts[3] === "items") {
      const { results } = await env.DB.prepare("SELECT * FROM item WHERE slug = ? ORDER BY created_at DESC LIMIT 200").bind(slug).all();
      return json({ items: results.map((i) => ({ ...i, data: JSON.parse(i.data) })) });
    }
  }
  if (parts[1] === "items" && parts[2] && parts[3] === "reply" && request.method === "POST") {
    const body = await request.json();
    await env.DB.prepare("UPDATE item SET status = ?, reply = ?, replied_at = ? WHERE id = ?").bind(body.status || "replied", body.message || "", now(), parts[2]).run();
    return json({ id: parts[2], status: body.status || "replied" });
  }
  return json({ error: "not found" }, 404);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    if (path === "/admin" || path.startsWith("/admin/")) return adminRoute(request, env, url, path);
    if (path === "/robots.txt") return new Response("User-agent: *\nAllow: /\n", { headers: { "content-type": "text/plain" } });
    const match = path.match(/^\/b\/([a-z0-9][a-z0-9-]*)(\/.*)?$/);
    if (match) {
      const rest = (match[2] || "").replace(/\/$/, "");
      return publicRoute(request, env, ctx, url, match[1], rest);
    }
    return new Response("Legible", { headers: { "content-type": "text/plain", "x-robots-tag": "noindex" } });
  },
};
