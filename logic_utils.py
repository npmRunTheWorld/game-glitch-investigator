def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome string.

    Returns: "Win", "Too High", or "Too Low"
    """
    if guess == secret:
        return "Win"

    if guess > secret:
        return "Too High"

    return "Too Low"


def guess_volatility(attempts_used: int, attempt_limit: int, elapsed: float) -> int:
    """
    Guess Volatility (GV) bonus. Rewards early, fast correct guesses.

    - Attempts 1–4: gentle linear decay (1.0 → 0.76), stays generous.
    - Attempt 5+: exponential crush — GV collapses to near zero.
    - Time component (0–100): decays over 2 minutes (120s).
    - At the final attempt the bonus is always 0.

    Examples (limit=8):
      Attempt 1,  5s → ~495   Attempt 2, 15s → ~455
      Attempt 3, 30s → ~411   Attempt 4, 45s → ~366
      Attempt 5, 60s → ~110   Attempt 6, 90s →  ~40   Attempt 8 → 0
    """
    if attempts_used >= attempt_limit:
        return 0
    # Smooth power curve: high reward early, gradual decay, ~40 pts at last-1 attempt
    remaining = 1.0 - (attempts_used - 1) / max(attempt_limit - 1, 1)
    attempt_factor = remaining ** 1.2
    # Time bonus decays over 2 minutes
    time_bonus = max(0, int(100 * max(0.0, 1.0 - elapsed / 120.0)))
    return int(400 * attempt_factor) + time_bonus


def update_score(current_score: int, outcome: str, penalty: int):
    """
    Update score based on outcome.

    Starting score is 100. Each wrong guess deducts `penalty` points
    (caller computes penalty = 100 // attempt_limit). Score floor is 0.
    Win preserves the current score; time bonus is applied separately in app.py.
    """
    if outcome == "Win":
        return current_score

    return max(0, current_score - penalty)
