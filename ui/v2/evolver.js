/* EVOLVER - right-rail nest (RefineX + SpunkworX) + TOKEX strip.
   Isolated from history re-render: dock lives outside #rail-scroll. */
(function () {
  "use strict";

  var STORAGE_TOKEX = "evalathan.tokex.v1";
  var STORAGE_CONN = "evalathan.evolver.connections.v1";
  var STORAGE_GUARD = "evalathan.evolver.guardrails.v1";

  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function loadTokex() {
    try {
      var raw = localStorage.getItem(STORAGE_TOKEX);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    return {
      gross_prompt: 0,
      gross_completion: 0,
      gross_total: 0,
      seismo_saved: 0,
      seismo_saved_pct: 0,
      net_prompt: 0,
      net_completion: 0,
      net_total: 0,
      lifetime_total: 0,
      lifetime_saved: 0,
      lifetime_pct: 0,
      lifetime_runs: 0,
      note: "How many tokens EVOLVER routes used - and how much Hi0 / routing saved. Sealed runs only; never invented.",
    };
  }

  function saveTokex(t) {
    localStorage.setItem(STORAGE_TOKEX, JSON.stringify(t));
  }

  function loadConn() {
    try {
      var raw = localStorage.getItem(STORAGE_CONN);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    return {
      connection: "local-freemium",
      model: "auto",
      fallbackPref: ["freemium", "byo"],
      providers: [
        { id: "local-freemium", label: "Freemium (SpunkworX)", status: "ready" },
        { id: "byo", label: "BYO / RefineX", status: "unlinked" },
      ],
    };
  }

  function loadGuard() {
    try {
      var raw = localStorage.getItem(STORAGE_GUARD);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    return {
      spendCapUsd: 25,
      rateLimitPerMin: 30,
      failClosed: true,
      dryRunDefault: true,
      kelkboomGate: false,
    };
  }

  function renderTokexDetail(detail, t) {
    if (!detail) return;
    detail.innerHTML =
      '<div class="tokex-block">' +
      "<div>GROSS TOKEX THIS RUN</div>" +
      "<div>prompt=" +
      escapeHtml(t.gross_prompt) +
      " · completion=" +
      escapeHtml(t.gross_completion) +
      " · total=" +
      escapeHtml(t.gross_total) +
      "</div></div>" +
      '<div class="tokex-block">' +
      "<div>EVALATHAN TOKEX SAVED</div>" +
      "<div>prompt=" +
      escapeHtml(t.seismo_saved) +
      " · total=" +
      Number(t.seismo_saved_pct || 0).toFixed(2) +
      "%</div></div>" +
      '<div class="tokex-block net">' +
      '<div class="tokex-net-label">NET TOKEX THIS RUN</div>' +
      '<div class="tokex-net-stats">prompt=' +
      escapeHtml(t.net_prompt) +
      " · completion=" +
      escapeHtml(t.net_completion) +
      " · total=" +
      escapeHtml(t.net_total) +
      "</div></div>" +
      '<div class="tokex-block">' +
      "<div>LIFETIME TOKEX</div>" +
      "<div>total=" +
      escapeHtml(t.lifetime_total) +
      " · saved=" +
      escapeHtml(t.lifetime_saved) +
      " (" +
      Number(t.lifetime_pct || 0).toFixed(2) +
      "% · " +
      escapeHtml(t.lifetime_runs) +
      " run(s))</div></div>" +
      '<div class="tokex-block"><div>' +
      escapeHtml(t.note || "") +
      "</div></div>";
  }

  function openConnectionsSheet() {
    var layer = $("evolver-conn-layer");
    if (!layer) return;
    var conn = loadConn();
    var g = loadGuard();
    var sel = $("evolver-conn-select");
    var model = $("evolver-conn-model");
    var cap = $("evolver-guard-cap");
    var rate = $("evolver-guard-rate");
    var fail = $("evolver-guard-fail");
    var dry = $("evolver-guard-dry");
    if (sel) {
      sel.innerHTML = "";
      (conn.providers || []).forEach(function (p) {
        var o = document.createElement("option");
        o.value = p.id;
        o.textContent = p.label + " (" + (p.status || "?") + ")";
        if (p.id === conn.connection) o.selected = true;
        sel.appendChild(o);
      });
    }
    if (model) model.value = conn.model || "auto";
    if (cap) cap.value = String(g.spendCapUsd);
    if (rate) rate.value = String(g.rateLimitPerMin);
    if (fail) fail.checked = !!g.failClosed;
    if (dry) dry.checked = !!g.dryRunDefault;
    layer.hidden = false;
  }

  function closeConnectionsSheet() {
    var layer = $("evolver-conn-layer");
    if (layer) layer.hidden = true;
  }

  function saveConnectionsSheet() {
    var conn = loadConn();
    var g = loadGuard();
    var sel = $("evolver-conn-select");
    var model = $("evolver-conn-model");
    var cap = $("evolver-guard-cap");
    var rate = $("evolver-guard-rate");
    var fail = $("evolver-guard-fail");
    var dry = $("evolver-guard-dry");
    if (sel) conn.connection = sel.value;
    if (model) conn.model = model.value || "auto";
    if (cap) g.spendCapUsd = Number(cap.value) || 0;
    if (rate) g.rateLimitPerMin = Number(rate.value) || 0;
    if (fail) g.failClosed = !!fail.checked;
    if (dry) g.dryRunDefault = !!dry.checked;
    localStorage.setItem(STORAGE_CONN, JSON.stringify(conn));
    localStorage.setItem(STORAGE_GUARD, JSON.stringify(g));
    closeConnectionsSheet();
    refreshGuardChip();
  }

  function refreshGuardChip() {
    var chip = $("evolver-guardrails-chip");
    if (!chip) return;
    var g = loadGuard();
    chip.textContent =
      "Guardrails · cap $" +
      g.spendCapUsd +
      " · " +
      g.rateLimitPerMin +
      "/min · " +
      (g.failClosed ? "fail-closed" : "fail-open");
    chip.title =
      "EVOLVER guardrails - spend cap, rate limit, fail-closed. Kelkboom gate held for later.";
  }

  function wireToggles(root) {
    var tokexBtn = root.querySelector("#tokex-toggle");
    var tokexPanel = root.querySelector("#tokex-panel");
    if (tokexBtn && tokexPanel) {
      tokexBtn.addEventListener("click", function () {
        var open = tokexPanel.hidden;
        tokexPanel.hidden = !open;
        tokexBtn.setAttribute("aria-expanded", open ? "true" : "false");
        if (open) renderTokexDetail($("tokex-detail"), loadTokex());
      });
    }

    var evBtn = root.querySelector("#evolver-toggle");
    var evPanel = root.querySelector("#evolver-panel");
    if (evBtn && evPanel) {
      evBtn.addEventListener("click", function () {
        var open = evPanel.hidden;
        evPanel.hidden = !open;
        evBtn.setAttribute("aria-expanded", open ? "true" : "false");
        root.classList.toggle("evolver-open", open);
      });
    }

    var connBtn = root.querySelector("#evolver-btn-connections");
    if (connBtn) connBtn.addEventListener("click", openConnectionsSheet);

    var guardChip = root.querySelector("#evolver-guardrails-chip");
    if (guardChip) guardChip.addEventListener("click", openConnectionsSheet);
  }

  function ensureDock() {
    var inner = document.querySelector("#runs-rail .runs-inner");
    if (!inner) return null;
    var dock = $("evolver-dock");
    if (
      dock &&
      (!dock.querySelector("#evolver-btn-spunkworx") ||
        (dock.querySelector("#evolver-btn-connections strong") &&
          dock.querySelector("#evolver-btn-connections strong").textContent !== "ConneX") ||
        (dock.querySelector("#evolver-btn-refinex .evolver-blurb") &&
          dock.querySelector("#evolver-btn-refinex .evolver-blurb").textContent.indexOf("API option") < 0))
    ) {
      dock.remove();
      dock = null;
    }
    if (dock) return dock;

    dock = document.createElement("div");
    dock.id = "evolver-dock";
    dock.className = "evolver-dock";
    dock.innerHTML =
      '<div class="slide-section tokex-section">' +
      '<button type="button" class="section-label tokex-toggle" id="tokex-toggle" aria-expanded="false" title="TOKEX - Token Expenditure">' +
      '<span class="rail-head-caret" aria-hidden="true">▸</span><span class="rail-head-label">TOKEX</span>' +
      "</button>" +
      '<div id="tokex-panel" class="tokex-panel" hidden><div id="tokex-detail" class="tokex-detail"></div></div>' +
      "</div>" +
      '<div class="slide-section evolver-section">' +
      '<button type="button" class="section-label evolver-toggle rail-head-evolver" id="evolver-toggle" aria-expanded="false" title="EVOLVER - code refinement loop; nests RefineX and SpunkworX">' +
      '<span class="rail-head-caret" aria-hidden="true">▸</span><span class="rail-head-label">EVOLVER</span>' +
      "</button>" +
      '<div id="evolver-panel" class="evolver-panel" hidden>' +
      '<button type="button" class="evolver-child" id="evolver-btn-refinex" title="RefineX - Paid/Bring-your-own API option under EVOLVER. Memo-driven code refine with spend caps.">' +
      "<strong>RefineX</strong>" +
      "<span class=\"evolver-blurb\">Paid/Bring-your-own API option. Hydra memos drive patches via linked models - inherits EVOLVER spend caps and rate limits.</span>" +
      "</button>" +
      '<button type="button" class="evolver-child" id="evolver-btn-spunkworx" title="SpunkworX - freemium Mixture of Experts option under EVOLVER">' +
      "<strong>SpunkworX</strong>" +
      "<span class=\"evolver-blurb\">Freemium MoE (Mixture of Experts) option. Staged Delphic rounds: generate → peer critique → strongest final → patch proposal only (no silent git write).</span>" +
      "</button>" +
      '<button type="button" class="evolver-child evolver-child-link" id="evolver-btn-connections" title="ConneX - choose provider, model, and fallback order for RefineX and SpunkworX">' +
      "<strong>ConneX</strong>" +
      "<span class=\"evolver-blurb\">One connection sheet for both options - provider status, model, fallback order.</span>" +
      "</button>" +
      '<button type="button" class="evolver-guardrails-chip" id="evolver-guardrails-chip" title="EVOLVER guardrails - spend caps, rate limits, fail-closed">Guardrails</button>' +
      "</div></div>";

    inner.appendChild(dock);
    wireToggles(dock);
    refreshGuardChip();
    return dock;
  }

  function ensureConnLayer() {
    var prior = $("evolver-conn-layer");
    if (prior) prior.remove();
    var layer = document.createElement("div");
    layer.id = "evolver-conn-layer";
    layer.className = "evolver-conn-layer";
    layer.hidden = true;
    layer.innerHTML =
      '<div class="evolver-conn-card" role="dialog" aria-modal="true" aria-labelledby="evolver-conn-title">' +
      '<div class="evolver-conn-head">' +
      '<h2 id="evolver-conn-title">EVOLVER ConneX</h2>' +
      '<button type="button" class="evolver-conn-close" id="evolver-conn-close" title="Close">×</button>' +
      "</div>" +
      '<p class="evolver-conn-lead">Link the models RefineX and SpunkworX may call. Guardrails below block spend and writes until you set safe limits.</p>' +
      '<div class="evolver-field">' +
      "<strong>Connection</strong>" +
      '<span class="evolver-blurb">Which provider path is active - freemium SpunkworX route or paid RefineX BYO keys (i.e. wire in your own Codex or Claude or Devin or Coder APIs).</span>' +
      '<select id="evolver-conn-select"></select></div>' +
      '<div class="evolver-field">' +
      "<strong>Model</strong>" +
      '<span class="evolver-blurb">Default model id for that connection. Use auto to let the router pick within the option.</span>' +
      '<input id="evolver-conn-model" type="text" placeholder="auto" autocomplete="off" /></div>' +
      "<hr />" +
      '<p class="evolver-conn-sub">Guardrails</p>' +
      '<div class="evolver-field">' +
      "<strong>Spend cap (USD)</strong>" +
      '<span class="evolver-blurb">Hard ceiling for EVOLVER agent spend this session. Routes stop when the cap would be exceeded.</span>' +
      '<input id="evolver-guard-cap" type="number" min="0" step="1" /></div>' +
      '<div class="evolver-field">' +
      "<strong>Rate limit / min</strong>" +
      '<span class="evolver-blurb">Max model or tool calls per minute. Stops runaway agent loops from hammering providers.</span>' +
      '<input id="evolver-guard-rate" type="number" min="1" step="1" /></div>' +
      '<div class="evolver-field evolver-field-check">' +
      '<label class="evolver-check"><input id="evolver-guard-fail" type="checkbox" /> Fail closed without caps</label>' +
      '<span class="evolver-blurb">If spend or rate caps are missing or zero, refuse to run rather than allowing unbounded calls.</span></div>' +
      '<div class="evolver-field evolver-field-check">' +
      '<label class="evolver-check"><input id="evolver-guard-dry" type="checkbox" /> Dry-run default (no silent prod writes)</label>' +
      '<span class="evolver-blurb">Propose patches only. No automatic git write or production apply until you explicitly approve.</span></div>' +
      '<div class="evolver-conn-actions">' +
      '<button type="button" class="evolver-conn-save" id="evolver-conn-save">Save</button>' +
      '<button type="button" class="evolver-conn-cancel" id="evolver-conn-cancel">Cancel</button>' +
      "</div></div>";
    document.body.appendChild(layer);
    $("evolver-conn-close").addEventListener("click", closeConnectionsSheet);
    $("evolver-conn-cancel").addEventListener("click", closeConnectionsSheet);
    $("evolver-conn-save").addEventListener("click", saveConnectionsSheet);
    layer.addEventListener("click", function (e) {
      if (e.target === layer) closeConnectionsSheet();
    });
  }

  function boot() {
    ensureDock();
    ensureConnLayer();
  }

  /* Public: let RefineX / SpunkworX routers record sealed TOKEX later */
  window.EvalathanEvolver = {
    loadTokex: loadTokex,
    saveTokex: saveTokex,
    recordRun: function (partial) {
      var t = loadTokex();
      Object.keys(partial || {}).forEach(function (k) {
        t[k] = partial[k];
      });
      t.lifetime_runs = Number(t.lifetime_runs || 0) + 1;
      t.lifetime_total = Number(t.lifetime_total || 0) + Number(t.net_total || 0);
      t.lifetime_saved = Number(t.lifetime_saved || 0) + Number(t.seismo_saved || 0);
      if (t.lifetime_total > 0) {
        t.lifetime_pct = (100 * t.lifetime_saved) / (t.lifetime_total + t.lifetime_saved);
      }
      saveTokex(t);
      var detail = $("tokex-detail");
      if (detail && $("tokex-panel") && !$("tokex-panel").hidden) {
        renderTokexDetail(detail, t);
      }
      return t;
    },
    openConnections: openConnectionsSheet,
    remount: boot,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
