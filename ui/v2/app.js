(function () {
  const GLOSS_SEARCH =
    "https://htmlpreview.github.io/?https://raw.githubusercontent.com/pedramgoshATgmail/EVALATHAN/cde53cbc5d66c631b88d202acd5f56bee9c23b26/docs/glossary.html";
  const GLOSS_MD = "https://github.com/pedramgoshATgmail/EVALATHAN/blob/main/GLOSSARY.md";
  const anchor = (id) => GLOSS_MD + "#user-content-" + id;

  const ENGINES = [
    {
      id: "hydra",
      label: "HYDRA",
      wordBlack: "assets/hydra-word-black.png",
      wordWhite: "assets/hydra-word-white.png",
      art: "assets/hydra-logo.png",
      showDragon: false,
      blurbs:
        "Routes sixteen software evalers across the product life cycle.\nEach evaler reports its own gate.\nA blank is not a fail and not a zero.",
      evalers: [
        "devly", "archly", "codely", "refactorly", "mixly", "runly", "levi", "menschly",
        "tokely", "pressly", "triadly", "chorely", "trajectly", "warrantly", "domly", "stackly",
      ].map((id) => ({ id, label: id[0].toUpperCase() + id.slice(1), href: anchor(id), later: false })),
    },
    {
      id: "dehydrus",
      label: "DEHYDRUS",
      wordBlack: "assets/dehydrus-word-black.png",
      wordWhite: "assets/dehydrus-word-white.png",
      art: "assets/hydra-logo.png",
      showDragon: false,
      blurbs:
        "Routes eight LuDaTs (Limited-universe Data Test sets) locked-past rooms under PRETRUWs (PREdiscovery TRuncated-Universes and Worlds).\nPhysical world-model and discovery claims stay off Hydra's vector.\nA missing world stays deferred.",
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
      wordBlack: "assets/benchrex-word-black.png",
      wordWhite: "assets/benchrex-word-white.png",
      art: null,
      showDragon: true,
      blurbs:
        "Deprecathan desk: Benchlux checks whether a claimed benchmark is still fit to cite.\nSeven criterion cells in v1 map saturation, contamination, skew, annotation error, obsolescence, assumptions, and drift.\nThree process cells (Assessly, Reportly, Notifyly) stay deferred for later.",
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
      wordBlack: "assets/biasrex-word-black.png",
      wordWhite: "assets/biasrex-word-white.png",
      art: null,
      showDragon: true,
      blurbs:
        "Four Benson-shaped bias cells for artifact-backed gates (Filterly, Meaningly, Hastely, Memoryly).\nDeferred cells stay blank - never one blended bias score.\nConfirmly and Automately stay deferred until interactive protocols ship.",
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

  let activeId = "hydra";
  let openId = "hydra";
  let past = loadPast();

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

  function renderEngines() {
    const light = theme() === "white";
    const root = document.getElementById("engines");
    root.innerHTML = "";
    ENGINES.forEach((e) => {
      const block = document.createElement("div");
      block.className = "engine-block";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "engine-btn" + (e.id === activeId ? " active" : "");
      const img = document.createElement("img");
      img.src = light ? e.wordWhite : e.wordBlack;
      img.alt = e.label;
      btn.appendChild(img);
      btn.addEventListener("click", () => {
        activeId = e.id;
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
    const e = engine(activeId);
    document.getElementById("blurbs").textContent = e.blurbs;
    const art = document.getElementById("hero-engine");
    const dragon = document.querySelector(".hero-dragon");
    if (e.art) {
      art.src = e.art;
      art.hidden = false;
      art.alt = e.label;
      dragon.hidden = true;
    } else {
      art.hidden = true;
      dragon.hidden = false;
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
      btn.title = "Open glossary for " + c.name;
      btn.addEventListener("click", () => {
        window.open(c.href || GLOSS_MD, "_blank", "noopener,noreferrer");
      });
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
      .slice(0, activeId === "hydra" ? 16 : activeId === "dehydrus" ? 8 : 7)
      .map((ev, i) => ({
        name: ev.label,
        status: i % 5 === 0 ? "deferred" : "pass",
        blurb:
          ev.later
            ? "Deferred - not a fail."
            : activeId === "dehydrus"
              ? "Looking for a sealed world file; blank stays deferred."
              : activeId === "benchrex"
                ? "Criterion check teased - evidence pack later."
                : activeId === "biasrex"
                  ? "Bias cell teased - artifact gate later."
                  : "Life-cycle gate scanned (local preview).",
        href: ev.href,
      }));
    const ran = cells.length;
    const deferred = cells.filter((c) => c.status === "deferred").length;
    const summary = ran + " cells · " + deferred + " deferred";
    const row = {
      title: target || "(no path)",
      when: new Date().toLocaleString(),
      engine: e.label,
      summary,
      target: target || "",
      cells,
    };
    past.unshift(row);
    savePast();
    renderPast(document.getElementById("past-search").value);
    paintResults(cells, target);
  }

  document.getElementById("btn-browse").addEventListener("click", () => {
    document.getElementById("folder-picker").click();
  });
  document.getElementById("folder-picker").addEventListener("change", (ev) => {
    const files = ev.target.files;
    if (!files || !files.length) return;
    const path = files[0].webkitRelativePath || files[0].name;
    const folder = String(path).split("/")[0] || path;
    document.getElementById("target-input").value = folder;
  });
  document.getElementById("btn-eval").addEventListener("click", () => {
    mockEvaluate(document.getElementById("target-input").value.trim());
  });
  document.getElementById("btn-new").addEventListener("click", () => {
    document.getElementById("target-input").value = "";
    document.getElementById("results").innerHTML = "";
  });
  document.getElementById("past-search").addEventListener("input", (e) => renderPast(e.target.value));
  document.getElementById("btn-gloss").addEventListener("click", () => {
    window.open(GLOSS_SEARCH, "_blank", "noopener,noreferrer");
  });
  document.getElementById("btn-selfbelt").addEventListener("click", () => {
    window.open(anchor("selfbelt"), "_blank", "noopener,noreferrer");
  });
  document.querySelectorAll(".theme-btn").forEach((b) => {
    b.addEventListener("click", () => setTheme(b.getAttribute("data-theme-set")));
  });

  setTheme(theme());
  renderPast();
})();
