/* PRICKLY desk policy - role trust groups + fair-use hint.
   Does not rewrite banks; loads assets/prickly-role-meta.json. */
(function () {
  "use strict";

  var META_URL = "assets/prickly-role-meta.json?v=3";

  function $(id) {
    return document.getElementById(id);
  }

  function rebuildKindSelect(meta) {
    var sel = $("prickly-dev-kind");
    if (!sel || !meta || !meta.roles) return;

    var groups = {
      trusted: { label: "Trusted corridor (vetted / approved)", keys: [] },
      disclosed: { label: "Use with care", keys: [] },
      prototype: { label: "Work-in-progress", keys: [] },
    };

    Object.keys(meta.roles).forEach(function (key) {
      var r = meta.roles[key];
      var g = r.ui_group || "prototype";
      if (!groups[g]) groups[g] = { label: g, keys: [] };
      groups[g].keys.push(key);
    });

    var prev = sel.value || "software_engineer";
    sel.innerHTML = "";

    ["trusted", "disclosed", "prototype"].forEach(function (gName) {
      var g = groups[gName];
      if (!g || !g.keys.length) return;
      var og = document.createElement("optgroup");
      og.label = g.label;
      g.keys.forEach(function (key) {
        var r = meta.roles[key];
        var opt = document.createElement("option");
        opt.value = key;
        var badge = "";
        if (r.badge === "prototype_rebuild") badge = " [new & work-in-progress]";
        else if (r.badge === "key_skew_disclosed") badge = " [use with care]";
        else if (r.badge === "architect_quarantine") badge = " [new & work-in-progress]";
        else if (r.badge === "new_pack") badge = " [new & work-in-progress]";
        opt.textContent = (r.label || key) + badge;
        if (r.warning) opt.title = r.warning;
        og.appendChild(opt);
      });
      sel.appendChild(og);
    });

    if ([].some.call(sel.options, function (o) { return o.value === prev; })) {
      sel.value = prev;
    } else {
      sel.value = "software_engineer";
    }

    wireTrustHint(meta);
    sel.addEventListener("change", function () {
      wireTrustHint(meta);
    });
  }

  function wireTrustHint(meta) {
    var sel = $("prickly-dev-kind");
    var host = $("prickly-dev-profile");
    if (!sel || !host || !meta || !meta.roles) return;

    var hint = $("prickly-role-trust");
    if (!hint) {
      hint = document.createElement("p");
      hint.id = "prickly-role-trust";
      hint.className = "prickly-role-trust";
      var lead = host.querySelector(".prickly-lead");
      if (lead && lead.nextSibling) host.insertBefore(hint, lead.nextSibling);
      else host.insertBefore(hint, host.querySelector(".prickly-form") || null);
    }

    var fair = $("prickly-fair-use");
    if (!fair) {
      fair = document.createElement("p");
      fair.id = "prickly-fair-use";
      fair.className = "prickly-fair-use";
      fair.textContent = meta.fair_use || "Practice feedback only - not for hire or promotion cuts.";
      host.insertBefore(fair, hint.nextSibling);
    }

    var r = meta.roles[sel.value];
    if (!r) {
      hint.textContent = "";
      return;
    }
    hint.setAttribute("data-trust", r.trust || "");
    var parts = [];
    if (r.trust === "corridor") {
      parts.push("Trusted corridor (vetted / approved) - best fit for practice right now.");
    } else if (r.trust === "disclose") {
      parts.push("Use with care - fine for practice; not vetted for hire or promotion cuts.");
    } else {
      parts.push("New & work-in-progress - not ready for consequential practice.");
    }
    if (r.warning) parts.push(r.warning);
    hint.textContent = parts.join(" ");
  }

  function boot() {
    fetch(META_URL)
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (meta) {
        if (meta) rebuildKindSelect(meta);
      })
      .catch(function () {});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
