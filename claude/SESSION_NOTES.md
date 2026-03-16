# Session Notes — 2026-03-16

## What We Accomplished

All critical and medium bugs from BUGLOGS.md have been fixed across 9 dedicated branches. Each branch follows the `action/tag-number` naming convention and has been pushed to origin.

### Branches Completed

| Branch | Fix |
|--------|-----|
| `refactor/arch-01` | Implemented all 4 `logic_utils.py` stubs (were raising `NotImplementedError`). `check_guess` returns plain string not tuple. Added `conftest.py` for pytest module resolution. |
| `fix/bug-01` | Fixed inverted hints in `app.py` — `Go HIGHER!` / `Go LOWER!` were swapped. |
| `fix/bug-03` | Hard difficulty range changed from `(1, 50)` to `(1, 200)` in both `app.py` and `logic_utils.py`. |
| `fix/bug-04` | Removed +5 score reward on even-attempt "Too High" guesses. Wrong guesses always deduct 5. |
| `refactor/arch-03` | `app.py` now imports from `logic_utils`. Local duplicate function definitions removed. `HINT_MESSAGES` dict added. Tuple unpack on `check_guess` removed. |
| `fix/bug-05.bug-06` | Attempts counter init changed from `1` to `0`. New Game and init are now consistent. |
| `fix/bug-07` | New Game now resets `score`, `status`, `history`, and uses `low/high` from difficulty instead of hardcoded `randint(1, 100)`. |
| `fix/ui-01` | Info banner now shows dynamic range (`low` to `high`) instead of hardcoded `1 to 100`. |
| `fix/ui-03` | Attempts counter only increments on valid guesses. Invalid input shows error without wasting an attempt. |

### Tests
- All 3 pytest tests passing across all branches: `test_winning_guess`, `test_guess_too_high`, `test_guess_too_low`

---

## In Progress / Not Done

- **PRs** — All 9 branches are pushed but no PRs have been opened to `main` yet (user declined at end of session)
- **BUG-02** — The even/odd `secret` cast bug is already neutralized in current code (both branches assign `st.session_state.secret` directly), no separate branch needed
- **UI-02** — Attempts left showing negative values — partially resolved by fixing BUG-05/06 but not explicitly addressed
- **UI-04** — No feedback when hint checkbox is unchecked — not fixed
- **UI-05** — Debug panel exposes secret number — not fixed
- **ARCH-04** — Dead `except TypeError` block — removed as part of `refactor/arch-03`
- **DEP-01** — `altair<5` missing lower bound in `requirements.txt` — not fixed

---

## Next Steps

1. Open PRs for all 9 branches → `main` when ready
2. Address remaining low-severity issues: UI-02, UI-04, UI-05, DEP-01
3. Complete `reflection.md` answers (sections 2, 3, 4 are still mostly blank)
4. Run a final end-to-end manual smoke test of the Streamlit app across all 3 difficulty modes
