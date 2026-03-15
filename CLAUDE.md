# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
python -m streamlit run app.py

# Run tests
pytest

# Run a single test
pytest tests/test_game_logic.py::test_winning_guess
```

## Project Overview

This is a **intentionally buggy** Streamlit number-guessing game used as an educational exercise. The goal is for students to find and fix the bugs, then refactor logic into `logic_utils.py`.

### Known Bugs (by design)

1. **Wrong hints** — `check_guess` in `app.py` returns "Go HIGHER!" when the guess is too high, and "Go LOWER!" when too low (inverted).
2. **Score logic bug** — `update_score` gives +5 points on even-numbered "Too High" guesses instead of penalizing.
3. **Hard difficulty range bug** — `get_range_for_difficulty("Hard")` returns `(1, 50)` but uses the same 1–100 range in the "Make a guess" info text (hardcoded to 100 instead of `high`).
4. **New Game resets attempts to 0** — but initial state sets attempts to 1, causing inconsistency.

### Architecture

- **`app.py`** — Streamlit UI and all game logic (currently duplicated with `logic_utils.py`). Uses `st.session_state` for `secret`, `attempts`, `score`, `status`, and `history`.
- **`logic_utils.py`** — Stub file where the four pure logic functions should be moved: `get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`. All currently raise `NotImplementedError`.
- **`tests/test_game_logic.py`** — Tests import from `logic_utils`. Tests expect `check_guess` to return just the outcome string (e.g., `"Win"`), not a tuple.

### Refactor Target

The assignment requires moving logic from `app.py` into `logic_utils.py` and making `pytest` pass. Note that tests call `check_guess(guess, secret)` and assert on the outcome string only — the current `app.py` implementation returns a tuple `(outcome, message)`, so the API must be reconciled when refactoring.