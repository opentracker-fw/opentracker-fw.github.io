/* Open the <details> that a link points at (or that holds its target), then scroll to it.
   Everything on the pages is readable without this. */
(function () {
  "use strict";
  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    if (!el) return;
    var opened = false;
    for (var n = el; n; n = n.parentElement) {
      if (n.tagName === "DETAILS" && !n.open) { n.open = true; opened = true; }
    }
    if (opened) el.scrollIntoView();
  }
  window.addEventListener("hashchange", openTarget);
  openTarget();
})();
