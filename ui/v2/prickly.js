/* PRICKLY - L&R + JaPoP (Just-a-Professional-or-Partnerable). Desk popup, local only. */
(function () {
  "use strict";

  const STORAGE_KEY = "evalathan.prickly.v1";
  const VARIANT_ROTATION_KEY = "evalathan.prickly.devVariantRot.v1";
  const DEV_VARIANT_NAMES = ["V1", "V2", "V3", "V4", "V5"];

  const els = {};
  let banks = { devRoles: null, devVariants: null, japopLevels: null };
  let state = {
    step: "home",
    testId: null,
    level: 1,
    maxLevel: 5,
    profile: {},
    items: [],
    idx: 0,
    answers: {},
    startedAt: null,
    elapsedMs: 0,
    tick: null,
    result: null,
    devVariant: null,
  };

  function $(id) {
    return document.getElementById(id);
  }

  const win = {
    dragging: false,
    resizing: false,
    dir: null,
    startX: 0,
    startY: 0,
    startL: 0,
    startT: 0,
    startW: 0,
    startH: 0,
    maximized: false,
    preMax: null,
  };

  function bindEls() {
    els.layer = $("prickly-layer");
    els.panel = $("prickly-panel") || (els.layer && els.layer.querySelector(".prickly-panel"));
    els.chrome = $("prickly-chrome");
    els.close = $("prickly-close");
    els.maxBtn = $("prickly-max");
    els.countNum = $("prickly-countdown-num");
    els.resultsList = $("prickly-results-list");
  }

  function clamp(n, lo, hi) {
    return Math.max(lo, Math.min(hi, n));
  }

  function panelRect() {
    const r = els.panel.getBoundingClientRect();
    return { left: r.left, top: r.top, width: r.width, height: r.height };
  }

  function placePanel(left, top, width, height, lockSize) {
    if (!els.panel) return;
    els.panel.classList.add("is-placed");
    els.panel.style.left = Math.round(left) + "px";
    els.panel.style.top = Math.round(top) + "px";
    els.panel.style.width = Math.round(width) + "px";
    if (lockSize) {
      els.panel.classList.add("is-sized");
      els.panel.style.height = Math.round(height) + "px";
    } else {
      els.panel.classList.remove("is-sized");
      els.panel.style.height = "auto";
    }
  }

  function centerPanel() {
    if (!els.panel || win.maximized) return;
    const w = Math.min(640, window.innerWidth * 0.94);
    els.panel.classList.add("is-placed");
    els.panel.classList.remove("is-sized");
    els.panel.style.width = Math.round(w) + "px";
    els.panel.style.height = "auto";
    els.panel.style.left = "0px";
    els.panel.style.top = "0px";
    const h = Math.min(els.panel.offsetHeight || 420, window.innerHeight * 0.92, 820);
    els.panel.style.left = Math.round((window.innerWidth - w) / 2) + "px";
    els.panel.style.top = Math.round(Math.max(8, (window.innerHeight - h) / 2)) + "px";
  }

  function setMaximized(on) {
    if (!els.panel) return;
    if (on) {
      if (!win.maximized) win.preMax = panelRect();
      win.maximized = true;
      els.panel.classList.add("is-maximized", "is-placed");
      if (els.maxBtn) els.maxBtn.title = "Restore";
    } else {
      win.maximized = false;
      els.panel.classList.remove("is-maximized");
      if (els.maxBtn) els.maxBtn.title = "Maximize / restore";
      if (win.preMax) {
        placePanel(win.preMax.left, win.preMax.top, win.preMax.width, win.preMax.height, true);
      } else {
        centerPanel();
      }
    }
  }

  function wireWindowChrome() {
    if (!els.panel) return;

    if (els.chrome) {
      els.chrome.addEventListener("pointerdown", function (e) {
        if (e.button !== 0) return;
        if (e.target.closest(".prickly-chrome-btn")) return;
        if (win.maximized) return;
        const r = panelRect();
        win.dragging = true;
        win.startX = e.clientX;
        win.startY = e.clientY;
        win.startL = r.left;
        win.startT = r.top;
        win.startW = r.width;
        win.startH = r.height;
        try {
          els.chrome.setPointerCapture(e.pointerId);
        } catch (err) {
          /* ignore */
        }
        e.preventDefault();
      });
      els.chrome.addEventListener("pointermove", function (e) {
        if (!win.dragging) return;
        const dx = e.clientX - win.startX;
        const dy = e.clientY - win.startY;
        const maxL = window.innerWidth - win.startW - 8;
        const maxT = window.innerHeight - 48;
        placePanel(
          clamp(win.startL + dx, 8, Math.max(8, maxL)),
          clamp(win.startT + dy, 8, Math.max(8, maxT)),
          win.startW,
          win.startH,
          els.panel.classList.contains("is-sized")
        );
      });
      function endDrag() {
        win.dragging = false;
      }
      els.chrome.addEventListener("pointerup", endDrag);
      els.chrome.addEventListener("pointercancel", endDrag);
      els.chrome.addEventListener("dblclick", function (e) {
        if (e.target.closest(".prickly-chrome-btn")) return;
        setMaximized(!win.maximized);
      });
    }

    if (els.maxBtn) {
      els.maxBtn.addEventListener("click", function () {
        setMaximized(!win.maximized);
      });
    }

    els.panel.querySelectorAll(".prickly-resize").forEach(function (handle) {
      handle.addEventListener("pointerdown", function (e) {
        if (e.button !== 0 || win.maximized) return;
        const r = panelRect();
        win.resizing = true;
        win.dir = handle.getAttribute("data-dir");
        win.startX = e.clientX;
        win.startY = e.clientY;
        win.startL = r.left;
        win.startT = r.top;
        win.startW = r.width;
        win.startH = r.height;
        try {
          handle.setPointerCapture(e.pointerId);
        } catch (err) {
          /* ignore */
        }
        e.preventDefault();
        e.stopPropagation();
      });
      handle.addEventListener("pointermove", function (e) {
        if (!win.resizing) return;
        const dx = e.clientX - win.startX;
        const dy = e.clientY - win.startY;
        const minW = 420;
        const minH = 320;
        let left = win.startL;
        let top = win.startT;
        let width = win.startW;
        let height = win.startH;
        const dir = win.dir || "";
        if (dir.indexOf("e") >= 0) width = clamp(win.startW + dx, minW, window.innerWidth - left - 8);
        if (dir.indexOf("s") >= 0) height = clamp(win.startH + dy, minH, window.innerHeight - top - 8);
        if (dir.indexOf("w") >= 0) {
          const nextW = clamp(win.startW - dx, minW, win.startL + win.startW - 8);
          left = win.startL + (win.startW - nextW);
          width = nextW;
        }
        if (dir.indexOf("n") >= 0) {
          const nextH = clamp(win.startH - dy, minH, win.startT + win.startH - 8);
          top = win.startT + (win.startH - nextH);
          height = nextH;
        }
        placePanel(left, top, width, height, true);
      });
      function endResize() {
        win.resizing = false;
        win.dir = null;
      }
      handle.addEventListener("pointerup", endResize);
      handle.addEventListener("pointercancel", endResize);
    });
  }

  function showOnly(id) {
    [
      "prickly-home",
      "prickly-dev-profile",
      "prickly-profile",
      "prickly-sit",
      "prickly-static",
      "prickly-result",
      "prickly-countdown",
    ].forEach(function (sid) {
      const node = $(sid);
      if (node) node.hidden = sid !== id;
    });
  }

  function setCountdownMode(on) {
    if (!els.panel) return;
    if (on) els.panel.classList.add("is-countdown");
    else els.panel.classList.remove("is-countdown");
  }

  function openPanel() {
    if (!els.layer) return;
    els.layer.hidden = false;
    if (!els.panel.classList.contains("is-placed") && !win.maximized) {
      centerPanel();
    }
    goHome();
  }

  function closePanel() {
    if (state.tick) {
      window.clearInterval(state.tick);
      state.tick = null;
    }
    setCountdownMode(false);
    if (els.layer) els.layer.hidden = true;
  }

  function goHome() {
    state.step = "home";
    state.testId = null;
    state.level = 1;
    state.result = null;
    state.devVariant = null;
    setCountdownMode(false);
    showOnly("prickly-home");
  }

  function loadStore() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{"saved":[]}');
    } catch (e) {
      return { saved: [] };
    }
  }

  function writeStore(store) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
    } catch (e) {
      /* ignore */
    }
  }

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function formatRailDate(iso) {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return String(iso || "");
    return (
      pad2(d.getMonth() + 1) +
      "/" +
      pad2(d.getDate()) +
      "/" +
      String(d.getFullYear()).slice(-2) +
      " " +
      pad2(d.getHours()) +
      ":" +
      pad2(d.getMinutes())
    );
  }

  function testTitle(res) {
    if (!res) return "PRICKLY";
    if (res.testId === "japop-lr") {
      return "JaPoP L&R · Level " + (res.level || 1);
    }
    if (res.testId === "japop-static") return "JaPoP Static";
    const kind = (res.profile && res.profile.kind) || "";
    const label =
      (banks.devRoles &&
        banks.devRoles.roles &&
        banks.devRoles.roles[kind] &&
        banks.devRoles.roles[kind].label) ||
      "Developer";
    const lv = res.level ? " · Level " + res.level : "";
    return "Dev L&R · " + label + lv;
  }

  function formatPricklyBlurb(res) {
    const dateStr = formatRailDate(res.savedAt || res.at);
    const title = testTitle(res);
    if (res.testId === "japop-static") {
      return dateStr + " - " + title + " · " + (res.band || "upload");
    }
    const pct = res.percent != null ? res.percent + "%" : "-";
    return dateStr + " - " + title + " · " + pct + " · " + (res.band || "");
  }

  function railGroupMeta(res) {
    /* Headings are evaler type only - specialty/level live in the blurb under each row */
    if (res.testId === "japop-lr") {
      return { key: "japop-lr", title: "JaPoP L&R" };
    }
    if (res.testId === "japop-static") {
      return { key: "japop-static", title: "JaPoP Static" };
    }
    return { key: "dev-lr", title: "Dev L&R" };
  }

  function appendPricklyRailNest(parent, label, kind, listEl, startCollapsed, targetTitle) {
    const nest = document.createElement("div");
    nest.className =
      "rail-nest" + (startCollapsed !== false ? " is-collapsed" : "");
    const head = document.createElement("button");
    head.type = "button";
    head.className =
      "rail-head" + (kind === "saved" ? " rail-head-saved" : " rail-head-latest");
    head.title = targetTitle ? label + targetTitle : label;
    head.setAttribute(
      "aria-expanded",
      nest.classList.contains("is-collapsed") ? "false" : "true"
    );
    /* Test-type titles (Dev L&R, JaPoP …) use accent lime - same as history targets */
    const labelHtml = targetTitle
      ? escapeHtml(label) +
        '<span class="rail-head-target">' +
        escapeHtml(targetTitle) +
        "</span>"
      : escapeHtml(label);
    head.innerHTML =
      '<span class="rail-head-caret" aria-hidden="true">▸</span>' +
      '<span class="rail-head-label">' +
      labelHtml +
      "</span>";
    head.addEventListener("click", function () {
      nest.classList.toggle("is-collapsed");
      head.setAttribute(
        "aria-expanded",
        nest.classList.contains("is-collapsed") ? "false" : "true"
      );
    });
    nest.appendChild(head);
    nest.appendChild(listEl);
    parent.appendChild(nest);
  }

  /* Same pattern as history right rail: nest opens to date rows; click opens GUI */
  function appendPricklyRunButton(ul, res, opts) {
    const li = document.createElement("li");
    if (opts && opts.latest) li.className = "is-latest";
    const b = document.createElement("button");
    b.type = "button";
    const blurb = formatPricklyBlurb(res);
    b.title = blurb;
    b.className = "run-entry-btn";
    b.innerHTML = '<span class="run-blurb">' + escapeHtml(blurb) + "</span>";
    b.addEventListener("click", function () {
      openSavedResult(res);
    });
    li.appendChild(b);
    ul.appendChild(li);
  }

  function appendPricklyEmptyLi(ul, text) {
    const li = document.createElement("li");
    li.className = "is-empty";
    li.textContent = text;
    ul.appendChild(li);
  }

  function renderSavedRail() {
    const host = els.resultsList || $("prickly-results-list");
    if (!host) return;
    const wasCollapsed = host.classList.contains("is-collapsed");
    host.innerHTML = "";
    if (wasCollapsed) host.classList.add("is-collapsed");
    const store = loadStore();
    const saved = store.saved || [];
    if (!saved.length) {
      const empty = document.createElement("p");
      empty.className = "prickly-rail-empty";
      empty.textContent = "No saved PRICKLY results yet.";
      host.appendChild(empty);
      return;
    }
    /* Same structure as history: per test-type rail-set with latest run + saved runs */
    const groups = [];
    const byKey = {};
    saved.forEach(function (res) {
      const meta = railGroupMeta(res);
      if (!byKey[meta.key]) {
        byKey[meta.key] = { key: meta.key, title: meta.title, items: [] };
        groups.push(byKey[meta.key]);
      }
      byKey[meta.key].items.push(res);
    });
    groups.forEach(function (g) {
      const wrap = document.createElement("div");
      wrap.className = "prickly-rail-set";
      const latest = g.items[0];
      const earlier = g.items.slice(1);

      const latestList = document.createElement("ul");
      latestList.className = "past-list past-list-latest";
      appendPricklyRunButton(latestList, latest, { latest: true });
      appendPricklyRailNest(
        wrap,
        "latest run for ",
        "latest",
        latestList,
        true,
        g.title
      );

      const savedList = document.createElement("ul");
      savedList.className = "past-list past-list-saved";
      if (!earlier.length) {
        appendPricklyEmptyLi(savedList, "No earlier saved runs yet.");
      } else {
        earlier.forEach(function (res) {
          appendPricklyRunButton(savedList, res, null);
        });
      }
      appendPricklyRailNest(
        wrap,
        "past runs for ",
        "saved",
        savedList,
        true,
        g.title
      );
      host.appendChild(wrap);
    });
  }

  function openSavedResult(res) {
    state.result = res;
    state.testId = res.testId;
    state.level = res.level || 1;
    state.profile = res.profile || {};
    if (els.layer) els.layer.hidden = false;
    paintResult(res, res.static || null, { fromSaved: true });
  }

  function loadBanks() {
    return Promise.all([
      fetch("assets/prickly-dev-banks-variants.json?v=8")
        .then(function (r) {
          return r.json();
        })
        .then(function (j) {
          banks.devVariants = j;
          if (j && j.maxLevel) state.maxLevel = Math.max(state.maxLevel || 5, j.maxLevel);
          /* Project V1 into legacy shape for any callers that still read banks.devRoles */
          if (j && j.variants && j.variants.V1) {
            banks.devRoles = {
              version: j.version,
              format: j.format,
              maxLevel: j.maxLevel || 5,
              roles: j.variants.V1.roles,
            };
          }
        })
        .catch(function () {
          /* Fallback to prior single-pack bank if variants missing */
          return fetch("assets/prickly-dev-banks.json?v=4")
            .then(function (r) {
              return r.json();
            })
            .then(function (j) {
              banks.devRoles = j;
              if (j && j.maxLevel) state.maxLevel = Math.max(state.maxLevel || 5, j.maxLevel);
            });
        }),
      fetch("assets/japop-lr-levels.json?v=2")
        .then(function (r) {
          return r.json();
        })
        .then(function (j) {
          banks.japopLevels = j;
          if (j && j.maxLevel) state.maxLevel = Math.max(state.maxLevel || 5, j.maxLevel);
        }),
    ]).catch(function () {
      /* banks optional offline */
    });
  }

  function loadVariantRotation() {
    try {
      return JSON.parse(localStorage.getItem(VARIANT_ROTATION_KEY) || "{}");
    } catch (e) {
      return {};
    }
  }

  function writeVariantRotation(map) {
    try {
      localStorage.setItem(VARIANT_ROTATION_KEY, JSON.stringify(map));
    } catch (e) {
      /* ignore */
    }
  }

  function chooseDevVariant(kind, level) {
    const key = String(kind || "software_engineer") + "|" + String(level || 1);
    const map = loadVariantRotation();
    const used = Array.isArray(map[key]) ? map[key].slice() : [];
    let pick = null;
    for (let i = 0; i < DEV_VARIANT_NAMES.length; i++) {
      if (used.indexOf(DEV_VARIANT_NAMES[i]) < 0) {
        pick = DEV_VARIANT_NAMES[i];
        break;
      }
    }
    if (!pick) {
      pick = used.length ? used[0] : "V1";
    }
    const next = used.filter(function (u) {
      return u !== pick;
    });
    next.push(pick);
    while (next.length > DEV_VARIANT_NAMES.length) next.shift();
    map[key] = next;
    writeVariantRotation(map);
    return pick;
  }

  function readJapopProfile() {
    return {
      role: ($("prickly-role") && $("prickly-role").value) || "",
      ageBand: ($("prickly-age") && $("prickly-age").value) || "",
      experience: ($("prickly-exp") && $("prickly-exp").value) || "",
      context: ($("prickly-context") && $("prickly-context").value) || "",
      howMet: ($("prickly-howmet") && $("prickly-howmet").value) || "",
      relation: ($("prickly-relation") && $("prickly-relation").value) || "",
      knownYears: ($("prickly-known") && $("prickly-known").value) || "",
    };
  }

  function readDevProfile() {
    return {
      kind: ($("prickly-dev-kind") && $("prickly-dev-kind").value) || "software_engineer",
      experience: ($("prickly-dev-exp") && $("prickly-dev-exp").value) || "",
      ageBand: ($("prickly-dev-age") && $("prickly-dev-age").value) || "",
      stack: ($("prickly-dev-stack") && $("prickly-dev-stack").value) || "",
      setting: ($("prickly-dev-setting") && $("prickly-dev-setting").value) || "",
    };
  }

  function shufflePick(items, n) {
    const list = (items || []).slice();
    for (let i = list.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const t = list[i];
      list[i] = list[j];
      list[j] = t;
    }
    return list.slice(0, Math.min(n, list.length));
  }

  function japopLevelPack(level) {
    const levels = banks.japopLevels && banks.japopLevels.levels;
    if (!levels) return null;
    return levels[String(level)] || null;
  }

  function devLevelPack(kind, level, variantName) {
    const vName = variantName || state.devVariant || "V1";
    const variants = banks.devVariants && banks.devVariants.variants;
    if (variants && variants[vName] && variants[vName].roles) {
      const role = variants[vName].roles[kind];
      if (role && role.levels) return role.levels[String(level)] || null;
    }
    const role = banks.devRoles && banks.devRoles.roles && banks.devRoles.roles[kind];
    if (!role) return null;
    if (role.levels) return role.levels[String(level)] || null;
    /* legacy flat items = level 1 only */
    if (level === 1 && role.items) {
      return { title: "Level 1", blurb: "", items: role.items };
    }
    return null;
  }

  function maxLevelFor(testId) {
    if (testId === "japop-lr") {
      return (banks.japopLevels && banks.japopLevels.maxLevel) || 5;
    }
    if (testId === "dev-lr") {
      return (
        (banks.devVariants && banks.devVariants.maxLevel) ||
        (banks.devRoles && banks.devRoles.maxLevel) ||
        5
      );
    }
    return 5;
  }

  function pickItems() {
    if (state.testId === "japop-lr") {
      const pack = japopLevelPack(state.level);
      if (!pack || !pack.items || !pack.items.length) return [];
      return shufflePick(pack.items, Math.min(10, pack.items.length));
    }
    const kind = (state.profile && state.profile.kind) || "software_engineer";
    /* One variant pack per sitting - 10 curated items; rotate V1-V5 across repeats */
    state.devVariant = chooseDevVariant(kind, state.level);
    const pack = devLevelPack(kind, state.level, state.devVariant);
    if (!pack || !pack.items || !pack.items.length) return [];
    /* Serve the full curated set of 10; light shuffle so order is not always slot 1→10 */
    return shufflePick(pack.items, Math.min(10, pack.items.length));
  }

  function beginFlow(testId) {
    state.testId = testId;
    state.level = 1;
    if (testId === "dev-lr") {
      state.step = "dev-profile";
      showOnly("prickly-dev-profile");
      return;
    }
    state.step = "profile";
    const title = $("prickly-profile-title");
    if (title) {
      title.textContent =
        testId === "japop-static"
          ? "JaPoP Static - show the paper trail"
          : "JaPoP L&R - are you and him/her a match?";
    }
    const hint = $("prickly-profile-hint");
    if (hint) {
      if (testId === "japop-static") {
        hint.innerHTML =
          "JaPoP (Just-a-Professional-or-Partnerable) Static is the evidence pass. Upload dated emails, texts/WhatsApp, and audio of your discussions so you can see whether this person acts like a partner - or only like a professional who replies when tapped. " +
          '<span class="prickly-hint-cta">Answer who you are below, then continue to the upload slots.</span>';
      } else {
        hint.innerHTML =
          "JaPoP (Just-a-Professional-or-Partnerable) is a Live & Realtime (L&R) questionnaire to assess whether the person you are considering as a co-founder or partner is suitable - or whether they are mainly a professional who is not fit for equal partnership. " +
          '<span class="prickly-hint-cta">Answer who you are below, then take a timed True/False. Each Next Level Test gets harder.</span>';
      }
    }
    const nextLabel = $("prickly-profile-next");
    if (nextLabel) {
      nextLabel.textContent = testId === "japop-static" ? "Continue to uploads" : "Continue to timed test";
    }
    showOnly("prickly-profile");
  }

  function afterDevProfile() {
    state.profile = readDevProfile();
    state.level = 1; /* kind picker always starts Level 1; Next Level skips this screen */
    startTimedFromProfile();
  }

  function afterJapopProfile() {
    state.profile = readJapopProfile();
    if (state.testId === "japop-static") {
      state.step = "static";
      showOnly("prickly-static");
      return;
    }
    state.level = 1; /* profile gate always starts Level 1; Next Level skips this screen */
    startTimedFromProfile();
  }

  function startTimedFromProfile() {
    state.items = pickItems();
    state.idx = 0;
    state.answers = {};
    if (!state.items.length) {
      window.alert("Question bank did not load for this selection.");
      goHome();
      return;
    }
    startCountdown();
  }

  function startCountdown() {
    state.step = "countdown";
    setCountdownMode(true);
    showOnly("prickly-countdown");
    let n = 3;
    if (els.countNum) els.countNum.textContent = String(n);
    const step = function () {
      if (n <= 0) {
        beginSitting();
        return;
      }
      if (els.countNum) els.countNum.textContent = String(n);
      n -= 1;
      window.setTimeout(step, 700);
    };
    step();
  }

  function beginSitting() {
    state.step = "sit";
    setCountdownMode(false);
    state.startedAt = Date.now();
    state.elapsedMs = 0;
    if (state.tick) window.clearInterval(state.tick);
    state.tick = window.setInterval(function () {
      state.elapsedMs = Date.now() - state.startedAt;
      paintClock();
    }, 250);
    showOnly("prickly-sit");
    paintQuestion();
  }

  function paintClock() {
    const el = $("prickly-clock");
    if (!el) return;
    const s = Math.floor(state.elapsedMs / 1000);
    el.textContent = pad2(Math.floor(s / 60)) + ":" + pad2(s % 60);
  }

  function paintQuestion() {
    const item = state.items[state.idx];
    const prog = $("prickly-progress");
    const stem = $("prickly-stem");
    let label = "Question " + (state.idx + 1) + " of " + state.items.length;
    if (state.testId === "japop-lr" || state.testId === "dev-lr") {
      label = "Level " + state.level + " · " + label;
    }
    if (prog) prog.textContent = label;
    if (stem) stem.textContent = item ? item.text : "";
    paintClock();
  }

  function answer(val) {
    const item = state.items[state.idx];
    if (!item) return;
    state.answers[item.id] = val;
    if (state.idx + 1 >= state.items.length) {
      finishSitting();
      return;
    }
    state.idx += 1;
    paintQuestion();
  }

  function bandCopy(band) {
    if (band === "strong") {
      return "Strong read. Most answers matched the key. Keep watching real behavior over time - one run is not a permanent stamp.";
    }
    if (band === "solid") {
      return "Solid read. You caught many of the traps, with a few misses. Review the misses before you trust a hire or partner call.";
    }
    if (band === "developing") {
      return "Developing. About half the judgment calls matched the key. Slow down on partner-vs-tool claims until the pattern is clearer.";
    }
    return "Priority gap. Many answers missed the key. Treat this as a learning pass, not a verdict on any named person.";
  }

  function finishSitting() {
    if (state.tick) {
      window.clearInterval(state.tick);
      state.tick = null;
    }
    let correct = 0;
    const misses = [];
    const missDetails = [];
    state.items.forEach(function (it) {
      const a = state.answers[it.id];
      if (a === it.answer) {
        correct += 1;
        return;
      }
      if (a === undefined) return;
      misses.push(it.id);
      missDetails.push({
        id: it.id,
        text: it.text,
        yours: a,
        correct: it.answer,
      });
    });
    const pct = Math.round((100 * correct) / state.items.length);
    const band = pct >= 80 ? "strong" : pct >= 60 ? "solid" : pct >= 40 ? "developing" : "priority gap";
    const pack =
      state.testId === "japop-lr"
        ? japopLevelPack(state.level)
        : state.testId === "dev-lr"
          ? devLevelPack(
              (state.profile && state.profile.kind) || "software_engineer",
              state.level,
              state.devVariant
            )
          : null;
    state.result = {
      id: "prk-" + Date.now().toString(36),
      testId: state.testId,
      level: state.testId === "japop-lr" || state.testId === "dev-lr" ? state.level : null,
      levelTitle: pack ? pack.title : null,
      variant: state.testId === "dev-lr" ? state.devVariant || null : null,
      profile: state.profile,
      percent: pct,
      correct: correct,
      total: state.items.length,
      band: band,
      misses: misses,
      missDetails: missDetails,
      elapsedMs: state.elapsedMs,
      at: new Date().toISOString(),
      savedAt: null,
    };
    paintResult(state.result, null);
  }

  function tfWord(v) {
    return v === true ? "True" : v === false ? "False" : String(v);
  }

  function missReviewHtml(res) {
    const details = res.missDetails || [];
    if (!details.length) {
      return "<p>No misses on this pass - every answered item matched the key.</p>";
    }
    const items = details
      .map(function (m, i) {
        return (
          '<li class="prickly-miss-item">' +
          '<p class="prickly-miss-q"><strong>Miss ' +
          (i + 1) +
          ".</strong> " +
          escapeHtml(m.text) +
          "</p>" +
          '<p class="prickly-miss-a">Your answer: <strong>' +
          escapeHtml(tfWord(m.yours)) +
          "</strong></p>" +
          '<p class="prickly-miss-a">Correct answer: <strong>' +
          escapeHtml(tfWord(m.correct)) +
          "</strong></p>" +
          "</li>"
        );
      })
      .join("");
    return (
      '<p class="prickly-result-kicker">Questions missed</p>' +
      '<ol class="prickly-miss-list">' +
      items +
      "</ol>"
    );
  }

  function fileNames(inputId) {
    const node = $(inputId);
    if (!node || !node.files || !node.files.length) return [];
    return Array.prototype.map.call(node.files, function (f) {
      return { name: f.name, size: f.size, type: f.type || "" };
    });
  }

  function scoreStaticUploads() {
    const slots = [
      {
        key: "email",
        label: "Email PDFs",
        files: fileNames("prickly-up-email"),
        notes: (($("prickly-note-email") && $("prickly-note-email").value) || "").trim(),
      },
      {
        key: "texts",
        label: "Texts / WhatsApp PDF",
        files: fileNames("prickly-up-texts"),
        notes: (($("prickly-note-texts") && $("prickly-note-texts").value) || "").trim(),
      },
      {
        key: "audio",
        label: "Audio",
        files: fileNames("prickly-up-audio"),
        notes: (($("prickly-note-audio") && $("prickly-note-audio").value) || "").trim(),
      },
      {
        key: "other",
        label: "Other",
        files: fileNames("prickly-up-other"),
        notes: (($("prickly-note-other") && $("prickly-note-other").value) || "").trim(),
      },
    ];

    const withFiles = slots.filter(function (s) {
      return s.files.length > 0;
    });
    if (!withFiles.length) {
      return {
        lean: "deferred",
        score: null,
        summary: "No files selected yet. Add at least one upload, then submit again.",
        bullets: [
          "Email PDF with visible dates and times.",
          "Texts / WhatsApp PDF with timestamps.",
          "Audio plus a note naming who is speaking.",
        ],
        slots: slots,
      };
    }

    const bullets = [];
    let noted = 0;
    withFiles.forEach(function (s) {
      const names = s.files
        .map(function (f) {
          return f.name;
        })
        .join(", ");
      bullets.push(s.label + ": " + s.files.length + " file(s) - " + names);
      if (s.notes) {
        noted += 1;
        bullets.push("Notes for " + s.label + ": " + s.notes);
      } else {
        bullets.push("Notes for " + s.label + ": missing - add who / context when you can.");
      }
    });

    const audio = slots.find(function (s) {
      return s.key === "audio";
    });
    if (audio && audio.files.length && !audio.notes) {
      bullets.push("Audio was uploaded without a speaker note - clarify who is talking before treating this as complete.");
    }

    const score = Math.min(100, 40 + withFiles.length * 12 + noted * 8);
    let lean = "received";
    if (withFiles.length >= 2 && noted >= 1) lean = "ready-for-review";
    if (withFiles.length === 1 && noted === 0) lean = "thin-upload";

    return {
      lean: lean,
      score: score,
      summary:
        "Uploads received on this device. File names and notes are stored with this result. Full automatic scoring from PDF and audio contents is not wired yet.",
      bullets: bullets,
      slots: slots,
    };
  }

  function kindLabel(kind) {
    const role = banks.devRoles && banks.devRoles.roles && banks.devRoles.roles[kind];
    return (role && role.label) || kind || "Developer";
  }

  function listComparable(res) {
    const store = loadStore();
    const saved = (store.saved || []).filter(function (r) {
      return !!r.savedAt;
    });
    if (!res) return [];
    /* Dev L&R: compare across expertise kinds (TA vs Data Engineer, etc.). */
    if (res.testId === "dev-lr") {
      return saved
        .filter(function (r) {
          return r.testId === "dev-lr";
        })
        .slice()
        .sort(function (a, b) {
          return new Date(a.savedAt || a.at || 0) - new Date(b.savedAt || b.at || 0);
        });
    }
    /* JaPoP / Static: same family */
    return saved
      .filter(function (r) {
        return r.testId === res.testId;
      })
      .slice()
      .sort(function (a, b) {
        return new Date(a.savedAt || a.at || 0) - new Date(b.savedAt || b.at || 0);
      });
  }

  function syncResultDock(res) {
    const del = $("prickly-delete");
    const cmp = $("prickly-compare");
    const save = $("prickly-save");
    const saved = !!(res && res.savedAt);
    if (del) del.hidden = !saved;
    if (save) save.hidden = saved;
    const peers = res ? listComparable(res) : [];
    if (cmp) cmp.hidden = peers.length < 2;
  }

  function askDelete(fn) {
    if (typeof window.askEvalathanDeleteConfirm === "function") {
      window.askEvalathanDeleteConfirm(fn);
      return;
    }
    if (window.confirm("Are you sure you want to delete?")) fn();
  }

  function deleteCurrentSaved() {
    if (!state.result || !state.result.savedAt || !state.result.id) return;
    const id = state.result.id;
    askDelete(function () {
      const store = loadStore();
      store.saved = (store.saved || []).filter(function (r) {
        return r.id !== id;
      });
      writeStore(store);
      renderSavedRail();
      state.result = null;
      goHome();
    });
  }

  function bandRank(band) {
    const map = { strong: 4, solid: 3, developing: 2, "priority gap": 1 };
    return map[band] || 0;
  }

  /** Composite for cross-expertise rank: harder levels count, then %. */
  function expertiseScore(r) {
    const lv = r.level || 1;
    const pct = typeof r.percent === "number" ? r.percent : 0;
    const missN = (r.missDetails || r.misses || []).length;
    return lv * 1000 + pct * 10 - missN;
  }

  function bestSitPerKind(peers) {
    const byKind = {};
    peers.forEach(function (r) {
      const kind = (r.profile && r.profile.kind) || "unknown";
      if (!byKind[kind] || expertiseScore(r) > expertiseScore(byKind[kind])) {
        byKind[kind] = r;
      }
    });
    return byKind;
  }

  function buildCompareFeedback(peers, focus) {
    const newest = focus || peers[peers.length - 1];
    const isDev = newest.testId === "dev-lr";
    const rows = peers.map(function (r) {
      return {
        when: formatRailDate(r.savedAt || r.at),
        title: testTitle(r),
        kind: (r.profile && r.profile.kind) || "",
        kindLabel: isDev ? kindLabel((r.profile && r.profile.kind) || "") : "",
        level: r.level || 1,
        percent: r.percent,
        band: r.band,
        correct: r.correct,
        total: r.total,
        secs: Math.floor((r.elapsedMs || 0) / 1000),
        missN: (r.missDetails || r.misses || []).length,
        id: r.id,
        composite: expertiseScore(r),
      };
    });

    const bullets = [];
    const kinds = {};
    peers.forEach(function (r) {
      const k = (r.profile && r.profile.kind) || (r.testId === "japop-lr" ? "japop" : r.testId);
      kinds[k] = (kinds[k] || 0) + 1;
    });
    const kindCount = Object.keys(kinds).length;

    bullets.push(
      "Compared " +
        peers.length +
        " saved result(s)" +
        (isDev
          ? " across " + kindCount + " Dev L&R expertise area(s). Cross-area compare is allowed - Technical Architect vs Data Engineer is valid."
          : " in the same JaPoP / Static family.") +
        " Proof basis: stored scores, levels, miss counts, and clocks on this device - not a free-form guess."
    );

    if (isDev && kindCount >= 2) {
      const best = bestSitPerKind(peers);
      const ranked = Object.keys(best)
        .map(function (k) {
          return { kind: k, sit: best[k], score: expertiseScore(best[k]) };
        })
        .sort(function (a, b) {
          return b.score - a.score;
        });
      const top = ranked[0];
      const second = ranked[1];
      bullets.push(
        "Agentic read - strongest expertise on file: <strong>" +
          escapeHtml(kindLabel(top.kind)) +
          "</strong> (best result Level " +
          (top.sit.level || 1) +
          ", " +
          (top.sit.percent != null ? top.sit.percent + "%" : "-") +
          ", band " +
          escapeHtml(top.sit.band || "") +
          ", misses " +
          (top.sit.missDetails || top.sit.misses || []).length +
          ")."
      );
      if (second) {
        const dPct =
          (top.sit.percent != null ? top.sit.percent : 0) - (second.sit.percent != null ? second.sit.percent : 0);
        const dLv = (top.sit.level || 1) - (second.sit.level || 1);
        let why =
          "Why over <strong>" +
          escapeHtml(kindLabel(second.kind)) +
          "</strong>: composite rank uses Level first (harder banks weigh more), then %, then fewer misses.";
        if (dLv > 0) {
          why +=
            " You reached a higher level in " +
            escapeHtml(kindLabel(top.kind)) +
            " (L" +
            (top.sit.level || 1) +
            " vs L" +
            (second.sit.level || 1) +
            ").";
        } else if (dLv === 0 && dPct !== 0) {
          why +=
            " Same peak level, but " +
            escapeHtml(kindLabel(top.kind)) +
            " scored " +
            (dPct > 0 ? dPct + " points higher" : Math.abs(dPct) + " points different") +
            ".";
        } else if (dLv < 0 && (top.sit.percent || 0) >= (second.sit.percent || 0)) {
          why +=
            " Even with level nuance, the stored % and miss pattern still favored " +
            escapeHtml(kindLabel(top.kind)) +
            " on the composite.";
        }
        bullets.push(why);
      }
      bullets.push(
        "Expertise ranking (best result each): " +
          ranked
            .map(function (x, i) {
              return (
                i +
                1 +
                ") " +
                escapeHtml(kindLabel(x.kind)) +
                " L" +
                (x.sit.level || 1) +
                " " +
                (x.sit.percent != null ? x.sit.percent + "%" : "-")
              );
            })
            .join(" · ") +
          "."
      );
      bullets.push(
        "Precedent: a high % on Level 1 in one craft does not beat a solid % on a higher level in another craft - harder banks count more in this compare."
      );
    } else {
      /* same-lane / same-family progression */
      const sameKind = peers.filter(function (r) {
        if (!isDev) return true;
        return ((r.profile && r.profile.kind) || "") === ((newest.profile && newest.profile.kind) || "");
      });
      const prev = sameKind.length >= 2 ? sameKind[sameKind.length - 2] : null;
      if (prev && newest.percent != null && prev.percent != null) {
        const d = newest.percent - prev.percent;
        const sameLevel = (newest.level || 1) === (prev.level || 1);
        if (sameLevel) {
          bullets.push(
            d === 0
              ? "Objective: score tied the prior saved result at the same level."
              : "Objective: score " +
                  (d > 0 ? "rose " + d : "fell " + Math.abs(d)) +
                  " points vs the prior saved result at Level " +
                  (newest.level || 1) +
                  "."
          );
        } else if ((newest.level || 1) > (prev.level || 1)) {
          bullets.push(
            "Precedent: level-up from L" +
              (prev.level || 1) +
              " to L" +
              (newest.level || 1) +
              ". Raw % is not 1:1 comparable; holding or rising % after a harder bank is stronger proof."
          );
        }
      }
      if (kindCount < 2 && isDev) {
        bullets.push(
          "Tip: save results in other Dev L&R kinds (e.g. Data Engineer and Technical Architect) to unlock cross-expertise ranking."
        );
      }
    }

    bullets.push(
      "Coverage: " +
        peers.length +
        " saved result(s)" +
        (isDev
          ? " · kinds: " +
            Object.keys(kinds)
              .map(function (k) {
                return escapeHtml(kindLabel(k)) + "=" + kinds[k];
              })
              .join(", ")
          : "") +
        "."
    );
    bullets.push(
      "Reminder: these are judgment-practice scores. Real partner or hire decisions still need dated real-world behavior."
    );

    return { rows: rows, bullets: bullets, newest: newest, crossExpertise: isDev && kindCount >= 2 };
  }

  function paintCompareView(res) {
    const peers = listComparable(res);
    if (peers.length < 2) {
      window.alert("Need at least two saved PRICKLY results to compare (they can be different Dev L&R expertise areas).");
      return;
    }
    const pack = buildCompareFeedback(peers, res);
    showOnly("prickly-result");
    const title = $("prickly-result-title");
    const body = $("prickly-result-body");
    if (title) title.textContent = pack.crossExpertise ? "PRICKLY Compare - across expertise" : "PRICKLY Compare";
    if (!body) return;

    const showKind = peers.some(function (r) {
      return r.testId === "dev-lr";
    });
    const tableRows = pack.rows
      .map(function (r) {
        const focus = r.id === (pack.newest && pack.newest.id);
        return (
          "<tr" +
          (focus ? ' class="is-focus"' : "") +
          ">" +
          "<td>" +
          escapeHtml(r.when) +
          "</td>" +
          (showKind ? "<td>" + escapeHtml(r.kindLabel || "-") + "</td>" : "") +
          "<td>" +
          escapeHtml(r.title) +
          "</td>" +
          "<td>L" +
          r.level +
          "</td>" +
          "<td>" +
          (r.percent != null ? r.percent + "%" : "-") +
          "</td>" +
          "<td>" +
          escapeHtml(r.band || "") +
          "</td>" +
          "<td>" +
          r.missN +
          "</td>" +
          "<td>" +
          r.secs +
          "s</td>" +
          "</tr>"
        );
      })
      .join("");

    body.innerHTML =
      '<div class="prickly-result-block">' +
      '<p class="prickly-result-kicker">Compare table</p>' +
      '<p class="prickly-result-sub">' +
      (pack.crossExpertise
        ? "All saved Dev L&R results (any expertise), oldest to newest. Focus row is the result you opened."
        : "Saved results in this family, oldest to newest. Focus row is the result you opened.") +
      "</p>" +
      '<table class="prickly-compare-table"><thead><tr>' +
      "<th>When</th>" +
      (showKind ? "<th>Expertise</th>" : "") +
      "<th>Test</th><th>Level</th><th>Score</th><th>Band</th><th>Misses</th><th>Clock</th>" +
      "</tr></thead><tbody>" +
      tableRows +
      "</tbody></table>" +
      "</div>" +
      '<div class="prickly-result-block">' +
      '<p class="prickly-result-kicker">Agentic evaler - which area you are stronger in (and why)</p>' +
      "<ul class=\"prickly-result-list\">" +
      pack.bullets
        .map(function (b) {
          return "<li>" + b + "</li>";
        })
        .join("") +
      "</ul>" +
      "</div>" +
      '<p><button type="button" class="prickly-back" id="prickly-compare-back">← Back to result</button></p>';

    const back = $("prickly-compare-back");
    if (back) {
      back.addEventListener("click", function () {
        paintResult(state.result, state.result && state.result.static, { fromSaved: !!state.result.savedAt });
      });
    }
    syncResultDock(res);
    const nextBtn = $("prickly-another");
    if (nextBtn) nextBtn.hidden = true;
    const delBtn = $("prickly-delete");
    if (delBtn) delBtn.hidden = !res.savedAt;
  }

  function paintResult(res, staticExtra, opts) {
    showOnly("prickly-result");
    const title = $("prickly-result-title");
    const body = $("prickly-result-body");
    const status = $("prickly-save-status");
    const nextBtn = $("prickly-another");
    if (status) {
      status.hidden = true;
      status.textContent = "";
    }
    syncResultDock(res);
    if (title) title.textContent = testTitle(res) + " - result";

    if (nextBtn) {
      if (res.testId === "japop-lr" || res.testId === "dev-lr") {
        nextBtn.hidden = false;
        const maxL = maxLevelFor(res.testId);
        const cur = res.level || 1;
        if (cur >= maxL) {
          nextBtn.textContent = "Retake Level " + maxL;
          nextBtn.title = "Retake the highest level (same hard bank)";
        } else {
          nextBtn.textContent = "Take Next Level Test";
          nextBtn.title = "Open Level " + (cur + 1) + " - harder, different questions";
        }
      } else {
        nextBtn.hidden = true;
      }
    }

    if (!body) return;

    if (res.testId === "japop-static") {
      const extra = staticExtra || res.static || {};
      body.innerHTML =
        '<div class="prickly-result-block">' +
        "<p class=\"prickly-result-kicker\">Upload status</p>" +
        "<p class=\"prickly-result-lead\">" +
        escapeHtml(extra.lean || res.band || "") +
        (extra.score != null ? " · provisional " + extra.score + "/100" : "") +
        "</p>" +
        "</div>" +
        '<div class="prickly-result-block">' +
        "<p>" +
        escapeHtml(extra.summary || "") +
        "</p>" +
        "</div>" +
        '<div class="prickly-result-block">' +
        "<p class=\"prickly-result-kicker\">What was attached</p>" +
        "<ul class=\"prickly-result-list\">" +
        (extra.bullets || [])
          .map(function (b) {
            return "<li>" + escapeHtml(b) + "</li>";
          })
          .join("") +
        "</ul>" +
        "</div>";
      return;
    }

    const secs = Math.floor((res.elapsedMs || 0) / 1000);
    const pack =
      res.testId === "japop-lr"
        ? japopLevelPack(res.level || 1)
        : res.testId === "dev-lr"
          ? devLevelPack((res.profile && res.profile.kind) || "software_engineer", res.level || 1)
          : null;
    const levelLine = pack
      ? "<p class=\"prickly-result-sub\">" +
        escapeHtml(pack.title || "Level " + (res.level || 1)) +
        ". " +
        escapeHtml(pack.blurb || "") +
        "</p>"
      : "";
    const variantLine =
      res.testId === "dev-lr" && res.variant
        ? "<p class=\"prickly-result-sub\">Question pack: " + escapeHtml(res.variant) + " of V1-V5</p>"
        : "";

    body.innerHTML =
      '<div class="prickly-result-block">' +
      "<p class=\"prickly-result-kicker\">Score</p>" +
      "<p class=\"prickly-result-lead\">" +
      res.percent +
      "% correct (" +
      res.correct +
      " of " +
      res.total +
      ")</p>" +
      "<p class=\"prickly-result-sub\">Band: <strong>" +
      escapeHtml(res.band) +
      "</strong></p>" +
      levelLine +
      variantLine +
      "</div>" +
      '<div class="prickly-result-block">' +
      "<p class=\"prickly-result-kicker\">What this means</p>" +
      "<p>" +
      escapeHtml(bandCopy(res.band)) +
      "</p>" +
      "</div>" +
      '<div class="prickly-result-block">' +
      "<p class=\"prickly-result-kicker\">Result details</p>" +
      "<p>Time on the clock: " +
      secs +
      " seconds.</p>" +
      "<p class=\"prickly-soft\">This is feedback for judgment practice - not a hire cut and not a stamp on a named person.</p>" +
      "</div>" +
      '<div class="prickly-result-block">' +
      missReviewHtml(res) +
      "</div>" +
      (opts && opts.fromSaved
        ? '<div class="prickly-result-block"><p class="prickly-soft">Opened from PRICKLY RESULTS.</p></div>'
        : "");
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function saveCurrentResult() {
    if (!state.result) return;
    const store = loadStore();
    store.saved = store.saved || [];
    const copy = Object.assign({}, state.result, {
      savedAt: new Date().toISOString(),
      id: state.result.id || "prk-" + Date.now().toString(36),
    });
    state.result = copy;
    store.saved = store.saved.filter(function (x) {
      return x.id !== copy.id;
    });
    store.saved.unshift(copy);
    store.saved = store.saved.slice(0, 60);
    writeStore(store);
    renderSavedRail();
    syncResultDock(state.result);
    const status = $("prickly-save-status");
    if (status) {
      status.hidden = false;
      status.textContent = "Saved under PRICKLY RESULTS on the left rail.";
    }
    /* nudge left rail open so the user sees it */
    const slide = $("slideout");
    const toggle = $("btn-toggle-engines");
    if (slide && slide.getAttribute("aria-hidden") === "true" && toggle) {
      toggle.click();
    }
  }

  function takeNextLevel() {
    if (state.testId !== "japop-lr" && state.testId !== "dev-lr") {
      goHome();
      return;
    }
    const maxL = maxLevelFor(state.testId);
    const cur = (state.result && state.result.level) || state.level || 1;
    const next = cur >= maxL ? maxL : cur + 1;
    state.level = next;
    state.devVariant = null; /* fresh pack rotation for the next level sitting */
    if (state.testId === "japop-lr") {
      state.profile = state.profile || readJapopProfile();
    } else {
      state.profile = state.profile || readDevProfile();
    }
    /* Guard: next bank must exist (probe V1); pickItems chooses the rotated variant */
    const kind = (state.profile && state.profile.kind) || "software_engineer";
    const pack =
      state.testId === "japop-lr"
        ? japopLevelPack(state.level)
        : devLevelPack(kind, state.level, "V1");
    if (!pack || !pack.items || !pack.items.length) {
      window.alert("Level " + state.level + " bank is missing. Staying on the previous level.");
      state.level = cur;
      return;
    }
    startTimedFromProfile();
  }

  function runStatic() {
    const extra = scoreStaticUploads();
    const res = {
      id: "prk-" + Date.now().toString(36),
      testId: "japop-static",
      profile: state.profile,
      percent: extra.score,
      band: extra.lean,
      at: new Date().toISOString(),
      savedAt: null,
      static: {
        lean: extra.lean,
        score: extra.score,
        summary: extra.summary,
        bullets: extra.bullets,
        slots: (extra.slots || []).map(function (s) {
          return { key: s.key, files: s.files, notes: s.notes };
        }),
      },
    };
    state.result = res;
    paintResult(res, extra);
  }

  function wire() {
    bindEls();
    if (!els.layer) return;

    const btn = $("btn-prickly");
    if (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        openPanel();
      });
    }
    if (els.close) els.close.addEventListener("click", closePanel);
    els.layer.addEventListener("click", function (e) {
      if (e.target === els.layer) closePanel();
    });
    wireWindowChrome();
    centerPanel();

    document.querySelectorAll("[data-prickly-test]").forEach(function (b) {
      b.addEventListener("click", function (e) {
        if (e.target && e.target.closest && e.target.closest("a.prickly-gloss-link")) {
          e.stopPropagation();
          return;
        }
        beginFlow(b.getAttribute("data-prickly-test"));
      });
    });
    document.querySelectorAll("#prickly-home a.prickly-gloss-link").forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.stopPropagation();
      });
    });

    const backHome = $("prickly-back-home");
    if (backHome) backHome.addEventListener("click", goHome);
    const backDev = $("prickly-dev-back");
    if (backDev) backDev.addEventListener("click", goHome);
    const backProf = $("prickly-back-profile");
    if (backProf) {
      backProf.addEventListener("click", function () {
        if (state.testId) beginFlow(state.testId);
        else goHome();
      });
    }

    const profNext = $("prickly-profile-next");
    if (profNext) profNext.addEventListener("click", afterJapopProfile);
    const devNext = $("prickly-dev-next");
    if (devNext) devNext.addEventListener("click", afterDevProfile);

    const trueBtn = $("prickly-true");
    const falseBtn = $("prickly-false");
    if (trueBtn)
      trueBtn.addEventListener("click", function () {
        answer(true);
      });
    if (falseBtn)
      falseBtn.addEventListener("click", function () {
        answer(false);
      });

    const staticGo = $("prickly-static-run");
    if (staticGo) staticGo.addEventListener("click", runStatic);

    const saveBtn = $("prickly-save");
    if (saveBtn) saveBtn.addEventListener("click", saveCurrentResult);
    const delBtn = $("prickly-delete");
    if (delBtn) delBtn.addEventListener("click", deleteCurrentSaved);
    const cmpBtn = $("prickly-compare");
    if (cmpBtn) {
      cmpBtn.addEventListener("click", function () {
        if (state.result) paintCompareView(state.result);
      });
    }
    const again = $("prickly-again");
    if (again) again.addEventListener("click", goHome);
    const another = $("prickly-another");
    if (another) another.addEventListener("click", takeNextLevel);

    const resultsHead = $("btn-prickly-results");
    if (resultsHead) {
      const list = els.resultsList || $("prickly-results-list");
      if (list && !list.classList.contains("is-collapsed")) {
        list.classList.add("is-collapsed");
      }
      resultsHead.setAttribute("aria-expanded", "false");
      resultsHead.addEventListener("click", function () {
        const host = els.resultsList || $("prickly-results-list");
        if (!host) return;
        host.classList.toggle("is-collapsed");
        const open = !host.classList.contains("is-collapsed");
        resultsHead.setAttribute("aria-expanded", open ? "true" : "false");
        if (open) renderSavedRail();
      });
    }

    loadBanks().then(function () {
      renderSavedRail();
    });
    renderSavedRail();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else {
    wire();
  }
})();
