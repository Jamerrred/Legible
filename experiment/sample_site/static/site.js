(function () {
  function seen(name) { return document.cookie.indexOf(name + "=1") !== -1; }
  function remember(name) { document.cookie = name + "=1; path=/; max-age=2592000; SameSite=Lax"; }

  var bar = document.getElementById("cookie-bar");
  if (bar && !seen("cookie_ok")) {
    bar.hidden = false;
    bar.querySelector("button").addEventListener("click", function () {
      remember("cookie_ok");
      bar.hidden = true;
    });
  }

  var promo = document.getElementById("promo");
  if (promo && !seen("promo_closed")) {
    setTimeout(function () { promo.hidden = false; }, 4000);
    promo.querySelector(".promo-close").addEventListener("click", function () {
      remember("promo_closed");
      promo.hidden = true;
    });
  }
})();
