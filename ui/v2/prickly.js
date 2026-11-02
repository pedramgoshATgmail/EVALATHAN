/* PRICKLY - L&R + JaPoP (Just-a-Professional-or-Partnerable). Desk popup, FUSS-simple. */
(function () {
  "use strict";

  const STORAGE_KEY = "evalathan.prickly.v1";
  const DURATION_NOTE =
    "Soft guidance (not a hard gate): about 3 weeks of dense timestamped comms is a provisional window; " +
    "about 6 months is a stronger pattern window. Longer runs are optional. " +
    "A blank or undated upload is deferred - not a fail and not a zero. " +
    "Cite-side: Buhler et al. 2021 relationship-satisfaction meta-analysis uses a 6-month minimum lag between assessments; " +
    "couple-communication meta-analyses treat multi-month windows as the useful pattern unit - not a hire cut.";

  const els = {};
  let banks = { dev: null, japop: null };
  let state = {
    step: "home",
    testId: null,
    profile: {},
    items: [],
    idx: 0,
    answers: {},
    startedAt: null,
    elapsedMs: 0,
    tick: null,
    result: null,
  };

  function $(id) {
    return document.getElementById(id);
  }

  function bindEls() {
    els.layer = $("prickly-layer");
    els.panel = els.layer && els.layer.querySelector(".prickly-panel");
    els.close = $("prickly-close");
    els.home = $("prickly-home");
    els.profile = $("prickly-profile");
    els.sit = $("prickly-sit");
    els.static = $("prickly-static");
    els.result = $("prickly-result");
    els.countdown = $("prickly-countdown");
    els.countNum = $("prickly-countdown-num");
  }

  function showOnly(id) {
    ["prickly-home", "prickly-profile", "prickly-sit", "prickly-static", "prickly-result", "prickly-countdown"].forEach(
      function (sid) {
        const node = $(sid);
        if (node) node.hidden = sid !== id;
      }
    );
  }

  function openPanel() {
    if (!els.layer) return;
    els.layer.hidden = false;
    goHome();
  }

  function closePanel() {
    if (state.tick) {
      window.clearInterval(state.tick);
      state.tick = null;
    }
    if (els.layer) els.layer.hidden = true;
  }

  function goHome() {
    state.step = "home";
    state.testId = null;
    state.result = null;
    showOnly("prickly-home");
  }

  function loadBanks() {
    return Promise.all([
      fetch("assets/prickly-dev-tf-bank.json")
        .then(function (r) {
          return r.json();
        })
        .then(function (j) {
          banks.dev = j;
        }),
      fetch("assets/japop-lr-tf-bank.json")
        .then(function (r) {
          return r.json();
        })
        .then(function (j) {
          banks.japop = j;
        }),
    ]).catch(function () {
      /* banks optional offline; sitters still see error on start */
    });
  }

  function readProfile() {
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

  function pickItems(testId) {
    const pack = testId === "japop-lr" ? banks.japop : banks.dev;
    if (!pack || !pack.items || !pack.items.length) return [];
    const list = pack.items.slice();
    for (let i = list.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const t = list[i];
      list[i] = list[j];
      list[j] = t;
    }
    return list.slice(0, Math.min(10, list.length));
  }

  function beginProfile(testId) {
    state.testId = testId;
    state.step = "profile";
    const title = $("prickly-profile-title");
    if (title) {
      title.textContent =
        testId === "japop-lr"
          ? "JaPoP L&R - who is sitting?"
          : testId === "japop-static"
            ? "JaPoP Static - who is assessing?"
            : "Prickly Developer L&R - who is sitting?";
    }
    const hint = $("prickly-profile-hint");
    if (hint) {
      hint.textContent =
        testId === "japop-static"
          ? "These checkboxes gate the static read. Then upload timestamped comms."
          : "These checkboxes are context for the timed True / False sitting. They do not change the answer key.";
    }
    const nextLabel = $("prickly-profile-next");
    if (nextLabel) {
      nextLabel.textContent = testId === "japop-static" ? "Continue to upload" : "Continue to timed test";
    }
    showOnly("prickly-profile");
  }

  function afterProfile() {
    state.profile = readProfile();
    if (state.testId === "japop-static") {
      state.step = "static";
      const note = $("prickly-duration-note");
      if (note) note.textContent = DURATION_NOTE;
      showOnly("prickly-static");
      return;
    }
    state.items = pickItems(state.testId);
    state.idx = 0;
    state.answers = {};
    if (!state.items.length) {
      window.alert("Question bank did not load. Check assets/prickly-*-tf-bank.json.");
      goHome();
      return;
    }
    startCountdown();
  }

  function startCountdown() {
    state.step = "countdown";
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
    const mm = String(Math.floor(s / 60)).padStart(2, "0");
    const ss = String(s % 60).padStart(2, "0");
    el.textContent = mm + ":" + ss;
  }

  function paintQuestion() {
    const item = state.items[state.idx];
    const prog = $("prickly-progress");
    const stem = $("prickly-stem");
    if (prog) prog.textContent = "Question " + (state.idx + 1) + " of " + state.items.length;
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

  function finishSitting() {
    if (state.tick) {
      window.clearInterval(state.tick);
      state.tick = null;
    }
    let correct = 0;
    const misses = [];
    state.items.forEach(function (it) {
      const a = state.answers[it.id];
      if (a === it.answer) correct += 1;
      else if (a !== undefined) misses.push(it.id);
    });
    const pct = Math.round((100 * correct) / state.items.length);
    const band = pct >= 80 ? "strong" : pct >= 60 ? "solid" : pct >= 40 ? "developing" : "priority gap";
    state.result = {
      testId: state.testId,
      profile: state.profile,
      percent: pct,
      correct: correct,
      total: state.items.length,
      band: band,
      misses: misses,
      elapsedMs: state.elapsedMs,
      at: new Date().toISOString(),
    };
    persistResult(state.result);
    paintResult(state.result, null);
  }

  function persistResult(res) {
    try {
      const prev = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{"sittings":[]}');
      prev.sittings = prev.sittings || [];
      prev.sittings.unshift(res);
      prev.sittings = prev.sittings.slice(0, 40);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(prev));
    } catch (e) {
      /* ignore */
    }
  }

  function paintResult(res, staticExtra) {
    showOnly("prickly-result");
    const title = $("prickly-result-title");
    const body = $("prickly-result-body");
    if (title) {
      title.textContent =
        res.testId === "japop-static"
          ? "JaPoP Static result"
          : res.testId === "japop-lr"
            ? "JaPoP L&R result"
            : "Prickly Developer L&R result";
    }
    if (!body) return;
    if (res.testId === "japop-static" && staticExtra) {
      body.innerHTML =
        "<p><strong>Partnerability lean:</strong> " +
        escapeHtml(staticExtra.lean) +
        " (" +
        staticExtra.score +
        "/100)</p>" +
        "<p>" +
        escapeHtml(staticExtra.summary) +
        "</p>" +
        "<ul>" +
        staticExtra.bullets.map(function (b) {
          return "<li>" + escapeHtml(b) + "</li>";
        }).join("") +
        "</ul>" +
        "<p class=\"prickly-soft\">" +
        escapeHtml(DURATION_NOTE) +
        "</p>";
      return;
    }
    const secs = Math.floor((res.elapsedMs || 0) / 1000);
    body.innerHTML =
      "<p><strong>Judgment:</strong> " +
      res.percent +
      "% (" +
      res.correct +
      " / " +
      res.total +
      ") - band <em>" +
      escapeHtml(res.band) +
      "</em></p>" +
      "<p><strong>Clock:</strong> " +
      secs +
      "s · confident misses: " +
      (res.misses || []).join(", ") +
      "</p>" +
      "<p class=\"prickly-soft\">Bands are feedback, not a hire cut. True/False replaced five-point Likert to reduce shade confusion (Prickly prompt 21 Nov 2026). Post-score ask-anything chat is on the roadmap - not wired yet.</p>";
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /** Parse timestamped lines: ISO date or YYYY-MM-DD, optional from: name, then text. */
  function parseComms(raw) {
    const lines = String(raw || "").split(/\r?\n/);
    const msgs = [];
    const re = /^(\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?)\s*[|,-]?\s*(?:from:\s*([^|]+)\|?)?\s*(.*)$/i;
    lines.forEach(function (line) {
      const t = line.trim();
      if (!t) return;
      const m = t.match(re);
      if (!m) return;
      const day = m[1].slice(0, 10);
      const from = (m[2] || "unknown").trim().toLowerCase() || "unknown";
      const text = (m[3] || "").trim();
      msgs.push({ day: day, from: from, text: text, ts: Date.parse(m[1].replace(" ", "T")) || Date.parse(day) });
    });
    msgs.sort(function (a, b) {
      return (a.ts || 0) - (b.ts || 0);
    });
    return msgs;
  }

  function scoreStatic(raw, selfLabel) {
    const msgs = parseComms(raw);
    if (!msgs.length) {
      return {
        lean: "deferred",
        score: null,
        summary: "No timestamped lines parsed. A blank or undated upload is deferred - not a fail and not a zero.",
        bullets: ["Use lines like: 2026-03-01 | from: alex | here is an idea…", DURATION_NOTE],
      };
    }
    const days = msgs.map(function (m) {
      return m.day;
    });
    const first = days[0];
    const last = days[days.length - 1];
    const spanMs = (Date.parse(last) || 0) - (Date.parse(first) || 0);
    const spanDays = Math.max(1, Math.round(spanMs / 86400000) + 1);
    const parties = {};
    msgs.forEach(function (m) {
      parties[m.from] = (parties[m.from] || 0) + 1;
    });
    const names = Object.keys(parties);
    const self = (selfLabel || "").trim().toLowerCase() || names[0] || "self";
    const otherNames = names.filter(function (n) {
      return n !== self && n !== "unknown";
    });
    const other = otherNames[0] || names.find(function (n) {
      return n !== self;
    }) || "other";
    const selfCount = parties[self] || 0;
    const otherCount = parties[other] || 0;
    let otherInit = 0;
    let prev = null;
    msgs.forEach(function (m) {
      if (m.from === other && (!prev || prev.from !== other)) otherInit += 1;
      prev = m;
    });
    let maxGap = 0;
    for (let i = 1; i < msgs.length; i++) {
      const g = ((msgs[i].ts || 0) - (msgs[i - 1].ts || 0)) / 86400000;
      if (g > maxGap) maxGap = g;
    }
    const replyRatio = selfCount ? otherCount / selfCount : 0;
    const initShare = msgs.length ? otherInit / Math.max(1, names.length > 1 ? Math.ceil(msgs.length / 4) : 1) : 0;
    let score = 50;
    score += Math.min(25, replyRatio * 25);
    score += Math.min(20, otherInit * 4);
    if (maxGap > 45) score -= 15;
    else if (maxGap > 21) score -= 8;
    if (spanDays < 21) score -= 10;
    else if (spanDays >= 180) score += 8;
    else if (spanDays >= 90) score += 4;
    score = Math.max(0, Math.min(100, Math.round(score)));
    let lean = "mixed";
    if (score >= 70) lean = "partner-leaning";
    else if (score <= 40) lean = "tool-leaning";
    const bullets = [
      "Span: " + spanDays + " days (" + first + " → " + last + ") across " + msgs.length + " dated lines.",
      "Counts: " + self + "=" + selfCount + ", " + other + "=" + otherCount + " · other thread starts≈" + otherInit + ".",
      "Longest gap between dated lines: ~" + Math.round(maxGap) + " days.",
      spanDays < 21
        ? "Window under ~3 weeks: treat as provisional only."
        : spanDays < 180
          ? "Window under ~6 months: useful, still maturing."
          : "Window ≥ ~6 months: stronger pattern window.",
      "Initiative ≠ proactiveness: reply-when-tapped can show integrity without partner-level volunteering.",
    ];
    return {
      lean: lean,
      score: score,
      summary:
        "Heuristic static read from timestamped volume and reciprocity - not a personality stamp and not a named-person dossier for publication.",
      bullets: bullets,
      spanDays: spanDays,
      replyRatio: replyRatio,
      initShare: initShare,
    };
  }

  function runStatic() {
    const raw = ($("prickly-comms") && $("prickly-comms").value) || "";
    const selfLabel = ($("prickly-self-label") && $("prickly-self-label").value) || "me";
    const extra = scoreStatic(raw, selfLabel);
    const res = {
      testId: "japop-static",
      profile: state.profile,
      percent: extra.score,
      band: extra.lean,
      at: new Date().toISOString(),
      static: extra,
    };
    state.result = res;
    persistResult(res);
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

    document.querySelectorAll("[data-prickly-test]").forEach(function (b) {
      b.addEventListener("click", function () {
        beginProfile(b.getAttribute("data-prickly-test"));
      });
    });
    const backHome = $("prickly-back-home");
    if (backHome) backHome.addEventListener("click", goHome);
    const backProf = $("prickly-back-profile");
    if (backProf)
      backProf.addEventListener("click", function () {
        if (state.testId) beginProfile(state.testId);
        else goHome();
      });
    const profNext = $("prickly-profile-next");
    if (profNext) profNext.addEventListener("click", afterProfile);

    const trueBtn = $("prickly-true");
    const falseBtn = $("prickly-false");
    if (trueBtn) trueBtn.addEventListener("click", function () {
      answer(true);
    });
    if (falseBtn) falseBtn.addEventListener("click", function () {
      answer(false);
    });

    const staticGo = $("prickly-static-run");
    if (staticGo) staticGo.addEventListener("click", runStatic);

    const again = $("prickly-again");
    if (again) again.addEventListener("click", goHome);
    const another = $("prickly-another");
    if (another) another.addEventListener("click", goHome);

    loadBanks();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else {
    wire();
  }
})();
