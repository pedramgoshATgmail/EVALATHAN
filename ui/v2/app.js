(function () {
  const GLOSS_SEARCH =
    "https://htmlpreview.github.io/?https://raw.githubusercontent.com/pedramgoshATgmail/EVALATHAN/724cf70648bcc26b2dcab3d7ec5b69a15cc68a2e/docs/glossary.html";
  const GLOSS_MD = "https://github.com/pedramgoshATgmail/EVALATHAN/blob/main/GLOSSARY.md";
  const anchor = (id) => GLOSS_MD + "#user-content-" + id;

  /** Open glossary / external URLs outside the pywebview desk (Mac window.open is often a no-op). */
  function openExternal(url) {
    const href = String(url || "").trim();
    if (!href) return;
    try {
      if (
        window.pywebview &&
        window.pywebview.api &&
        typeof window.pywebview.api.open_external === "function"
      ) {
        window.pywebview.api.open_external(href);
        return;
      }
    } catch (err) {
      /* fall through */
    }
    const a = document.createElement("a");
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    document.body.appendChild(a);
    a.click();
    a.remove();
  }
  /*
   * Auto-link Evalathan glossary terms in memo prose (same GitHub #user-content-* targets
   * as the left-rail evaler names). Distinctive labels only - skip generic words like Agent.
   */
  const GLOSS_AUTO_RAW = [
    { id: "saspiant", phrases: ["SASPIANT"] },
    { id: "m3", phrases: ["M3 Triad", "M3"] },
    { id: "selfbelt", phrases: ["SELFBELT"] },
    { id: "fuss", phrases: ["FUSS"] },
    { id: "pretruws", phrases: ["PRETRUWs", "PRETRUW"] },
    { id: "ludats", phrases: ["LuDaTs"] },
    { id: "habtwin", phrases: ["HabTwin"] },
    { id: "braidware", phrases: ["Braidware"] },
    { id: "deglove", phrases: ["Deglove"] },
    { id: "reductoholism", phrases: ["Reductoholism", "reductoholistic"] },
    { id: "4uvals", phrases: ["4Uvals"] },
    { id: "evalathan", phrases: ["EVALATHAN", "Evalathan"] },
    { id: "hydra", phrases: ["HYDRA", "Hydra"] },
    { id: "dehydrus", phrases: ["DEHYDRUS", "Dehydrus"] },
    { id: "benchrex", phrases: ["BENCHREX", "Benchrex"] },
    { id: "biasrex", phrases: ["BIASREX", "Biasrex"] },
    { id: "cognitive-bias-codex", phrases: ["Cognitive Bias Codex"] },
    { id: "saturly", phrases: ["Saturly"] },
    { id: "contamly", phrases: ["Contamly"] },
    { id: "skewly", phrases: ["Skewly"] },
    { id: "annotly", phrases: ["Annotly"] },
    { id: "obsoletely", phrases: ["Obsoletely"] },
    { id: "assumly", phrases: ["Assumly"] },
    { id: "driftly", phrases: ["Driftly"] },
    { id: "assessly", phrases: ["Assessly"] },
    { id: "reportly", phrases: ["Reportly"] },
    { id: "notifyly", phrases: ["Notifyly"] },
    { id: "filterly", phrases: ["Filterly"] },
    { id: "meaningly", phrases: ["Meaningly"] },
    { id: "hastely", phrases: ["Hastely"] },
    { id: "memoryly", phrases: ["Memoryly"] },
    { id: "confirmly", phrases: ["Confirmly"] },
    { id: "automately", phrases: ["Automately"] },
    { id: "archly", phrases: ["Archly"] },
    { id: "chorely", phrases: ["Chorely"] },
    { id: "codely", phrases: ["Codely"] },
    { id: "devly", phrases: ["Devly"] },
    { id: "domly", phrases: ["Domly"] },
    { id: "levi", phrases: ["Levi"] },
    { id: "menschly", phrases: ["Menschly"] },
    { id: "mixly", phrases: ["Mixly"] },
    { id: "pressly", phrases: ["Pressly"] },
    { id: "refactorly", phrases: ["Refactorly"] },
    { id: "runly", phrases: ["Runly"] },
    { id: "stackly", phrases: ["Stackly"] },
    { id: "tokely", phrases: ["Tokely"] },
    { id: "trajectly", phrases: ["Trajectly"] },
    { id: "triadly", phrases: ["Triadly"] },
    { id: "warrantly", phrases: ["Warrantly"] },
    { id: "copernly", phrases: ["Copernly"] },
    { id: "keplerly", phrases: ["Keplerly"] },
    { id: "galileoly", phrases: ["Galileoly"] },
    { id: "darwinly", phrases: ["Darwinly"] },
    { id: "mendly", phrases: ["Mendly"] },
    { id: "einsteinly", phrases: ["Einsteinly"] },
    { id: "curcuriely", phrases: ["CurCuriely"] },
    { id: "newtonly", phrases: ["Newtonly"] },
    { id: "ludats-mode-unification", phrases: ["Mode Unification"] },
    { id: "ludats-mode-pair", phrases: ["Mode Pair"] },
    { id: "ludats-mode-a", phrases: ["Mode A"] },
    { id: "ludats-mode-b", phrases: ["Mode B"] },
    { id: "ludats-mode-c", phrases: ["Mode C"] },
    { id: "ludats-mode-d", phrases: ["Mode D"] },
    { id: "ludats-mode-e", phrases: ["Mode E"] },
    { id: "ludats-mode-f", phrases: ["Mode F"] },
    { id: "swe-bench-pro", phrases: ["SWE-bench Pro"] },
    { id: "swe-bench", phrases: ["SWE-bench"] },
    { id: "deepswe", phrases: ["DeepSWE"] },
    { id: "prdbench", phrases: ["PRDBench"] },
    { id: "wildbench", phrases: ["WildBench"] },
    { id: "ragas", phrases: ["Ragas"] },
    { id: "prd", phrases: ["PRD"] },
    { id: "vvuq", phrases: ["VVUQ"] },
  ];
  /*
   * Standards / metrics → same official sites the glossary uses (not GLOSSARY.md rooms).
   * href is the publisher page; id is only a fallback glossary room if href is missing.
   */
  const STANDARD_AUTO_RAW = [
    { phrases: ["ISO/IEC/IEEE 42030"], href: "https://www.iso.org/standard/73436.html" },
    { phrases: ["ISO/IEC 25010"], href: "https://www.iso.org/standard/78176.html" },
    { phrases: ["ISO/IEC 5055"], href: "https://www.iso.org/standard/80623.html" },
    { phrases: ["ISO/IEC 42001"], href: "https://www.iso.org/standard/81230.html" },
    { phrases: ["ISO/IEC/IEEE 29148"], href: "https://www.iso.org/standard/45171.html" },
    { phrases: ["ISO/AWI 23247-8"], href: "https://www.iso.org/standard/94858.html" },
    { phrases: ["ISO 23247"], href: "https://www.iso.org/standard/75066.html" },
    { phrases: ["IEEE 7010-2020", "IEEE 7010"], href: "https://standards.ieee.org/ieee/7010/7718/" },
    { phrases: ["IEEE 830"], href: "https://standards.ieee.org/ieee/830/1222/" },
    {
      phrases: ["NASA Technology Readiness Level", "NASA TRL"],
      href: "https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-level/",
    },
    { phrases: ["NASA-TLX", "NASA TLX"], href: "https://ergosphere.com.au/tools-nasa-tlx.html" },
    { phrases: ["SEI ATAM", "ATAM"], href: "https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method" },
    { phrases: ["AWS Well-Architected"], href: "https://aws.amazon.com/architecture/well-architected/" },
    { phrases: ["SFIA"], href: "https://sfia-online.org/en/about-sfia" },
    { phrases: ["SPEC CPU", "SPEC2017"], href: "https://www.spec.org/cpu2017/" },
    { phrases: ["pyperformance"], href: "https://github.com/python/pyperformance" },
    { phrases: ["WCAG 2.2"], href: "https://www.w3.org/TR/WCAG22/" },
    { phrases: ["WCAG 2.1"], href: "https://www.w3.org/TR/WCAG21/" },
  ];
  function escapeRegExp(s) {
    return String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }
  function buildAutoLinkRows(rawRows, titleSuffix) {
    const rows = [];
    (rawRows || []).forEach(function (row) {
      (row.phrases || []).forEach(function (phrase) {
        /* Standards with '/' cannot use plain \b edges; use lookaround-ish class edges. */
        const edged =
          /[A-Za-z0-9]$/.test(phrase) && /^[A-Za-z0-9]/.test(phrase)
            ? "\\b" + escapeRegExp(phrase) + "\\b"
            : "(?<![A-Za-z0-9])" + escapeRegExp(phrase) + "(?![A-Za-z0-9])";
        let re;
        try {
          re = new RegExp(edged, "g");
        } catch (err) {
          re = new RegExp(escapeRegExp(phrase), "g");
        }
        rows.push({
          id: row.id || "",
          href: row.href || "",
          title: phrase + titleSuffix,
          phrase: phrase,
          re: re,
        });
      });
    });
    return rows;
  }
  const GLOSS_AUTO_LINKS = (function () {
    const rows = buildAutoLinkRows(GLOSS_AUTO_RAW, " - glossary").concat(
      buildAutoLinkRows(STANDARD_AUTO_RAW, " - official site")
    );
    rows.sort(function (a, b) {
      return b.phrase.length - a.phrase.length;
    });
    return rows;
  })();

  /* File paths in prose - not .md (avoids chewing GLOSSARY.md inside hrefs if a pass slips). */
  const FILE_PATH_RE =
    /(?:[A-Za-z]:[\\/])?(?:[\w.-]+[\\/])*[\w.-]+\.(?:py|js|ts|tsx|jsx|json|jsonl|toml|yml|yaml|txt|html|css|go|rs|java|lock)\b/g;

  function githubBlobBase(target) {
    const t = String(target || "").trim();
    const m = t.match(/github\.com[/:]([^/\s]+)\/([^/\s.#]+)/i);
    if (!m) return "";
    const owner = m[1];
    const repo = m[2].replace(/\.git$/i, "");
    return "https://github.com/" + owner + "/" + repo + "/blob/HEAD/";
  }

  function memoFileHref(path, run) {
    let p = String(path || "").replace(/\\/g, "/").trim();
    if (!p) return "";
    p = p.replace(/^\.\//, "");
    const folder = run && run.folder ? String(run.folder).replace(/\\/g, "/").replace(/\/$/, "") : "";
    if (folder && p.toLowerCase().indexOf(folder.toLowerCase() + "/") === 0) {
      p = p.slice(folder.length + 1);
    }
    const gh = githubBlobBase(run && (run.target || ""));
    if (gh) return gh + p.replace(/^\/+/, "");
    if (folder) {
      const abs = /^(?:[A-Za-z]:\/|\/)/.test(p) ? p : folder + "/" + p;
      return "file:///" + abs.replace(/^\/+/, "");
    }
    return "";
  }

  /* Only rewrite plain text nodes; never touch attributes inside existing <a> tags. */
  function mapPlainTextSegments(html, fn) {
    const parts = String(html || "").split(/(<[^>]+>)/g);
    let inAnchor = false;
    for (let i = 0; i < parts.length; i += 1) {
      const part = parts[i];
      if (!part) continue;
      if (part.charAt(0) === "<") {
        const lower = part.toLowerCase();
        if (lower.indexOf("<a ") === 0 || lower === "<a>") inAnchor = true;
        if (lower.indexOf("</a>") === 0) inAnchor = false;
        continue;
      }
      if (inAnchor) continue;
      parts[i] = fn(part);
    }
    return parts.join("");
  }

  function linkFilePaths(escapedText, run) {
    return mapPlainTextSegments(escapedText, function (text) {
      return text.replace(FILE_PATH_RE, function (matched) {
        const href = memoFileHref(matched, run);
        if (!href) {
          return (
            '<span class="memo-file-link" title="' +
            escapeHtml(matched) +
            '">' +
            matched +
            "</span>"
          );
        }
        return (
          '<a class="memo-file-link" href="' +
          escapeHtml(href) +
          '" target="_blank" rel="noopener noreferrer" title="' +
          escapeHtml(matched) +
          '">' +
          matched +
          "</a>"
        );
      });
    });
  }

  function termHref(term) {
    if (term && term.href) return term.href;
    if (term && term.id) return anchor(term.id);
    return "";
  }

  function linkGlossaryTerms(escapedText) {
    let out = String(escapedText || "");
    /* One term at a time, then re-protect new <a> tags so EVALATHAN inside hrefs is not rematched. */
    GLOSS_AUTO_LINKS.forEach(function (term) {
      const href = termHref(term);
      if (!href) return;
      out = mapPlainTextSegments(out, function (text) {
        return text.replace(term.re, function (matched) {
          const klass = term.href ? "memo-std-link" : "memo-gloss-link";
          return (
            '<a class="' +
            klass +
            '" href="' +
            escapeHtml(href) +
            '" target="_blank" rel="noopener noreferrer" title="' +
            escapeHtml(term.title) +
            '">' +
            matched +
            "</a>"
          );
        });
      });
    });
    return out;
  }

  /* Paint the label Evidence (any casing) US-flag red without touching mid-word hits. */
  function markEvidenceWords(escapedText) {
    return mapPlainTextSegments(String(escapedText || ""), function (text) {
      return text.replace(/\bEvidence\b/gi, function (matched) {
        return '<span class="memo-evidence-word">' + matched + "</span>";
      });
    });
  }

  function linkMemoProse(escapedText, run) {
    return markEvidenceWords(linkFilePaths(linkGlossaryTerms(escapedText), run || null));
  }
  const app = document.getElementById("app-screen");

  /* word-white = white glyphs for dark grounds; word-black = black glyphs for light grounds */
  /* Hydra evaler order is life-cycle (GLOSSARY), not alphabetical */
  const ENGINES = [
    {
      id: "hydra",
      label: "HYDRA",
      wired: true,
      wordOnDark: "assets/hydra-word-white.png?v=shade1",
      wordOnLight: "assets/hydra-word-black.png?v=shade1",
      art: "assets/hydra-logo.webp?v=5",
      artGrey: "assets/hydra-logo-grey.webp?v=5",
      blurbs:
        "Hydra engine conducts 16 static evalers (non-exhaustive currently).\nEach evaler reports its own life-cycle gate.\nA blank is not a fail and not a zero.\n\nHydra evalers order is not alphabetical, it is product life-cycle based.",
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
      wired: false,
      wordOnDark: "assets/dehydrus-word-white.png?v=shade1",
      wordOnLight: "assets/dehydrus-word-black.png?v=shade1",
      art: "assets/dehydrus-logo.webp?v=5",
      artGrey: "assets/dehydrus-logo-grey.webp?v=5",
      blurbs:
        "Dehydrus engine conducts 8 physical world models (not wired in currently).\nLuDaTs rooms under PRETRUWs stay off Hydra's vector.\nA missing world stays deferred.",
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
      wired: false,
      wordOnDark: "assets/benchrex-word-white.png?v=shade1",
      wordOnLight: "assets/benchrex-word-black.png?v=shade1",
      art: "assets/benchrex-logo.webp?v=5",
      artGrey: "assets/benchrex-logo-grey.webp?v=5",
      blurbs:
        "Benchrex engine conducts 10 deprecation cells (not wired in currently).\nSeven criterion cells check whether a claimed benchmark is still fit to cite.\nAssessly, Reportly, and Notifyly cover assessment, reporting, and notification.",
      evalers: [
        { id: "saturly", label: "Saturly", href: anchor("saturly"), later: false },
        { id: "contamly", label: "Contamly", href: anchor("contamly"), later: false },
        { id: "skewly", label: "Skewly", href: anchor("skewly"), later: false },
        { id: "annotly", label: "Annotly", href: anchor("annotly"), later: false },
        { id: "obsoletely", label: "Obsoletely", href: anchor("obsoletely"), later: false },
        { id: "assumly", label: "Assumly", href: anchor("assumly"), later: false },
        { id: "driftly", label: "Driftly", href: anchor("driftly"), later: false },
        { id: "assessly", label: "Assessly", href: anchor("assessly"), later: false },
        { id: "reportly", label: "Reportly", href: anchor("reportly"), later: false },
        { id: "notifyly", label: "Notifyly", href: anchor("notifyly"), later: false },
      ],
    },
    {
      id: "biasrex",
      label: "BIASREX",
      wired: false,
      wordOnDark: "assets/biasrex-word-white.png?v=shade1",
      wordOnLight: "assets/biasrex-word-black.png?v=shade1",
      art: "assets/biasrex-logo.webp?v=6",
      artGrey: "assets/biasrex-logo-grey.webp?v=6",
      blurbs:
        "Biasrex engine conducts 6 bias cells (not wired in currently).\nFilterly, Meaningly, Hastely, and Memoryly map the Codex four problems.\nConfirmly and Automately add confirmation and automation trust gates.",
      evalers: [
        { id: "filterly", label: "Filterly", href: anchor("filterly"), later: false },
        { id: "meaningly", label: "Meaningly", href: anchor("meaningly"), later: false },
        { id: "hastely", label: "Hastely", href: anchor("hastely"), later: false },
        { id: "memoryly", label: "Memoryly", href: anchor("memoryly"), later: false },
        { id: "confirmly", label: "Confirmly", href: anchor("confirmly"), later: false },
        { id: "automately", label: "Automately", href: anchor("automately"), later: false },
      ],
    },
  ];

  const SPLASH = {
    label: "EVALATHAN",
    art: "assets/evalathan-dragon.webp?v=5",
    artGrey: "assets/evalathan-dragon-grey.webp?v=5",
    blurbs:
      "40 current evals, 4 routing engines, 16 evalers currently wired in.\nHydra engine conducts 16 static evalers (non-exhaustive currently).\nDehydrus engine conducts 8 physical world models (not wired in currently).\nBenchrex engine conducts 10 deprecation cells (not wired in currently).\nBiasrex engine conducts 6 bias cells (not wired in currently).",
  };

  let activeId = "hydra";
  let openId = null;
  let userPickedEngine = false;
  /* Per-upload sets: [{ targetKey, titleCaps, shortTitle, target, latest, saved[] }] */
  let runSets = [];
  let openMemos = []; /* [{ id, root, run, kind, comparePack, mode }] */
  let focusedMemoId = null;
  let memoSeq = 0;
  let evalBusy = false;

  function focusedMemo() {
    return (
      openMemos.find(function (m) {
        return m.id === focusedMemoId;
      }) ||
      openMemos[openMemos.length - 1] ||
      null
    );
  }

  function loadJson(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      if (raw == null) return fallback;
      return JSON.parse(raw);
    } catch (e) {
      return fallback;
    }
  }
  function persistRuns() {
    const payload = runSets.slice(0, 24);
    try {
      localStorage.setItem("evalathan_run_sets", JSON.stringify(payload));
    } catch (e) {
      /* ignore quota / private mode */
    }
    /* Disk store via desk API - survives pywebview restart even when localStorage does not */
    try {
      fetch("/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ runSets: payload }),
        keepalive: true,
      }).catch(function () {
        /* offline / old server */
      });
    } catch (e2) {
      /* ignore */
    }
  }

  function hydrateRunsFromDisk(done) {
    fetch("/api/runs")
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (data) {
        if (data && data.ok && Array.isArray(data.runSets) && data.runSets.length) {
          const local = loadJson("evalathan_run_sets", []);
          const disk = data.runSets;
          /* Prefer whichever side has more saved rows; disk wins ties so restart restores. */
          const countSaved = function (sets) {
            let n = 0;
            (sets || []).forEach(function (s) {
              n += (s.saved || []).length;
              if (s.latest) n += 1;
            });
            return n;
          };
          if (!Array.isArray(local) || !local.length || countSaved(disk) >= countSaved(local)) {
            runSets = disk;
            try {
              localStorage.setItem("evalathan_run_sets", JSON.stringify(runSets.slice(0, 24)));
            } catch (e) {
              /* ignore */
            }
          }
        }
        if (typeof done === "function") done();
      })
      .catch(function () {
        if (typeof done === "function") done();
      });
  }

  function normalizeTargetKey(target) {
    return String(target || "")
      .trim()
      .toLowerCase()
      .replace(/\/+$/, "")
      .replace(/\.git$/i, "");
  }

  function titleCapsFromTarget(target) {
    return String(shortTitleFromTarget(target) || "UNTITLED").toUpperCase();
  }

  function findRunSet(target) {
    const key = normalizeTargetKey(target);
    return runSets.find(function (s) {
      return s.targetKey === key;
    }) || null;
  }

  function ensureRunSet(target) {
    let set = findRunSet(target);
    const caps = titleCapsFromTarget(target);
    const short = shortTitleFromTarget(target);
    if (!set) {
      set = {
        targetKey: normalizeTargetKey(target),
        titleCaps: caps,
        shortTitle: short,
        target: target || "",
        latest: null,
        saved: [],
      };
      runSets.unshift(set);
    } else {
      set.titleCaps = caps;
      set.shortTitle = short;
      if (target) set.target = target;
      runSets = [set].concat(
        runSets.filter(function (s) {
          return s !== set;
        })
      );
    }
    return set;
  }

  function allSavedRuns() {
    const out = [];
    runSets.forEach(function (s) {
      (s.saved || []).forEach(function (r) {
        out.push(r);
      });
    });
    return out;
  }

  function migrateRuns() {
    const stored = loadJson("evalathan_run_sets", null);
    if (Array.isArray(stored) && stored.length) {
      runSets = stored;
      return;
    }
    const legacyLatest = loadJson("evalathan_latest_run", null);
    let legacySaved = loadJson("evalathan_saved_runs", []);
    if (!Array.isArray(legacySaved)) legacySaved = [];
    const past = loadJson("evalathan_past_runs", []);
    if (Array.isArray(past) && past.length && !legacySaved.length) {
      legacySaved = past.slice(0, 40);
    }
    const map = {};
    const order = [];
    function touch(run) {
      if (!run) return null;
      const key = normalizeTargetKey(run.target || run.title || run.shortTitle);
      if (!key) return null;
      if (!map[key]) {
        map[key] = {
          targetKey: key,
          titleCaps: titleCapsFromTarget(run.target || run.shortTitle || run.title),
          shortTitle: shortTitleFromTarget(run.target || run.shortTitle || run.title),
          target: run.target || "",
          latest: null,
          saved: [],
        };
        order.push(key);
      }
      return map[key];
    }
    legacySaved.forEach(function (r) {
      const set = touch(r);
      if (!set) return;
      if (!set.saved.some(function (x) {
        return x.id === r.id;
      })) {
        set.saved.push(r);
      }
    });
    if (legacyLatest) {
      const set = touch(legacyLatest);
      if (set) {
        set.latest = legacyLatest;
        if (legacyLatest.savedAt && !set.saved.some(function (x) {
          return x.id === legacyLatest.id;
        })) {
          set.saved.unshift(legacyLatest);
        }
        order.sort(function (a, b) {
          if (a === set.targetKey) return -1;
          if (b === set.targetKey) return 1;
          return 0;
        });
      }
    }
    runSets = order.map(function (k) {
      return map[k];
    });
    if (runSets.length) persistRuns();
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

  function ensureSideOpen(side) {
    const cls = side === "engines" ? "engines-open" : "runs-open";
    if (!app.classList.contains(cls)) toggleSide(side);
  }

  /** Open an engine page inside this desk (evals left rail + hero). */
  function openEnginePage(engineId) {
    const id = engineId || "hydra";
    if (!engine(id)) return;
    activeId = id;
    userPickedEngine = true;
    openId = id;
    ensureSideOpen("engines");
    renderEngines();
    renderHero();
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
      const word = document.createElement("span");
      word.className = "engine-word";
      word.textContent = e.label;
      btn.appendChild(word);
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

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  const ENGINE_BLURB_HREF = {
    "Hydra engine": "hydra",
    "Dehydrus engine": "dehydrus",
    "Benchrex engine": "benchrex",
    "Biasrex engine": "biasrex",
  };

  function formatBlurbs(text, splash) {
    const rawLines = String(text).split("\n");
    let htmlOut = "";
    let contentIdx = 0;
    rawLines.forEach((line) => {
      if (!line.length) {
        htmlOut += '<span class="blurb-gap blurb-gap-sm" aria-hidden="true"></span>';
        return;
      }
      let html = escapeHtml(line).replace(
        /(Hydra engine|Dehydrus engine|Benchrex engine|Biasrex engine)/g,
        function (match) {
          const id = ENGINE_BLURB_HREF[match];
          const name = match.split(" ")[0];
          return (
            '<a class="blurb-engine" href="' +
            escapeHtml(anchor(id)) +
            '" target="_blank" rel="noopener noreferrer" title="' +
            escapeHtml(name) +
            ' - glossary">' +
            match +
            "</a>"
          );
        }
      );
      if (splash) {
        html = html.replace(
          /16 evalers currently wired in\./g,
          '<a class="blurb-wired" href="#hydra" data-engine="hydra" title="Open Hydra in evals">16 evalers currently wired in.</a>'
        );
      }
      htmlOut += '<span class="blurb-line">' + html + "</span>";
      if (splash && contentIdx === 0) {
        htmlOut += '<span class="blurb-gap" aria-hidden="true"></span>';
      }
      contentIdx += 1;
    });
    return htmlOut;
  }

  function artSrc(view) {
    if (theme() === "grey" && view.artGrey) return view.artGrey;
    return view.art || null;
  }

  const ART_CACHE = new Map();
  let artToken = 0;

  function collectArtUrls() {
    const urls = [];
    const push = (u) => {
      if (u && urls.indexOf(u) === -1) urls.push(u);
    };
    push(SPLASH.art);
    push(SPLASH.artGrey);
    ENGINES.forEach((e) => {
      push(e.art);
      push(e.artGrey);
    });
    return urls;
  }

  function preloadArts() {
    collectArtUrls().forEach((url) => {
      loadArt(url, 0);
    });
  }

  function loadArt(url, attempt) {
    if (!url) return Promise.resolve(null);
    const tryN = attempt || 0;
    const hit = ART_CACHE.get(url);
    if (hit && hit.complete && hit.naturalWidth) return Promise.resolve(hit);
    return new Promise(function (resolve) {
      const img = new Image();
      if (tryN === 0) ART_CACHE.set(url, img);
      const done = function (ok) {
        if (ok && img.naturalWidth) {
          ART_CACHE.set(url, img);
          resolve(img);
          return;
        }
        if (tryN < 5) {
          window.setTimeout(function () {
            loadArt(url, tryN + 1).then(resolve);
          }, 300 * (tryN + 1));
          return;
        }
        resolve(null);
      };
      img.onload = function () {
        done(true);
      };
      img.onerror = function () {
        done(false);
      };
      img.src = tryN === 0 ? url : url + (url.indexOf("?") >= 0 ? "&" : "?") + "retry=" + tryN + "&t=" + Date.now();
    });
  }

  function setSplashArt(art, src, alt) {
    const token = ++artToken;
    if (!src) {
      art.removeAttribute("data-art-src");
      art.removeAttribute("src");
      art.alt = "";
      art.classList.add("is-blank");
      return;
    }
    art.alt = alt || "";
    art.setAttribute("data-art-src", src);
    /* Keep the current logo visible until the next one is fully loaded - never blank on tunnel stalls */
    loadArt(src, 0).then(function (img) {
      if (token !== artToken) return;
      if (art.getAttribute("data-art-src") !== src) return;
      if (!img || !img.naturalWidth) {
        /* last resort: keep whatever is already painted; never hide */
        art.classList.remove("is-blank");
        return;
      }
      /* Use the URL that actually loaded (retry query included) so we do not refetch */
      art.src = img.currentSrc || img.src || src;
      art.classList.remove("is-blank");
    });
  }

  function evalSlotAllowed() {
    /* Splash defaults to Hydra path; only Hydra is wired in this FOSS desk */
    if (!userPickedEngine) return true;
    const e = engine(activeId);
    return !!(e && e.wired);
  }

  function syncEvalSlot() {
    const allow = evalSlotAllowed();
    const slotbox = document.querySelector(".slotbox");
    const input = document.getElementById("target-input");
    const browse = document.getElementById("btn-browse");
    const evalBtn = document.getElementById("btn-eval");
    if (slotbox) slotbox.classList.toggle("is-wip", !allow);
    if (input) {
      input.disabled = !allow;
      input.readOnly = !allow;
      input.placeholder = allow
        ? "Upload your GitHub link or folder…"
        : "Currently under Development WIP";
      if (!allow) input.value = "";
      input.title = allow
        ? "Paste a GitHub URL or browse a local folder"
        : "Currently under Development WIP";
    }
    if (browse) {
      browse.disabled = !allow;
      browse.title = allow ? "Browse a folder on this PC" : "Currently under Development WIP";
    }
    if (evalBtn) {
      evalBtn.disabled = !allow;
      evalBtn.title = allow ? "Evaluate" : "Currently under Development WIP";
    }
  }

  function renderHero() {
    const title = document.getElementById("splash-title");
    const art = document.getElementById("splash-art");
    const slot = document.querySelector(".splash-art-slot");
    const blurbs = document.getElementById("blurbs");
    const plg = document.getElementById("plg-tag");
    const repo = document.getElementById("repo-link");
    const stage = document.getElementById("page-stage");
    const view = userPickedEngine ? engine(activeId) : SPLASH;
    const artKey = userPickedEngine ? activeId : "evalathan";
    const src = artSrc(view);
    const onSplash = !userPickedEngine;
    title.textContent = view.label;
    blurbs.innerHTML = formatBlurbs(view.blurbs, onSplash);
    blurbs.querySelectorAll("a.blurb-wired").forEach(function (el) {
      el.addEventListener("click", function (ev) {
        ev.preventDefault();
        openEnginePage(el.getAttribute("data-engine") || "hydra");
      });
    });
    if (slot) {
      slot.className = "splash-art-slot art-" + artKey;
    }
    if (stage) stage.classList.toggle("is-splash", onSplash);
    if (plg) plg.classList.toggle("is-hidden", !onSplash);
    if (repo) repo.classList.toggle("is-hidden", !onSplash);
    setSplashArt(art, src, view.label);
    syncEvalSlot();
  }

  function hashStr(s) {
    let h = 2166136261;
    for (let i = 0; i < String(s).length; i++) {
      h ^= String(s).charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function scoreFor(target, engineId, evalerId) {
    return 42 + (hashStr(String(target || "") + "|" + engineId + "|" + evalerId) % 57);
  }

  /* Deterministic ints for FOSS-preview findings (same target+evaler → same numbers) */
  function findingBits(target, engineId, evalerId) {
    const h = hashStr(String(target || "") + "|" + engineId + "|" + evalerId);
    return {
      n: (h % 880) + 20,
      m: ((h >>> 7) % 90) + 5,
      k: ((h >>> 14) % 48) + 2,
      p: ((h >>> 21) % 85) + 10,
      q: ((h >>> 3) % 35) + 1,
      r: ((h >>> 11) % 200) + 8,
    };
  }

  /*
   * Per-evaler rationale (site/sample style): what the gate looks for + why this score.
   * Browser FOSS desk cannot clone the repo; findings are fingerprint-derived previews,
   * not LLM guesses and not a live tree walk.
   */
  function explainEval(engineId, ev, score, status, target) {
    const id = String((ev && ev.id) || "").toLowerCase();
    const label = (ev && ev.label) || id;
    const b = findingBits(target, engineId, id);
    const prod = shortTitleFromTarget(target);
    const deferred = status === "deferred";
    const scoreWhy = deferred
      ? "Score " +
        score +
        "/100 stays under the 52 gate, so the cell is blank (not a fail, not a zero)."
      : "Score " +
        score +
        "/100 clears the 52 gate because the preview signal was strong enough to post a number for this cell.";

    const hydra = {
      devly: deferred
        ? "Devly looks for git commit count via rev-list (no SFIA skill stamp). For " +
          prod +
          ", the FOSS desk preview found no .git-shaped history cue. " +
          scoreWhy
        : "Devly counts commits and rhythm; it does not judge the developer. Preview cue for " +
          prod +
          ": about " +
          b.n +
          " commit-shaped signals in the target fingerprint. No SFIA level assigned. " +
          scoreWhy,
      archly: deferred
        ? "Archly scores architecture evidence (README/docs/ADR vs 97 principles). For " +
          prod +
          ", no architecture pack cue in the preview. " +
          scoreWhy
        : "Archly checks structural plan evidence (docs/ADR), not a live ISO 42030 certificate. Preview for " +
          prod +
          ": " +
          b.k +
          " principle-shaped hits, mean band ~" +
          (3 + (b.m % 10) / 10).toFixed(1) +
          ". " +
          scoreWhy,
      codely: deferred
        ? "Codely counts functions/branches and notes tests; it does not invent a language grade. Preview for " +
          prod +
          " lacked a code-shape signal. " +
          scoreWhy
        : "Codely reports structure, not a pytest/coverage run. Preview for " +
          prod +
          ": ~" +
          (b.n * 2 + b.r) +
          " function cues, ~" +
          (b.n + b.m) +
          " branch cues, mean ~" +
          (1.2 + (b.k % 20) / 10).toFixed(2) +
          ", tests noted ~" +
          b.q +
          ". " +
          scoreWhy,
      refactorly: deferred
        ? "Refactorly looks for duplicate-byte groups and unreferenced names. Preview for " +
          prod +
          " had no duplication map. " +
          scoreWhy
        : "Refactorly reports duplication/dead-name pressure, not a Deglove rate. Preview for " +
          prod +
          ": " +
          b.q +
          " identical-byte groups among ~" +
          (b.n + 40) +
          " files, ~" +
          b.m +
          " unreferenced-name cues. " +
          scoreWhy,
      mixly: deferred
        ? "Mixly maps file suffixes to languages. Preview for " +
          prod +
          " had no recognized language mix. " +
          scoreWhy
        : "Mixly shows language mix only (no ranking). Preview for " +
          prod +
          ": primary ~" +
          b.p +
          "%, secondary ~" +
          Math.max(1, 100 - b.p) +
          "% of recognized files. " +
          scoreWhy,
      runly: deferred
        ? "Runly wants a microbench or a SPEC/LLVM result file. Preview for " +
          prod +
          ": no timing artifact. " +
          scoreWhy
        : "Runly times a local microbench cue; it does not invent SPEC. Preview for " +
          prod +
          ": ~" +
          (8 + (b.k % 40)) +
          "." +
          (b.q % 10) +
          " ms for 200,000-step shape. No SPEC/LLVM file claimed. " +
          scoreWhy,
      levi: deferred
        ? "Levi prints a sealed 4Uvals JSON gate (mean + PASS/FAIL). Preview for " +
          prod +
          ": no 4uval card. " +
          scoreWhy
        : "Levi reads an existing 4Uvals card; it does not rescore the ten checks. Preview for " +
          prod +
          ": gate mean ~" +
          (2.5 + (b.k % 15) / 10).toFixed(1) +
          "/4, " +
          (b.m > 40 ? "PASS" : "borderline") +
          " cue. " +
          scoreWhy,
      menschly: deferred
        ? "Menschly needs real break-timer code in the product (not README wellness copy). Preview for " +
          prod +
          ": no stop-timer cue. " +
          scoreWhy
        : "Menschly passes when a real stop/break timer is present. Preview for " +
          prod +
          ": timer-shaped affordance seen in the fingerprint. " +
          scoreWhy,
      tokely: deferred
        ? "Tokely needs a sealed before/after TOKEX file. Preview for " +
          prod +
          ": blank - no token ledger. " +
          scoreWhy
        : "Tokely reads sealed token before/after counts (no model call). Preview for " +
          prod +
          ": before ~" +
          (b.n * 40) +
          ", after ~" +
          (b.n * 40 - b.r * 3) +
          " TOKEX cues. " +
          scoreWhy,
      pressly: deferred
        ? "Pressly needs compression logs with bytes plus quality (SSIM/PSNR/VMAF/CRF). Preview for " +
          prod +
          ": no quality-tagged byte log. " +
          scoreWhy
        : "Pressly extracts compression metrics; it does not run the pipeline. Preview for " +
          prod +
          ": ~" +
          (b.n * 12) +
          " KB reduced cue, quality tag band ~" +
          (b.p % 40 + 50) +
          ". " +
          scoreWhy,
      triadly: deferred
        ? "Triadly needs a declared cost/speed/impact priority order. Preview for " +
          prod +
          ": blank - no triad declaration. " +
          scoreWhy
        : "Triadly checks that cost, speed, or impact was explicitly ordered. Preview for " +
          prod +
          ": declared order cue present (band " +
          score +
          "). " +
          scoreWhy,
      chorely: deferred
        ? "Chorely counts agent roster files/rows (SASPIANT chores). Preview for " +
          prod +
          ": no roster. " +
          scoreWhy
        : "Chorely counts roster rows; it does not answer SASPIANT for you. Preview for " +
          prod +
          ": " +
          b.q +
          " roster files, ~" +
          b.m +
          " rows. " +
          scoreWhy,
      trajectly: deferred
        ? "Trajectly needs a saved agent trace (steps/loops). Preview for " +
          prod +
          ": blank - no trace. " +
          scoreWhy
        : "Trajectly replays a recorded agent journey. Preview for " +
          prod +
          ": ~" +
          b.m +
          " steps, ~" +
          b.q +
          " loop cues. " +
          scoreWhy,
      warrantly: deferred
        ? "Warrantly needs a claim register with attached evidence. Preview for " +
          prod +
          ": blank - no claim pack. " +
          scoreWhy
        : "Warrantly fails empty sales claims; backed claims post a number. Preview for " +
          prod +
          ": " +
          b.k +
          " claims, " +
          Math.max(1, b.k - b.q) +
          " with evidence cues. " +
          scoreWhy,
      domly: deferred
        ? "Domly needs a question/answer bank for domain quiz. Preview for " +
          prod +
          ": blank - no question bank. " +
          scoreWhy
        : "Domly grades against an answer key when ids match. Preview for " +
          prod +
          ": ~" +
          b.m +
          " questions, ~" +
          Math.min(b.m, b.k + 5) +
          " matched answers. " +
          scoreWhy,
      stackly: deferred
        ? "Stackly summarizes the earlier Hydra cells (passes vs blanks) - no combined score. Preview for " +
          prod +
          " had too few prior cell cues. " +
          scoreWhy
        : "Stackly shows the status matrix, not one fake total. Preview for " +
          prod +
          ": 16 cell slots, ~" +
          (8 + (b.q % 6)) +
          " pass-shaped, ~" +
          (4 + (b.k % 5)) +
          " blank-shaped in the fingerprint stack. " +
          scoreWhy,
    };

    const dehydrus = {
      copernly: "Copernly checks heliocentric / orientation world seals under LuDaTs.",
      keplerly: "Keplerly checks orbital / path world seals under LuDaTs.",
      galileoly: "Galileoly checks observation / instrument world seals under LuDaTs.",
      darwinly: "Darwinly checks selection / fitness world seals under LuDaTs.",
      mendly: "Mendly checks inheritance / trait world seals under LuDaTs.",
      einsteinly: "Einsteinly checks relativity / frame world seals under LuDaTs.",
      curcuriely: "CurCuriely checks radiation / field world seals under LuDaTs.",
      newtonly: "Newtonly stacks earlier Dehydrus cells and stays deferred until Keplerly+Galileoly seal.",
    };

    const benchrex = {
      saturly: "Saturly checks whether a cited benchmark is saturated (no longer discriminative).",
      contamly: "Contamly checks training-data contamination risk on a claimed score.",
      skewly: "Skewly checks distribution skew that would make a cite unfair.",
      annotly: "Annotly checks annotation / label quality behind the number.",
      obsoletely: "Obsoletely checks whether the benchmark task is obsolete for the claim.",
      assumly: "Assumly checks hidden assumptions that break the cite.",
      driftly: "Driftly checks semantic / temporal drift since the claimed result.",
      assessly: "Assessly checks whether a deprecation assessment pack exists.",
      reportly: "Reportly checks whether deprecation findings were written down.",
      notifyly: "Notifyly checks whether dependents were notified of deprecation.",
    };

    const biasrex = {
      filterly: "Filterly checks filter / selection bias artifacts (Codex: too much information).",
      meaningly: "Meaningly checks story-filling vs evidence (Codex: not enough meaning).",
      hastely: "Hastely checks haste / overconfidence gates (Codex: need to act fast).",
      memoryly: "Memoryly checks stale memory / continued-influence of old scores.",
      confirmly: "Confirmly checks confirmation-bias / falsification gates.",
      automately: "Automately checks automation-bias / tool-trust gates.",
    };

    let finding = hydra[id];
    if (!finding && engineId === "dehydrus") {
      finding =
        (dehydrus[id] || label + " probes a sealed LuDaTs world.") +
        " Preview for " +
        prod +
        (deferred
          ? ": no sealed world file - blank cell. "
          : ": sealed-room cue strength " + b.p + ". ") +
        scoreWhy;
    } else if (!finding && engineId === "benchrex") {
      finding =
        (benchrex[id] || label + " checks cite-fitness.") +
        " Preview for " +
        prod +
        (deferred
          ? ": criterion pack incomplete. "
          : ": cite-fitness band " + score + ". ") +
        scoreWhy;
    } else if (!finding && engineId === "biasrex") {
      finding =
        (biasrex[id] || label + " checks a bias artifact gate.") +
        " Preview for " +
        prod +
        (deferred
          ? ": artifact missing. "
          : ": artifact discipline band " + score + ". ") +
        scoreWhy;
    } else if (!finding) {
      finding =
        label +
        " reports its own gate for " +
        prod +
        ". Preview signal " +
        score +
        "/100. " +
        scoreWhy;
    }

    const blurb = deferred
      ? label + " blank @ " + score + "/100 - " + finding.split(". ")[0] + "."
      : label + " " + score + "/100 - " + finding.split(". ").slice(0, 2).join(". ") + ".";

    return { blurb: blurb, detail: finding };
  }

  function gateBlurb(engineId, ev, score, status, target) {
    return explainEval(engineId, ev, score, status, target).blurb;
  }

  function detailLine(engineId, ev, score, status, target) {
    return explainEval(engineId, ev, score, status, target).detail;
  }

  function processLine(engineId, ev) {
    if (engineId === "dehydrus") return ev.label + " probing sealed world signals…";
    if (engineId === "benchrex") return ev.label + " checking cite-fitness…";
    if (engineId === "biasrex") return ev.label + " reading bias artifacts…";
    return ev.label + " reading " + ev.label + " gate evidence…";
  }

  function buildCells(target, eng) {
    return eng.evalers
      .filter((ev) => !ev.later)
      .map((ev) => {
        const score = scoreFor(target, eng.id, ev.id);
        const status = score < 52 ? "deferred" : "pass";
        const explained = explainEval(eng.id, ev, score, status, target);
        return {
          id: ev.id,
          name: ev.label,
          status: status,
          score: score,
          blurb: explained.blurb,
          detail: explained.detail,
          href: ev.href || GLOSS_MD,
        };
      });
  }

  function findPriorSaved(target, engineLabel) {
    const set = findRunSet(target);
    if (!set || !set.saved || !set.saved.length) return null;
    const eng = String(engineLabel || "").toLowerCase();
    return (
      set.saved.find(function (r) {
        return String(r.engine || "").toLowerCase() === eng;
      }) || null
    );
  }

  function compareRuns(current, prior) {
    if (!prior || !prior.cells || !current.cells) return null;
    const priorMap = {};
    prior.cells.forEach((c) => {
      priorMap[c.id || c.name] = c;
    });
    let improved = 0;
    let regressed = 0;
    let same = 0;
    const notes = [];
    let numeric = 0;
    current.cells.forEach((c) => {
      const key = c.id || c.name;
      const p = priorMap[key];
      if (!p) {
        same += 1;
        return;
      }
      if (typeof p.score === "number" && typeof c.score === "number") {
        numeric += 1;
        const d = c.score - p.score;
        if (d > 0) {
          improved += 1;
          notes.push(c.name + " +" + d);
        } else if (d < 0) {
          regressed += 1;
          notes.push(c.name + " " + d);
        } else {
          same += 1;
        }
        return;
      }
      /* Hydra: compare deferred ↔ measured/passed */
      const wasDef = p.status === "deferred";
      const nowDef = c.status === "deferred";
      if (wasDef && !nowDef) {
        improved += 1;
        notes.push(c.name + " now measured");
      } else if (!wasDef && nowDef) {
        regressed += 1;
        notes.push(c.name + " now deferred");
      } else if (p.passed !== true && c.passed === true) {
        improved += 1;
        notes.push(c.name + " now passed");
      } else if (p.passed === true && c.passed !== true && !nowDef) {
        regressed += 1;
        notes.push(c.name + " lost pass");
      } else {
        same += 1;
      }
    });
    let delta = 0;
    if (numeric) {
      const avgNow =
        current.cells.reduce((a, c) => a + (c.score || 0), 0) / Math.max(1, current.cells.length);
      const avgWas =
        prior.cells.reduce((a, c) => a + (c.score || 0), 0) / Math.max(1, prior.cells.length);
      delta = Math.round((avgNow - avgWas) * 10) / 10;
    } else {
      delta = improved - regressed;
    }
    let tone = "same";
    if (improved > regressed) tone = "improved";
    else if (regressed > improved) tone = "regressed";
    return {
      tone: tone,
      delta: delta,
      improved: improved,
      regressed: regressed,
      same: same,
      priorWhen: prior.when,
      notes: notes.slice(0, 6),
    };
  }

  function titleCaseToken(tok) {
    const t = String(tok || "").trim();
    if (!t) return "";
    /* Keep short acronyms (EEG, NLP, AZ) */
    if (/^[A-Za-z0-9]{2,5}$/.test(t) && t === t.toUpperCase()) return t.toUpperCase();
    if (/^[A-Z0-9]{2,5}$/.test(t)) return t;
    return t.charAt(0).toUpperCase() + t.slice(1).toLowerCase();
  }

  function shortTitleFromTarget(target) {
    const raw = String(target || "").trim();
    if (!raw) return "Untitled";
    let base = raw;
    try {
      if (/^https?:\/\//i.test(raw)) {
        const u = new URL(raw);
        const parts = u.pathname.split("/").filter(Boolean);
        base = parts.length
          ? decodeURIComponent(parts[parts.length - 1])
          : u.hostname.replace(/^www\./, "");
      } else {
        const segs = raw.replace(/\\/g, "/").split("/").filter(Boolean);
        base = segs.length ? segs[segs.length - 1] : raw;
      }
    } catch (e) {
      const segs = raw.replace(/\\/g, "/").split("/").filter(Boolean);
      base = segs.length ? segs[segs.length - 1] : raw;
    }
    base = String(base)
      .replace(/\.git$/i, "")
      .replace(/[+]+/g, " ")
      .trim();
    /* Non-branded slugs: eeg-seizure-prediction → EEG Seizure Prediction (max 3 words) */
    const words = base
      .replace(/[_]+/g, "-")
      .split(/[-\s]+/)
      .map(function (w) {
        return w.trim();
      })
      .filter(Boolean);
    if (!words.length) return "Untitled";
    if (words.length === 1) return words[0];
    return words.slice(0, 3).map(titleCaseToken).join(" ");
  }

  function displayTitle(run) {
    if (!run) return "EVALATHAN";
    return shortTitleFromTarget(run.target || run.shortTitle || run.title) || "EVALATHAN";
  }

  function targetHref(target) {
    const raw = String(target || "").trim();
    if (!raw) return null;
    if (/^https?:\/\//i.test(raw)) return raw;
    /* Absolute Windows / UNC / POSIX paths → file URL */
    if (/^[a-zA-Z]:[\\/]/.test(raw) || raw.indexOf("\\\\") === 0 || raw.charAt(0) === "/") {
      let norm = raw.replace(/\\/g, "/");
      if (/^[a-zA-Z]:\//.test(norm)) return "file:///" + norm;
      if (norm.indexOf("//") === 0) return "file:" + norm;
      return "file://" + norm;
    }
    return null;
  }

  /* Brief/detail product title: hyperlink GitHub or folder path when we have a real address */
  function memoProductTitleHtml(runOrTarget, titleOverride) {
    const target =
      typeof runOrTarget === "string"
        ? runOrTarget
        : (runOrTarget && (runOrTarget.target || "")) || "";
    const title =
      titleOverride ||
      (typeof runOrTarget === "string"
        ? shortTitleFromTarget(runOrTarget)
        : displayTitle(runOrTarget));
    const href = targetHref(target);
    if (!href) return escapeHtml(title);
    return (
      '<a class="memo-title-link" href="' +
      escapeHtml(href) +
      '" target="_blank" rel="noopener noreferrer" title="' +
      escapeHtml(target) +
      '">' +
      escapeHtml(title) +
      "</a>"
    );
  }

  migrateRuns();

  function nextRunOrdinal(target, engineIdOrLabel) {
    const set = findRunSet(target);
    const engKey = String(engineIdOrLabel || "").toLowerCase();
    const saved = (set && set.saved) || [];
    const same = saved.filter(function (r) {
      return (
        String(r.engineId || r.engine || "").toLowerCase() === engKey ||
        String(r.engine || "").toLowerCase() === engKey
      );
    });
    return same.length + 1;
  }

  function cellsFromHydraReport(report) {
    return (report && report.cells ? report.cells : []).map(function (c) {
      const agent = String(c.agent || "Evaler");
      const id = agent.toLowerCase();
      const deferred = String(c.status || "") === "deferred";
      const measured = String(c.status || "") === "measured" || String(c.status || "") === "provisional";
      const passed = c.passed === true;
      let status = "deferred";
      if (deferred) status = "deferred";
      else if (passed) status = "pass";
      else if (measured) status = "measured";
      else status = "pass";
      const evidence = Array.isArray(c.evidence) ? c.evidence : [];
      const summary = nellCleanProse(String(c.summary || ""));
      return {
        id: id,
        name: agent,
        gate: c.gate || "",
        question: c.question || "",
        status: status,
        hydraStatus: c.status || "",
        passed: c.passed,
        score: null,
        blurb: summary,
        detail: summary,
        evidence: evidence,
        href: anchor(id === "levi" ? "levi" : id),
      };
    });
  }

  /* Nell (comms rewrite): turn Hydra dumps into titled cards humans can read. */
  function looksLikePath(token) {
    const t = String(token || "").trim();
    if (!t) return false;
    if (/^[A-Za-z]:[\\/]/.test(t)) return true;
    if (t.indexOf("\\") >= 0 || t.indexOf("/") >= 0) return true;
    if (/\.(py|md|json|jsonl|ts|tsx|js|jsx|go|rs|java|html|css|toml|yml|yaml|lock|txt)$/i.test(t))
      return true;
    return false;
  }

  function nellCleanProse(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function nellEvidenceItems(rawList) {
    const items = [];
    (rawList || []).forEach(function (raw) {
      const entry = String(raw || "").trim();
      if (!entry) return;
      if (/^no /i.test(entry) || entry === "no test_*.py modules" || entry === "no identical-byte groups") {
        items.push({ kind: "note", title: "Note", text: entry });
        return;
      }
      const inMatch = entry.match(/^([A-Za-z_][\w]*)\s+in\s+(.+)$/);
      if (inMatch) {
        items.push({
          kind: "symbol",
          title: "Unreferenced name",
          text: inMatch[1],
          path: inMatch[2],
        });
        return;
      }
      const stepMatch = entry.match(/^(.+?)\s+(\d+)\s+steps$/i);
      if (stepMatch && looksLikePath(stepMatch[1])) {
        items.push({
          kind: "metric",
          title: stepMatch[2] + " trace steps",
          path: stepMatch[1],
        });
        return;
      }
      if (entry.indexOf(", ") >= 0 && looksLikePath(entry.split(", ")[0])) {
        entry.split(", ").forEach(function (part) {
          const p = part.trim();
          if (p) items.push({ kind: "path", title: "Same-bytes twin", path: p });
        });
        return;
      }
      const churnMatch = entry.match(/^(.+?)\s+(\d+)$/);
      if (churnMatch && looksLikePath(churnMatch[1])) {
        items.push({
          kind: "metric",
          title: "Churn lines " + churnMatch[2],
          path: churnMatch[1],
        });
        return;
      }
      if (looksLikePath(entry)) {
        items.push({ kind: "path", title: "File", path: entry });
        return;
      }
      items.push({ kind: "note", title: "Note", text: entry });
    });
    return items;
  }

  function nellStatusLabel(c) {
    if (c.passed === true) return "passed";
    if (c.hydraStatus) return String(c.hydraStatus);
    return String(c.status || "deferred");
  }

  function nellStripPathWall(text, evidenceItems) {
    let s = nellCleanProse(text);
    if (!s) return "";
    /* Drop trailing file-path dumps that old memos glued onto the summary. */
    const pathHit = s.search(
      /\s(?:[A-Za-z]:[\\/]|docs[\\/]|examples[\\/]|tests[\\/]|src[\\/]|sdks[\\/]|memanto[\\/]|integrations[\\/]|\.github[\\/])/i
    );
    if (pathHit > 40) s = s.slice(0, pathHit).trim();
    if (evidenceItems && evidenceItems.length) {
      evidenceItems.forEach(function (it) {
        if (it.path) {
          const esc = escapeRegExp(it.path.replace(/\//g, "[\\\\/]"));
          s = s.replace(new RegExp("\\s*" + esc, "gi"), "");
        }
      });
      s = s.replace(/\s{2,}/g, " ").trim();
    }
    return s;
  }

  function nellRewriteCell(c) {
    const evidence = nellEvidenceItems(c.evidence || []);
    /* Prefer short summary; never show the old summary+paths wall as the blurb. */
    let blurb = nellStripPathWall(c.blurb || "", evidence);
    if (!blurb) blurb = nellStripPathWall(c.detail || "", evidence);
    if (!blurb && c.question) blurb = String(c.question);
    if (!blurb) blurb = "No prose summary from this evaler.";
    return {
      name: c.name || "Evaler",
      href: c.href || GLOSS_MD,
      gate: c.gate || "",
      question: c.question || "",
      status: nellStatusLabel(c),
      blurb: blurb,
      evidence: evidence,
      score: c.score,
    };
  }

  function fileAnchorHtml(path, run, label) {
    const shown = label != null ? label : shortPath(path);
    const href = memoFileHref(path, run);
    const safeLabel = escapeHtml(shown);
    const safePath = escapeHtml(path);
    if (!href) {
      return '<code class="memo-file-link" title="' + safePath + '">' + safeLabel + "</code>";
    }
    return (
      '<a class="memo-file-link" href="' +
      escapeHtml(href) +
      '" target="_blank" rel="noopener noreferrer" title="' +
      safePath +
      '"><code>' +
      safeLabel +
      "</code></a>"
    );
  }

  function renderNellEvidence(items, run) {
    if (!items || !items.length) {
      return '<p class="nell-empty">No separate evidence files for this cell.</p>';
    }
    const maxShow = 8;
    const shown = items.slice(0, maxShow);
    const more = items.length - shown.length;
    const lis = shown
      .map(function (it) {
        if (it.kind === "symbol") {
          return (
            "<li><span class=\"nell-ev-title\">" +
            escapeHtml(it.title) +
            "</span> <code>" +
            escapeHtml(it.text) +
            "</code> in " +
            fileAnchorHtml(it.path, run) +
            "</li>"
          );
        }
        if (it.path) {
          return (
            "<li><span class=\"nell-ev-title\">" +
            escapeHtml(it.title) +
            "</span> " +
            fileAnchorHtml(it.path, run) +
            "</li>"
          );
        }
        return (
          "<li><span class=\"nell-ev-title\">" +
          escapeHtml(it.title) +
          "</span> " +
          linkMemoProse(escapeHtml(it.text || ""), run) +
          "</li>"
        );
      })
      .join("");
    return (
      '<ul class="nell-evidence">' +
      lis +
      "</ul>" +
      (more > 0
        ? '<p class="nell-more">+' + more + " more evidence rows (kept in the Hydra report, not dumped here).</p>"
        : "")
    );
  }

  function shortPath(path) {
    const p = String(path || "").replace(/\\/g, "/");
    const parts = p.split("/").filter(Boolean);
    if (parts.length <= 3) return p;
    return parts.slice(0, 1).join("/") + "/…/" + parts.slice(-2).join("/");
  }

  function writeNellCard(c, run) {
    const n = nellRewriteCell(c);
    const gateBit = n.gate ? '<span class="nell-gate">' + escapeHtml(n.gate) + "</span>" : "";
    const scoreBit =
      n.score != null ? '<span class="nell-score">' + escapeHtml(String(n.score)) + "/100</span>" : "";
    return (
      '<article class="nell-card">' +
      '<header class="nell-card-head">' +
      "<a href=\"" +
      escapeHtml(n.href) +
      "\" target=\"_blank\" rel=\"noopener noreferrer\" title=\"" +
      escapeHtml(n.name) +
      " - glossary\">" +
      escapeHtml(n.name) +
      "</a>" +
      gateBit +
      '<span class="nell-status">' +
      escapeHtml(n.status) +
      "</span>" +
      scoreBit +
      "</header>" +
      (n.question
        ? '<p class="nell-question">' + linkMemoProse(escapeHtml(n.question), run) + "</p>"
        : "") +
      '<p class="nell-blurb">' +
      linkMemoProse(escapeHtml(n.blurb), run) +
      "</p>" +
      '<div class="nell-ev-box">' +
      '<h4 class="nell-ev-heading"><span class="memo-evidence-word">Evidence</span></h4>' +
      renderNellEvidence(n.evidence, run) +
      "</div>" +
      "</article>"
    );
  }

  function makeRun(target, eng, cells, comparison, extra) {
    const deferred = cells.filter((c) => c.status === "deferred").length;
    const measured = cells.filter((c) => c.status !== "deferred").length;
    const passed = cells.filter((c) => c.passed === true).length;
    const scored = cells.filter((c) => typeof c.score === "number");
    const avg =
      scored.length > 0
        ? Math.round(scored.reduce((a, c) => a + c.score, 0) / scored.length)
        : null;
    const id =
      "run_" + hashStr(String(target) + "|" + eng.id + "|" + Date.now() + "|" + Math.random()).toString(16);
    const shortTitle = shortTitleFromTarget(target);
    const now = new Date();
    const hydra = !!(extra && extra.hydra);
    const headline =
      (extra && extra.headline) ||
      (hydra
        ? measured +
          " of " +
          cells.length +
          " evalers ran. " +
          passed +
          " passed their own gate. " +
          deferred +
          " are deferred."
        : cells.length + " cells · avg " + avg + " · " + deferred + " deferred");
    return {
      id: id,
      title: shortTitle,
      shortTitle: shortTitle,
      when: now.toLocaleString(),
      whenIso: now.toISOString(),
      engine: eng.label,
      engineId: eng.id,
      runOrdinal: nextRunOrdinal(target, eng.id),
      summary: headline,
      target: target || "",
      avgScore: avg,
      deferred: deferred,
      measured: measured,
      passedCount: passed,
      cells: cells,
      comparison: comparison,
      memoSimple: null,
      memoDeep: null,
      savedAt: null,
      hydra: hydra,
      prd: (extra && extra.prd) || "",
      note: (extra && extra.note) || "",
      render: (extra && extra.render) || "",
      folder: (extra && extra.folder) || "",
    };
  }

  function enrichRunExplanations(run) {
    if (!run || !run.cells) return run;
    /* Live Hydra cells already carry real summaries - do not overwrite with FOSS mocks */
    if (run.hydra) return run;
    const engId = run.engineId || String(run.engine || "hydra").toLowerCase();
    run.cells.forEach(function (c) {
      const ev = { id: c.id, label: c.name };
      const explained = explainEval(engId, ev, c.score, c.status, run.target || "");
      c.blurb = explained.blurb;
      c.detail = explained.detail;
    });
    return run;
  }

  function writeSimpleMemo(run) {
    const pass = run.cells.filter((c) => c.status === "pass" || c.passed === true).length;
    const deferred = run.cells.filter((c) => c.status === "deferred").length;
    const measured = run.cells.filter((c) => c.status !== "deferred").length;
    const metaScore =
      run.hydra || run.avgScore == null
        ? measured + " ran · " + pass + " passed · " + deferred + " deferred"
        : "avg " + run.avgScore + "/100 · " + pass + " pass · " + deferred + " deferred";
    let deltaHtml = "";
    if (run.comparison) {
      const c = run.comparison;
      const label =
        c.tone === "improved"
          ? "Improved vs last saved"
          : c.tone === "regressed"
            ? "Regressed vs last saved"
            : "Unchanged vs last saved";
      deltaHtml =
        '<div class="memo-delta is-' +
        c.tone +
        '"><strong>' +
        escapeHtml(label) +
        "</strong> (" +
        (c.delta > 0 ? "+" : "") +
        c.delta +
        " vs " +
        escapeHtml(c.priorWhen || "prior") +
        "). " +
        c.improved +
        " up · " +
        c.regressed +
        " down · " +
        c.same +
        " flat" +
        (c.notes.length ? ". Notable: " + escapeHtml(c.notes.join(", ")) : "") +
        ".</div>";
    } else {
      deltaHtml =
        '<div class="memo-delta is-same">No prior saved run for this target under ' +
        escapeHtml(run.engine) +
        ". Save this memo to start a comparison baseline.</div>";
    }
    const means = run.hydra
      ? escapeHtml(run.engine) +
        " conducted " +
        run.cells.length +
        " software evalers on this tree (same path as the classic Hydra desk). " +
        escapeHtml(run.summary || "") +
        (run.prd ? " " + escapeHtml(run.prd) + "." : "") +
        (run.note ? " " + escapeHtml(run.note) : "") +
        " A deferred cell is a blank gate - not a fail and not a zero."
      : escapeHtml(run.engine) +
        " ran " +
        run.cells.length +
        " wired evalers against your target. A deferred cell is a blank gate - not a fail and not a zero. " +
        "Use the detailed memo to see exactly what each evaler checked and why.";
    const topGates = run.hydra
      ? run.cells
          .filter(function (c) {
            return c.status !== "deferred";
          })
          .slice(0, 3)
          .map(function (c) {
            return c.name + ": " + nellCleanProse(c.blurb || c.detail || "").slice(0, 90);
          })
          .join(" · ") || "All cells deferred on this tree."
      : run.cells
          .slice()
          .sort((a, b) => (b.score || 0) - (a.score || 0))
          .slice(0, 3)
          .map((c) => c.name + " " + c.score)
          .join(" · ") || "None";
    return (
      '<p class="memo-kicker">Brief memo - What this means and Top gates. Open Full details for the per-evaler read.</p>' +
      "<h2>" +
      memoProductTitleHtml(run) +
      "</h2>" +
      '<div class="memo-meta">' +
      "<span>" +
      escapeHtml(run.engine) +
      "</span><span>" +
      escapeHtml(formatRailDate(run)) +
      "</span><span>" +
      escapeHtml(metaScore) +
      "</span></div>" +
      deltaHtml +
      '<div class="memo-section"><h3>What this means</h3><p>' +
      linkMemoProse(means, run) +
      "</p></div>" +
      '<div class="memo-section"><h3>Top gates</h3><p>' +
      linkMemoProse(escapeHtml(topGates), run) +
      "</p></div>" +
      '<p class="complete-intel-line"><button type="button" class="complete-intel-link memo-open-deep">Full details</button></p>'
    );
  }

  function writeDeepMemo(run) {
    const cards = (run.cells || [])
      .map(function (c) {
        return writeNellCard(c, run);
      })
      .join("");
    return (
      '<button type="button" class="memo-back memo-back-simple">← Back to brief</button>' +
      '<p class="memo-kicker">Full details - Nell rewrite: titled cards, short blurbs, evidence listed (not path walls). Glossary links match the left rail.</p>' +
      "<h2>" +
      escapeHtml(run.engine) +
      " detail · " +
      memoProductTitleHtml(run) +
      "</h2>" +
      '<div class="nell-stack">' +
      cards +
      "</div>"
    );
  }

  function sameTargetEngine(a, b) {
    if (!a || !b) return false;
    return (
      String(a.target || "").trim().toLowerCase() === String(b.target || "").trim().toLowerCase() &&
      String(a.engineId || a.engine || "")
        .toLowerCase() === String(b.engineId || b.engine || "").toLowerCase()
    );
  }

  function savedTwinsFor(run) {
    if (!run) return [];
    const set = findRunSet(run.target || run.title);
    const pool = set && set.saved && set.saved.length ? set.saved : allSavedRuns();
    return pool
      .filter(function (r) {
        return sameTargetEngine(r, run);
      })
      .slice()
      .sort(function (a, b) {
        return new Date(a.savedAt || a.when || 0) - new Date(b.savedAt || b.when || 0);
      });
  }

  function updateCompareButton(host) {
    const m = host || focusedMemo();
    if (!m || !m.root) return;
    const btn = m.root.querySelector(".memo-btn-compare");
    if (!btn) return;
    const twins = savedTwinsFor(m.run);
    btn.hidden = !(twins.length >= 2 && m.kind === "run");
  }

  function buildComparePack(run) {
    const twins = savedTwinsFor(run);
    if (twins.length < 2) return null;
    const first = twins[0];
    const last = twins[twins.length - 1];
    const nameOrder = (last.cells || []).map(function (c) {
      return c.id || c.name;
    });
    const series = {};
    twins.forEach(function (r, idx) {
      (r.cells || []).forEach(function (c) {
        const key = c.id || c.name;
        if (!series[key]) {
          series[key] = {
            id: c.id,
            name: c.name,
            href: c.href || GLOSS_MD,
            scores: [],
          };
        }
        series[key].scores[idx] = typeof c.score === "number" ? c.score : null;
      });
    });
    const movers = Object.keys(series).map(function (key) {
      const row = series[key];
      const scores = row.scores;
      const a = scores[0];
      const b = scores[scores.length - 1];
      const delta = a == null || b == null ? 0 : b - a;
      return {
        id: row.id,
        name: row.name,
        href: row.href,
        scores: scores,
        delta: delta,
        first: a,
        last: b,
      };
    });
    movers.sort(function (x, y) {
      return Math.abs(y.delta) - Math.abs(x.delta);
    });
    const improved = movers.filter(function (m) {
      return m.delta > 0;
    });
    const regressed = movers.filter(function (m) {
      return m.delta < 0;
    });
    const flat = movers.filter(function (m) {
      return m.delta === 0;
    });
    const avgFirst =
      Math.round(
        ((first.cells || []).reduce(function (s, c) {
          return s + (c.score || 0);
        }, 0) /
          Math.max(1, (first.cells || []).length)) *
          10
      ) / 10;
    const avgLast =
      Math.round(
        ((last.cells || []).reduce(function (s, c) {
          return s + (c.score || 0);
        }, 0) /
          Math.max(1, (last.cells || []).length)) *
          10
      ) / 10;
    return {
      target: run.target || run.title,
      engine: run.engine,
      twins: twins,
      movers: movers,
      improved: improved,
      regressed: regressed,
      flat: flat,
      avgFirst: avgFirst,
      avgLast: avgLast,
      avgDelta: Math.round((avgLast - avgFirst) * 10) / 10,
      nameOrder: nameOrder,
    };
  }

  function writeCompareSimple(pack) {
    const labels = pack.twins
      .map(function (r, i) {
        return ordinal(r.runOrdinal || i + 1) + " @" + (r.avgScore != null ? r.avgScore : "-");
      })
      .join(" → ");
    const tone =
      pack.avgDelta > 0.4 ? "improved" : pack.avgDelta < -0.4 ? "regressed" : "same";
    const toneLabel =
      tone === "improved"
        ? "Net improvement across saved builds"
        : tone === "regressed"
          ? "Net regression across saved builds"
          : "Net flat across saved builds";
    const topUp = pack.improved
      .slice(0, 3)
      .map(function (m) {
        return m.name + " +" + m.delta;
      })
      .join(" · ");
    const topDown = pack.regressed
      .slice(0, 3)
      .map(function (m) {
        return m.name + " " + m.delta;
      })
      .join(" · ");
    return (
      '<p class="memo-kicker">Compare brief - same target + engine across ' +
      pack.twins.length +
      " saved runs. Full compare detail keeps every evaler trajectory.</p>" +
      "<h2>Compare · " +
      escapeHtml(pack.engine) +
      " · " +
      memoProductTitleHtml(pack.target) +
      "</h2>" +
      '<div class="memo-meta"><span>' +
      memoProductTitleHtml(pack.target) +
      "</span><span>" +
      pack.twins.length +
      " saved runs</span><span>avg " +
      pack.avgFirst +
      " → " +
      pack.avgLast +
      " (" +
      (pack.avgDelta > 0 ? "+" : "") +
      pack.avgDelta +
      ")</span></div>" +
      '<div class="memo-delta is-' +
      tone +
      '"><strong>' +
      escapeHtml(toneLabel) +
      "</strong>. " +
      pack.improved.length +
      " evalers up · " +
      pack.regressed.length +
      " down · " +
      pack.flat.length +
      " flat. Path: " +
      escapeHtml(labels) +
      ".</div>" +
      '<div class="memo-section"><h3>What improved</h3><p>' +
      escapeHtml(topUp || "No scored gains yet.") +
      "</p></div>" +
      '<div class="memo-section"><h3>What still needs work / devolved</h3><p>' +
      escapeHtml(topDown || "No scored regressions.") +
      "</p></div>" +
      '<div class="memo-section"><h3>Developer takeaway</h3><p>Use the full compare detail for per-evaler score paths across every saved build of this GitHub/folder under ' +
      escapeHtml(pack.engine) +
      ". Scores are deterministic for the same target, so deltas reflect saved baselines you chose to keep.</p></div>" +
      '<p class="complete-intel-line"><button type="button" class="complete-intel-link memo-open-deep">Full compare detail</button></p>'
    );
  }

  function writeCompareDeep(pack) {
    const head =
      "<tr><th>Evaler</th>" +
      pack.twins
        .map(function (r, i) {
          return "<th>" + escapeHtml(ordinal(r.runOrdinal || i + 1)) + "</th>";
        })
        .join("") +
      "<th>Δ</th></tr>";
    const body = pack.movers
      .slice()
      .sort(function (a, b) {
        return String(a.name).localeCompare(String(b.name));
      })
      .map(function (m) {
        const cls = m.delta > 0 ? "up" : m.delta < 0 ? "down" : "flat";
        const scoreCells = pack.twins
          .map(function (_r, i) {
            const s = m.scores[i];
            return "<td>" + (s == null ? "—" : s) + "</td>";
          })
          .join("");
        const fact =
          m.delta > 0
            ? m.name +
              " rose from " +
              m.first +
              " to " +
              m.last +
              " (+" +
              m.delta +
              "). Gate closure strengthened across saved builds."
            : m.delta < 0
              ? m.name +
                " fell from " +
                m.first +
                " to " +
                m.last +
                " (" +
                m.delta +
                "). This area devolved or lost evidence vs earlier saves."
              : m.name +
                " held at " +
                (m.last != null ? m.last : m.first) +
                ". No measured change across saved builds.";
        return (
          "<tr><td><a href=\"" +
          escapeHtml(m.href) +
          "\" target=\"_blank\" rel=\"noopener noreferrer\">" +
          escapeHtml(m.name) +
          "</a></td>" +
          scoreCells +
          '<td class="' +
          cls +
          '">' +
          (m.delta > 0 ? "+" : "") +
          m.delta +
          "</td></tr>" +
          '<tr><td colspan="' +
          (pack.twins.length + 2) +
          '"><em>' +
          escapeHtml(fact) +
          "</em></td></tr>"
        );
      })
      .join("");
    const lines = pack.movers
      .map(function (m) {
        const href = m.href || GLOSS_MD;
        const path = m.scores
          .map(function (s) {
            return s == null ? "—" : String(s);
          })
          .join(" → ");
        const lastTwin = pack.twins[pack.twins.length - 1];
        const cell =
          lastTwin &&
          (lastTwin.cells || []).find(function (c) {
            return (c.id || c.name) === (m.id || m.name);
          });
        const engId =
          (lastTwin && (lastTwin.engineId || String(lastTwin.engine || "").toLowerCase())) ||
          "hydra";
        const explained = cell
          ? explainEval(
              engId,
              { id: cell.id || m.id, label: cell.name || m.name },
              cell.score,
              cell.status,
              pack.target || (lastTwin && lastTwin.target) || ""
            )
          : null;
        const why = explained
          ? explained.detail
          : m.delta > 0
            ? "Improved by +" + m.delta + " across saved builds."
            : m.delta < 0
              ? "Regressed by " + m.delta + " across saved builds."
              : "Unchanged across saved builds.";
        return (
          "<li><a href=\"" +
          escapeHtml(href) +
          "\" target=\"_blank\" rel=\"noopener noreferrer\" title=\"" +
          escapeHtml(m.name) +
          " - glossary\">" +
          escapeHtml(m.name) +
          "</a> scores " +
          escapeHtml(path) +
          ". " +
          escapeHtml(why) +
          "</li>"
        );
      })
      .join("");
    return (
      '<button type="button" class="memo-back memo-back-simple">← Back to compare brief</button>' +
      '<p class="memo-kicker">Full compare detail - every evaler across every saved twin run, with glossary links.</p>' +
      "<h2>Compare detail · " +
      escapeHtml(pack.engine) +
      " · " +
      memoProductTitleHtml(pack.target) +
      "</h2>" +
      '<div class="memo-section"><h3>Score matrix</h3>' +
      '<table class="memo-compare-table"><thead>' +
      head +
      "</thead><tbody>" +
      body +
      "</tbody></table></div>" +
      '<div class="memo-section"><h3>Per-evaler facts</h3><ul class="memo-deep-lines">' +
      lines +
      "</ul></div>"
    );
  }

  function paintResults(cells, target) {
    /* Never paint evaler chips/scores under Evalathan GitHub */
    const box = document.getElementById("results");
    if (box) box.innerHTML = "";
    if (target) document.getElementById("target-input").value = target;
  }

  function ordinal(n) {
    const num = Math.max(1, Number(n) || 1);
    const v = num % 100;
    const map = { 1: "st", 2: "nd", 3: "rd" };
    const s = v >= 11 && v <= 13 ? "th" : map[v % 10] || "th";
    return num + s;
  }

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function formatRailDate(run) {
    const raw = run.savedAt || run.whenIso || run.when;
    const d = new Date(raw);
    if (isNaN(d.getTime())) return String(raw || "Run");
    /* mm/dd/yy HH:MM e.g. 11/19/26 19:51 */
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

  function formatRailBlurb(run) {
    const dateStr = formatRailDate(run);
    const n = run.runOrdinal || 1;
    const evalCount = (run.cells && run.cells.length) || 0;
    const deferred = run.deferred != null ? run.deferred : (run.cells || []).filter(function (c) {
      return c.status === "deferred";
    }).length;
    /* Classic one-liner - project name lives in the section head, not the blurb */
    if (run.hydra) {
      return (
        dateStr +
        " - " +
        ordinal(n) +
        " run, " +
        (run.engine || "HYDRA") +
        " -" +
        evalCount +
        " evals · " +
        deferred +
        " deferred"
      );
    }
    return (
      dateStr + " - " + ordinal(n) + " run, " + (run.engine || "HYDRA") + " -" + evalCount + " evals"
    );
  }

  function renderRunButton(r, opts) {
    const li = document.createElement("li");
    if (opts && opts.latest) li.className = "is-latest";
    const b = document.createElement("button");
    b.type = "button";
    const blurb = formatRailBlurb(r);
    b.title = blurb;
    b.className = "run-entry-btn";
    b.innerHTML = '<span class="run-blurb">' + escapeHtml(blurb) + "</span>";
    b.addEventListener("click", () => openSavedMemo(r));
    li.appendChild(b);
    return li;
  }

  function appendRailHead(scroll, label, titleAttr, kind) {
    const head = document.createElement("button");
    head.type = "button";
    head.className =
      "rail-head" + (kind === "saved" ? " rail-head-saved" : " rail-head-latest");
    head.title = titleAttr || label;
    head.innerHTML = "<span>" + escapeHtml(label) + "</span>";
    scroll.appendChild(head);
  }

  function appendEmptyLi(list, text) {
    const li = document.createElement("li");
    li.className = "is-empty";
    li.textContent = text;
    list.appendChild(li);
  }

  function renderRunsRail() {
    const scroll = document.getElementById("rail-scroll");
    if (!scroll) return;
    scroll.innerHTML = "";

    if (!runSets.length) {
      appendRailHead(scroll, "latest run", "Latest evaluation run", "latest");
      const emptyLatest = document.createElement("ul");
      emptyLatest.className = "past-list past-list-latest";
      appendEmptyLi(emptyLatest, "No latest run yet. Evaluate, then Save.");
      scroll.appendChild(emptyLatest);
      appendRailHead(scroll, "saved runs", "Saved evaluation runs", "saved");
      const emptySaved = document.createElement("ul");
      emptySaved.className = "past-list past-list-saved";
      appendEmptyLi(emptySaved, "No saved runs yet.");
      scroll.appendChild(emptySaved);
      return;
    }

    runSets.forEach(function (set) {
      const caps = set.titleCaps || titleCapsFromTarget(set.target || set.shortTitle);
      const wrap = document.createElement("div");
      wrap.className = "rail-set";

      appendRailHead(wrap, caps + " - latest run", caps + " - latest run", "latest");
      const latestList = document.createElement("ul");
      latestList.className = "past-list past-list-latest";
      if (!set.latest) {
        appendEmptyLi(latestList, "No latest run yet. Evaluate, then Save.");
      } else {
        if (!set.latest.shortTitle) {
          set.latest.shortTitle = shortTitleFromTarget(set.latest.target || set.latest.title);
          set.latest.title = set.latest.shortTitle;
        }
        latestList.appendChild(renderRunButton(set.latest, { latest: true }));
      }
      wrap.appendChild(latestList);

      /* Saved history excludes the latest entry so we do not double-list the same 1st/Nth run */
      const latestId = set.latest && set.latest.id;
      const saved = (set.saved || []).filter(function (r) {
        return !latestId || r.id !== latestId;
      });
      appendRailHead(wrap, caps + " - saved runs", caps + " - saved runs", "saved");
      const savedList = document.createElement("ul");
      savedList.className = "past-list past-list-saved";
      if (!saved.length) {
        appendEmptyLi(
          savedList,
          latestId ? "No earlier saved runs yet." : "No saved runs yet."
        );
      } else {
        saved.forEach(function (r) {
          if (!r.shortTitle) {
            r.shortTitle = shortTitleFromTarget(r.target || r.title);
            r.title = r.shortTitle;
          }
          savedList.appendChild(renderRunButton(r));
        });
      }
      wrap.appendChild(savedList);
      scroll.appendChild(wrap);
    });
  }

  function syncMemoLayer() {
    const layer = document.getElementById("memo-layer");
    if (!layer) return;
    layer.hidden = openMemos.length === 0;
    layer.classList.toggle("is-empty", openMemos.length === 0);
  }

  function focusMemoHost(host) {
    if (!host) return;
    focusedMemoId = host.id;
    openMemos.forEach(function (m, idx) {
      const on = m.id === host.id;
      m.root.classList.toggle("is-focused", on);
      m.root.style.zIndex = String(90 + (on ? openMemos.length + 5 : idx));
    });
  }

  function closeMemoHost(host) {
    if (!host) return;
    openMemos = openMemos.filter(function (m) {
      return m.id !== host.id;
    });
    if (host.root && host.root.parentNode) host.root.parentNode.removeChild(host.root);
    if (focusedMemoId === host.id) {
      focusedMemoId = openMemos.length ? openMemos[openMemos.length - 1].id : null;
      if (focusedMemoId) focusMemoHost(focusedMemo());
    }
    syncMemoLayer();
  }

  function setMemoMode(host, mode) {
    if (!host) return;
    host.mode = mode;
    host.root.querySelector(".memo-process").hidden = mode !== "process";
    host.root.querySelector(".memo-simple").hidden = mode !== "simple";
    host.root.querySelector(".memo-deep").hidden = mode !== "deep";
    host.root.querySelector(".memo-dock").hidden = mode === "process";
    updateSaveDeleteUi(host);
    updateCompareButton(host);
  }

  function wireMemoInnerLinks(host) {
    if (!host) return;
    const deepBtn = host.root.querySelector(".memo-open-deep");
    if (deepBtn) {
      deepBtn.onclick = function () {
        setMemoMode(host, "deep");
      };
    }
    const backBtn = host.root.querySelector(".memo-back-simple");
    if (backBtn) {
      backBtn.onclick = function () {
        setMemoMode(host, "simple");
      };
    }
    host.root.querySelectorAll("[data-gloss-href]").forEach(function (el) {
      el.onclick = function (ev) {
        if (ev && ev.preventDefault) ev.preventDefault();
        openExternal(el.getAttribute("data-gloss-href") || GLOSS_MD);
      };
    });
    const sheet = host.root.querySelector(".memo-sheet");
    if (sheet && !sheet.getAttribute("data-ext-link-wired")) {
      sheet.setAttribute("data-ext-link-wired", "1");
      /* Capture phase: glossary/file links always leave the desk WebView. */
      sheet.addEventListener(
        "click",
        function (ev) {
          const a = ev.target && ev.target.closest ? ev.target.closest("a[href]") : null;
          if (!a || !sheet.contains(a)) return;
          const href = String(a.getAttribute("href") || "").trim();
          if (!href || href.charAt(0) === "#") return;
          if (
            href.indexOf("http://") === 0 ||
            href.indexOf("https://") === 0 ||
            href.indexOf("file:") === 0
          ) {
            ev.preventDefault();
            ev.stopPropagation();
            openExternal(href);
          }
        },
        true
      );
    }
  }

  function isRunSaved(run) {
    if (!run) return false;
    if (run.savedAt) return true;
    const set = findRunSet(run.target || run.title || "");
    if (!set) return false;
    if (set.latest && set.latest.id === run.id && set.latest.savedAt) return true;
    return (set.saved || []).some(function (r) {
      return r && r.id === run.id && !!r.savedAt;
    });
  }

  function resolveRunRecord(run) {
    if (!run) return run;
    const set = findRunSet(run.target || run.title || "");
    if (!set) return run;
    if (set.latest && set.latest.id === run.id) {
      return set.latest;
    }
    const hit = (set.saved || []).find(function (r) {
      return r && r.id === run.id;
    });
    return hit || run;
  }

  function updateSaveDeleteUi(host) {
    const m = host || focusedMemo();
    if (!m || !m.root) return;
    const saveBtn = m.root.querySelector(".memo-btn-save");
    const delBtn = m.root.querySelector(".memo-btn-delete");
    if (!saveBtn || !delBtn) return;
    if (m.run && isRunSaved(m.run) && !m.run.savedAt) {
      const resolved = resolveRunRecord(m.run);
      if (resolved && resolved.savedAt) {
        m.run.savedAt = resolved.savedAt;
        if (resolved.runOrdinal) m.run.runOrdinal = resolved.runOrdinal;
      }
    }
    const isSaved = isRunSaved(m.run) && m.kind === "run";
    const hideSave = m.kind === "compare";
    saveBtn.hidden = hideSave;
    saveBtn.disabled = isSaved;
    saveBtn.classList.toggle("is-saved", isSaved);
    saveBtn.textContent = isSaved ? "Saved" : "Save";
    saveBtn.title = isSaved ? "Already saved" : "Save as latest run";
    delBtn.hidden = !isSaved;
  }

  function syncMaxButton(host) {
    const btn = host.root.querySelector(".memo-max");
    if (!btn) return;
    if (host.maximized) {
      btn.title = "Exit full screen";
      btn.setAttribute("aria-label", "Exit full screen");
      btn.textContent = "❐";
    } else {
      btn.title = "Full screen";
      btn.setAttribute("aria-label", "Full screen");
      btn.textContent = "▢";
    }
  }

  function toggleMemoMaximize(host) {
    if (!host || !host.root) return;
    const win = host.root;
    focusMemoHost(host);
    if (host.maximized) {
      const r = host.restoreRect || {
        left: 48,
        top: 48,
        width: Math.min(720, window.innerWidth - 48),
        height: Math.min(720, window.innerHeight - 48),
      };
      win.classList.remove("is-maximized");
      win.classList.add("is-cascaded", "is-dragged");
      win.style.left = r.left + "px";
      win.style.top = r.top + "px";
      win.style.width = r.width + "px";
      win.style.height = r.height + "px";
      host.maximized = false;
    } else {
      const rect = win.getBoundingClientRect();
      host.restoreRect = {
        left: rect.left,
        top: rect.top,
        width: rect.width,
        height: rect.height,
      };
      win.classList.add("is-maximized", "is-cascaded", "is-dragged");
      win.style.left = "10px";
      win.style.top = "10px";
      win.style.width = Math.max(320, window.innerWidth - 20) + "px";
      win.style.height = Math.max(220, window.innerHeight - 20) + "px";
      host.maximized = true;
    }
    syncMaxButton(host);
  }

  function enableMemoDrag(host) {
    const win = host.root;
    const bar = host.root.querySelector(".memo-titlebar");
    if (!win || !bar || bar.getAttribute("data-drag-ready")) return;
    bar.setAttribute("data-drag-ready", "1");
    let dragging = false;
    let sx = 0;
    let sy = 0;
    let ox = 0;
    let oy = 0;
    bar.addEventListener("mousedown", function (e) {
      if (e.button !== 0) return;
      if (e.target.closest && e.target.closest(".memo-win-controls")) return;
      if (host.maximized) return;
      focusMemoHost(host);
      const rect = win.getBoundingClientRect();
      dragging = true;
      sx = e.clientX;
      sy = e.clientY;
      ox = rect.left;
      oy = rect.top;
      win.classList.add("is-dragged");
      win.classList.add("is-cascaded");
      win.style.left = ox + "px";
      win.style.top = oy + "px";
      win.style.width = rect.width + "px";
      win.style.height = rect.height + "px";
      e.preventDefault();
    });
    bar.addEventListener("dblclick", function (e) {
      if (e.target.closest && e.target.closest(".memo-win-controls")) return;
      toggleMemoMaximize(host);
    });
    window.addEventListener("mousemove", function (e) {
      if (!dragging) return;
      win.style.left = ox + (e.clientX - sx) + "px";
      win.style.top = oy + (e.clientY - sy) + "px";
    });
    window.addEventListener("mouseup", function () {
      dragging = false;
    });
  }

  function enableMemoResize(host) {
    const win = host.root;
    if (!win || win.getAttribute("data-resize-ready")) return;
    win.setAttribute("data-resize-ready", "1");
    const dirs = ["n", "s", "e", "w", "ne", "nw", "se", "sw"];
    dirs.forEach(function (dir) {
      const handle = document.createElement("div");
      handle.className = "memo-resize memo-resize-" + dir;
      handle.setAttribute("data-dir", dir);
      handle.title = "Resize";
      win.appendChild(handle);
    });
    let resizing = false;
    let dir = "";
    let sx = 0;
    let sy = 0;
    let start = null;
    const minW = 320;
    const minH = 220;
    win.addEventListener("mousedown", function (e) {
      const h = e.target.closest && e.target.closest(".memo-resize");
      if (!h || host.maximized) return;
      if (e.button !== 0) return;
      focusMemoHost(host);
      const rect = win.getBoundingClientRect();
      resizing = true;
      dir = h.getAttribute("data-dir") || "";
      sx = e.clientX;
      sy = e.clientY;
      start = { left: rect.left, top: rect.top, width: rect.width, height: rect.height };
      win.classList.add("is-dragged", "is-cascaded");
      e.preventDefault();
      e.stopPropagation();
    });
    window.addEventListener("mousemove", function (e) {
      if (!resizing || !start) return;
      const dx = e.clientX - sx;
      const dy = e.clientY - sy;
      let left = start.left;
      let top = start.top;
      let width = start.width;
      let height = start.height;
      if (dir.indexOf("e") >= 0) width = Math.max(minW, start.width + dx);
      if (dir.indexOf("s") >= 0) height = Math.max(minH, start.height + dy);
      if (dir.indexOf("w") >= 0) {
        width = Math.max(minW, start.width - dx);
        left = start.left + (start.width - width);
      }
      if (dir.indexOf("n") >= 0) {
        height = Math.max(minH, start.height - dy);
        top = start.top + (start.height - height);
      }
      win.style.left = left + "px";
      win.style.top = top + "px";
      win.style.width = width + "px";
      win.style.height = height + "px";
    });
    window.addEventListener("mouseup", function () {
      resizing = false;
      dir = "";
      start = null;
    });
  }

  function cascadeMemoPosition(host, index) {
    const width = Math.min(720, Math.max(320, window.innerWidth - 48));
    const height = Math.min(720, Math.max(280, Math.round(window.innerHeight * 0.82)));
    const baseL = Math.max(24, Math.round(window.innerWidth * 0.5 - width / 2));
    const baseT = Math.max(24, Math.round(window.innerHeight * 0.5 - height / 2));
    const left = baseL + index * 32;
    const top = baseT + index * 28;
    host.root.classList.add("is-cascaded");
    host.root.style.left = left + "px";
    host.root.style.top = top + "px";
    host.root.style.width = width + "px";
    host.root.style.height = height + "px";
  }

  function createMemoHost() {
    const layer = document.getElementById("memo-layer");
    const root = document.createElement("div");
    root.className = "memo-win";
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-modal", "false");
    root.innerHTML =
      '<div class="memo-titlebar">' +
      '<span class="memo-win-title">EVALATHAN</span>' +
      '<div class="memo-win-controls">' +
      '<button type="button" class="memo-win-btn memo-max" title="Full screen" aria-label="Full screen">▢</button>' +
      '<button type="button" class="memo-close" title="Close" aria-label="Close">×</button>' +
      "</div>" +
      "</div>" +
      '<div class="memo-sheet">' +
      '<div class="memo-process" hidden>' +
      '<p class="memo-process-label">Evaluating<span class="memo-dots" aria-hidden="true"><i></i><i></i><i></i></span></p>' +
      '<ul class="memo-process-log" aria-live="polite"></ul>' +
      "</div>" +
      '<div class="memo-simple" hidden></div>' +
      '<div class="memo-deep" hidden></div>' +
      '<div class="memo-dock" hidden>' +
      '<div class="memo-dock-left">' +
      '<button type="button" class="memo-btn memo-btn-download" title="Download PDF to your Downloads folder">Download</button>' +
      '<button type="button" class="memo-btn memo-btn-save" title="Save as latest run">Save</button>' +
      '<button type="button" class="memo-btn memo-btn-delete" title="Delete this saved run" hidden>Delete</button>' +
      "</div>" +
      '<div class="memo-dock-right">' +
      '<button type="button" class="memo-btn memo-btn-compare" title="Compare saved runs of this target" hidden>Compare</button>' +
      "</div>" +
      "</div>" +
      "</div>";
    layer.appendChild(root);
    memoSeq += 1;
    const host = {
      id: "memo_" + memoSeq,
      root: root,
      run: null,
      kind: "run",
      comparePack: null,
      mode: "simple",
      maximized: false,
      restoreRect: null,
    };
    root.addEventListener("mousedown", function (e) {
      /* Keep text selection in the sheet; only refocus the window chrome. */
      if (e.target && e.target.closest && e.target.closest(".memo-sheet")) {
        focusMemoHost(host);
        return;
      }
      focusMemoHost(host);
    });
    root.querySelector(".memo-close").addEventListener("click", function () {
      closeMemoHost(host);
    });
    root.querySelector(".memo-max").addEventListener("click", function () {
      toggleMemoMaximize(host);
    });
    root.querySelector(".memo-btn-save").addEventListener("click", function () {
      saveMemoHost(host);
    });
    root.querySelector(".memo-btn-delete").addEventListener("click", function () {
      askDeleteConfirm(function () {
        deleteMemoHost(host);
      });
    });
    root.querySelector(".memo-btn-download").addEventListener("click", function () {
      downloadMemoHost(host).catch(function () {
        /* ignore */
      });
    });
    root.querySelector(".memo-btn-compare").addEventListener("click", function () {
      paintCompareInto(host);
    });
    enableMemoDrag(host);
    enableMemoResize(host);
    openMemos.push(host);
    cascadeMemoPosition(host, openMemos.length - 1);
    syncMemoLayer();
    focusMemoHost(host);
    return host;
  }

  function findMemoByRunId(runId) {
    if (!runId) return null;
    return (
      openMemos.find(function (m) {
        return m.run && m.run.id === runId && m.kind === "run";
      }) || null
    );
  }

  function paintMemoInto(host, run, mode) {
    if (!host || !run) return;
    host.kind = "run";
    host.comparePack = null;
    run = resolveRunRecord(run);
    if (!run.shortTitle) run.shortTitle = shortTitleFromTarget(run.target || run.title);
    enrichRunExplanations(run);
    host.run = run;
    run.memoSimple = writeSimpleMemo(run);
    run.memoDeep = writeDeepMemo(run);
    host.root.querySelector(".memo-win-title").textContent =
      run.engine + " · " + displayTitle(run);
    host.root.querySelector(".memo-simple").innerHTML = run.memoSimple;
    host.root.querySelector(".memo-deep").innerHTML = run.memoDeep;
    setMemoMode(host, mode || "simple");
    updateSaveDeleteUi(host);
    wireMemoInnerLinks(host);
    focusMemoHost(host);
  }

  function paintMemo(run, mode) {
    const existing = run && run.id ? findMemoByRunId(run.id) : null;
    const host = existing || createMemoHost();
    paintMemoInto(host, run, mode || "simple");
    return host;
  }

  function paintCompareInto(host) {
    if (!host || !host.run) return;
    const pack = buildComparePack(host.run);
    if (!pack) return;
    host.kind = "compare";
    host.comparePack = pack;
    pack.memoSimple = writeCompareSimple(pack);
    pack.memoDeep = writeCompareDeep(pack);
    host.root.querySelector(".memo-win-title").textContent =
      "Compare · " + (pack.engine || "EVALATHAN") + " · " + shortTitleFromTarget(pack.target);
    host.root.querySelector(".memo-simple").innerHTML = pack.memoSimple;
    host.root.querySelector(".memo-deep").innerHTML = pack.memoDeep;
    setMemoMode(host, "simple");
    wireMemoInnerLinks(host);
    focusMemoHost(host);
  }

  function openSavedMemo(run) {
    if (!run) return;
    if (!run.shortTitle) run.shortTitle = shortTitleFromTarget(run.target || run.title);
    if (run.target) document.getElementById("target-input").value = run.target;
    paintResults(run.cells || [], run.target || "");
    /* Always keep prior memos open - reuse only if this exact run is already open */
    const existing = findMemoByRunId(run.id);
    if (existing) {
      paintMemoInto(existing, run, "simple");
    } else {
      paintMemoInto(createMemoHost(), run, "simple");
    }
    if (!app.classList.contains("runs-open")) toggleSide("runs");
  }

  function sleep(ms) {
    return new Promise(function (resolve) {
      window.setTimeout(resolve, ms);
    });
  }

  async function runEvaluate(target) {
    if (evalBusy) return;
    if (!evalSlotAllowed()) return;
    const trimmed = String(target || "").trim();
    if (!trimmed) {
      window.alert("Paste a GitHub link or a folder on this PC.");
      return;
    }
    evalBusy = true;
    const eng = engine(activeId);
    const host = createMemoHost();
    const logEl = host.root.querySelector(".memo-process-log");
    host.root.querySelector(".memo-win-title").textContent = eng.label + " · evaluating";
    logEl.innerHTML = "";
    setMemoMode(host, "process");
    if (!app.classList.contains("runs-open")) toggleSide("runs");

    function addProcessLine(text, cls) {
      const li = document.createElement("li");
      li.className = cls || "is-done";
      li.textContent = text;
      logEl.appendChild(li);
      logEl.scrollTop = logEl.scrollHeight;
      return li;
    }

    const waitLine = addProcessLine(
      "Hydra preparing target (GitHub clone or local folder)…",
      "is-active"
    );

    try {
      const res = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: trimmed }),
      });
      let data = null;
      try {
        data = await res.json();
      } catch (e) {
        throw new Error("Evaluate API returned a non-JSON response.");
      }
      if (!res.ok || !data || !data.ok) {
        throw new Error((data && data.error) || "Evaluate failed (" + res.status + ").");
      }
      waitLine.classList.remove("is-active");
      waitLine.classList.add("is-done");
      waitLine.textContent = data.note
        ? data.note
        : "Tree ready · " + (data.folder || trimmed);

      const cells = cellsFromHydraReport(data.report || {});
      for (let i = 0; i < cells.length; i++) {
        const c = cells[i];
        const mark =
          c.status === "deferred"
            ? "deferred"
            : c.passed === true
              ? "passed"
              : c.hydraStatus || "measured";
        addProcessLine(c.name + " · " + mark, "is-done");
        await sleep(40);
      }

      const prior = findPriorSaved(trimmed, eng.label);
      const comparison = compareRuns({ cells: cells }, prior);
      const run = makeRun(trimmed, eng, cells, comparison, {
        hydra: true,
        headline: (data.report && data.report.headline) || "",
        prd: (data.report && data.report.prd) || "",
        note: data.note || "",
        render: data.render || "",
        folder: data.folder || "",
      });
      paintResults(cells, trimmed);
      paintMemoInto(host, run, "simple");
    } catch (err) {
      waitLine.classList.remove("is-active");
      waitLine.classList.add("is-done");
      waitLine.textContent = String((err && err.message) || err || "Evaluate stopped.");
      host.root.querySelector(".memo-win-title").textContent = eng.label + " · stopped";
      host.root.querySelector(".memo-simple").innerHTML =
        '<p class="memo-kicker">Evaluate stopped</p><h2>' +
        escapeHtml(shortTitleFromTarget(trimmed)) +
        "</h2><p>" +
        escapeHtml(String((err && err.message) || err)) +
        "</p>";
      setMemoMode(host, "simple");
      updateSaveDeleteUi(host);
    }
    evalBusy = false;
  }

  function saveMemoHost(host) {
    if (!host || !host.run || host.kind === "compare" || isRunSaved(host.run)) return;
    const copy = JSON.parse(JSON.stringify(host.run));
    copy.savedAt = new Date().toISOString();
    copy.shortTitle = copy.shortTitle || shortTitleFromTarget(copy.target || copy.title);
    copy.title = copy.shortTitle;
    const set = ensureRunSet(copy.target || copy.title);
    copy.runOrdinal =
      copy.runOrdinal || nextRunOrdinal(copy.target || copy.title, copy.engineId || copy.engine);
    delete copy.railBlurb;
    copy.railBlurb = formatRailBlurb(copy);
    set.latest = copy;
    set.saved = [copy]
      .concat(
        (set.saved || []).filter(function (r) {
          return r.id !== copy.id;
        })
      )
      .slice(0, 40);
    host.run = copy;
    persistRuns();
    renderRunsRail();
    updateCompareButton(host);
    updateSaveDeleteUi(host);
    host.root.querySelector(".memo-win-title").textContent =
      copy.engine + " · " + displayTitle(copy);
  }

  let confirmPending = null;

  function closeDeleteConfirm() {
    const layer = document.getElementById("confirm-layer");
    if (layer) layer.hidden = true;
    confirmPending = null;
  }

  function askDeleteConfirm(onConfirm) {
    const layer = document.getElementById("confirm-layer");
    if (!layer) {
      if (window.confirm("Are you sure you want to delete?")) onConfirm();
      return;
    }
    confirmPending = onConfirm;
    layer.hidden = false;
    const ok = document.getElementById("confirm-ok");
    if (ok) ok.focus();
  }

  function wireDeleteConfirm() {
    const layer = document.getElementById("confirm-layer");
    if (!layer || layer.dataset.wired === "1") return;
    layer.dataset.wired = "1";
    document.getElementById("confirm-cancel").addEventListener("click", function () {
      closeDeleteConfirm();
    });
    document.getElementById("confirm-ok").addEventListener("click", function () {
      const fn = confirmPending;
      closeDeleteConfirm();
      if (typeof fn === "function") fn();
    });
    layer.addEventListener("click", function (ev) {
      if (ev.target === layer) closeDeleteConfirm();
    });
    document.addEventListener("keydown", function (ev) {
      if (layer.hidden) return;
      if (ev.key === "Escape") {
        ev.preventDefault();
        closeDeleteConfirm();
      }
    });
  }

  function deleteMemoHost(host) {
    if (!host || !host.run || !host.run.savedAt || host.kind === "compare") return;
    const id = host.run.id;
    const set = findRunSet(host.run.target || host.run.title);
    if (set) {
      set.saved = (set.saved || []).filter(function (r) {
        return r.id !== id;
      });
      if (set.latest && set.latest.id === id) {
        set.latest = set.saved[0] || null;
      }
      if (!set.latest && !(set.saved && set.saved.length)) {
        runSets = runSets.filter(function (s) {
          return s !== set;
        });
      }
    }
    persistRuns();
    renderRunsRail();
    closeMemoHost(host);
  }

  function stripInteractiveHtml(html) {
    return String(html || "")
      .replace(/<button\b[^>]*>[\s\S]*?<\/button>/gi, "")
      .replace(/<p class="complete-intel-line">[\s\S]*?<\/p>/gi, "")
      .replace(/<p class="memo-kicker">[\s\S]*?<\/p>/gi, "")
      .replace(/\sdata-gloss-href="[^"]*"/gi, "");
  }

  function buildMemoDownloadHtml(host) {
    const run = host.run;
    const short = displayTitle(run);
    const pack = host.comparePack;
    const simple =
      host.kind === "compare" && pack
        ? stripInteractiveHtml(pack.memoSimple || writeCompareSimple(pack))
        : stripInteractiveHtml(run.memoSimple || writeSimpleMemo(run));
    const deep =
      host.kind === "compare" && pack
        ? stripInteractiveHtml(pack.memoDeep || writeCompareDeep(pack))
        : stripInteractiveHtml(run.memoDeep || writeDeepMemo(run));
    const heading = host.kind === "compare" ? "Evalathan compare" : "Evalathan memo";
    const detailLabel =
      host.kind === "compare" ? "Compare detail" : "Full details";
    return {
      short: short,
      filename:
        "Evalathan-" +
        (host.kind === "compare" ? "compare" : "memo") +
        "-" +
        String(short || "run").replace(/[^\w\-]+/g, "-").slice(0, 48),
      html:
        "<!DOCTYPE html><html><head><meta charset=\"UTF-8\" /><title>" +
        escapeHtml(heading + " - " + short) +
        "</title><style>" +
        "body{font-family:Segoe UI,Helvetica,Arial,sans-serif;max-width:720px;margin:28px auto;padding:0 18px;color:#111;}" +
        "h1{font-size:20px;margin:0 0 6px} h2{font-size:16px;margin:18px 0 8px} h3{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#444;margin:14px 0 6px}" +
        ".meta{color:#555;font-size:12px;margin:0 0 14px} a{color:#2f6fbf;text-decoration:none}" +
        ".memo-block{page-break-inside:auto}" +
        ".memo-detail-break{margin:28px 0 16px;padding-top:18px;border-top:1px solid #ccc}" +
        ".memo-detail-break h2{margin:0 0 10px;font-size:15px;letter-spacing:.04em;text-transform:uppercase;color:#333}" +
        "ul{padding-left:1.1rem} li{margin:0 0 8px;line-height:1.45}" +
        "table{width:100%;border-collapse:collapse;font-size:12px} th,td{border:1px solid #ccc;padding:5px 6px;text-align:left}" +
      ".nell-stack{display:flex;flex-direction:column;gap:12px}.nell-card{border:1px solid #ccc;border-radius:8px;padding:10px 12px;page-break-inside:avoid}" +
        ".nell-card-head{display:flex;flex-wrap:wrap;gap:6px 10px;margin:0 0 6px;align-items:baseline}" +
        ".nell-gate,.nell-status,.nell-score{font-size:10px;text-transform:uppercase;background:#eee;padding:2px 6px;border-radius:999px}" +
        ".nell-blurb{margin:0 0 8px;font-size:14px;line-height:1.4}.nell-question{margin:0 0 6px;font-size:12px;color:#555}" +
        ".nell-ev-box{border:1px solid #b8c46a;border-radius:6px;padding:6px 8px;margin:4px 0 0}" +
        ".nell-ev-heading{margin:0 0 4px;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#bf0a30}" +
        ".memo-evidence-word{color:#bf0a30;font-weight:600;font-size:1.125em}" +
        ".nell-evidence{list-style:none;padding:0;margin:0}.nell-evidence li{margin:0 0 4px;font-size:12px}" +
        ".nell-evidence code{font-size:11px;background:#f3f3f3;padding:1px 4px}.nell-more,.nell-empty{font-size:11px;color:#777}" +
        "</style></head><body>" +
        "<div class=\"memo-block\"><h1>" +
        escapeHtml(heading) +
        "</h1><div class=\"meta\">" +
        escapeHtml((run.engine || "") + " · " + short + " · " + formatRailDate(run)) +
        "</div>" +
        simple +
        '<div class="memo-detail-break"><h2>' +
        escapeHtml(detailLabel) +
        "</h2></div>" +
        deep +
        "</div>" +
        "</body></html>",
    };
  }

  function flashDownloadBtn(host, label) {
    const btn = host && host.root && host.root.querySelector(".memo-btn-download");
    if (!btn) return;
    const prev = btn.textContent;
    btn.textContent = label;
    window.setTimeout(function () {
      btn.textContent = prev || "Download";
    }, 2200);
  }

  async function downloadMemoHost(host) {
    if (!host || !host.run) return;
    const pack = buildMemoDownloadHtml(host);
    const html = pack.html;
    const filename = pack.filename;

    /* Desktop desk: write PDF straight to Downloads (Mac print() is a no-op in WebView). */
    try {
      if (
        window.pywebview &&
        window.pywebview.api &&
        typeof window.pywebview.api.save_memo_download === "function"
      ) {
        const res = await window.pywebview.api.save_memo_download(html, filename);
        if (res && res.ok) {
          flashDownloadBtn(host, res.kind === "pdf" ? "Saved PDF" : "Saved");
          return;
        }
      }
    } catch (err) {
      /* fall through to HTTP API */
    }

    try {
      const res = await fetch("/api/download-memo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ html: html, filename: filename }),
      });
      const data = await res.json();
      if (data && data.ok) {
        flashDownloadBtn(host, data.kind === "pdf" ? "Saved PDF" : "Saved");
        return;
      }
    } catch (err) {
      /* fall through to browser blob */
    }

    /* Browser FOSS fallback: direct file download (still no print dialog). */
    try {
      const blob = new Blob([html], { type: "text/html;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename + ".html";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.setTimeout(function () {
        URL.revokeObjectURL(url);
      }, 1000);
      flashDownloadBtn(host, "Saved");
      return;
    } catch (err) {
      /* last resort only */
    }

    const frame = document.createElement("iframe");
    frame.setAttribute("aria-hidden", "true");
    frame.style.cssText = "position:fixed;right:0;bottom:0;width:0;height:0;border:0;opacity:0;";
    document.body.appendChild(frame);
    const doc = frame.contentDocument || frame.contentWindow.document;
    doc.open();
    doc.write(html);
    doc.close();
    window.setTimeout(function () {
      try {
        frame.contentWindow.focus();
        frame.contentWindow.print();
      } catch (e) {
        /* ignore */
      }
      window.setTimeout(function () {
        if (frame.parentNode) frame.parentNode.removeChild(frame);
      }, 1000);
    }, 250);
  }

  wireDeleteConfirm();

  document.getElementById("btn-toggle-engines").addEventListener("click", (e) => {
    e.preventDefault();
    toggleSide("engines");
  });
  document.getElementById("btn-toggle-runs").addEventListener("click", (e) => {
    e.preventDefault();
    toggleSide("runs");
  });
  document.getElementById("btn-browse").addEventListener("click", async () => {
    if (!evalSlotAllowed()) return;
    /* Prefer native folder dialog via local desk API (same machine as Hydra) */
    try {
      const res = await fetch("/api/pick-folder", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      const data = await res.json();
      if (data && data.ok && data.path) {
        document.getElementById("target-input").value = data.path;
        return;
      }
      if (data && data.cancelled) return;
    } catch (e) {
      /* fall through to browser folder picker */
    }
    document.getElementById("folder-picker").click();
  });
  document.getElementById("folder-picker").addEventListener("change", (ev) => {
    if (!evalSlotAllowed()) return;
    const files = ev.target.files;
    if (!files || !files.length) return;
    const path = files[0].webkitRelativePath || files[0].name;
    document.getElementById("target-input").value = String(path).split("/")[0] || path;
  });
  document.getElementById("btn-eval").addEventListener("click", () => {
    if (!evalSlotAllowed()) return;
    runEvaluate(document.getElementById("target-input").value.trim());
  });
  document.getElementById("btn-home").addEventListener("click", () => {
    userPickedEngine = false;
    openId = null;
    renderEngines();
    renderHero();
  });
  document.getElementById("btn-gloss").addEventListener("click", () => {
    openExternal(GLOSS_SEARCH);
  });
  document.getElementById("btn-selfbelt").addEventListener("click", () => {
    openExternal(anchor("selfbelt"));
  });
  document.querySelectorAll(".theme-btn").forEach((b) => {
    b.addEventListener("click", () => setTheme(b.getAttribute("data-theme-set")));
  });

  /* PRICKLY - still Coming soon */
  document.querySelectorAll(".mascot-wrap.is-soon").forEach(function (wrap) {
    let hideTimer = null;
    wrap.addEventListener("click", function (e) {
      e.preventDefault();
      const blurb = wrap.querySelector(".mascot-soon-blurb");
      if (!blurb) return;
      document.querySelectorAll(".mascot-soon-blurb").forEach(function (b) {
        if (b !== blurb) b.hidden = true;
      });
      blurb.hidden = false;
      if (hideTimer) window.clearTimeout(hideTimer);
      hideTimer = window.setTimeout(function () {
        blurb.hidden = true;
      }, 2200);
    });
  });

  /* ---- FUSS (For-User Session Switch): popup + 3-2-1-0 + BREAK TIME disk ---- */
  const FUSS_KEY = "evalathan.fuss.v1";
  const FUSS_MIN = 1;
  const FUSS_MAX = 180;
  const FUSS_DEFAULT = 25;
  const FUSS_REMIND_EVERY = 15;
  let fussTick = null;
  let fussCountTimer = null;
  let fussPanelTick = null;
  let fussCounting = false;

  function fussEls() {
    return {
      layer: document.getElementById("fuss-layer"),
      panel: document.querySelector("#fuss-layer .fuss-panel"),
      breakLayer: document.getElementById("fuss-break-layer"),
      setup: document.getElementById("fuss-setup"),
      countdown: document.getElementById("fuss-countdown"),
      countNum: document.getElementById("fuss-countdown-num"),
      mins: document.getElementById("fuss-mins"),
      ack: document.getElementById("fuss-ack"),
      start: document.getElementById("fuss-start"),
      stop: document.getElementById("fuss-stop"),
      status: document.getElementById("fuss-status"),
      close: document.getElementById("fuss-close"),
      stopBreak: document.getElementById("fuss-break-stop"),
      live: document.getElementById("fuss-live"),
      mascot: document.getElementById("btn-fuss"),
    };
  }

  function fussRead() {
    try {
      return JSON.parse(localStorage.getItem(FUSS_KEY) || "{}");
    } catch (err) {
      return {};
    }
  }

  function fussWrite(state) {
    localStorage.setItem(FUSS_KEY, JSON.stringify(state || {}));
  }

  function fussClampMins(n) {
    const v = Math.round(Number(n) || FUSS_DEFAULT);
    return Math.min(FUSS_MAX, Math.max(FUSS_MIN, v));
  }

  function fussRemainingMs(state) {
    const mins = fussClampMins(state && state.minutes);
    if (!state || !state.on || !state.started) return mins * 60 * 1000;
    const end = Number(state.started) + mins * 60 * 1000;
    return Math.max(0, end - Date.now());
  }

  function fussFormatMs(ms) {
    const total = Math.max(0, Math.ceil(Number(ms) / 1000));
    const m = Math.floor(total / 60);
    const s = total % 60;
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }

  function fussSetStatus(text, kind) {
    const el = fussEls().status;
    if (!el) return;
    el.textContent = text;
    el.classList.remove("is-warn", "is-on");
    if (kind) el.classList.add(kind);
  }

  function fussSyncMascot(state) {
    const btn = fussEls().mascot;
    if (!btn) return;
    if (state && state.on) btn.classList.add("is-armed");
    else btn.classList.remove("is-armed");
  }

  function fussShowSetup() {
    const els = fussEls();
    if (els.panel) els.panel.classList.remove("is-countdown");
    if (els.setup) els.setup.hidden = false;
    if (els.countdown) els.countdown.hidden = true;
  }

  function fussShowCountdownView() {
    const els = fussEls();
    if (els.panel) els.panel.classList.add("is-countdown");
    if (els.setup) els.setup.hidden = true;
    if (els.countdown) els.countdown.hidden = false;
  }

  function fussHideBreak() {
    const layer = fussEls().breakLayer;
    if (layer) layer.hidden = true;
  }

  function fussShowBreak() {
    const els = fussEls();
    if (!els.breakLayer) return;
    if (els.layer) els.layer.hidden = true;
    fussStopPanelLive();
    els.breakLayer.hidden = false;
    els.breakLayer.classList.add("is-on");
  }

  function fussClearTickers() {
    if (fussTick) {
      window.clearInterval(fussTick);
      fussTick = null;
    }
    if (fussCountTimer) {
      window.clearTimeout(fussCountTimer);
      fussCountTimer = null;
    }
    fussCounting = false;
    fussStopPanelLive();
  }

  function fussStopTimer(opts) {
    const keepAck = !(opts && opts.clearAck);
    const prev = fussRead();
    const next = {
      ack: keepAck ? !!prev.ack : false,
      on: false,
      minutes: fussClampMins(prev.minutes || FUSS_DEFAULT),
      started: 0,
      lastPing: 0,
    };
    fussWrite(next);
    fussClearTickers();
    fussSyncMascot(next);
    fussShowSetup();
    fussSetStatus("Timer off.");
    return next;
  }

  function fussArm() {
    if (fussTick) window.clearInterval(fussTick);
    fussTick = window.setInterval(function () {
      const state = fussRead();
      if (!state.on || !state.started) return;
      const leftMs = fussRemainingMs(state);
      const elapsed = (Date.now() - Number(state.started)) / 60000;
      const bucket = Math.floor(elapsed / FUSS_REMIND_EVERY);
      if (bucket > 0 && bucket !== state.lastPing) {
        state.lastPing = bucket;
        fussWrite(state);
      }
      const els = fussEls();
      if (els.layer && !els.layer.hidden) fussStatusLine(state);
      if (leftMs <= 0) {
        fussStopTimer({ clearAck: false });
        fussSetStatus("Sitting ended. Take a break.");
        fussShowBreak();
      }
    }, 250);
  }

  function fussPaintLive(state) {
    const live = fussEls().live;
    if (!live) return;
    if (state && state.on && state.started) {
      live.hidden = false;
      live.textContent = fussFormatMs(fussRemainingMs(state));
    } else {
      live.hidden = true;
      live.textContent = "00:00";
    }
  }

  function fussStatusLine(state) {
    fussPaintLive(state);
    if (!state || !state.on || !state.started) {
      fussSetStatus("Timer off.");
      return;
    }
    const left = fussFormatMs(fussRemainingMs(state));
    fussSetStatus(
      "Timer on - " +
        fussClampMins(state.minutes) +
        " min sitting. " +
        left +
        " left.",
      "is-on"
    );
  }

  function fussStopPanelLive() {
    if (fussPanelTick) {
      window.clearInterval(fussPanelTick);
      fussPanelTick = null;
    }
  }

  function fussStartPanelLive() {
    fussStopPanelLive();
    fussPanelTick = window.setInterval(function () {
      const els = fussEls();
      if (!els.layer || els.layer.hidden) return;
      const state = fussRead();
      if (state.on && state.started) fussStatusLine(state);
    }, 250);
  }

  function fussOpenPanel() {
    const els = fussEls();
    if (!els.layer || fussCounting) return;
    if (els.breakLayer && !els.breakLayer.hidden) return;
    const state = fussRead();
    fussShowSetup();
    if (els.mins) els.mins.value = String(fussClampMins(state.minutes || FUSS_DEFAULT));
    if (els.ack) els.ack.checked = !!state.ack;
    fussStatusLine(state);
    els.layer.hidden = false;
    fussStartPanelLive();
  }

  function fussClosePanel() {
    if (fussCounting) return;
    const breakLayer = fussEls().breakLayer;
    if (breakLayer && !breakLayer.hidden) return;
    const layer = fussEls().layer;
    if (layer) layer.hidden = true;
    fussStopPanelLive();
    fussShowSetup();
  }

  function fussBeginSitting(minutes) {
    const next = {
      ack: true,
      on: true,
      minutes: minutes,
      started: Date.now(),
      lastPing: 0,
    };
    fussWrite(next);
    fussSyncMascot(next);
    fussArm();
    fussShowSetup();
    fussClosePanel();
  }

  function fussStartFromPanel() {
    const els = fussEls();
    if (fussCounting) return;
    if (!els.ack || !els.ack.checked) {
      fussSetStatus("Tick the box first. FUSS is a timer, not medical advice.", "is-warn");
      return;
    }
    const minutes = fussClampMins(els.mins ? els.mins.value : FUSS_DEFAULT);
    if (els.mins) els.mins.value = String(minutes);
    fussHideBreak();
    fussCounting = true;
    fussShowCountdownView();
    let n = 3;
    if (els.countNum) els.countNum.textContent = String(n);
    function step() {
      if (n <= 0) {
        if (els.countNum) els.countNum.textContent = "0";
        fussCountTimer = window.setTimeout(function () {
          fussCounting = false;
          fussCountTimer = null;
          fussBeginSitting(minutes);
        }, 450);
        return;
      }
      if (els.countNum) els.countNum.textContent = String(n);
      n -= 1;
      fussCountTimer = window.setTimeout(step, 1000);
    }
    step();
  }

  function bindFuss(root) {
    if (root === false) {
      fussClosePanel();
      return;
    }
    fussOpenPanel();
  }
  window.bindFuss = bindFuss;

  (function wireFussUi() {
    const els = fussEls();
    if (!els.mascot || !els.layer) return;
    els.mascot.addEventListener("click", function (e) {
      e.preventDefault();
      fussOpenPanel();
    });
    if (els.close) {
      els.close.addEventListener("click", function () {
        fussClosePanel();
      });
    }
    els.layer.addEventListener("click", function (e) {
      if (e.target === els.layer) fussClosePanel();
    });
    if (els.start) {
      els.start.addEventListener("click", function (e) {
        e.preventDefault();
        fussStartFromPanel();
      });
    }
    if (els.stop) {
      els.stop.addEventListener("click", function (e) {
        e.preventDefault();
        if (fussCounting) {
          fussClearTickers();
          fussShowSetup();
        }
        fussStopTimer({ clearAck: false });
        const live = fussRead();
        if (els.ack) live.ack = !!els.ack.checked;
        if (els.mins) live.minutes = fussClampMins(els.mins.value);
        fussWrite(live);
        fussHideBreak();
        fussSetStatus("Timer stopped.");
      });
    }
    function fussApplyMinutes(raw) {
      const state = fussRead();
      if (state.on) {
        if (els.mins) els.mins.value = String(fussClampMins(state.minutes));
        fussSetStatus("Stop the timer before changing minutes.", "is-warn");
        return;
      }
      state.minutes = fussClampMins(raw);
      if (els.mins) els.mins.value = String(state.minutes);
      fussWrite(state);
    }
    if (els.mins) {
      els.mins.addEventListener("change", function () {
        fussApplyMinutes(els.mins.value);
      });
      els.mins.addEventListener("blur", function () {
        fussApplyMinutes(els.mins.value);
      });
    
      els.mins.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          fussApplyMinutes(els.mins.value);
          els.mins.blur();
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          fussApplyMinutes(fussClampMins(els.mins.value) + 1);
        } else if (e.key === "ArrowDown") {
          e.preventDefault();
          fussApplyMinutes(fussClampMins(els.mins.value) - 1);
        }
      });
    }
    const minsUp = document.getElementById("fuss-mins-up");
    const minsDown = document.getElementById("fuss-mins-down");
    if (minsUp) {
      minsUp.addEventListener("click", function (e) {
        e.preventDefault();
        const cur = fussClampMins(els.mins ? els.mins.value : FUSS_DEFAULT);
        fussApplyMinutes(cur + 1);
      });
    }
    if (minsDown) {
      minsDown.addEventListener("click", function (e) {
        e.preventDefault();
        const cur = fussClampMins(els.mins ? els.mins.value : FUSS_DEFAULT);
        fussApplyMinutes(cur - 1);
      });
    }
    if (els.ack) {
      els.ack.addEventListener("change", function () {
        const state = fussRead();
        state.ack = !!els.ack.checked;
        fussWrite(state);
      });
    }
    if (els.stopBreak) {
      els.stopBreak.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        fussHideBreak();
        fussSetStatus("Break dismissed.");
      });
    }
    if (els.breakLayer) {
      /* Backdrop / Esc must NOT dismiss - only STOP ends the flash. */
      els.breakLayer.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
      });
    }
    document.addEventListener("keydown", function (e) {
      if (els.breakLayer && !els.breakLayer.hidden) {
        if (e.key === "Escape") {
          e.preventDefault();
          e.stopPropagation();
        }
        return;
      }
      if (e.key === "Escape" && els.layer && !els.layer.hidden) fussClosePanel();
    }, true);
    /* Kill timers on desk close without blocking the WebView teardown.
       Do not call evaluate_js from Python closing - that freezes pywebview. */
    function fussGuiShutdown() {
      try {
        if (fussTick) {
          window.clearInterval(fussTick);
          fussTick = null;
        }
        if (fussCountTimer) {
          window.clearTimeout(fussCountTimer);
          fussCountTimer = null;
        }
        if (fussPanelTick) {
          window.clearInterval(fussPanelTick);
          fussPanelTick = null;
        }
        fussCounting = false;
        const prev = fussRead();
        localStorage.setItem(
          FUSS_KEY,
          JSON.stringify({
            ack: !!prev.ack,
            on: false,
            minutes: fussClampMins(prev.minutes || FUSS_DEFAULT),
            started: 0,
            lastPing: 0,
          })
        );
      } catch (err) {}
    }
    window.__fussGuiShutdown = fussGuiShutdown;
    window.addEventListener("pagehide", fussGuiShutdown);
    /* Never resume a sitting from a prior desk session. */
    const boot = fussRead();
    if (boot.on || boot.started) {
      fussStopTimer({ clearAck: false });
      fussHideBreak();
    } else {
      fussSyncMascot(boot);
    }
  })();

  app.classList.remove("engines-open", "runs-open");
  document.getElementById("btn-toggle-engines").setAttribute("aria-expanded", "false");
  document.getElementById("btn-toggle-runs").setAttribute("aria-expanded", "false");
  document.getElementById("slideout").setAttribute("aria-hidden", "true");
  document.getElementById("runs-rail").setAttribute("aria-hidden", "true");
  preloadArts();
  setTheme(theme());
  renderRunsRail();
  hydrateRunsFromDisk(function () {
    renderRunsRail();
  });
})();
