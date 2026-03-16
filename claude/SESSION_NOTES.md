# Session Notes — 2026-03-16 (Session 3)

## What We Accomplished

All UI modernization work completed and pushed to `feature/ui-modernization`.

### Changes This Session

| Area | Details |
|------|---------|
| **Layout** | 15%/85% top section: Score/Attempts/Time (left) + GV box + chart (right). Bottom: Guess form (left) + History (right) |
| **Live timer** | JS `setInterval` ticks every second via `window.parent.document` — Time counter, GV box, and GV label in Vega SVG all update live |
| **GV formula** | Smooth power curve `^1.2`, base 400, 100pt time bonus decaying over 2min. Generous through guess 4, gradual decay, ~40–70 pts at guess 7, 0 at last attempt |
| **GV display fix** | Display used `attempts` (0-indexed), win used post-incremented `attempts` — fixed by passing `attempts + 1` to display so both are consistent |
| **History chips** | Red = too low, Green = too high, Gold = win. Color legend always shown above chips |
| **Show Hints checkbox** | On by default; toggling hides hint banner |
| **New Game button** | Moved below Submit Guess in the play area |
| **Range validation** | Out-of-range input rejected with error, no attempt consumed (replaces silent clamping) |
| **Score = 0 on loss** | Explicitly zeroed on last attempt, absorbing integer-division remainder |
| **Chart from guess 0** | Changed `len(hist) > 1` to `>= 1` so chart shows at game start |
| **Submit button style** | Teal `#00b09b` → coral `#ff6348` gradient |

### Branch
`feature/ui-modernization` — pushed, PR opened to `main`

---

## In Progress / Not Done

- **PRs from Session 1** — 9 older fix/refactor branches still have no PRs open to `main`
- **UI-04** — No feedback when hint checkbox is unchecked (now partially addressed with Show Hints toggle)
- **DEP-01** — `altair<5` missing lower bound in `requirements.txt`
- **reflection.md** — Sections 2, 3, 4 still mostly blank

---

---

## Session 3 — 2026-03-16

### What We Accomplished

Added two live annotation labels to the Altair score projection chart (`app.py`, +49 lines):

| Change | Details |
|--------|---------|
| **GV label on Win ▲ tip** | `+{gv_now} GV` text mark in matching green/orange/red color |
| **Live GV chart update via JS** | `tick()` now queries `.vega-embed svg text` nodes, finds the "GV" label, and rewrites content + fill color every second |
| **Loss score label on Lose ▼ tip** | Red `{lose_score} pts` text mark below the lose projection endpoint |

### Files Changed
| File | +Lines | -Lines |
|------|--------|--------|
| `app.py` | 49 | 0 |

---

## Next Steps

1. Commit this session's chart annotation changes
2. Open PR `feature/ui-modernization` → `main`
3. Open PRs for the 9 Session 1 branches → `main`
4. Fill out `reflection.md` sections 2–4
5. Fix DEP-01 in `requirements.txt`
6. Final manual smoke test across all 3 difficulty modes
