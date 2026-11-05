// Test customers working live. Shared by the onboarding view and the Simulations screen.
import { esc, icon } from "../core.js";

export const asked = (query) => String(query || "").replace(/\s*\(?https?:\/\/\S+\)?/g, "").replace(/\s*\(The business's information page is\s*\)?\.?\)?$/, "").trim();

export function liveTrace(sim) {
  if (!sim || !sim.agents.length) return `<div class="row"><span class="ring"></span><span class="shimmer">Writing questions for the test customers</span></div>`;
  return `<div class="customers customers--live">${sim.agents.map((agent, n) => {
    const stuck = agent.done && ["unknown", "blocked"].includes(agent.outcome);
    const cls = !agent.done ? "agent-surface" : stuck ? "is-stuck" : "is-done";
    const badge = !agent.done ? `<span class="badge badge--agent"><span class="ring" style="width:11px;height:11px"></span> Working</span>` : stuck ? `<span class="badge badge--pen">${icon("x")} Stuck</span>` : `<span class="badge badge--ok">${icon("check")} Answered</span>`;
    const offset = agent.total - agent.steps.length;
    const lines = agent.steps.map((text, i) => `<div id="t-${n}-${offset + i}">${!agent.done && i === agent.steps.length - 1 ? `<span class="shimmer">› ${esc(text)}</span>` : `› ${esc(text)}`}</div>`).join("");
    return `<article class="cust ${cls}" id="live-${n}"><div class="between">${badge}<span class="tiny num" style="opacity:.7">${agent.total} ${agent.total === 1 ? "step" : "steps"}</span></div><p class="cust-quote">“${esc(asked(agent.query))}”</p><div class="cust-trace">${lines || `<div><span class="shimmer">› Starting</span></div>`}</div></article>`;
  }).join("")}</div>`;
}
