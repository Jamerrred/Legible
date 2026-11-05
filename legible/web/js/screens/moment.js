// The moment a page goes live: cobalt opens from the button the owner pressed.
import { $, actions, copyButton, domain, esc, icon, plural } from "../core.js";

export function showLiveMoment(site, count, rect) {
  const cx = rect ? `${rect.left + rect.width / 2}px` : "50%";
  const cy = rect ? `${rect.top + rect.height / 2}px` : "50%";
  $("#overlay").innerHTML = `<div class="live-moment agent-surface" style="--cx:${cx};--cy:${cy}" role="dialog" aria-modal="true" aria-label="Your page is live">
    <div class="live-inner">
      <h1 class="focus-in" style="--i:6">Your page is live.</h1>
      <div class="live-link focus-in" style="--i:9">${esc(domain(site.link))}</div>
      <p class="focus-in" style="--i:11">${plural(count, "fact")} confirmed. Any agent can now read them, work out a quote and send you a booking request. Anything you haven't confirmed stays private.</p>
      <div class="row row--wrap focus-in" style="--i:12">${copyButton(site.link, "Link", { cls: "btn--on-agent btn--lg" })}<a class="btn btn--ghost-agent btn--lg" href="#/simulations" data-do="closeMoment" data-keep-route="1">${icon("play")} Test it again</a><button class="btn btn--ghost-agent btn--lg" data-do="closeMoment">Back to my facts</button></div>
    </div></div>`;
}

export function closeMoment() {
  const el = $(".live-moment");
  if (!el) return;
  el.classList.add("closing");
  setTimeout(() => { $("#overlay").innerHTML = ""; }, 340);
}
actions.closeMoment = (el) => {
  closeMoment();
  if (el.dataset.keepRoute) location.hash = "#/simulations";
};
