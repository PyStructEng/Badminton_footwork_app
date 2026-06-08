import streamlit as st
import random
import time

st.set_page_config(
    page_title="Badminton Footwork Lab",
    page_icon="🏸",
    layout="centered"
)

# -----------------------------
# Basic data
# -----------------------------
CORNERS = [
    "Front Left",
    "Front Right",
    "Side Left",
    "Side Right",
    "Rear Left",
    "Rear Right",
]

CORNER_EMOJI = {
    "Front Left": "↖️",
    "Front Right": "↗️",
    "Side Left": "⬅️",
    "Side Right": "➡️",
    "Rear Left": "↙️",
    "Rear Right": "↘️",
}

# -----------------------------
# Session state
# -----------------------------
if "running" not in st.session_state:
    st.session_state.running = False

if "current_corner" not in st.session_state:
    st.session_state.current_corner = "Ready"

if "rep_count" not in st.session_state:
    st.session_state.rep_count = 0

if "history" not in st.session_state:
    st.session_state.history = []

if "start_time" not in st.session_state:
    st.session_state.start_time = None


# -----------------------------
# UI
# -----------------------------
st.title("🏸 Badminton Footwork Lab")
st.caption("Simple six-corner footwork caller")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    interval = st.slider(
        "Seconds between calls",
        min_value=1.0,
        max_value=8.0,
        value=3.0,
        step=0.5
    )

with col2:
    total_time = st.slider(
        "Session length / minutes",
        min_value=1,
        max_value=20,
        value=3,
        step=1
    )

mode = st.radio(
    "Training mode",
    ["Random six corners", "Front court only", "Rear court only", "Side only"],
    horizontal=False
)

if mode == "Front court only":
    active_corners = ["Front Left", "Front Right"]
elif mode == "Rear court only":
    active_corners = ["Rear Left", "Rear Right"]
elif mode == "Side only":
    active_corners = ["Side Left", "Side Right"]
else:
    active_corners = CORNERS

st.markdown("---")

display = st.empty()
progress_bar = st.progress(0)
timer_text = st.empty()
rep_text = st.empty()

button_col1, button_col2, button_col3 = st.columns(3)

with button_col1:
    start_button = st.button("▶️ Start", use_container_width=True)

with button_col2:
    stop_button = st.button("⏹️ Stop", use_container_width=True)

with button_col3:
    reset_button = st.button("🔄 Reset", use_container_width=True)

if reset_button:
    st.session_state.running = False
    st.session_state.current_corner = "Ready"
    st.session_state.rep_count = 0
    st.session_state.history = []
    st.session_state.start_time = None
    st.rerun()

if stop_button:
    st.session_state.running = False

if start_button:
    st.session_state.running = True
    st.session_state.rep_count = 0
    st.session_state.history = []
    st.session_state.start_time = time.time()

# -----------------------------
# Main training loop
# -----------------------------
if st.session_state.running:
    total_seconds = total_time * 60
    elapsed = 0

    while st.session_state.running and elapsed < total_seconds:
        corner = random.choice(active_corners)
        st.session_state.current_corner = corner
        st.session_state.rep_count += 1
        st.session_state.history.append(corner)

        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, int(total_seconds - elapsed))
        progress = min(1.0, elapsed / total_seconds)

        display.markdown(
            f"""
            <div style="text-align: center; padding: 30px; border-radius: 20px; border: 2px solid #ddd;">
                <div style="font-size: 80px;">{CORNER_EMOJI[corner]}</div>
                <div style="font-size: 42px; font-weight: bold;">{corner}</div>
                <div style="font-size: 18px; color: gray;">Move → recover to base → wait for next call</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        progress_bar.progress(progress)
        timer_text.subheader(f"⏱️ Time remaining: {remaining} sec")
        rep_text.subheader(f"✅ Reps: {st.session_state.rep_count}")

        time.sleep(interval)

    st.session_state.running = False
    st.success("Session complete! Nice work.")

else:
    display.markdown(
        f"""
        <div style="text-align: center; padding: 30px; border-radius: 20px; border: 2px solid #ddd;">
            <div style="font-size: 70px;">🏸</div>
            <div style="font-size: 36px; font-weight: bold;">Ready</div>
            <div style="font-size: 18px; color: gray;">Set your interval and session length, then press Start.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    rep_text.subheader(f"✅ Reps: {st.session_state.rep_count}")

# -----------------------------
# Session summary
# -----------------------------
st.markdown("---")
st.subheader("Session summary")

if st.session_state.history:
    st.write("Last few calls:")
    st.write(" → ".join(st.session_state.history[-12:]))

    counts = {corner: st.session_state.history.count(corner) for corner in CORNERS}
    st.bar_chart(counts)
else:
    st.info("No session data yet.")