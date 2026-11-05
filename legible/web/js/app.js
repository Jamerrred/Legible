// The Legible owner app: plain modules with no build step. Each screen loads its data, returns HTML
// and leaves the moving to morphing and view transitions.
import { $, actions, api, app, esc, fail, forms, icon, isBusy, morph, plural, route, screens, state, stopPoll, withTransition, domain, toast } from "./core.js";
import "./screens/websites.js";
import "./screens/simulations.js";
import "./screens/resource.js";
import "./screens/inbox.js";
import "./screens/bookings.js";

const view = $("#view");
const rail = $("#rail");
const NAV = [["websites", "globe", "Websites"], ["simulations", "flask-conical", "Simulations"], ["resource", "file-text", "Resource"], ["inbox", "inbox", "Inbox"], ["bookings", "calendar-check", "Bookings"]];
const BRAND = "Legible".split("").map((c, i) => `<span style="--i:${i}">${c}</span>`).join("");

async function loadSites() {
  if (!state.config) state.config = await api("/config");
  state.sites = await api("/websites");
  const wanted = localStorage.getItem("legible.site");
  state.site = state.sites.find((s) => s.id === wanted) || state.sites[0] || null;
}

// What each stop on the thread says right now.
function stepsFor(site) {
  if (!site) return { websites: ["Add your website", false, 0], simulations: ["", false, 0], resource: ["", false, 0], inbox: ["", false, 0], bookings: ["", false, 0] };
  const n = site.needs;
  const c = site.checks;
  const busy = isBusy(site);
  const score = c.latest ? `${c.latest.answered} of ${c.latest.queries} got an answer` : "No check yet";
  const facts = site.facts.draft + site.facts.confirmed;
  return {
    websites: [busy ? "Reading your website" : site.live ? "Live" : "Not public yet", false, 0],
    simulations: [c.running ? "Agents are working" : n.missing ? plural(n.missing, "question") + " for you" : score, Boolean(n.missing), n.missing],
    resource: [n.review ? `${plural(site.facts.draft, "fact")} to confirm` : n.proposals ? "A change to confirm" : facts ? plural(facts, "fact") : "Not built yet", Boolean(n.review || n.proposals), 0],
    inbox: [n.agent_questions ? plural(n.agent_questions, "question") + " from agents" : site.page_reads ? plural(site.page_reads, "page read") : "No agents yet", Boolean(n.agent_questions), n.agent_questions],
    bookings: [n.bookings ? `${n.bookings} need${n.bookings === 1 ? "s" : ""} a reply` : "Nothing waiting", Boolean(n.bookings), n.bookings],
  };
}

// How far along the owner's path this site has come, for the ink on the thread.
function progress(site) {
  if (!site || isBusy(site)) return 0;
  if (site.needs.missing) return 1;
  if (!site.live) return 2;
  return site.page_reads ? 4 : 3;
}

function railHtml() {
  const site = state.site;
  const now = route();
  const steps = stepsFor(site);
  const reached = progress(site);
  const next = site?.next;
  const nextCard = !site ? "" : next
    ? `<a class="next-card" href="#/${next.screen}"><span class="eyebrow">Next</span><b>${esc(next.label)}${next.busy ? "" : icon("arrow-right")}</b><small>${esc(next.note)}</small></a>`
    : `<div class="next-card next-card--quiet"><span class="eyebrow">Next</span><b>You're all caught up</b><small>New questions land here when agents get stuck.</small></div>`;
  return `<a class="brand" href="#/websites" aria-label="Legible home"><img class="brand-mark" src="favicon.svg" alt=""><span class="brand-word">${BRAND}</span></a>
    ${site ? `<a class="site-chip" href="#/websites"><span class="dot ${site.live ? "dot--live" : ""}"></span><span class="grow"><b class="ellipsis">${esc(site.name || site.slug)}</b><small class="ellipsis">${esc(domain(site.url))}</small></span></a>` : ""}
    <div class="thread" id="thread" style="--fill:${reached * 54}px"><span class="thread-fill"></span><span class="thread-ind" id="thread-ind"></span>${NAV.map(([id, ic, label], i) => {
      const [line, needs, count] = steps[id];
      return `<a class="step ${now === id ? "on" : ""} ${i < reached ? "done" : ""} ${needs ? "needs" : ""}" href="#/${id}" id="nav-${id}" ${now === id ? 'aria-current="page"' : ""}><span class="step-node">${icon(ic)}</span><span class="step-text"><b>${label}</b>${line ? `<small>${esc(line)}</small>` : ""}</span>${count ? `<span class="count">${count}</span>` : ""}</a>`;
    }).join("")}</div>
    <div class="rail-spacer"></div>${nextCard}
    ${state.config?.demo ? `<p class="demo-note">Demo copy: sample data, sped up. <a href="/demo/reset">Start over</a></p>` : ""}`;
}

function syncIndicator() {
  const on = $(".step.on", rail);
  const thread = $("#thread");
  if (!on || !thread) return;
  thread.style.setProperty("--y", `${on.offsetTop}px`);
  thread.style.setProperty("--h", `${on.offsetHeight}px`);
}
function paintRail() {
  morph(rail, railHtml());
  syncIndicator();
}
app.refreshRail = async () => {
  try {
    await loadSites();
    paintRail();
  } catch { /* The next poll tries again. */ }
};

let token = 0;
let lastRoute = null;
const needSite = () => `<div class="screen"><div class="blank"><div class="blank-inner"><h1 class="t-1">Add a website first</h1><p class="soft">Legible starts by reading your website.</p><a class="btn btn--primary" href="#/websites">${icon("plus")} Add a website</a></div></div></div>`;

app.render = async ({ morphInTransition = false } = {}) => {
  const mine = ++token;
  stopPoll();
  try {
    await loadSites();
    if (mine !== token) return;
    const name = route();
    const screen = screens[name];
    document.body.dataset.route = name;
    if (!screen) {
      location.hash = "#/websites";
      return;
    }
    paintRail();
    if (name !== "websites" && !state.site) {
      view.innerHTML = needSite();
      lastRoute = name;
      return;
    }
    const data = await screen.load();
    if (mine !== token) return;
    const key = `${name}${location.hash.includes("/new") ? "/new" : ""}`;
    const html = `<div class="screen screen--${name}">${screen.view(data)}</div>`;
    const swap = key !== lastRoute;
    lastRoute = key;
    if (swap) withTransition(() => { view.innerHTML = html; screen.after?.(data); });
    else if (morphInTransition) withTransition(() => { morph(view, html); screen.after?.(data); });
    else {
      morph(view, html);
      screen.after?.(data);
    }
  } catch (error) {
    if (mine !== token) return;
    view.innerHTML = `<div class="screen"><div class="blank"><div class="blank-inner"><h1 class="t-1">Couldn't load this</h1><p class="soft">${esc(error.message)}</p><button class="btn" data-do="reload">Try again</button></div></div></div>`;
  }
};

actions.copy = (el) => {
  navigator.clipboard.writeText(el.dataset.text).then(() => {
    el.classList.add("copied");
    setTimeout(() => el.classList.remove("copied"), 1700);
    toast(`${el.dataset.label} copied`);
  }, () => toast("Couldn't copy. Select it and copy by hand."));
};
actions.reload = () => app.render();

document.addEventListener("click", async (event) => {
  const el = event.target.closest("[data-do]");
  if (!el || el.disabled) return;
  if (el.dataset.self && event.target !== el) return; // Clicks inside a popup don't close it.
  try {
    await actions[el.dataset.do](el);
  } catch (error) {
    fail(error);
  }
});
document.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target.closest("[data-form]");
  if (!form) return;
  const buttons = [...form.querySelectorAll("button")];
  buttons.forEach((b) => { b.disabled = true; });
  try {
    await forms[form.dataset.form](form, event.submitter);
  } catch (error) {
    fail(error);
    state.working = false;
    buttons.forEach((b) => { b.disabled = false; });
  }
});
document.addEventListener("keydown", (event) => {
  const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName);
  if (event.key === "Escape") {
    if ($(".editing") || $(".cell-input")) return app.render();
    if ($(".live-moment")) return actions.closeMoment({ dataset: {} });
    if ($(".modal-back")) return actions.closeConnect();
  }
  if (!typing && !event.metaKey && !event.ctrlKey && !event.altKey && /^[1-5]$/.test(event.key)) location.hash = `#/${NAV[+event.key - 1][0]}`;
});
window.addEventListener("hashchange", () => app.render());
window.addEventListener("resize", syncIndicator);

rail.innerHTML = `<a class="brand" href="#/websites"><img class="brand-mark" src="favicon.svg" alt=""><span class="brand-word">${BRAND}</span></a>`;
app.render();
