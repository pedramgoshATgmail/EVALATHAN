(function () {
  const GLOSS_SEARCH =
    "https://htmlpreview.github.io/?https://raw.githubusercontent.com/pedramgoshATgmail/EVALATHAN/cde53cbc5d66c631b88d202acd5f56bee9c23b26/docs/glossary.html";
  const GLOSS_MD = "https://github.com/pedramgoshATgmail/EVALATHAN/blob/main/GLOSSARY.md";
  const anchor = (id) => GLOSS_MD + "#user-content-" + id;
  const app = document.getElementById("app-screen");

  /* word-white = white glyphs for dark grounds; word-black = black glyphs for light grounds */
  /* Hydra evaler order is life-cycle (GLOSSARY), not alphabetical */
  const ENGINES = [
    {
      id: "hydra",
      label: "HYDRA",
      wordOnDark: "assets/hydra-word-white.png",
      wordOnLight: "assets/hydra-word-black.png",
      art: "assets/hydra-logo.png",
      blurbs:
        "Hydra engine conducts 16 static evalers (non-exhaustive).\nEach evaler reports its own life-cycle gate.\nA blank is not a fail and not a zero.",
      evalers: [
        "devly", "archly", "codely", "refactorly", "mixly", "runly", "levi", "menschly",
        "tokely", "pressly", "triadly", "chorely", "trajectly", "warrantly", "domly", "stackly",
      ].map((id) => ({
        id,
        label: id === "levi" ? "Levi" : id[0].toUpperCase() + id.slice(1),
        href: anchor(id),
        later: false,
      })),
    },
    {
      id: "dehydrus",
      label: "DEHYDRUS",
      wordOnDark: "assets/dehydrus-word-white.png",
      wordOnLight: "assets/dehydrus-word-black.png",
      art: "assets/dehydrus-logo.png",
      blurbs:
        "Dehydrus engine conducts 8 physical world models (not wired in currently).\nLuDaTs (Limited-universe Data Test sets) rooms under PRETRUWs stay off Hydra's vector.\nA missing world stays deferred.",
      evalers: [
        "copernly", "keplerly", "galileoly", "darwinly", "mendly", "einsteinly", "curcuriely", "newtonly",
      ].map((id) => ({
        id,
        label: id === "curcuriely" ? "CurCuriely" : id[0].toUpperCase() + id.slice(1),
        href: anchor(id),
        later: false,
      })),
    },
    {
      id: "benchrex",
      label: "BENCHREX",
      wordOnDark: "assets/benchrex-word-white.png",
      wordOnLight: "assets/benchrex-word-black.png",
      art: "assets/benchrex-logo.png",
      blurbs:
        "Benchrex engine conducts 10 Benchlux cells (3 not wired in currently).\nSeven criterion cells check whether a claimed benchmark is still fit to cite.\nAssessly, Reportly, and Notifyly stay deferred.",
      evalers: [
        { id: "saturly", label: "Saturly", href: GLOSS_MD, later: false },
        { id: "contamly", label: "Contamly", href: GLOSS_MD, later: false },
        { id: "skewly", label: "Skewly", href: GLOSS_MD, later: false },
        { id: "annotly", label: "Annotly", href: GLOSS_MD, later: false },
        { id: "obsoletely", label: "Obsoletely", href: GLOSS_MD, later: false },
        { id: "assumly", label: "Assumly", href: GLOSS_MD, later: false },
        { id: "driftly", label: "Driftly", href: GLOSS_MD, later: false },
        { id: "assessly", label: "Assessly", href: GLOSS_MD, later: true },
        { id: "reportly", label: "Reportly", href: GLOSS_MD, later: true },
        { id: "notifyly", label: "Notifyly", href: GLOSS_MD, later: true },
      ],
    },
    {
      id: "biasrex",
      label: "BIASREX",
      wordOnDark: "assets/biasrex-word-white.png",
      wordOnLight: "assets/biasrex-word-black.png",
      art: null,
      blurbs:
        "Biasrex engine conducts 6 bias cells (2 not wired in currently).\nFilterly, Meaningly, Hastely, and Memoryly are artifact-backed gates.\nConfirmly and Automately stay deferred.",
      evalers: [
        { id: "filterly", label: "Filterly", href: GLOSS_MD, later: false },
        { id: "meaningly", label: "Meaningly", href: GLOSS_MD, later: false },
        { id: "hastely", label: "Hastely", href: GLOSS_MD, later: false },
        { id: "memoryly", label: "Memoryly", href: GLOSS_MD, later: false },
        { id: "confirmly", label: "Confirmly", href: GLOSS_MD, later: true },
        { id: "automately", label: "Automately", href: GLOSS_MD, later: true },
      ],
    },
  ];

  const SPLASH = {
    label: "EVALATHAN",
    art: "assets/evalathan-dragon.png",
    blurbs:
      "40 current evals, 4 routing engines.\nHydra engine conducts 16 static evalers (non-exhaustive).\nDehydrus engine conducts 8 physical world models (not wired in currently).\nBenchrex engine conducts 10 Benchlux cells (3 not wired in currently).\nBiasrex engine conducts 6 bias cells (2 not wired in currently).",
  };

  let activeId = "hydra";
  let openId = null;
  let past = loadPast();
  let userPickedEngine = false;

  function loadPast() {
    try {
      return JSON.parse(localStorage.getItem("evalathan_past_runs") || "[]");
    } catch (e) {
      return [];
    }
  }
  function savePast() {
    localStorage.setItem("evalathan_past_runs", JSON.stringify(past.slice(0, 40)));
  }

  function theme() {
    return document.documentElement.getAttribute("data-theme") || "black";
  }
  function setTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    localStorage.setItem("evalathan_theme", t);
    document.querySelectorAll(".theme-btn").forEach((b) => {
      b.classList.toggle("is-on", b.getAttribute("data-theme-set") === t);
    });
    renderEngines();
    renderHero();
  }

  function engine(id) {
    return ENGINES.find((e) => e.id === id) || ENGINES[0];
  }

  function wordSrc(e) {
    return theme() === "white" ? e.wordOnLight : e.wordOnDark;
  }

  function toggleSide(side) {
    const cls = side === "engines" ? "engines-open" : "runs-open";
    const open = !app.classList.contains(cls);
    app.classList.toggle(cls, open);
    const btn = document.getElementById(side === "engines" ? "btn-toggle-engines" : "btn-toggle-runs");
    const panel = document.getElementById(side === "engines" ? "slideout" : "runs-rail");
    if (btn) btn.setAttribute("aria-expanded", String(open));
    if (panel) panel.setAttribute("aria-hidden", String(!open));
  }

  function renderEngines() {
    const root = document.getElementById("engine-stack");
    root.innerHTML = "";
    ENGINES.forEach((e) => {
      const block = document.createElement("div");
      block.className = "engine-block";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "engine-btn" + (e.id === activeId ? " active" : "");
      btn.title = e.label + " - router engine";
      const img = document.createElement("img");
      img.src = wordSrc(e);
      img.alt = e.label;
      btn.appendChild(img);
      btn.addEventListener("click", () => {
        activeId = e.id;
        userPickedEngine = true;
        openId = openId === e.id ? null : e.id;
        renderEngines();
        renderHero();
      });
      block.appendChild(btn);
      if (openId === e.id) {
        const sub = document.createElement("div");
        sub.className = "engine-sub";
        e.evalers.forEach((ev) => {
          if (ev.later) {
            const s = document.createElement("span");
            s.className = "later";
            s.textContent = ev.label + " (later)";
            s.title = "Teased - not shipped yet";
            sub.appendChild(s);
          } else {
            const a = document.createElement("a");
            a.href = ev.href;
            a.target = "_blank";
            a.rel = "noopener noreferrer";
            a.textContent = ev.label;
            a.title = ev.label + " - glossary";
            sub.appendChild(a);
          }
        });
        block.appendChild(sub);
      }
      root.appendChild(block);
    });
  }

  function renderHero() {
    const title = document.getElementById("splash-title");
    const art = document.getElementById("splash-art");
    const slot = document.querySelector(".splash-art-slot");
    const blurbs = document.getElementById("blurbs");
    const view = userPickedEngine ? engine(activeId) : SPLASH;
    const artKey = userPickedEngine ? activeId : "evalathan";
    title.textContent = view.label;
    blurbs.textContent = view.blurbs;
    if (slot) {
      slot.className = "splash-art-slot art-" + artKey;
    }
    if (view.art) {
      art.src = view.art;
      art.alt = view.label;
      art.classList.remove("is-blank");
    } else {
      art.src =
        "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
      art.alt = "";
      art.classList.add("is-blank");
    }
  }

  function renderPast(filter) {
    const list = document.getElementById("past-list");
    const q = String(filter || "").trim().toLowerCase();
    const rows = past.filter((r) => !q || JSON.stringify(r).toLowerCase().includes(q));
    document.getElementById("past-count").textContent = "(" + past.length + ")";
    list.innerHTML = "";
    if (!rows.length) {
      const li = document.createElement("li");
      li.className = "is-empty";
      li.textContent = "No past evaluation runs yet.";
      list.appendChild(li);
      return;
    }
    rows.forEach((r) => {
      const li = document.createElement("li");
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = r.title + "\n" + r.when + " · " + r.engine + " · " + r.summary;
      b.addEventListener("click", () => paintResults(r.cells || [], r.target || ""));
      li.appendChild(b);
      list.appendChild(li);
    });
  }

  function paintResults(cells, target) {
    const box = document.getElementById("results");
    box.innerHTML = "";
    if (target) document.getElementById("target-input").value = target;
    cells.forEach((c) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chip " + (c.status || "deferred");
      btn.innerHTML = "<strong>" + escapeHtml(c.name) + "</strong><span>" + escapeHtml(c.blurb) + "</span>";
      btn.addEventListener("click", () => window.open(c.href || GLOSS_MD, "_blank", "noopener,noreferrer"));
      box.appendChild(btn);
    });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function mockEvaluate(target) {
    const e = engine(activeId);
    const cells = e.evalers
      .filter((ev) => !ev.later)
      .map((ev, i) => ({
        name: ev.label,
        status: i % 5 === 0 ? "deferred" : "pass",
        blurb:
          activeId === "dehydrus"
            ? "Looking for a sealed world file; blank stays deferred."
            : activeId === "benchrex"
              ? "Criterion check teased - evidence pack later."
              : activeId === "biasrex"
                ? "Bias cell teased - artifact gate later."
                : "Life-cycle gate scanned (local preview).",
        href: ev.href,
      }));
    const deferred = cells.filter((c) => c.status === "deferred").length;
    past.unshift({
      title: target || "(no path)",
      when: new Date().toLocaleString(),
      engine: e.label,
      summary: cells.length + " cells · " + deferred + " deferred",
      target: target || "",
      cells,
    });
    savePast();
    renderPast(document.getElementById("past-search").value);
    paintResults(cells, target);
    if (!app.classList.contains("runs-open")) toggleSide("runs");
  }

  document.getElementById("btn-toggle-engines").addEventListener("click", (e) => {
    e.preventDefault();
    toggleSide("engines");
  });
  document.getElementById("btn-toggle-runs").addEventListener("click", (e) => {
    e.preventDefault();
    toggleSide("runs");
  });
  document.getElementById("btn-browse").addEventListener("click", () => {
    document.getElementById("folder-picker").click();
  });
  document.getElementById("folder-picker").addEventListener("change", (ev) => {
    const files = ev.target.files;
    if (!files || !files.length) return;
    const path = files[0].webkitRelativePath || files[0].name;
    document.getElementById("target-input").value = String(path).split("/")[0] || path;
  });
  document.getElementById("btn-eval").addEventListener("click", () => {
    mockEvaluate(document.getElementById("target-input").value.trim());
  });
  document.getElementById("btn-new").addEventListener("click", () => {
    document.getElementById("target-input").value = "";
    document.getElementById("results").innerHTML = "";
  });
  document.getElementById("past-search").addEventListener("input", (e) => renderPast(e.target.value));
  document.getElementById("btn-home").addEventListener("click", () => {
    userPickedEngine = false;
    openId = null;
    renderEngines();
    renderHero();
  });
  document.getElementById("btn-gloss").addEventListener("click", () => {
    window.open(GLOSS_SEARCH, "_blank", "noopener,noreferrer");
  });
  document.getElementById("btn-selfbelt").addEventListener("click", () => {
    window.open(anchor("selfbelt"), "_blank", "noopener,noreferrer");
  });
  document.querySelectorAll(".theme-btn").forEach((b) => {
    b.addEventListener("click", () => setTheme(b.getAttribute("data-theme-set")));
  });

  app.classList.remove("engines-open", "runs-open");
  document.getElementById("btn-toggle-engines").setAttribute("aria-expanded", "false");
  document.getElementById("btn-toggle-runs").setAttribute("aria-expanded", "false");
  document.getElementById("slideout").setAttribute("aria-hidden", "true");
  document.getElementById("runs-rail").setAttribute("aria-hidden", "true");
  setTheme(theme());
  renderPast();
})();
