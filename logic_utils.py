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
    Guess Volatility (GV) bonus. Rewards fast, early correct guesses.
    Max bonus ~200. Approaches 0 at the last attempt or after 120 seconds.
    """
    attempt_factor = max(0.0, 1.0 - attempts_used / attempt_limit)
    time_factor = max(0.0, 1.0 - elapsed / 120.0)
    return int(200 * attempt_factor * time_factor)


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
