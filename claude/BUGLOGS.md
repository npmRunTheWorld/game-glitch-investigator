# Vulnerability Report: Game Glitch Investigator

All issues found across `app.py`, `logic_utils.py`, `tests/test_game_logic.py`, and `requirements.txt`.

---

## Logic Bugs

### BUG-01: Inverted Higher/Lower Hints
**File:** `app.py:37-40`
**Severity:** Critical
When the guess is too high the message says "Go HIGHER!", and when the guess is too low it says "Go LOWER!". The conditions are swapped — the game actively misleads the player.

```python
# Current (wrong)
if guess > secret:
    return "Too High", "📈 Go HIGHER!"
else:
    return "Too Low", "📉 Go LOWER!"

# Should be
if guess > secret:
    return "Too High", "📉 Go LOWER!"
else:
    return "Too Low", "📈 Go HIGHER!"
```

---

### BUG-02: Secret Number Cast to String on Even Attempts
**File:** `app.py:158-163`
**Severity:** Critical
Every even-numbered attempt converts the secret to a `str` before passing it to `check_guess`. This causes string vs. int comparison (e.g., `"9" > 50` is `True` in Python because `"9" > "5"` lexicographically). The player can never reliably win on even attempts.

```python
# Current (wrong)
if st.session_state.attempts % 2 == 0:
    secret = str(st.session_state.secret)   # breaks comparison
else:
    secret = st.session_state.secret
```

The `secret` variable should always be `st.session_state.secret` with no type conversion.

---

### BUG-03: Hard Mode Is Easier Than Normal Mode
**File:** `app.py:9-10`
**Severity:** Medium
Hard difficulty uses range `1–50`, which is a smaller (easier) range than Normal's `1–100`. Hard should use a larger range to be harder.

```python
# Current (wrong)
if difficulty == "Hard":
    return 1, 50

# Intended behavior: Hard should have a wider range, e.g. 1–200
```

---

### BUG-04: Score Can Increase on Wrong Guesses
**File:** `app.py:57-60`
**Severity:** Medium
When the outcome is "Too High" and the attempt number is even, the player receives +5 points. Incorrect guesses should never award points — this creates an exploitable scoring mechanic.

```python
if outcome == "Too High":
    if attempt_number % 2 == 0:
        return current_score + 5   # rewards a wrong answer
    return current_score - 5
```

---

### BUG-05: Attempts Counter Starts at 1, Not 0
**File:** `app.py:96`
**Severity:** Low
`st.session_state.attempts` is initialized to `1`, then incremented at the top of the submit handler before any logic runs (`app.py:148`). The first guess is counted as attempt 2, making the "attempts left" display off by one.

```python
# Initialized to 1 (wrong)
if "attempts" not in st.session_state:
    st.session_state.attempts = 1

# Then immediately incremented on submit
st.session_state.attempts += 1
```

---

### BUG-06: New Game Resets attempts to 0 but Init Sets It to 1
**File:** `app.py:135`
**Severity:** Low
The "New Game" button sets `st.session_state.attempts = 0`, but initialization sets it to `1`. These two paths are inconsistent — the first attempt of a fresh game and the first attempt after "New Game" behave differently.

---

### BUG-07: New Game Does Not Reset Status or Score
**File:** `app.py:134-138`
**Severity:** Medium
The "New Game" button resets `attempts` and `secret`, but does not reset `st.session_state.status` or `st.session_state.score`. If a player wins or loses, clicking "New Game" still leaves `status` as `"won"` or `"lost"`, causing `st.stop()` to fire immediately and blocking the new game.

---

## UI / UX Issues

### UI-01: Info Banner Always Shows Range 1–100 Regardless of Difficulty
**File:** `app.py:109-112`
**Severity:** Medium
The info banner is hardcoded to say "Guess a number between 1 and 100" even when Easy (1–20) or Hard (1–50) is selected.

```python
st.info(
    f"Guess a number between 1 and 100. "   # hardcoded, ignores difficulty
    ...
)
```

Should use the `low` and `high` variables already computed on `app.py:87`.

---

### UI-02: "Attempts Left" Can Show Negative Values
**File:** `app.py:111`
**Severity:** Low
Because `attempts` starts at 1 and is incremented before the limit check, the displayed count `attempt_limit - st.session_state.attempts` can reach -1 before the game-over state is applied.

---

### UI-03: Invalid Guess Still Increments Attempt Counter
**File:** `app.py:148, 152-153`
**Severity:** Medium
`st.session_state.attempts += 1` runs unconditionally before input validation. Submitting blank input or a non-number wastes an attempt. The increment should only happen on a valid, parsed guess.

---

### UI-04: Hint Checkbox Hides Feedback but Still Consumes Attempt
**File:** `app.py:165-166`
**Severity:** Low
When "Show hint" is unchecked, the guess is still processed and the attempt consumed, but the player gets no feedback at all — not even confirmation that their guess was recorded. A neutral acknowledgment ("Guess submitted.") should appear regardless of the hint setting.

---

### UI-05: Debug Info Is Always Visible to Players
**File:** `app.py:114-119`
**Severity:** Low
The "Developer Debug Info" expander that reveals the secret number, score, and history is shipped in the main UI. Any player can open it to trivially win the game. This should be gated behind an environment variable or removed entirely in production.

---

## Architecture / Code Quality Issues

### ARCH-01: logic_utils.py Is Unimplemented
**File:** `logic_utils.py:1-27`
**Severity:** Critical
All four functions in `logic_utils.py` raise `NotImplementedError`. The game logic has not been refactored out of `app.py` as required. The test suite imports from `logic_utils` and will fail entirely until this is done.

---

### ARCH-02: Test Suite Expects a Different Return Type Than app.py Provides
**File:** `tests/test_game_logic.py:6, 11, 16`
**Severity:** Critical
The tests assert that `check_guess` returns a plain string (`"Win"`, `"Too High"`, `"Too Low"`), but the implementation in `app.py` returns a tuple `(outcome, message)`. The refactored version in `logic_utils.py` must return only the outcome string to match the test contract.

---

### ARCH-03: Duplicate Logic Between app.py and logic_utils.py
**File:** `app.py`, `logic_utils.py`
**Severity:** Medium
All four functions (`get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`) are defined in `app.py`. Once implemented in `logic_utils.py`, `app.py` must import from there and remove its own copies — otherwise changes in one place won't be reflected in the other.

---

### ARCH-04: check_guess Has an Unreachable String-Fallback Code Path
**File:** `app.py:42-47`
**Severity:** Low
The `except TypeError` block in `check_guess` re-implements comparison logic for string inputs. This path only exists because of BUG-02 (the deliberate string cast). Once BUG-02 is fixed, this entire block is dead code and should be removed.

---

## Dependency Issues

### DEP-01: altair Pinned Below Major Version Without Upper Bound Clarity
**File:** `requirements.txt:2`
**Severity:** Low
`altair<5` pins the package below a major version without specifying a lower bound. If Altair 3.x is installed it may be incompatible with the Streamlit version in use. A more precise pin (e.g., `altair>=4.0,<5`) is safer.

---

## Summary Table

| ID      | Category       | Severity | Description                                          |
|---------|----------------|----------|------------------------------------------------------|
| BUG-01  | Logic          | Critical | Higher/Lower hints are inverted                      |
| BUG-02  | Logic          | Critical | Secret cast to string on even attempts               |
| BUG-03  | Logic          | Medium   | Hard mode range is smaller than Normal               |
| BUG-04  | Logic          | Medium   | Wrong guesses can award points                       |
| BUG-05  | Logic          | Low      | Attempt counter starts at 1 instead of 0             |
| BUG-06  | Logic          | Low      | New Game and init use inconsistent starting attempts |
| BUG-07  | Logic          | Medium   | New Game does not reset status or score              |
| UI-01   | UI/UX          | Medium   | Info banner hardcodes range 1–100                    |
| UI-02   | UI/UX          | Low      | Attempts left can display negative                   |
| UI-03   | UI/UX          | Medium   | Invalid guesses consume an attempt                   |
| UI-04   | UI/UX          | Low      | No feedback when hint is hidden                      |
| UI-05   | UI/UX          | Low      | Debug panel exposes secret number to players         |
| ARCH-01 | Architecture   | Critical | logic_utils.py functions all raise NotImplementedError |
| ARCH-02 | Architecture   | Critical | Tests expect string return; app.py returns tuple     |
| ARCH-03 | Architecture   | Medium   | Logic duplicated between app.py and logic_utils.py   |
| ARCH-04 | Architecture   | Low      | Dead code: string fallback in check_guess            |
| DEP-01  | Dependencies   | Low      | altair<5 missing lower bound                         |
