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
    3: {"label": "Side Left", "emoji": "⬅️"},
    4: {"label": "Side Right", "emoji": "➡️"},
    5: {"label": "Rear Left", "emoji": "↙️"},
    6: {"label": "Rear Right", "emoji": "↘️"},
}

MODE_ZONES = {
    "Random six corners": [1, 2, 3, 4, 5, 6],
    "Front court only": [1, 2],
    "Side only": [3, 4],
    "Rear court only": [5, 6],
}

# -----------------------------
# Session state
# -----------------------------
if "running" not in st.session_state:
    st.session_state.running = False
if "current_zone" not in st.session_state:
    st.session_state.current_zone = None
if "rep_count" not in st.session_state:
    st.session_state.rep_count = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None


# -----------------------------
# Helpers
# -----------------------------
def speak_number(number: int):
    """Speak the zone number in the browser."""
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


def court_html(active_zone=None, show_labels=True):
    """Return a simple badminton court graphic with six numbered zones."""
    def zone_style(zone):
        if zone == active_zone:
            return "background:#ffeaa7; border:4px solid #222; transform:scale(1.03);"
        return "background:#f8f9fa; border:2px solid #777;"

    def zone_block(zone):
        label = ZONES[zone]["label"] if show_labels else ""
        return f"""
        <div class="zone" style="{zone_style(zone)}">
            <div class="zone-number">{zone}</div>
            <div class="zone-label">{label}</div>
        </div>
        """

    return f"""
    <style>
        .court {{
            max-width: 520px;
            margin: 0 auto;
            border: 5px solid #222;
            border-radius: 12px;
            background: #ffffff;
            padding: 10px;
        }}
        .court-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: repeat(3, 120px);
            gap: 8px;
        }}
        .zone {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            transition: all 0.2s ease-in-out;
        }}
        .zone-number {{
            font-size: 54px;
            font-weight: 800;
            line-height: 1;
        }}
        .zone-label {{
            font-size: 16px;
            color: #555;
            margin-top: 8px;
        }}
        .net {{
            text-align: center;
            font-size: 14px;
            font-weight: bold;
            color: #444;
            margin: 8px 0;
        }}
        .base {{
            text-align: center;
            margin-top: 10px;
            font-size: 14px;
            color: #555;
        }}
    </style>

    <div class="court">
        <div class="net">NET / FRONT COURT</div>
        <div class="court-grid">
            {zone_block(1)}
            {zone_block(2)}
            {zone_block(3)}
            {zone_block(4)}
            {zone_block(5)}
            {zone_block(6)}
        </div>
        <div class="base">Start from base → move to called number → recover to base</div>
    </div>
    """


def display_call(zone, display_mode):
    label = ZONES[zone]["label"]
    emoji = ZONES[zone]["emoji"]

    if display_mode == "Number only":
        return f"""
        <div style="text-align:center; padding:25px;">
            <div style="font-size:100px; font-weight:900;">{zone}</div>
            <div style="font-size:20px; color:gray;">Move to zone {zone}</div>
        </div>
        """
    elif display_mode == "Direction only":
        return f"""
        <div style="text-align:center; padding:25px;">
            <div style="font-size:80px;">{emoji}</div>
            <div style="font-size:42px; font-weight:bold;">{label}</div>
        </div>
        """
    else:
        return f"""
        <div style="text-align:center; padding:25px;">
            <div style="font-size:95px; font-weight:900;">{zone}</div>
            <div style="font-size:36px; font-weight:bold;">{label}</div>
            <div style="font-size:54px;">{emoji}</div>
        </div>
        """


# -----------------------------
# UI
# -----------------------------
st.title("🏸 Badminton Footwork Lab")
st.caption("Six-corner badminton footwork caller with numbered court zones")

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
    ["Random six corners", "Front court only", "Side only", "Rear court only"],
    horizontal=False
)

display_mode = st.radio(
    "Display style",
    ["Number + direction", "Number only", "Direction only"],
    horizontal=True
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

button_col1, button_col2, button_col3 = st.columns(3)

with button_col1:
    start_button = st.button("▶️ Start", use_container_width=True)

with button_col2:
    stop_button = st.button("⏹️ Stop", use_container_width=True)

with button_col3:
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
# Main app display
# -----------------------------
if st.session_state.running:
    total_seconds = total_time * 60
    elapsed = 0

    while st.session_state.running and elapsed < total_seconds:
        zone = random.choice(active_zones)

        st.session_state.current_zone = zone
        st.session_state.rep_count += 1
        st.session_state.history.append(zone)

        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, int(total_seconds - elapsed))
        progress = min(1.0, elapsed / total_seconds)

        court_placeholder.markdown(
            court_html(active_zone=zone, show_labels=show_court_labels),
            unsafe_allow_html=True
        )

        call_placeholder.markdown(
            display_call(zone, display_mode),
            unsafe_allow_html=True
        )

        if enable_voice:
            speak_number(zone)

        progress_bar.progress(progress)
        timer_text.subheader(f"⏱️ Time remaining: {remaining} sec")
        rep_text.subheader(f"✅ Reps: {st.session_state.rep_count}")

        time.sleep(interval)

    st.session_state.running = False
    st.success("Session complete! Nice work.")

else:
    court_placeholder.markdown(
        court_html(active_zone=None, show_labels=show_court_labels),
        unsafe_allow_html=True
    )
    call_placeholder.markdown(
        """
        <div style="text-align:center; padding:25px;">
            <div style="font-size:70px;">🏸</div>
            <div style="font-size:36px; font-weight:bold;">Ready</div>
            <div style="font-size:18px; color:gray;">Set your options, then press Start.</div>
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
    st.write(" → ".join(str(x) for x in st.session_state.history[-12:]))

    counts = {f"Zone {zone}": st.session_state.history.count(zone) for zone in range(1, 7)}
    st.bar_chart(counts)

    with st.expander("Zone map"):
        for zone in range(1, 7):
            st.write(f"**{zone}** = {ZONES[zone]['label']}")
else:
    st.info("No session data yet.")
