// Simulations: the score, what each test customer did, and the questions that unblock them.
import { $, actions, api, app, circled, esc, forms, icon, isBusy, morph, plural, pollMs, post, roll, route, screens, seats, startPoll, state, toast, when, withTransition } from "../core.js";
import { asked, liveTrace } from "./live.js";

const SOURCE = { simulation: "A test customer got stuck", agent_activity: "Real agents hit this", interview: "Missing from your website" };
const GLYPH = { read: "file-text", quote: "calculator", search: "search", browse: "mouse-pointer-click", math: "sigma", say: "message-circle" };

const broke = (run) => run.result?.error || (run.result?.answer || "").startsWith("The model stopped responding");
const seatOf = (run) => (run.settled ? "ok" : broke(run) ? "crashed" : "stuck");

// The path a test customer took. Fewer dots and no browser is the whole point.
function pathHtml(run) {
  const steps = (run.path || []).filter((s) => s.kind !== "say" && s.kind !== "finish");
  const dots = steps.map((s) => `<span class="path-step path-step--${s.kind}" title="${esc(s.text)}">${icon(GLYPH[s.kind] || "circle")}</span>`).join("");
  const end = run.settled ? `<span class="path-step path-step--end-ok" title="Answered">${icon("check")}</span>` : broke(run) ? "" : `<span class="path-step path-step--end-stuck" title="Stuck">${icon("x")}</span>`;
  const usedBrowser = steps.some((s) => s.kind === "browse");
  const quoted = steps.filter((s) => s.kind === "quote").length;
  const note = usedBrowser ? "Had to open a browser" : quoted ? `${plural(quoted, "live quote")}, no browser` : steps.length ? "No browser needed" : "";
  return `<div class="path" aria-label="${steps.length} steps">${dots}${end}</div>${note ? `<span class="path-note">${note}</span>` : ""}`;
}

// Mark the sentence where the agent gave up, the way you'd circle it on paper.
function answerHtml(run) {
  const text = esc(broke(run) ? "The test agent crashed before it finished. This doesn't count against you." : run.result?.answer || "No answer.");
  if (run.settled || broke(run)) return text;
  return text.replace(/I can(?:&#39;|')t (?:tell|confirm|give)(?: a| an)?(?: all-in)?(?: total)?/, (phrase) => circled(phrase));
}

function customerCard(run, n, questions, firstRuns, isLater) {
  const before = isLater ? firstRuns.find((r) => r.query === run.query) : null;
  const beforeSteps = before ? (before.path || []).filter((s) => !["say", "finish"].includes(s.kind)).length : 0;
  const was = before && !before.settled && run.settled ? `<span class="path-note"><span class="pen strong">Before:</span> stuck after ${plural(beforeSteps, "step")}</span>` : "";
  const blockers = run.settled ? [] : questions.filter((q) => (q.payload?.blocks || []).includes(run.query));
  const needs = blockers.map((q) => `<span class="need ${q.status === "done" ? "done" : ""}">${q.status === "done" ? icon("check") : ""}${esc(q.payload.chip || q.payload.topic || "A missing fact")}</span>`).join("");
  const badge = run.settled ? `<span class="badge badge--ok">${icon("check")} Answered</span>` : broke(run) ? `<span class="badge badge--muted">${icon("minus")} Agent crashed</span>` : `<span class="badge badge--pen">${icon("x")} Stuck</span>`;
  return `<article class="cust" id="cust-${n}"><div class="between">${badge}</div>
    <p class="cust-quote">“${esc(asked(run.query))}”</p>
    <p class="cust-answer">${answerHtml(run)}</p>
    <div class="stack" style="gap:6px;margin-top:auto">${pathHtml(run)}${was}</div>
    ${needs ? `<div class="cust-foot">${needs}</div>` : ""}</article>`;
}

function checkTab(sim, current, runsById) {
  const running = sim.status === "running";
  const runs = runsById[sim.id];
  const seatRow = runs ? seats(runs.map(seatOf)) : running ? "" : seats(Array.from({ length: sim.summary.queries }, (_, i) => (i < sim.summary.answered ? "ok" : "stuck")));
  return `<button class="check-tab ${current ? "on" : ""}" data-do="pickSim" data-id="${sim.id}" id="ck-${sim.id}">
    <span class="between"><span class="small strong">${esc(sim.target === "resource" ? "On your Legible page" : "On your website")}</span><span class="tiny muted">${esc(when(sim.created_at))}</span></span>
    <span class="check-score">${running ? `<span class="ring"></span><small>Running</small>` : `${roll(sim.summary.answered)}<small>of ${sim.summary.queries} got an answer</small>`}</span>
    ${seatRow}</button>`;
}

function questionCard(q) {
  return `<article class="q-card" id="q-${q.id}" style="view-transition-name:q-${q.id}">
    <span class="q-source"><span class="dot dot--pen"></span>${esc(SOURCE[q.source] || "Missing")}</span>
    <h3>${esc(q.title)}</h3>
    ${q.body ? `<p class="q-why">${esc(q.body)}</p>` : ""}
    ${q.payload?.suggested ? `<button class="chip" type="button" data-do="useSuggested" data-text="${esc(q.payload.suggested)}">${esc(q.payload.suggested)}</button>` : ""}
    <form data-form="answer" data-id="${q.id}"><div class="field"><input name="text" required placeholder="Answer in your own words" autocomplete="off" aria-label="Your answer"><button class="send" aria-label="Send answer">${icon("arrow-up")}</button></div></form>
    <div><button class="btn btn--ghost btn--sm" data-do="dismiss" data-id="${q.id}" style="margin-left:-8px">This doesn't apply</button></div>
  </article>`;
}

function deckHtml(missing) {
  const open = missing.open;
  if (!open.some((q) => q.id === state.activeQuestion)) state.activeQuestion = open[0]?.id || null;
  const active = open.find((q) => q.id === state.activeQuestion);
  const rest = open.filter((q) => q !== active).map((q) => `<button class="q-next" data-do="pickQuestion" data-id="${q.id}" id="q-${q.id}" style="view-transition-name:q-${q.id}"><span class="dot dot--pen"></span><span class="grow ellipsis">${esc(q.title)}</span>${icon("arrow-up")}</button>`).join("");
  const answer = state.lastAnswer;
  const receipt = answer ? `<div class="q-receipt" id="receipt-${answer.id}"><b>${esc(answer.summary)}</b>${answer.lines.length ? `<ul>${answer.lines.map((l) => `<li>+ ${esc(l)}</li>`).join("")}</ul>` : ""}</div>` : "";
  const answered = missing.answered.filter((q) => q.status === "done").slice(0, 6).map((q) => `<div class="q-done" id="q-${q.id}" style="view-transition-name:q-${q.id}">${icon("check")}<span class="grow">${esc(q.title)}</span></div>`).join("");
  const none = !open.length ? `<div class="q-card"><h3>Nothing's missing right now</h3><p class="q-why">When a test customer or a real agent gets stuck, the question lands here.</p></div>` : "";
  return `<aside class="deck" id="deck">
    <div class="section-head" style="margin-bottom:2px"><h2 class="t-2">What's missing</h2>${open.length ? `<span class="count">${open.length}</span>` : ""}</div>
    ${receipt}${active ? questionCard(active) : none}${rest}
    ${answered ? `<div style="margin-top:10px"><div class="eyebrow" style="margin-bottom:6px">Now on your page</div>${answered}</div>` : ""}
  </aside>`;
}

// When the page isn't live yet, a re-check still reads the website, so say what will move the score.
function nextHint(site, open) {
  if (open) return "";
  if (site.needs.review) return `<p class="small soft" style="margin-bottom:12px">Confirm your facts next, then run the check again on your Legible page.</p>`;
  return "";
}

async function pollSim() {
  if (route() !== "simulations") return;
  try {
    const trace = await api(`/websites/${state.site.id}/trace`);
    if (!trace.simulation && !isBusy({ stage: trace.stage })) return app.render();
    const el = $("#live");
    if (el) morph(el, liveTrace(trace.simulation));
  } catch { /* The next poll tries again. */ }
  startPoll(pollSim, pollMs());
}

screens.simulations = {
  async load() {
    const id = state.site.id;
    const [missing, sims] = await Promise.all([api(`/websites/${id}/missing`), api(`/websites/${id}/simulations`)]);
    if (!sims.some((s) => s.id === state.selectedSim)) state.selectedSim = sims[0]?.id || null;
    const finished = sims.filter((s) => s.status === "done");
    const details = await Promise.all(finished.map((s) => api(`/simulations/${s.id}`)));
    const runsById = Object.fromEntries(details.map((d) => [d.id, d.runs]));
    return { missing, sims, runsById, current: details.find((d) => d.id === state.selectedSim) || sims.find((s) => s.id === state.selectedSim) || null };
  },
  view({ missing, sims, runsById, current }) {
    const site = state.site;
    const running = sims.some((s) => s.status === "running") || isBusy(site);
    const ordered = [...sims].reverse();
    const questions = [...missing.open, ...missing.answered];
    const finished = ordered.filter((s) => s.status === "done");
    const firstRuns = finished.length ? [...runsById[finished[0].id]].sort((a, b) => a.settled - b.settled) : [];
    const place = (run) => firstRuns.findIndex((r) => r.query === run.query);
    const isLater = finished.length > 1 && current?.id !== finished[0].id;
    const pushCheck = site.next?.label === "Run the check again" || !sims.length;
    const body = current?.status === "running"
      ? `<div id="live">${liveTrace(null)}</div>`
      : current?.runs
        ? `<div class="customers">${[...current.runs].sort((a, b) => place(a) - place(b)).map((run) => customerCard(run, place(run), questions, firstRuns, isLater)).join("")}</div>`
        : `<div class="empty-line"><b>No check has run yet</b>A check sends test customers at your website to find what they can't answer.</div>`;
    return `<div class="scroll"><div class="page" style="width:min(1320px,100%)">
      <header class="page-head"><div><h1 class="t-1">Simulations</h1><p>Agents ask what your real customers ask. Whatever stops them comes back to you as a question.</p></div>
        <button class="btn ${pushCheck ? "btn--agent" : ""} btn--lg" data-do="runCheck" ${running ? "disabled" : ""}>${running ? `<span class="ring"></span> Agents are working` : `${icon("play")} ${sims.length ? "Run the check again" : "Run a check"}`}</button></header>
      <div class="sims"><div>
        <div class="score-band">${ordered.slice(-3).map((s) => checkTab(s, s.id === state.selectedSim, runsById)).join("")}</div>
        ${nextHint(site, missing.open.length)}
        ${body}
      </div>${deckHtml(missing)}</div>
    </div></div>`;
  },
  after({ sims }) {
    if (sims.some((s) => s.status === "running") || isBusy(state.site)) startPoll(pollSim, 80);
  },
};

function linesFromOps(ops) {
  return (ops || []).flatMap((op) => {
    const item = op.item || {};
    if (op.op === "delete") return [];
    if (op.op === "set") return [`${op.path}: ${typeof op.value === "object" ? "set" : op.value}`];
    const amount = item.amount ?? item.fee;
    return [item.statement || `${item.label || item.name}${amount ? `, $${amount}` : ""}`];
  }).slice(0, 5);
}

Object.assign(actions, {
  pickSim: (el) => { state.selectedSim = el.dataset.id; app.render(); },
  pickQuestion: (el) => {
    state.activeQuestion = el.dataset.id;
    withTransition(() => app.render());
  },
  useSuggested: (el) => {
    const input = el.closest("article").querySelector("input[name=text]");
    input.value = el.dataset.text;
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
  },
  dismiss: async (el) => {
    await post(`/inbox/${el.dataset.id}/dismiss`);
    app.render();
  },
  runCheck: async () => {
    await post(`/websites/${state.site.id}/simulations`, { target: state.site.live ? "resource" : "storefront" });
    state.selectedSim = null;
    state.lastAnswer = null;
    toast("Test customers are on their way");
    setTimeout(() => app.render(), 500);
  },
});

forms.answer = async (form) => {
  const id = form.dataset.id;
  const result = await post(`/inbox/${id}/answer`, { text: form.text.value.trim(), scope: form.once?.checked ? "once" : "everyone" });
  state.lastAnswer = { id, summary: result.summary || "Saved", lines: linesFromOps(result.ops) };
  toast(result.summary || "Saved", { do: "undo", label: "Undo" });
  await app.render({ morphInTransition: true });
};
