/* Image picker: highlights the 3.0 images that contain every ticked module. */
(function () {
  "use strict";
  var data = window.OT_DATA;
  var form = document.getElementById("picker");
  if (!data || !form) return;

  var out = document.getElementById("pick-out");
  var rows = document.querySelectorAll("#image-table tbody tr[data-variant], .flav-cards .flav[data-variant]");
  var byId = {};
  data.modules.forEach(function (m) { byId[m.id] = m; });

  function addChecks(kind, sel) {
    var box = document.querySelector(sel + " .checks");
    data.modules.filter(function (m) { return m.kind === kind; }).forEach(function (m) {
      var label = document.createElement("label");
      label.className = "check";
      var input = document.createElement("input");
      input.type = "checkbox";
      input.name = "module";
      input.value = m.id;
      label.appendChild(input);
      label.appendChild(document.createTextNode(m.name));
      box.appendChild(label);
    });
  }
  addChecks("synth", "#pick-synths");
  addChecks("effect", "#pick-effects");

  function names(ids) {
    return ids.map(function (id) { return byId[id].name; }).join(", ");
  }

  function el(tag, text, cls) {
    var e = document.createElement(tag);
    if (text) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }

  function imageLink(im) {
    var a = el("a", im.name + " (" + im.file + ")");
    a.href = "#get-" + im.profile;
    return a;
  }

  function update() {
    var picked = Array.prototype.map.call(
      form.querySelectorAll("input[name=module]:checked"), function (i) { return i.value; });
    var matches = data.images.filter(function (im) {
      return picked.every(function (id) { return im.modules.indexOf(id) >= 0; });
    });
    var matchSet = {};
    matches.forEach(function (im) { matchSet[im.variant] = true; });

    rows.forEach(function (tr) {
      var on = picked.length > 0 && matchSet[tr.getAttribute("data-variant")];
      tr.classList.toggle("is-match", !!on);
      tr.classList.toggle("is-dim", picked.length > 0 && !on);
    });

    out.textContent = "";
    out.className = "picker-out";
    if (!picked.length) {
      out.appendChild(el("p", "Tick synths or effects to see which images have them all."));
      return;
    }
    if (matches.length) {
      out.classList.add("ok");
      var p = el("p");
      p.appendChild(el("strong", matches.length === 1 ? "1 image has " : matches.length + " images have "));
      p.appendChild(document.createTextNode("all of " + names(picked) + ": "));
      matches.forEach(function (im, i) {
        if (i) p.appendChild(document.createTextNode(", "));
        p.appendChild(imageLink(im));
      });
      p.appendChild(document.createTextNode("."));
      out.appendChild(p);
      return;
    }
    out.classList.add("none");
    var best = 0;
    var scored = data.images.map(function (im) {
      var missing = picked.filter(function (id) { return im.modules.indexOf(id) < 0; });
      best = Math.max(best, picked.length - missing.length);
      return { im: im, missing: missing };
    });
    var p1 = el("p");
    p1.appendChild(el("strong", "No image has all of these. "));
    p1.appendChild(document.createTextNode(
      "Only one image can be installed at a time, so pick the closest one or untick something."));
    out.appendChild(p1);
    if (best > 0) {
      scored.filter(function (s) { return picked.length - s.missing.length === best; }).forEach(function (s) {
        var p = el("p");
        p.appendChild(document.createTextNode("Closest: "));
        p.appendChild(imageLink(s.im));
        p.appendChild(document.createTextNode(", without " + names(s.missing) + "."));
        out.appendChild(p);
      });
    }
  }

  form.addEventListener("change", update);
  document.getElementById("pick-clear").addEventListener("click", function () {
    form.querySelectorAll("input[name=module]").forEach(function (i) { i.checked = false; });
    update();
  });
  update();
})();
