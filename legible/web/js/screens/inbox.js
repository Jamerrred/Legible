// Inbox: only what agents did and asked. A funnel, their questions, a feed and unmet demand.
import { actions, api, app, esc, forms, icon, money, post, roll, screens, startPoll, state, titled, toast, when, words } from "../core.js";

function feedLine(event) {
  const job = event.inputs || {};
  const what = [titled(job.service), titled(job.variant), job.zip].filter(Boolean).join(", ");
  switch (event.event) {
    case "page_hit": return { glyph: "file-text", cls: "", text: `Read ${event.path === "/" ? "your main page" : event.path}`, detail: event.agent || "" };
    case "quote": return { glyph: "calculator", cls: "quote", text: `Worked out a quote${what ? `: ${what}` : ""}`, detail: typeof event.total === "number" ? money("$", event.total) : event.status === "needs_info" ? "Needed more details" : "" };
    case "dead_end": return { glyph: "circle-slash", cls: "dead", text: `Dead end${what ? `: ${what}` : ""}`, detail: words(event.reason) };
    case "request": return { glyph: "calendar-check", cls: "request", text: `Sent a booking request${what ? `: ${what}` : ""}`, detail: words(event.outcome) };
    case "question": return { glyph: "message-circle", cls: "", text: `Asked: “${event.text}”`, detail: "" };
    default: return { glyph: "circle", cls: "", text: event.event, detail: "" };
  }
}

// One series on one scale, so each bar is a share of the page reads, with the number beside it as text.
function funnelStep(n, label, glyph, top, dead = false) {
  return `<div class="funnel-step ${dead ? "funnel-step--dead" : ""}"><b>${roll(n)}</b><span class="funnel-label">${icon(glyph)}${label}</span><div class="funnel-bar" aria-hidden="true"><i style="--w:${top ? Math.max(Math.round((n / top) * 100), n ? 4 : 0) : 0}%"></i></div></div>`;
}

function agentQuestion(q) {
  return `<article class="q-card" id="q-${q.id}" style="margin-bottom:10px"><span class="q-source" style="color:var(--agent)"><span class="dot dot--agent"></span>An agent asked this for a customer</span><h3>${esc(q.title)}</h3><p class="q-why">Your answer shows on the status page that agent checks.</p>
    <form data-form="answer" data-id="${q.id}" class="stack" style="gap:9px"><div class="field"><input name="text" required placeholder="Answer in your own words" autocomplete="off" aria-label="Your answer"><button class="send" aria-label="Send answer">${icon("arrow-up")}</button></div>
    <label class="switch small"><input type="checkbox" name="once"><span class="track"></span>Just this once, don't add it to my page</label></form></article>`;
}

screens.inbox = {
  async load() {
    const id = state.site.id;
    const [activity, items] = await Promise.all([api(`/websites/${id}/activity`), api(`/websites/${id}/inbox?kinds=agent_question`)]);
    return { activity, items };
  },
  view({ activity, items }) {
    const c = activity.counts;
    const top = Math.max(c.page_reads, 1);
    const feed = activity.feed.slice(0, 30).map((event) => {
      const line = feedLine(event);
      return `<div class="feed-row" id="ev-${esc(event.id)}"><span class="feed-glyph ${line.cls ? `feed-glyph--${line.cls}` : ""}">${icon(line.glyph)}</span><div class="feed-main">${esc(line.text)}${line.detail ? `<small>${esc(line.detail)}</small>` : ""}</div><span class="feed-time">${esc(when(event.ts))}</span></div>`;
    }).join("");
    const wanted = activity.unmet_demand.map((d) => `<div class="demand"><b>${esc(d.title)}</b>${d.body ? `<small>${esc(d.body)}</small>` : ""}</div>`).join("");
    const agents = (activity.agents || []).map(([name, n]) => `<div class="agent-row"><span>${esc(name)}</span><span class="num muted">${n}</span></div>`).join("");
    return `<div class="scroll"><div class="page">
      <header class="page-head"><div><h1 class="t-1">Inbox</h1><p>What agents did on your page, and what they asked you.</p></div><button class="btn" data-do="review">${icon("refresh-cw")} Review activity now</button></header>
      <div class="funnel">${funnelStep(c.page_reads, "Read your page", "file-text", top)}${funnelStep(c.quotes, "Worked out a quote", "calculator", top)}${funnelStep(c.requests, "Sent a request", "calendar-check", top)}${funnelStep(c.dead_ends, "Hit a dead end", "circle-slash", top, true)}</div>
      <div class="inbox-grid"><div>
        ${items.length ? `<section style="margin-bottom:34px"><div class="section-head"><h2 class="t-2">Agents are asking</h2><span class="count">${items.length}</span></div>${items.map(agentQuestion).join("")}</section>` : ""}
        <section><div class="section-head"><h2 class="t-2">What agents did</h2></div>${feed || `<div class="empty-line"><b>No agents yet</b>Put your link on your website, and what agents do will show up here.</div>`}</section>
      </div><aside>
        <div class="section-head"><h2 class="t-2">Wanted, but not offered</h2></div>${wanted || `<p class="small muted">Nothing yet.</p>`}
        ${agents ? `<div class="section-head" style="margin-top:30px"><h2 class="t-2">Which agents</h2></div>${agents}` : ""}
        <p class="side-note">You can only see agents that reach your Legible page. An agent that stops at your own website stays invisible.</p>
      </aside></div>
    </div></div>`;
  },
  after() {
    startPoll(function keepCurrent() {
      if (/^(INPUT|TEXTAREA)$/.test(document.activeElement?.tagName)) return startPoll(keepCurrent, 5000);
      app.render();
    }, 5000);
  },
};

actions.review = async () => {
  const result = await post(`/websites/${state.site.id}/revise`);
  toast(result.signals ? `Reviewed ${result.signals} signals: ${result.questions} new questions, ${result.insights} insights` : "Nothing new to review");
  app.render();
};

export { forms };
