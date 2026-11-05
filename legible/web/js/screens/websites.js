// Websites: add a site, watch Legible read it, then the desk with the link and the score.
import { $, actions, api, app, copyButton, domain, esc, fail, forms, icon, isBusy, morph, plural, pollMs, post, roll, route, screens, seatsFromScore, startPoll, state, toast } from "../core.js";
import { liveTrace } from "./live.js";

const ACCOUNTS = [
  ["googlecalendar", "vendor/google-calendar.svg", "Google Calendar", "Keeps closures and blocked dates current"],
  ["googlesheets", "vendor/google-sheets.svg", "Google Sheets", "Keep your price list in a sheet"],
];
const STAGES = [["crawling", "Read your website"], ["extracting", "Build your fact sheet"], ["interviewing", "Work out what's missing"], ["checking", "Test it with customer agents"]];

function startView() {
  return `<section class="start" id="start">
    <form class="start-form" data-form="addSite">
      <h1 class="t-hero focus-in">Which website should agents read?</h1>
      <p>Legible reads your site, tests it with customer agents and asks you what's missing. Nothing goes public until you confirm it.</p>
      <div class="field field--xl"><input name="url" type="url" required aria-label="Your website address" placeholder="https://yourbusiness.com" autofocus><button class="send" aria-label="Read this website">${icon("arrow-up", "i--lg")}</button></div>
      <label class="switch"><input type="checkbox" name="check" checked><span class="track"></span>Also test it with customer agents, about 5 minutes</label>
    </form>
  </section>`;
}

// ---- Legible at work

function stagesHtml(trace) {
  const at = STAGES.findIndex(([id]) => id === trace.stage);
  return `<ol class="stages">${STAGES.map(([id, label], i) => {
    const done = trace.stage === "ready" || (at >= 0 && i < at);
    const now = i === at || (trace.stage === "queued" && i === 0);
    return `<li class="stage ${done ? "done" : ""} ${now ? "now" : ""}"><i></i><span>${label}</span></li>`;
  }).join("")}</ol>`;
}

function pageCard(page, live) {
  const path = page.url.replace(/^https?:\/\/[^/]+/, "") || "/";
  const lines = Math.min(3 + Math.round((page.chars || 0) / 900), 9);
  const widths = [92, 78, 88, 64, 95, 72, 84, 58, 90];
  const bars = Array.from({ length: lines }, (_, i) => `<span class="bar" style="--w:${widths[i % 9]}%"></span>`);
  const images = Array.from({ length: page.images || 0 }, () => `<span class="img ${live ? "" : "img--read"}">${icon("image")}</span>`);
  return `<article class="page-card ${live ? "is-reading" : ""}" id="pg-${esc(path.replace(/\W/g, "_"))}">
    <header><span class="ellipsis">${esc(path)}</span><span>${esc(page.title || "")}</span></header>
    ${images.join("")}${bars.join("")}
    <footer>${Number(page.chars || 0).toLocaleString()} characters${page.images ? `, ${plural(page.images, "image")}` : ""}</footer></article>`;
}

function factFeed(trace) {
  const facts = trace.facts || { count: 0, lines: [] };
  const rows = facts.lines.map((line, i) => `<li class="focus-in" style="--i:${i}" id="fl-${i}"><span>${esc(line.text)}</span>${line.value ? `<span>${esc(line.value)}</span>` : ""}</li>`).join("");
  const ghosts = [84, 68, 92, 58, 76, 88].map((w) => `<div class="ghost-line" style="--w:${w}%"></div>`).join("");
  const asking = trace.stage === "interviewing" || trace.questions?.length ? trace.questions.slice(0, 3).map((q, i) => `<li class="focus-in" style="--i:${i}" id="ak-${i}"><span class="dot dot--pen"></span><span>${esc(q)}</span></li>`).join("") : "";
  return `<aside class="fact-feed">
    <div class="fact-feed-head"><span class="eyebrow">Facts found on your website</span><b>${roll(facts.count)}</b></div>
    ${rows ? `<ul>${rows}</ul>` : `<div>${ghosts}</div>`}
    ${asking ? `<div class="stack" style="gap:8px;margin-top:6px"><span class="eyebrow">Not on your website</span><ul class="asking">${asking}</ul></div>` : ""}
  </aside>`;
}

function theatreBody(trace) {
  if (trace.stage === "checking" || trace.simulation) return `<div class="stack" style="gap:14px"><p class="soft">Each one is a real agent, asking what a real customer asks. They only have what's on your website.</p>${liveTrace(trace.simulation)}</div>`;
  const pages = trace.pages || [];
  const reading = trace.stage === "crawling" || trace.stage === "queued";
  const cards = pages.map((p, i) => pageCard(p, reading && i === pages.length - 1)).join("");
  return `<div class="reading"><div class="page-stack">${cards || `<article class="page-card is-reading" id="pg-wait"><header><span>Opening your website</span></header><span class="bar"></span><span class="bar" style="--w:70%"></span><span class="bar" style="--w:84%"></span></article>`}</div>${factFeed(trace)}</div>`;
}

function theatreHtml(trace) {
  return `<header class="theatre-head">
      <span class="eyebrow">You can leave this page while Legible works</span>
      <h1 class="t-1 focus-in">Getting to know ${esc(trace.name)}</h1>
      <p class="soft" id="stage-note">${esc(trace.stage_note || "Starting")}</p>
      ${stagesHtml(trace)}
    </header>
    <div class="theatre-body">${theatreBody(trace)}</div>`;
}

async function pollTheatre() {
  if (route() !== "websites") return;
  try {
    const trace = await api(`/websites/${state.site.id}/trace`);
    if (["ready", "failed"].includes(trace.stage)) return app.render();
    const el = $("#theatre");
    if (el) morph(el, theatreHtml(trace));
    app.refreshRail();
  } catch { /* The next poll tries again. */ }
  startPoll(pollTheatre, pollMs());
}

// ---- The desk

function deskView(site) {
  const checks = site.checks;
  const score = checks.latest;
  const pass = site.live
    ? `<article class="pass agent-surface"><div class="between"><span class="row strong">${icon("link")} Your link</span><span class="badge badge--agent"><span class="dot dot--live"></span>Agents can read it</span></div>
        <div class="pass-link">${esc(domain(site.link))}</div>
        <p class="pass-note">One link for any agent. It reads your facts, works out quotes and sends you booking requests.${site.page_reads ? ` Agents have read it ${plural(site.page_reads, "time")} so far.` : ""}</p>
        <div class="row row--wrap">${copyButton(site.link, "Link", { cls: "btn--on-agent" })}<a class="btn btn--ghost-agent" href="${esc(site.link)}" target="_blank" rel="noopener">${icon("external-link")} Open the page</a></div></article>`
    : `<article class="pass pass--off"><span class="row strong">${icon("lock")} Your link</span>
        <div class="pass-link" aria-hidden="true">${esc(domain(site.link))}</div>
        <p class="pass-note">This comes into focus once you've confirmed your facts. Nothing is public until then.</p>
        ${site.next && !site.next.busy && ["simulations", "resource"].includes(site.next.screen) ? `<div><a class="btn btn--primary" href="#/${site.next.screen}">${esc(site.next.label)}</a></div>` : ""}</article>`;
  const scoreTile = score
    ? `<a class="score-tile" href="#/simulations"><div class="between"><span class="strong">Test customers</span>${checks.count > 1 && checks.first.answered !== score.answered ? `<span class="badge badge--ok">Up from ${checks.first.answered}</span>` : ""}</div>
        <div class="score-big">${roll(score.answered)}<span class="of">of ${score.queries}</span></div>
        ${seatsFromScore(score.answered, score.queries)}
        <p class="small soft">got a real answer from ${score.target === "resource" ? "your Legible page" : "your website"}.</p></a>`
    : `<div class="score-tile"><span class="strong">Test customers</span><p class="small soft" style="margin-top:auto">No check has run yet. A check sends agents at your website to find what they can't answer.</p></div>`;
  const linked = (id) => (site.connections || []).some((c) => c.toolkit === id && c.status === "connected");
  const accounts = ACCOUNTS.map(([id, img, name, help]) => `<div class="account-row"><img src="${img}" alt=""><div class="grow"><div class="strong">${name}</div><div class="small muted">${help}</div></div>${linked(id) ? `<span class="badge badge--ok">${icon("check")} Connected</span>` : `<button class="btn btn--sm" data-do="openConnect">Connect</button>`}</div>`).join("");
  const others = state.sites.length > 1 ? `<div class="site-tabs">${state.sites.map((s) => `<button class="site-tab ${s.id === site.id ? "on" : ""}" data-do="pickSite" data-id="${s.id}"><span class="dot ${s.live ? "dot--live" : ""}"></span>${esc(s.name || s.slug)}</button>`).join("")}</div>` : "";
  return `<div class="scroll"><div class="page">
    <header class="page-head"><div class="grow"><span class="eyebrow">${esc(domain(site.url))}</span><h1 class="t-1" style="margin-top:6px">${esc(site.name || site.slug)}</h1></div><a class="btn" href="#/websites/new">${icon("plus")} Add a website</a></header>
    ${others}
    <div class="desk">${pass}${scoreTile}</div>
    ${site.live ? `<section class="desk-section"><div class="section-head"><div><h2 class="t-2">Put the link on your website</h2><p class="small soft" style="margin-top:3px">Paste this line on your pricing or booking page. Any agent reading that page will see it.</p></div><button class="btn btn--sm" data-do="checkLink">${icon("search-check")} Check it's on your site</button></div>
      <div class="paste-row"><span>${esc(site.link_line)}</span>${copyButton(site.link_line, "Line", { cls: "btn--sm", caption: "Copy" })}</div>
      <div class="paste-row"><span class="mono">${esc(site.link_line_html)}</span>${copyButton(site.link_line_html, "HTML", { cls: "btn--sm", caption: "Copy" })}</div></section>` : ""}
    <section class="desk-section"><div class="section-head"><div><h2 class="t-2">Connected accounts</h2><p class="small soft" style="margin-top:3px">Optional. Legible reads these and asks you before anything changes.</p></div></div>${accounts}</section>
  </div></div>`;
}

screens.websites = {
  async load() {
    const adding = location.hash.includes("/new") || !state.sites.length;
    if (adding) return { adding };
    const site = await api(`/websites/${state.site.id}`);
    return { site, trace: isBusy(site) ? await api(`/websites/${site.id}/trace`) : null };
  },
  view({ adding, site, trace }) {
    if (adding) return startView();
    if (trace) return `<section class="theatre" id="theatre">${theatreHtml(trace)}</section>`;
    if (site.stage === "failed") return `<div class="blank"><div class="blank-inner"><h1 class="t-1">This website couldn't be read</h1><p class="soft">${esc(site.stage_note)}</p><a class="btn btn--primary" href="#/websites/new">Try another address</a></div></div>`;
    return deskView(site);
  },
  after({ trace }) {
    if (trace) startPoll(pollTheatre, pollMs());
  },
};

// ---- Connect popup

const connect = { configured: false, rows: {} };
function renderConnect() {
  const notice = connect.configured ? "" : `<p class="small soft" style="padding:12px 14px;margin:14px 0;border-radius:12px;background:var(--bg)">Connecting accounts is optional, and Legible works without it. To turn it on, add <code class="mono">COMPOSIO_API_KEY</code> to your <code class="mono">.env</code> file and restart Legible.</p>`;
  const rows = ACCOUNTS.map(([id, img, name, help]) => {
    const row = connect.rows[id] || {};
    const isOn = row.step === "done" || (state.site.connections || []).some((c) => c.toolkit === id && c.status === "connected");
    const right = isOn ? `<span class="badge badge--ok">${icon("check")} Connected</span>` : row.step === "waiting" ? `<span class="ring"></span>` : `<button class="btn btn--sm" data-do="startConnect" data-id="${id}" ${connect.configured ? "" : "disabled"}>Connect</button>`;
    const waiting = row.step === "waiting" ? `<p class="small soft">Finish signing in in the new window, then come back here.</p>${id === "googlesheets" ? `<input class="note" style="min-height:0;height:36px" id="sheet-id" placeholder="Paste your spreadsheet's ID">` : ""}<div><button class="btn btn--primary btn--sm" data-do="finishConnect" data-id="${id}">I've connected it</button></div>` : "";
    return `<div class="stack" style="gap:9px;padding:13px 0;border-top:1px solid var(--line)"><div class="row"><img src="${img}" alt="" width="26" height="26"><div class="grow"><div class="strong">${name}</div><div class="small muted">${help}</div></div>${right}</div>${waiting}${row.error ? `<p class="small pen">${esc(row.error)}</p>` : ""}</div>`;
  }).join("");
  $("#overlay").innerHTML = `<div class="modal-back" data-do="closeConnect" data-self="1"><div class="modal" role="dialog" aria-modal="true" aria-label="Connect an account"><div class="between"><h2 class="t-2">Connect an account</h2><button class="btn btn--ghost btn--icon" data-do="closeConnect" aria-label="Close">${icon("x")}</button></div><p class="small soft" style="margin-top:6px">Legible reads what you connect and proposes changes for you to confirm. Connections run through Composio.</p>${notice}<div style="margin-top:14px">${rows}</div></div></div>`;
}

Object.assign(actions, {
  openConnect: async () => {
    const available = await api("/connections/available");
    connect.configured = available.configured;
    connect.rows = {};
    renderConnect();
  },
  closeConnect: () => {
    $("#overlay").innerHTML = "";
    app.render();
  },
  startConnect: async (el) => {
    const id = el.dataset.id;
    connect.rows[id] = { step: "waiting" };
    renderConnect();
    try {
      const result = await post(`/websites/${state.site.id}/connections`, { toolkit: id });
      window.open(result.connect_link, "_blank", "noopener,width=520,height=680");
    } catch (error) {
      connect.rows[id] = { error: error.message };
      renderConnect();
    }
  },
  finishConnect: async (el) => {
    const id = el.dataset.id;
    const sheet = $("#sheet-id")?.value.trim();
    try {
      const result = await post(`/websites/${state.site.id}/connections/${id}/sync`, sheet ? { spreadsheet_id: sheet } : {});
      connect.rows[id] = { step: "done" };
      renderConnect();
      toast(result.proposal ? "Connected. Proposed changes are waiting on your Resource page" : "Connected. Nothing new to change");
    } catch (error) {
      connect.rows[id] = { step: "waiting", error: error.message };
      renderConnect();
    }
  },
  pickSite: (el) => {
    localStorage.setItem("legible.site", el.dataset.id);
    state.selectedSim = state.selectedBooking = null;
    state.agentView = false;
    location.hash = "#/websites";
    app.render();
  },
  checkLink: async () => {
    const result = await post(`/websites/${state.site.id}/check-link`);
    toast(result.found ? "Found it on your website. Agents can reach your page now" : "It's not on your website's home page yet");
    if (result.found) app.render();
  },
});

forms.addSite = async (form) => {
  const site = await post("/websites", { url: form.url.value.trim(), run_check: form.check.checked });
  localStorage.setItem("legible.site", site.id);
  if (location.hash === "#/websites") app.render();
  else location.hash = "#/websites";
};

export { fail };
