import json
import random
import streamlit as st
import streamlit.components.v1 as components
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score

HINT_MESSAGES = {
    "Too High": ("📉 Too High — Go Lower", "inverse"),
    "Too Low": ("📈 Too Low — Go Higher", "inverse"),
    "Win": ("🎉 Correct!", "inverse"),
}

st.set_page_config(
    page_title="Glitch Guesser",
    page_icon="🎮",
    layout="centered",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 640px; }
    h1 { font-size: 1.8rem !important; font-weight: 700; }
    .stMetric { background: #f8f9fa; border-radius: 10px; padding: 0.5rem 1rem; }
    div[data-testid="stForm"] { border: none; padding: 0; }
    .guess-chip {
        display: inline-block;
        background: #f0f0f0;
        border-radius: 20px;
        padding: 2px 12px;
        margin: 2px;
        font-size: 0.85rem;
        color: #444;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("⚙️ Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {"Easy": 6, "Normal": 8, "Hard": 5}
attempt_limit = attempt_limit_map[difficulty]
low, high = get_range_for_difficulty(difficulty)

st.sidebar.divider()
st.sidebar.caption("Range")
st.sidebar.markdown(f"**{low} — {high}**")
st.sidebar.caption("Max Attempts")
st.sidebar.markdown(f"**{attempt_limit}**")

# ── Session state ─────────────────────────────────────────────────────────────
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "status" not in st.session_state:
    st.session_state.status = "playing"
if "history" not in st.session_state:
    st.session_state.history = []
if "game_id" not in st.session_state:
    st.session_state.game_id = 0
if "last_hint" not in st.session_state:
    st.session_state.last_hint = None

# ── Debug → browser DevTools console ─────────────────────────────────────────
_debug_state = {
    "secret": st.session_state.secret,
    "attempts": st.session_state.attempts,
    "score": st.session_state.score,
    "difficulty": difficulty,
    "status": st.session_state.status,
    "history": st.session_state.history,
}
components.html(
    f"<script>console.log('[DEBUG] Game State:', {json.dumps(_debug_state)});</script>",
    height=0,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎮 Glitch Guesser")
st.caption("Guess the secret number. Something might still be off.")
st.divider()

# ── Stats row ─────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Score", st.session_state.score)
col2.metric("Attempts", f"{st.session_state.attempts} / {attempt_limit}")
col3.metric("Range", f"{low} – {high}")

st.divider()

# ── Game over / won states ────────────────────────────────────────────────────
if st.session_state.status == "won":
    st.success(f"🏆 You won! The secret was **{st.session_state.secret}**. Final score: **{st.session_state.score}**")
elif st.session_state.status == "lost":
    st.error(f"💀 Out of attempts! The secret was **{st.session_state.secret}**. Score: **{st.session_state.score}**")

# ── New Game button ───────────────────────────────────────────────────────────
if st.button("New Game 🔁", use_container_width=True):
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.game_id += 1
    st.session_state.history = []
    st.session_state.last_hint = None
    st.session_state.secret = random.randint(low, high)
    st.rerun()

if st.session_state.status != "playing":
    st.stop()

st.markdown("#### Your Guess")

# ── Number input with live range clamping warning ────────────────────────────
guess_val = st.number_input(
    f"Enter a number ({low} – {high})",
    min_value=low,
    max_value=high,
    step=1,
    key=f"guess_num_{difficulty}_{st.session_state.game_id}",
    label_visibility="visible",
)

if guess_val == high:
    st.caption(f"⚠️ Maximum value is {high} — clamped.")
elif guess_val == low:
    st.caption(f"⚠️ Minimum value is {low} — clamped.")

show_hint = st.checkbox("Show hint", value=True)

# ── Submit ────────────────────────────────────────────────────────────────────
if st.button("Submit Guess 🚀", use_container_width=True, type="primary"):
    st.session_state.attempts += 1
    st.session_state.history.append(guess_val)

    outcome = check_guess(guess_val, st.session_state.secret)
    st.session_state.last_hint = outcome

    st.session_state.score = update_score(
        current_score=st.session_state.score,
        outcome=outcome,
        attempt_number=st.session_state.attempts,
    )

    if outcome == "Win":
        st.balloons()
        st.session_state.status = "won"
    elif st.session_state.attempts >= attempt_limit:
        st.session_state.status = "lost"

    st.rerun()

# ── Hint feedback ─────────────────────────────────────────────────────────────
if show_hint and st.session_state.last_hint:
    label, _ = HINT_MESSAGES[st.session_state.last_hint]
    if st.session_state.last_hint == "Win":
        st.success(label)
    elif st.session_state.last_hint == "Too High":
        st.warning(label)
    else:
        st.info(label)

# ── Guess history ─────────────────────────────────────────────────────────────
if st.session_state.history:
    st.divider()
    st.caption("Guess History")
    chips = " ".join(
        f'<span class="guess-chip">{g}</span>'
        for g in st.session_state.history
    )
    st.markdown(chips, unsafe_allow_html=True)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
