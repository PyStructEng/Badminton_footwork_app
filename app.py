import streamlit as st
import random
import time
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Badminton Footwork Lab",
    page_icon="🏸",
    layout="centered"
)

# -----------------------------
# Court zones
# -----------------------------
ZONES = {
    1: {"label": "Front Left", "emoji": "↖️"},
    2: {"label": "Front Right", "emoji": "↗️"},
    3: {"label": "Middle Left", "emoji": "⬅️"},
    4: {"label": "Middle Right", "emoji": "➡️"},
    5: {"label": "Rear Left", "emoji": "↙️"},
    6: {"label": "Rear Right", "emoji": "↘️"},
}

MODE_ZONES = {
    "Random six corners": [1, 2, 3, 4, 5, 6],
    "Front court only": [1, 2],
    "Middle court only": [3, 4],
    "Rear court only": [5, 6],
}


# -----------------------------
# Session state
# -----------------------------
defaults = {
    "running": False,
    "current_zone": None,
    "rep_count": 0,
    "history": [],
    "start_time": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------
# Helpers
# -----------------------------
def speak_number(number: int):
    components.html(
        f"""
        <script>
        const msg = new SpeechSynthesisUtterance("{number}");
        msg.rate = 1.0;
        msg.pitch = 1.0;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
        </script>
        """,
        height=0,
    )


def badminton_court_html(active_zone=None, show_labels=True):
    def cell(zone):
        is_active = zone == active_zone
        bg = "#fff3b0" if is_active else "#f7fbff"
        border = "4px solid #111" if is_active else "2px solid #1f2937"
        shadow = "0 0 18px rgba(0,0,0,0.28)" if is_active else "none"
        scale = "scale(1.03)" if is_active else "scale(1)"
        label = ZONES[zone]["label"] if show_labels else ""
        return f"""
        <div class="zone-cell" style="background:{bg}; border:{border}; box-shadow:{shadow}; transform:{scale};">
            <div class="zone-number">{zone}</div>
            <div class="zone-name">{label}</div>
        </div>
        """

    return f"""
    <style>
        .court-wrapper {{
            width: 100%;
            max-width: 430px;
            margin: 0 auto 14px auto;
            padding: 14px;
            border-radius: 18px;
            background: #e8f5e9;
            border: 4px solid #111827;
            font-family: Arial, sans-serif;
        }}
        .court-title {{
            text-align: center;
            font-weight: 800;
            font-size: 16px;
            margin-bottom: 8px;
            color: #111827;
        }}
        .badminton-court {{
            position: relative;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: repeat(3, 120px);
            gap: 0;
            border: 5px solid #111827;
            background: white;
        }}
        .badminton-court:before {{
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            top: 33.33%;
            border-top: 5px solid #111827;
            z-index: 3;
        }}
        .badminton-court:after {{
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            top: 66.66%;
            border-top: 5px solid #111827;
            z-index: 3;
        }}
        .center-line {{
            position: absolute;
            top: 0;
            bottom: 0;
            left: 50%;
            border-left: 5px solid #111827;
            z-index: 3;
        }}
        .net-line {{
            text-align: center;
            font-weight: 800;
            font-size: 13px;
            color: #111827;
            margin-bottom: 6px;
        }}
        .zone-cell {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: all 0.2s ease;
            z-index: 1;
            margin: 4px;
            border-radius: 8px;
        }}
        .zone-number {{
            font-size: 58px;
            font-weight: 900;
            line-height: 1;
            color: #111827;
        }}
        .zone-name {{
            font-size: 14px;
            color: #374151;
            margin-top: 8px;
            font-weight: 600;
        }}
        .base-note {{
            text-align: center;
            margin-top: 10px;
            font-size: 13px;
            color: #111827;
            font-weight: 600;
        }}
    </style>

    <div class="court-wrapper">
        <div class="court-title">Badminton Court Zone Map</div>
        <div class="net-line">NET / FRONT COURT</div>
        <div class="badminton-court">
            <div class="center-line"></div>
            {cell(1)}
            {cell(2)}
            {cell(3)}
            {cell(4)}
            {cell(5)}
            {cell(6)}
        </div>
        <div class="base-note">Base position is around the middle. Move to the called number, then recover.</div>
    </div>
    """


def call_display_html(zone, display_mode):
    label = ZONES[zone]["label"]
    emoji = ZONES[zone]["emoji"]

    if display_mode == "Number only":
        main = f"<div style='font-size:112px; font-weight:900;'>{zone}</div><div style='font-size:20px;color:#6b7280;'>Zone {zone}</div>"
    elif display_mode == "Direction only":
        main = f"<div style='font-size:76px;'>{emoji}</div><div style='font-size:38px;font-weight:800;'>{label}</div>"
    else:
        main = f"<div style='font-size:104px; font-weight:900;'>{zone}</div><div style='font-size:30px;font-weight:800;'>{label}</div><div style='font-size:44px;'>{emoji}</div>"

    return f"""
    <div style="text-align:center; padding:18px; border:2px solid #e5e7eb; border-radius:18px; margin-top:10px;">
        {main}
    </div>
    """


# -----------------------------
# UI
# -----------------------------
st.title("🏸 Badminton Footwork Lab")
st.caption("Six-corner footwork caller with numbered badminton court zones")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    interval = st.slider("Seconds between calls", 1.0, 8.0, 3.0, 0.5)
with col2:
    total_time = st.slider("Session length / minutes", 1, 20, 3, 1)

mode = st.radio(
    "Training mode",
    ["Random six corners", "Front court only", "Middle court only", "Rear court only"],
)

display_mode = st.radio(
    "Display style",
    ["Number + direction", "Number only", "Direction only"],
    horizontal=True,
)

show_court_labels = st.checkbox("Show direction labels inside court", value=True)
enable_voice = st.checkbox("Speak the number", value=True)

active_zones = MODE_ZONES[mode]

st.markdown("---")

court_placeholder = st.empty()
call_placeholder = st.empty()
progress_bar = st.progress(0)
timer_text = st.empty()
rep_text = st.empty()

b1, b2, b3 = st.columns(3)
with b1:
    start_button = st.button("▶️ Start", use_container_width=True)
with b2:
    stop_button = st.button("⏹️ Stop", use_container_width=True)
with b3:
    reset_button = st.button("🔄 Reset", use_container_width=True)

if reset_button:
    st.session_state.running = False
    st.session_state.current_zone = None
    st.session_state.rep_count = 0
    st.session_state.history = []
    st.session_state.start_time = None
    st.rerun()

if stop_button:
    st.session_state.running = False

if start_button:
    st.session_state.running = True
    st.session_state.current_zone = None
    st.session_state.rep_count = 0
    st.session_state.history = []
    st.session_state.start_time = time.time()

# -----------------------------
# Main loop
# -----------------------------
if st.session_state.running:
    total_seconds = total_time * 60

    while st.session_state.running:
        elapsed = time.time() - st.session_state.start_time
        if elapsed >= total_seconds:
            break

        zone = random.choice(active_zones)
        st.session_state.current_zone = zone
        st.session_state.rep_count += 1
        st.session_state.history.append(zone)

        remaining = max(0, int(total_seconds - elapsed))
        progress = min(1.0, elapsed / total_seconds)

        court_placeholder.markdown(
            badminton_court_html(active_zone=zone, show_labels=show_court_labels),
            unsafe_allow_html=True,
        )

        call_placeholder.markdown(
            call_display_html(zone, display_mode),
            unsafe_allow_html=True,
        )

        if enable_voice:
            speak_number(zone)

        progress_bar.progress(progress)
        timer_text.subheader(f"⏱️ Time remaining: {remaining} sec")
        rep_text.subheader(f"✅ Reps: {st.session_state.rep_count}")

        time.sleep(interval)

    st.session_state.running = False
    progress_bar.progress(1.0)
    st.success("Session complete! Nice work.")

else:
    court_placeholder.markdown(
        badminton_court_html(active_zone=None, show_labels=show_court_labels),
        unsafe_allow_html=True,
    )
    call_placeholder.markdown(
        """
        <div style="text-align:center; padding:20px; border:2px solid #e5e7eb; border-radius:18px;">
            <div style="font-size:62px;">🏸</div>
            <div style="font-size:34px; font-weight:800;">Ready</div>
            <div style="font-size:17px; color:#6b7280;">Set your options, then press Start.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    rep_text.subheader(f"✅ Reps: {st.session_state.rep_count}")

# -----------------------------
# Summary
# -----------------------------
st.markdown("---")
st.subheader("Session summary")

if st.session_state.history:
    st.write("Last few calls:")
    st.write(" → ".join(str(x) for x in st.session_state.history[-12:]))

    counts = {f"Zone {zone}": st.session_state.history.count(zone) for zone in range(1, 7)}
    st.bar_chart(counts)

    with st.expander("Zone map"):
        for zone in range(1, 7):
            st.write(f"**{zone}** = {ZONES[zone]['label']}")
else:
    st.info("No session data yet.")
