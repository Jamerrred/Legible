// Bookings: each request reads like a ticket, with the bill the page worked out.
import { actions, api, app, demoAgentsArrive, esc, forms, icon, money, post, screens, shortDate, startPoll, state, titled, toast, when } from "../core.js";

const title = (b) => {
  const job = b.payload?.details?.inputs || {};
  const name = titled(job.service) || "A job";
  return job.when ? `${name} on ${shortDate(job.when)}` : name;
};
const replyParts = (resolution) => {
  const m = String(resolution || "").match(/^(\w+): ([\s\S]*)$/);
  return m ? { status: m[1], text: m[2] } : { status: "", text: resolution };
};
const STAMP = { accepted: ["ok", "check", "Accepted"], suggested: ["muted", "clock", "Asked for another time"], declined: ["pen", "x", "Declined"] };

function ticket(b) {
  const d = b.payload?.details || {};
  const job = d.inputs || {};
  const kv = (k, v) => (v ? `<div class="kv"><span>${k}</span><span>${esc(v)}</span></div>` : "");
  const bill = (d.lines || []).map((l) => `<li><span>${esc(l.label)}</span><span>${money("$", l.amount)}</span></li>`).join("");
  const tax = d.tax ? `<li><span>Tax</span><span>${money("$", d.tax)}</span></li>` : "";
  const total = typeof d.total === "number" || d.total?.low ? `<div class="bill-total"><span class="small soft">The page quoted</span><b>${money("$", d.total)}</b></div>` : "";
  const sender = d.submitted_by === "agent" ? `Sent by ${d.agent_name || "an agent"}` : "Sent by the customer";
  const reply = replyParts(b.resolution);
  const stamp = STAMP[reply.status];
  const defaults = "Add a note. It shows on the status page the agent checks.";
  const actionsHtml = b.status === "open"
    ? `<form class="ticket-actions" data-form="bookingReply" data-id="${b.id}"><textarea class="note" name="message" placeholder="${defaults}"></textarea><div class="row row--wrap"><button class="btn btn--primary" name="status" value="accepted">${icon("check")} Accept booking</button><button class="btn" name="status" value="suggested">${icon("clock")} Suggest another time</button><button class="btn btn--ghost" name="status" value="declined">Decline</button></div></form>`
    : `<div class="ticket-actions"><div>${stamp ? `<span class="stamp ${stamp[0]}">${icon(stamp[1])} ${stamp[2]}</span>` : ""}</div></div>`;
  const statusLine = b.status !== "open" ? `<div class="status-line"><code>${esc(b.status_url)}</code><div>${esc(reply.text)}</div><div style="margin-top:8px"><a href="${esc(b.status_url)}" target="_blank" rel="noopener">See the status page the agent reads</a></div></div>` : "";
  return `<div class="ticket" id="ticket-${b.id}">
      <div class="ticket-top"><span class="row small muted">${icon("bot")} ${esc(sender)}, ${esc(when(b.created_at))}</span><h2>${esc(title(b))}</h2></div>
      <div class="ticket-tear"></div>
      <div class="ticket-body">${kv("Customer", d.name)}${kv("Email", d.email)}${kv("Phone", d.phone)}${kv("Vehicle size", titled(job.variant))}${kv("Add-ons", (job.addons || []).map(titled).join(", "))}${kv("ZIP code", job.zip)}${kv("Notes", d.notes)}</div>
      ${bill || total ? `<div class="ticket-tear"></div><div class="ticket-body"><ul class="bill">${bill}${tax}</ul>${total}</div>` : ""}
      ${actionsHtml}
    </div>${statusLine}`;
}

screens.bookings = {
  async load() {
    await demoAgentsArrive();
    const rows = await api(`/websites/${state.site.id}/bookings`);
    if (!rows.some((b) => b.id === state.selectedBooking)) state.selectedBooking = rows[0]?.id || null;
    return { rows };
  },
  view({ rows }) {
    const current = rows.find((b) => b.id === state.selectedBooking);
    if (!rows.length) return `<div class="blank"><div class="blank-inner"><h1 class="t-1">No booking requests yet</h1><p class="soft">When an agent sends one for a customer, it lands here for you to accept or decline.</p></div></div>`;
    const list = rows.map((b) => `<button class="booking-item ${b.id === state.selectedBooking ? "on" : ""}" data-do="pickBooking" data-id="${b.id}" id="bk-${b.id}"><span class="between tiny"><span class="row strong" style="gap:6px;color:var(--ink-2)">${b.status === "open" ? '<span class="dot dot--pen"></span>Needs a reply' : `<span class="dot dot--live"></span>Replied`}</span><span class="muted">${esc(when(b.created_at))}</span></span><b>${esc(title(b))}</b><span class="tiny muted">${esc(b.payload?.details?.name || "")}</span></button>`).join("");
    return `<div class="bookings"><aside class="booking-list"><h1 class="t-2">Bookings</h1>${list}</aside><section class="booking-detail">${current ? ticket(current) : ""}</section></div>`;
  },
  after() {
    startPoll(function keepCurrent() {
      if (/^(INPUT|TEXTAREA)$/.test(document.activeElement?.tagName)) return startPoll(keepCurrent, 5000);
      app.render();
    }, 5000);
  },
};

actions.pickBooking = (el) => {
  state.selectedBooking = el.dataset.id;
  app.render();
};
forms.bookingReply = async (form, submitter) => {
  const status = submitter?.value || "accepted";
  const defaults = { accepted: "Yes, that works. We'll be in touch to confirm.", suggested: "That time doesn't work. Please suggest another.", declined: "Sorry, we can't take this one." };
  await post(`/bookings/${form.dataset.id}/reply`, { status, message: form.message.value.trim() || defaults[status] });
  toast("Reply sent. The agent will see it on its status page");
  app.render();
};
