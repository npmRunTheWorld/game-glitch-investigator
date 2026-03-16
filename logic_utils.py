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

    - Attempt component (0–150): full at guess 1, linear drop to 0 at last guess.
    - Time component (0–50): gentle decay over 5 minutes (300s).
    - At the final attempt the bonus is always 0.

    Examples (limit=8):
      Attempt 1,  5s → ~199   Attempt 2, 10s → ~176
      Attempt 4, 30s → ~109   Attempt 7, 60s →  ~61   Attempt 8 →    0
    """
    if attempts_used >= attempt_limit:
        return 0
    # Linear drop: first guess = 1.0, last-1 guess approaches 0
    attempt_factor = 1.0 - (attempts_used - 1) / max(attempt_limit - 1, 1)
    # Gentle time decay — meaningful only after 5 minutes
    time_bonus = max(0, int(50 * max(0.0, 1.0 - elapsed / 300.0)))
    return int(150 * attempt_factor) + time_bonus


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
