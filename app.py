import json
import random
import time
import pandas as pd
import altair as alt
import streamlit as st
import streamlit.components.v1 as components
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
    guess_volatility,
)

HINT_MESSAGES = {
    "Too High": ("📉 Too High — Go Lower", "warning"),
    "Too Low": ("📈 Too Low — Go Higher", "info"),
    "Win": ("🎉 Correct!", "success"),
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
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.5rem;
        box-shadow: 0 4px 15px rgba(26, 26, 46, 0.3);
        transition: all 0.2s ease;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        box-shadow: 0 6px 20px rgba(26, 26, 46, 0.5);
        transform: translateY(-1px);
    }
    div[data-testid="stFormSubmitButton"] button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(26, 26, 46, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
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
    st.session_state.score = 100
if "status" not in st.session_state:
    st.session_state.status = "playing"
if "history" not in st.session_state:
    st.session_state.history = []
if "game_id" not in st.session_state:
    st.session_state.game_id = 0
if "last_hint" not in st.session_state:
    st.session_state.last_hint = None
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "score_delta" not in st.session_state:
    st.session_state.score_delta = None
if "score_history" not in st.session_state:
    st.session_state.score_history = [100]

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
elapsed = int(time.time() - st.session_state.start_time)
penalty = 100 // attempt_limit
gv_now = guess_volatility(st.session_state.attempts, attempt_limit, elapsed)

col1, col2, col3 = st.columns(3)
col1.metric(
    "Score",
    st.session_state.score,
    delta=st.session_state.score_delta,
    delta_color="normal",
)
col2.metric("Attempts", f"{st.session_state.attempts} / {attempt_limit}")
col3.metric("Time", f"{elapsed}s")

st.divider()

# ── Win / Loss banner ─────────────────────────────────────────────────────────
if st.session_state.status == "won":
    st.success(
        f"🏆 You won! Secret was **{st.session_state.secret}** · "
        f"Time: **{elapsed}s** · Final score: **{st.session_state.score}**"
    )
elif st.session_state.status == "lost":
    st.error(
        f"💀 Out of attempts! Secret was **{st.session_state.secret}**. "
        f"Score: **{st.session_state.score}**"
    )

# ── New Game button ───────────────────────────────────────────────────────────
if st.button("New Game 🔁", use_container_width=True):
    st.session_state.attempts = 0
    st.session_state.score = 100
    st.session_state.status = "playing"
    st.session_state.game_id += 1
    st.session_state.history = []
    st.session_state.last_hint = None
    st.session_state.score_delta = None
    st.session_state.score_history = [100]
    st.session_state.start_time = time.time()
    st.session_state.secret = random.randint(low, high)
    st.rerun()

# ── Hint feedback ─────────────────────────────────────────────────────────────
if st.session_state.last_hint:
    label, kind = HINT_MESSAGES[st.session_state.last_hint]
    if kind == "success":
        st.success(label)
    elif kind == "warning":
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

# ── Score chart with projections ──────────────────────────────────────────────
if len(st.session_state.score_history) > 1 or st.session_state.status != "playing":
    st.divider()
    st.caption("Score · Guess Volatility Projections")

    hist = st.session_state.score_history
    n = len(hist) - 1  # index of current score point
    current_score = hist[-1]

    win_proj = current_score + gv_now
    lose_proj = max(0, current_score - penalty)

    actual_df = pd.DataFrame({
        "attempt": list(range(len(hist))),
        "score": hist,
        "series": "Score",
    })

    if st.session_state.status == "playing":
        proj_df = pd.DataFrame({
            "attempt": [n, n + 1, n, n + 1],
            "score": [current_score, win_proj, current_score, lose_proj],
            "series": ["Win Projection", "Win Projection", "Lose Projection", "Lose Projection"],
        })
        chart_df = pd.concat([actual_df, proj_df], ignore_index=True)
    else:
        chart_df = actual_df

    color_scale = alt.Scale(
        domain=["Score", "Win Projection", "Lose Projection"],
        range=["#4C6EF5", "#2CA02C", "#D62728"],
    )
    dash_scale = alt.condition(
        alt.datum.series == "Score",
        alt.value([1, 0]),
        alt.value([5, 3]),
    )

    chart = (
        alt.Chart(chart_df)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("attempt:Q", title="Attempt", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("score:Q", title="Score", scale=alt.Scale(domain=[0, 130])),
            color=alt.Color("series:N", scale=color_scale, legend=alt.Legend(title=None)),
            strokeDash=dash_scale,
            tooltip=["attempt:Q", "score:Q", "series:N"],
        )
        .properties(height=200)
    )

    if st.session_state.status == "playing":
        gv_label = alt.Chart(pd.DataFrame({
            "attempt": [n + 1],
            "score": [win_proj],
            "text": [f"+{gv_now} GV"],
        })).mark_text(dy=-12, color="#2CA02C", fontWeight="bold").encode(
            x="attempt:Q",
            y="score:Q",
            text="text:N",
        )
        st.altair_chart(chart + gv_label, use_container_width=True)
    else:
        st.altair_chart(chart, use_container_width=True)

# ── Stop here if game is over ─────────────────────────────────────────────────
if st.session_state.status != "playing":
    st.divider()
    st.caption("Built by an AI that claims this code is production-ready.")
    st.stop()

# ── Guess form ────────────────────────────────────────────────────────────────
st.markdown("#### Your Guess")
show_hint = st.checkbox("Show hint", value=True)

with st.form("guess_form"):
    raw_guess = st.text_input(
        f"Enter a number ({low} – {high})",
        placeholder=f"{low} – {high}",
        key=f"guess_input_{difficulty}_{st.session_state.game_id}",
    )
    submit = st.form_submit_button("Submit Guess", use_container_width=True, type="primary")

if submit:
    ok, guess_val, err = parse_guess(raw_guess)

    if not ok:
        st.error(err)
    else:
        if guess_val > high:
            st.caption(f"⚠️ {guess_val} is above the maximum — clamped to {high}.")
            guess_val = high
        elif guess_val < low:
            st.caption(f"⚠️ {guess_val} is below the minimum — clamped to {low}.")
            guess_val = low

        st.session_state.attempts += 1
        st.session_state.history.append(guess_val)

        outcome = check_guess(guess_val, st.session_state.secret)
        st.session_state.last_hint = outcome

        prev_score = st.session_state.score

        if outcome == "Win":
            elapsed_on_win = int(time.time() - st.session_state.start_time)
            gv_bonus = guess_volatility(
                st.session_state.attempts, attempt_limit, elapsed_on_win
            )
            st.session_state.score = update_score(prev_score, outcome, penalty) + gv_bonus
            st.session_state.score_delta = gv_bonus if gv_bonus > 0 else None
            st.balloons()
            st.session_state.status = "won"
        else:
            st.session_state.score = update_score(prev_score, outcome, penalty)
            st.session_state.score_delta = -penalty
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"

        st.session_state.score_history.append(st.session_state.score)
        st.rerun()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
