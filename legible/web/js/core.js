// What every screen shares: data, rendering, small display helpers and the action registry.

export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
export const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
export const icon = (name, cls = "") => `<svg class="i ${cls}" aria-hidden="true"><use href="vendor/icons.svg#${name}"></use></svg>`;
export const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;

export const state = { sites: [], site: null, config: null, selectedSim: null, selectedBooking: null, agentView: false, working: false, clarify: null, activeQuestion: null, lastAnswer: null, flash: null, quote: null };

export async function api(path, options = {}) {
  const init = { ...options };
  if (options.body !== undefined) {
    init.body = JSON.stringify(options.body);
    init.headers = { "content-type": "application/json" };
  }
  const response = await fetch(path, init);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "That didn't work. Try again.");
  return data;
}
export const post = (path, body = {}) => api(path, { method: "POST", body });

// Rendering. Same-screen updates morph, so only what changed moves. Route changes cross-fade.
const calm = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
export function morph(el, html) {
  window.Idiomorph.morph(el, html, {
    morphStyle: "innerHTML",
    ignoreActiveValue: true,
    callbacks: { beforeAttributeUpdated: (name, node) => !(name === "open" && node.tagName === "DETAILS") },
  });
}
export function withTransition(update) {
  if (!document.startViewTransition || calm()) return update();
  document.startViewTransition(update);
}

// Display helpers
export const when = (iso) => {
  const d = new Date(iso);
  return Number.isNaN(+d) ? "" : d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
};
export const shortDate = (iso) => {
  const d = new Date(`${iso}T12:00:00`);
  return Number.isNaN(+d) ? iso : d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
};
export const words = (text) => {
  const w = String(text || "").replace(/[-_]+/g, " ").trim();
  return w ? w[0].toUpperCase() + w.slice(1) : "";
};
export const titled = (text) => String(text || "").replace(/[-_]+/g, " ").trim().replace(/\b\w/g, (c) => c.toUpperCase());
export const domain = (url) => String(url || "").replace(/^https?:\/\//, "").replace(/\/$/, "");
const SYMBOL = { USD: "$", EUR: "€", GBP: "£", INR: "₹" };
export const currency = (rec) => SYMBOL[rec?.currency || "USD"] ?? "";
export const money = (symbol, n) => {
  if (n === null || n === undefined || n === "") return "Not stated";
  if (typeof n === "object") return `${money(symbol, n.low)} to ${money(symbol, n.high)}`;
  return `${symbol}${Number(n).toLocaleString(undefined, { minimumFractionDigits: Number.isInteger(+n) ? 0 : 2, maximumFractionDigits: 2 })}`;
};

// Digits that roll. The columns transition by themselves when a morph changes --d.
export const roll = (n) => `<span class="roll" role="img" aria-label="${esc(n)}">${String(n).split("").map((d) => `<span class="roll-col" style="--d:${d}" aria-hidden="true">${"0123456789".split("").map((x) => `<i>${x}</i>`).join("")}</span>`).join("")}</span>`;

// The owner's pen: a loose circle and underline that stretch to whatever they mark.
const CIRCLE = '<svg class="mark mark--circle" viewBox="0 0 120 44" preserveAspectRatio="none" aria-hidden="true"><path d="M30 6C52 1 92 2 108 12c13 9 9 21-8 26-24 7-62 7-82 0C2 32-1 21 9 13 20 4 46 2 70 4"/></svg>';
const UNDER = '<svg class="mark mark--under" viewBox="0 0 120 8" preserveAspectRatio="none" aria-hidden="true"><path d="M1 5C20 2 38 6 58 4s42-2 61 1"/></svg>';
export const circled = (html) => `<span class="marked">${html}${CIRCLE}</span>`;
export const underlined = (html) => `<span class="marked">${html}${UNDER}</span>`;

// A row of seats: one for each test customer. Colour is never the only signal, since a label always sits beside it.
export const seats = (runs) => `<div class="seats" aria-hidden="true">${runs.map((r) => `<i class="${r}"></i>`).join("")}</div>`;
export const seatsFromScore = (answered, total) => seats(Array.from({ length: total }, (_, i) => (i < answered ? "ok" : "stuck")));

export const copyButton = (text, label, { cls = "", caption = "Copy link" } = {}) => `<button class="btn ${cls}" type="button" data-do="copy" data-text="${esc(text)}" data-label="${esc(label)}"><span class="copy-swap">${icon("copy")}${icon("check")}</span>${esc(caption)}</button>`;

// Toast
let toastTimer;
export function toast(message, action) {
  const el = $("#toast");
  el.innerHTML = `<span>${esc(message)}</span>${action ? `<button data-do="${action.do}">${esc(action.label)}</button>` : ""}`;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), action ? 7000 : 3200);
}
export const fail = (error) => toast(error.message || "That didn't work. Try again.");

// Registries that each screen adds to, plus a shared poll that a new render always cancels.
export const actions = {};
export const forms = {};
export const screens = {};
const pollBox = { timer: null };
export const stopPoll = () => clearTimeout(pollBox.timer);
export const startPoll = (fn, ms) => {
  clearTimeout(pollBox.timer);
  pollBox.timer = setTimeout(fn, ms);
};
export const route = () => (location.hash.replace(/^#\/?/, "") || "websites").split("/")[0];
export const isBusy = (site) => site && !["ready", "failed"].includes(site.stage);
export const pollMs = () => (state.config?.demo ? 500 : 1200);

// Set by app.js, so screens can ask for a re-render without importing it.
export const app = { render: async () => {}, refreshRail: async () => {} };
