# Evalathan UI/UX v2 (v0.3.2 desk)

Replaces the old Tk Hydra window. **Evaluate** calls the same `prepare()` + Hydra `conduct()` path (sixteen real evalers). Dehydrus / Benchrex / Biasrex slots stay WIP.

SEISMO-style overlay rails. **Splash = both sides closed.** Corner words open the sliders.

- Top-left **evals** (lime mono) → left engines rail (HYDRA / DEHYDRUS / BENCHREX / BIASREX wordmark headers)
- Top-right **history** (lime mono) → right **latest run** + **saved runs** rail

Splash brand stack (matches PDF ref): red dragon mark → **EVALATHAN** title → rule → three mono blurbs → pill upload. No blue Hydra art on the splash.

## Open in a browser

```bat
python ui\v2\serve.py
```

http://127.0.0.1:8787/

Hard-refresh (Ctrl+Shift+R) after pulls.

## Evaluate → memo

**Evaluate** opens a processing popup (fading dots + per-evaler blurbs), then the same window becomes a short developer memo. **Full detailed memo** lists each evaler on its own line with the same glossary hyperlinks as the left rail. **Download** (orange) opens a print/PDF pack; **Save** (green) writes **latest run** and appends **saved runs** in localStorage (compares the same target against the prior saved twin).

## Desktop icon

```powershell
powershell -ExecutionPolicy Bypass -File ui\v2\install_desktop_shortcut.ps1
```

Creates `Evalathan (Hydra GUI).lnk` on the Desktop using `assets/favicon.ico`.

## Themes

White / Grey / Black (in the left rail once opened). Engine wordmarks use white glyphs on dark themes and black glyphs on white.

## Slotbox

Pill: *Upload your GitHub link or folder…* Buttons: **Browse**, **Evaluate**.
