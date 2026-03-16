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
    "Too Low":  ("📈 Too Low — Go Higher", "info"),
    "Win":      ("🎉 Correct!", "success"),
}

# Dark background tones — cycle with each guess
BG_TONES = [
    "#0d0d1a", "#0a0f14", "#0a140f", "#14100a",
    "#140a0a", "#0a1414", "#100a14", "#14140a",
]

GV_TOOLTIP = (
    "Guess Volatility (GV) — bonus points awarded for winning. "
    "Bigger reward the earlier and faster you guess correctly. "
    "At the last attempt GV reaches 0."
)

st.set_page_config(page_title="Glitch Guesser", page_icon="🎮", layout="centered")

# ── Sidebar ───────────────────────────────────────────────────────────────────
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Normal", "Hard"], index=1)
attempt_limit_map = {"Easy": 6, "Normal": 8, "Hard": 5}
attempt_limit = attempt_limit_map[difficulty]
low, high = get_range_for_difficulty(difficulty)

st.sidebar.divider()
st.sidebar.caption("Range"); st.sidebar.markdown(f"**{low} — {high}**")
st.sidebar.caption("Max Attempts"); st.sidebar.markdown(f"**{attempt_limit}**")

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "secret": random.randint(low, high),
    "attempts": 0, "score": 100, "status": "playing",
    "history": [], "game_id": 0, "last_hint": None,
    "start_time": time.time(), "score_delta": None,
    "score_history": [100],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Background cycling ────────────────────────────────────────────────────────
bg = BG_TONES[st.session_state.attempts % len(BG_TONES)]

elapsed = int(time.time() - st.session_state.start_time)
penalty = 100 // attempt_limit
gv_now  = guess_volatility(st.session_state.attempts, attempt_limit, elapsed)

st.markdown(f"""
<style>
  .stApp {{ background-color: {bg}; transition: background-color 0.8s ease; }}
  .stApp, .stApp p, .stApp label, .stApp span, .stApp div {{
      color: #e8e8f0 !important;
  }}
  .block-container {{ padding-top: 1.2rem; max-width: 680px; }}
  h1 {{ font-size: 1.6rem !important; font-weight: 700; color: #ffffff !important; }}
  div[data-testid="stForm"] {{ border: none; padding: 0; }}
  .guess-chip {{
      display: inline-block; background: rgba(255,255,255,0.1);
      border-radius: 20px; padding: 1px 10px; margin: 2px;
      font-size: 0.82rem; color: #ccc;
  }}
  div[data-testid="stFormSubmitButton"] button {{
      background: linear-gradient(135deg, #4c6ef5 0%, #3b5bdb 100%);
      color: #fff; font-size: 0.95rem; font-weight: 600;
      letter-spacing: 0.06em; border: none; border-radius: 10px;
      padding: 0.6rem 1.4rem;
      box-shadow: 0 4px 14px rgba(76,110,245,0.4);
      transition: all 0.2s ease;
  }}
  div[data-testid="stFormSubmitButton"] button:hover {{
      box-shadow: 0 6px 20px rgba(76,110,245,0.6); transform: translateY(-1px);
  }}
  div[data-testid="stFormSubmitButton"] button:active {{
      transform: translateY(0); box-shadow: 0 2px 8px rgba(76,110,245,0.3);
  }}
</style>
""", unsafe_allow_html=True)

# ── Debug → browser DevTools ──────────────────────────────────────────────────
_dbg = json.dumps({
    "secret": st.session_state.secret, "attempts": st.session_state.attempts,
    "score": st.session_state.score, "difficulty": difficulty,
    "status": st.session_state.status, "history": st.session_state.history,
})
components.html(f"<script>console.log('[DEBUG] Game State:', {_dbg});</script>", height=0)

# ── Header + stats ────────────────────────────────────────────────────────────
st.title("🎮 Glitch Guesser")

c1, c2, c3 = st.columns(3)
c1.metric("Score", st.session_state.score,
          delta=st.session_state.score_delta, delta_color="normal")
c2.metric("Attempts", f"{st.session_state.attempts} / {attempt_limit}")
c3.metric("Time", f"{elapsed}s")

# ── Win / Loss banner + New Game ──────────────────────────────────────────────
if st.session_state.status == "won":
    st.success(f"🏆 Won! Secret: **{st.session_state.secret}** · {elapsed}s · Score: **{st.session_state.score}**")
elif st.session_state.status == "lost":
    st.error(f"💀 Out of attempts! Secret was **{st.session_state.secret}**. Score: **{st.session_state.score}**")

col_ng, col_hint = st.columns([2, 1])
with col_ng:
    if st.button("New Game 🔁", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.session_state.game_id += 1
        st.session_state.secret = random.randint(low, high)
        st.session_state.start_time = time.time()
        st.rerun()

# ── Hint feedback ─────────────────────────────────────────────────────────────
if st.session_state.last_hint:
    label, kind = HINT_MESSAGES[st.session_state.last_hint]
    {"success": st.success, "warning": st.warning, "info": st.info}[kind](label)

# ── Two-column: form left, history+chart right ────────────────────────────────
left, right = st.columns([1, 1], gap="medium")

with left:
    if st.session_state.status == "playing":
        with st.form("guess_form"):
            raw_guess = st.text_input(
                f"Guess ({low}–{high})",
                placeholder=f"{low}–{high}",
                key=f"gi_{difficulty}_{st.session_state.game_id}",
            )
            submit = st.form_submit_button(
                "Submit Guess", use_container_width=True, type="primary"
            )

        if submit:
            ok, guess_val, err = parse_guess(raw_guess)
            if not ok:
                st.error(err)
            else:
                if guess_val > high:
                    st.caption(f"⚠️ Clamped to {high}.")
                    guess_val = high
                elif guess_val < low:
                    st.caption(f"⚠️ Clamped to {low}.")
                    guess_val = low

                st.session_state.attempts += 1
                st.session_state.history.append(guess_val)
                outcome = check_guess(guess_val, st.session_state.secret)
                st.session_state.last_hint = outcome
                prev = st.session_state.score

                if outcome == "Win":
                    gv = guess_volatility(
                        st.session_state.attempts, attempt_limit,
                        int(time.time() - st.session_state.start_time)
                    )
                    st.session_state.score = update_score(prev, outcome, penalty) + gv
                    st.session_state.score_delta = gv if gv > 0 else None
                    st.balloons()
                    st.session_state.status = "won"
                else:
                    st.session_state.score = update_score(prev, outcome, penalty)
                    st.session_state.score_delta = -penalty
                    if st.session_state.attempts >= attempt_limit:
                        st.session_state.status = "lost"

                st.session_state.score_history.append(st.session_state.score)
                st.rerun()

    # GV info box (always visible)
    st.markdown("---")
    gv_color = "#2CA02C" if gv_now > 50 else ("#FFA500" if gv_now > 20 else "#D62728")
    st.markdown(
        f'<div title="{GV_TOOLTIP}" style="background:rgba(255,255,255,0.07);'
        f'border-radius:8px;padding:8px 12px;cursor:help;">'
        f'<span style="font-size:0.75rem;color:#aaa;">Guess Volatility (?)</span><br>'
        f'<span style="font-size:1.4rem;font-weight:700;color:{gv_color};">+{gv_now}</span>'
        f'<span style="font-size:0.8rem;color:#aaa;"> pts if you win now</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

with right:
    # Guess history chips
    if st.session_state.history:
        st.caption("History")
        chips = " ".join(
            f'<span class="guess-chip">{g}</span>'
            for g in st.session_state.history
        )
        st.markdown(chips, unsafe_allow_html=True)

    # Score chart with projections
    if len(st.session_state.score_history) > 1:
        hist = st.session_state.score_history
        n = len(hist) - 1
        current_score = hist[-1]

        actual_df = pd.DataFrame({
            "attempt": list(range(len(hist))),
            "score":   hist,
            "series":  "Score",
        })

        if st.session_state.status == "playing":
            win_score  = current_score + gv_now
            lose_score = max(0, current_score - penalty)
            proj_df = pd.DataFrame({
                "attempt": [n, n + 1, n, n + 1],
                "score":   [current_score, win_score, current_score, lose_score],
                "series":  ["Win ▲", "Win ▲", "Lose ▼", "Lose ▼"],
            })
            chart_df = pd.concat([actual_df, proj_df], ignore_index=True)
        else:
            chart_df = actual_df

        color_scale = alt.Scale(
            domain=["Score", "Win ▲", "Lose ▼"],
            range=["#748FFC", "#2CA02C", "#D62728"],
        )

        base = (
            alt.Chart(chart_df)
            .mark_line(point=True, strokeWidth=2)
            .encode(
                x=alt.X("attempt:Q", title=None, axis=alt.Axis(tickMinStep=1, labelColor="#aaa", gridColor="#333")),
                y=alt.Y("score:Q",   title=None, scale=alt.Scale(domain=[0, max(130, current_score + gv_now + 20)]),
                        axis=alt.Axis(labelColor="#aaa", gridColor="#333")),
                color=alt.Color("series:N", scale=color_scale,
                                legend=alt.Legend(title=None, labelColor="#ccc")),
                strokeDash=alt.condition(
                    alt.datum.series == "Score",
                    alt.value([1, 0]), alt.value([5, 3])
                ),
                tooltip=[
                    alt.Tooltip("attempt:Q", title="Attempt"),
                    alt.Tooltip("score:Q",   title="Score"),
                    alt.Tooltip("series:N",  title="Series"),
                ],
            )
            .properties(height=160, background="transparent")
            .configure_view(strokeOpacity=0)
        )

        if st.session_state.status == "playing" and gv_now > 0:
            gv_label = (
                alt.Chart(pd.DataFrame({
                    "attempt": [n + 1],
                    "score":   [current_score + gv_now],
                    "text":    [f"+{gv_now} GV"],
                    "tooltip_text": [GV_TOOLTIP],
                }))
                .mark_text(dy=-12, color="#2CA02C", fontWeight="bold", fontSize=11)
                .encode(
                    x="attempt:Q", y="score:Q", text="text:N",
                    tooltip=alt.Tooltip("tooltip_text:N", title="Guess Volatility"),
                )
            )
            st.altair_chart(base + gv_label, use_container_width=True)
        else:
            st.altair_chart(base, use_container_width=True)

st.caption("Built by an AI that claims this code is production-ready.")
