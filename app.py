import random
import time
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Badminton Footwork Drill",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Data
# --------------------------------------------------
ZONES = {
    1: "Front Left",
    2: "Front Right",
    3: "Mid Left",
    4: "Mid Right",
    5: "Rear Left",
    6: "Rear Right",
}

DRILL_MODES = {
    "6 Corner Random": [1, 2, 3, 4, 5, 6],
    "Front Court": [1, 2],
    "Mid Court": [3, 4],
    "Rear Court": [5, 6],
    "Left Side": [1, 3, 5],
    "Right Side": [2, 4, 6],
}


# --------------------------------------------------
# Session State
# --------------------------------------------------
DEFAULTS = {
    "page": "Drill",
    "running": False,
    "phase": "idle",  # idle, prepare, active, rest, finished
    "current_zone": 1,
    "round": 0,
    "completed": 0,
    "best_streak": 0,
    "streak": 0,
    "history": [],
    "last_tick": time.time(),
    "phase_start": time.time(),
    "next_call_start": time.time(),
    "session_log": [],
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# --------------------------------------------------
# CSS
# --------------------------------------------------
st.markdown(
    """
<style>
    :root {
        --bg: #08111b;
        --panel: #111c28;
        --panel2: #172332;
        --line: rgba(255,255,255,0.13);
        --text: #f8fafc;
        --muted: #cbd5e1;
        --blue: #38a3ff;
        --green: #39d353;
        --yellow: #ffd60a;
        --red: #ff3b30;
        --orange: #ff9f0a;
        --purple: #bf5af2;
    }

    .stApp {
        background: radial-gradient(circle at top, #132231 0%, #08111b 42%, #050a10 100%);
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #162231 0%, #0b1420 100%);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] * {
        color: var(--text);
    }

    .sidebar-title {
        font-size: 30px;
        font-weight: 900;
        line-height: 1.15;
        margin: 8px 0 34px 0;
    }

    .sidebar-footer {
        position: fixed;
        bottom: 18px;
        font-size: 15px;
        color: var(--muted);
    }

    .control-label {
        font-size: 13px;
        color: var(--muted);
        margin: 18px 0 8px 0;
        font-weight: 700;
        text-transform: uppercase;
    }

    .how-card {
        border: 1px solid rgba(56,163,255,0.55);
        background: linear-gradient(135deg, rgba(23,55,94,0.55), rgba(18,31,46,0.9));
        padding: 18px;
        border-radius: 8px;
        margin-top: 26px;
    }

    .how-card h3 {
        font-size: 16px;
        color: #bfdbfe;
        margin: 0 0 12px 0;
    }

    .how-card ol {
        padding-left: 22px;
        margin: 0;
        line-height: 1.85;
    }

    .top-tabs {
        display: flex;
        justify-content: center;
        gap: 26px;
        margin: 0 0 12px 0;
    }

    .tab-button {
        padding: 12px 22px;
        border-radius: 8px;
        border: 1px solid transparent;
        color: #e5e7eb;
        font-size: 18px;
        font-weight: 700;
        text-decoration: none;
    }

    .tab-button.active {
        background: rgba(56,163,255,0.22);
        border-color: rgba(56,163,255,0.65);
        color: #8cc8ff;
    }

    .main-shell {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(17, 28, 40, 0.82);
        box-shadow: 0 18px 45px rgba(0,0,0,0.28);
        overflow: hidden;
    }

    .top-panel {
        display: grid;
        grid-template-columns: 1.2fr 1.5fr 0.95fr;
        gap: 28px;
        align-items: center;
        padding: 18px 26px;
        border-bottom: 1px solid var(--line);
    }

    .call-card {
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 8px;
        padding: 22px 28px 18px 28px;
        min-height: 190px;
        text-align: center;
        background: rgba(9,18,28,0.42);
    }

    .status-title {
        color: var(--orange);
        font-weight: 900;
        font-size: 20px;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }

    .big-number {
        font-size: 78px;
        font-weight: 950;
        line-height: 1;
        color: white;
        text-shadow: 0 4px 18px rgba(0,0,0,0.35);
    }

    .direction-text {
        font-size: 28px;
        font-weight: 900;
        margin-top: 10px;
        color: white;
    }

    .progress-track {
        width: 100%;
        height: 4px;
        background: rgba(255,255,255,0.08);
        margin: 22px 0 10px 0;
        border-radius: 999px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: var(--yellow);
        border-radius: 999px;
    }

    .next-call {
        color: #e5e7eb;
        font-size: 17px;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 28px 52px;
    }

    .stat {
        display: grid;
        grid-template-columns: 50px 1fr;
        align-items: center;
    }

    .stat-icon {
        font-size: 35px;
        line-height: 1;
    }

    .stat-label {
        color: var(--muted);
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
    }

    .stat-value {
        font-size: 22px;
        font-weight: 900;
        margin-top: 4px;
    }

    .stat-green { color: var(--green); }
    .stat-blue { color: var(--blue); }
    .stat-purple { color: var(--purple); }
    .stat-orange { color: var(--orange); }

    .action-panel {
        border-left: 1px solid var(--line);
        padding-left: 26px;
        display: flex;
        flex-direction: column;
        gap: 14px;
    }

    .btn-red, .btn-dark {
        width: 100%;
        border: none;
        border-radius: 7px;
        padding: 18px;
        color: white;
        font-weight: 900;
        font-size: 18px;
        text-align: center;
    }

    .btn-red {
        background: linear-gradient(180deg, #ff4a40, #ef2d24);
    }

    .btn-dark {
        background: linear-gradient(180deg, #313d4b, #202b36);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .court-section {
        padding: 18px 28px 26px 28px;
    }

    .court-heading {
        text-align: center;
        font-size: 24px;
        font-weight: 950;
        margin-bottom: 8px;
    }

    .court-subheading {
        text-align: center;
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 5px;
    }

    .court-wrap {
        max-width: 1160px;
        margin: 0 auto;
        perspective: 900px;
    }

    .court {
        position: relative;
        height: 460px;
        background: linear-gradient(90deg, #367a3b, #438f45, #367a3b);
        border: 1px solid rgba(255,255,255,0.55);
        box-shadow: inset 0 0 40px rgba(255,255,255,0.08), 0 18px 25px rgba(0,0,0,0.3);
        clip-path: polygon(7% 0%, 93% 0%, 100% 100%, 0% 100%);
        transform: rotateX(7deg);
        transform-origin: bottom center;
        border-radius: 5px;
    }

    .court-line {
        position: absolute;
        background: rgba(255,255,255,0.92);
        z-index: 3;
    }

    .top-line { top: 4%; left: 9%; width: 82%; height: 3px; }
    .bottom-line { bottom: 4%; left: 4%; width: 92%; height: 3px; }
    .left-line { top: 4%; left: 9%; width: 3px; height: 92%; }
    .right-line { top: 4%; right: 9%; width: 3px; height: 92%; }
    .center-dash {
        position: absolute;
        top: 6%;
        bottom: 4%;
        left: 50%;
        border-left: 2px dashed rgba(255,255,255,0.85);
        z-index: 3;
    }
    .net-line-court { top: 4%; left: 50%; width: 3px; height: 92%; }
    .left-service { top: 5%; left: 30%; width: 3px; height: 90%; }
    .right-service { top: 5%; right: 30%; width: 3px; height: 90%; }
    .front-service { top: 35%; left: 7%; width: 86%; height: 3px; }
    .rear-service { bottom: 23%; left: 4.5%; width: 91%; height: 3px; }

    .zone-badge {
        position: absolute;
        width: 54px;
        height: 54px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 29px;
        font-weight: 950;
        border: 2px solid #0b0f14;
        z-index: 7;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }

    .zone-yellow {
        background: #ffeb00;
        color: #000;
    }

    .zone-white {
        background: #f8fafc;
        color: #000;
    }

    .zone-active {
        background: #38a3ff !important;
        color: #fff !important;
        box-shadow: 0 0 24px rgba(56,163,255,0.95), 0 4px 12px rgba(0,0,0,0.4);
        transform: scale(1.15);
    }

    .zone-label {
        position: absolute;
        color: white;
        font-size: 17px;
        font-weight: 900;
        z-index: 7;
        text-shadow: 0 2px 8px rgba(0,0,0,0.55);
    }

    .base {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-weight: 950;
        font-size: 22px;
        text-align: center;
        z-index: 8;
        text-shadow: 0 2px 8px rgba(0,0,0,0.45);
    }

    .feet {
        font-size: 34px;
        line-height: 1;
        display: block;
        margin-bottom: 3px;
    }

    .back-label {
        text-align: center;
        font-size: 20px;
        font-weight: 950;
        margin-top: 8px;
    }

    .tip-box {
        max-width: 1160px;
        margin: 14px auto 0 auto;
        border: 1px solid rgba(56,163,255,0.75);
        background: linear-gradient(90deg, rgba(18,55,92,0.62), rgba(18,38,61,0.54));
        border-radius: 6px;
        padding: 17px 22px;
        color: #dbeafe;
        font-size: 16px;
    }

    .bottom-quote {
        text-align: center;
        color: var(--muted);
        margin: 16px 0 0 0;
        font-size: 16px;
    }

    .history-card, .about-card {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(17,28,40,0.82);
        padding: 24px;
        margin-top: 10px;
    }

    div[data-testid="stButton"] > button {
        width: 100%;
        border-radius: 7px;
        border: 1px solid rgba(255,255,255,0.12);
        font-weight: 900;
        min-height: 50px;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(180deg, #ff4a40, #ef2d24);
        color: white;
    }

    .stSelectbox, .stRadio, .stNumberInput {
        color: white;
    }

    @media (max-width: 900px) {
        .top-panel {
            grid-template-columns: 1fr;
        }
        .action-panel {
            border-left: none;
            padding-left: 0;
        }
        .court {
            height: 360px;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def speak(text: str):
    safe = str(text).replace('"', '\\"')
    components.html(
        f"""
        <script>
            const msg = new SpeechSynthesisUtterance("{safe}");
            msg.rate = 1.0;
            msg.pitch = 1.0;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(msg);
        </script>
        """,
        height=0,
    )


def active_class(zone):
    return " zone-active" if st.session_state.current_zone == zone and st.session_state.running else ""


def zone_display_text(zone, call_type):
    if call_type == "Number only":
        return str(zone)
    if call_type == "Direction only":
        return ZONES[zone]
    return f"{zone} - {ZONES[zone]}"


def court_html():
    current = st.session_state.current_zone if st.session_state.running else None

    def badge(zone, left, top, color="white"):
        active = " zone-active" if current == zone else ""
        colour = "zone-yellow" if color == "yellow" else "zone-white"
        return f'<div class="zone-badge {colour}{active}" style="left:{left}%; top:{top}%;">{zone}</div>'

    return f"""
    <div class="court-wrap">
        <div class="court">
            <div class="court-line top-line"></div>
            <div class="court-line bottom-line"></div>
            <div class="court-line left-line"></div>
            <div class="court-line right-line"></div>
            <div class="court-line net-line-court"></div>
            <div class="center-dash"></div>
            <div class="court-line left-service"></div>
            <div class="court-line right-service"></div>
            <div class="court-line front-service"></div>
            <div class="court-line rear-service"></div>

            {badge(1, 10, 6, "yellow")}
            {badge(2, 86, 6, "yellow")}
            {badge(3, 8, 35, "white")}
            {badge(4, 87, 35, "white")}
            {badge(5, 7, 72, "white")}
            {badge(6, 90, 72, "white")}

            <div class="zone-label" style="left:9%; top:23%;">Front Left</div>
            <div class="zone-label" style="right:8%; top:23%;">Front Right</div>
            <div class="zone-label" style="left:8%; top:49%;">Mid Left</div>
            <div class="zone-label" style="right:8%; top:49%;">Mid Right</div>
            <div class="zone-label" style="left:6%; top:87%;">Rear Left</div>
            <div class="zone-label" style="right:6%; top:87%;">Rear Right</div>

            <div class="base">
                <span class="feet">👣</span>
                BASE
            </div>
        </div>
        <div class="back-label">BASE / BACK COURT</div>
    </div>
    """


def reset_drill():
    st.session_state.running = False
    st.session_state.phase = "idle"
    st.session_state.current_zone = 1
    st.session_state.round = 0
    st.session_state.completed = 0
    st.session_state.streak = 0
    st.session_state.best_streak = 0
    st.session_state.history = []
    st.session_state.last_tick = time.time()
    st.session_state.phase_start = time.time()
    st.session_state.next_call_start = time.time()


def start_drill():
    reset_drill()
    st.session_state.running = True
    st.session_state.phase = "prepare"
    st.session_state.phase_start = time.time()
    st.session_state.next_call_start = time.time()


def stop_drill():
    if st.session_state.history:
        st.session_state.session_log.append(
            {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "completed": st.session_state.completed,
                "best_streak": st.session_state.best_streak,
                "history": list(st.session_state.history),
            }
        )
    st.session_state.running = False
    st.session_state.phase = "finished"


def tick(active_zones, interval, prepare_time, rest_time, total_rounds, call_type, voice_on):
    now = time.time()

    if not st.session_state.running:
        return

    if st.session_state.phase == "prepare":
        if now - st.session_state.phase_start >= prepare_time:
            st.session_state.phase = "active"
            st.session_state.phase_start = now
            st.session_state.next_call_start = now

    elif st.session_state.phase == "active":
        if st.session_state.round >= total_rounds:
            stop_drill()
            return

        if now - st.session_state.next_call_start >= interval or st.session_state.round == 0:
            zone = random.choice(active_zones)
            st.session_state.current_zone = zone
            st.session_state.round += 1
            st.session_state.completed += 1
            st.session_state.streak += 1
            st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
            st.session_state.history.append(zone)
            st.session_state.next_call_start = now

            if voice_on:
                speak(zone_display_text(zone, call_type))

            if rest_time > 0:
                st.session_state.phase = "rest"
                st.session_state.phase_start = now

    elif st.session_state.phase == "rest":
        if now - st.session_state.phase_start >= rest_time:
            st.session_state.phase = "active"
            st.session_state.next_call_start = now


def time_remaining_for_card(prepare_time, interval, rest_time):
    now = time.time()
    if st.session_state.phase == "prepare":
        return max(0, prepare_time - (now - st.session_state.phase_start)), "GET READY"
    if st.session_state.phase == "rest":
        return max(0, rest_time - (now - st.session_state.phase_start)), "REST"
    if st.session_state.phase == "active":
        return max(0, interval - (now - st.session_state.next_call_start)), "GO"
    if st.session_state.phase == "finished":
        return 0, "FINISHED"
    return 0, "READY"


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">Badminton<br>Footwork Drill 🏸</div>', unsafe_allow_html=True)

    st.markdown('<div class="control-label">DRILL MODE</div>', unsafe_allow_html=True)
    drill_mode = st.selectbox("Drill mode", list(DRILL_MODES.keys()), label_visibility="collapsed")

    st.markdown('<div class="control-label">CALL TYPE (On Screen & Voice)</div>', unsafe_allow_html=True)
    call_type = st.radio(
        "Call type",
        ["Number only", "Direction only", "Number + Direction"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="control-label">INTERVAL (sec)</div>', unsafe_allow_html=True)
    interval = st.number_input("Interval", min_value=0.5, max_value=10.0, value=3.0, step=0.5, label_visibility="collapsed")

    st.markdown('<div class="control-label">PREPARE TIME (sec)</div>', unsafe_allow_html=True)
    prepare_time = st.number_input("Prepare time", min_value=0, max_value=20, value=3, step=1, label_visibility="collapsed")

    st.markdown('<div class="control-label">REST TIME (sec)</div>', unsafe_allow_html=True)
    rest_time = st.number_input("Rest time", min_value=0, max_value=20, value=0, step=1, label_visibility="collapsed")

    st.markdown('<div class="control-label">TOTAL ROUNDS</div>', unsafe_allow_html=True)
    total_rounds = st.number_input("Total rounds", min_value=1, max_value=300, value=30, step=1, label_visibility="collapsed")

    voice_on = st.checkbox("Voice call", value=True)

    st.markdown(
        """
        <div class="how-card">
            <h3>HOW TO USE</h3>
            <ol>
                <li>Start the drill</li>
                <li>Move to the called zone</li>
                <li>Recover back to base (center)</li>
                <li>Get ready for next call</li>
            </ol>
        </div>
        <div class="sidebar-footer">Made with ❤️ for badminton players</div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# Top navigation
# --------------------------------------------------
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    t1, t2, t3 = st.columns(3)
    if t1.button("▷ Drill", use_container_width=True):
        st.session_state.page = "Drill"
    if t2.button("⌁ History", use_container_width=True):
        st.session_state.page = "History"
    if t3.button("ⓘ About", use_container_width=True):
        st.session_state.page = "About"


# --------------------------------------------------
# Main Pages
# --------------------------------------------------
active_zones = DRILL_MODES[drill_mode]

if st.session_state.page == "Drill":
    tick(active_zones, interval, prepare_time, rest_time, total_rounds, call_type, voice_on)

    remaining, phase_label = time_remaining_for_card(prepare_time, interval, rest_time)
    card_number = int(round(remaining)) if st.session_state.phase == "prepare" else st.session_state.current_zone
    call_text = zone_display_text(st.session_state.current_zone, call_type)

    if st.session_state.phase == "idle":
        phase_label = "READY"
        card_number = "▶"
        next_text = "Press Start Drill"
        progress_pct = 0
    elif st.session_state.phase == "prepare":
        next_text = f"Starting in {remaining:.1f} sec"
        progress_pct = 100 * (1 - remaining / max(prepare_time, 1))
    elif st.session_state.phase == "active":
        next_text = f"Next call in {remaining:.1f} sec"
        progress_pct = 100 * (1 - remaining / max(interval, 0.1))
    elif st.session_state.phase == "rest":
        next_text = f"Rest {remaining:.1f} sec"
        progress_pct = 100 * (1 - remaining / max(rest_time, 1))
    else:
        next_text = "Drill complete"
        progress_pct = 100

    shown_main = card_number if st.session_state.phase in ["idle", "prepare"] else call_text

    status_word = "Running" if st.session_state.running else ("Finished" if st.session_state.phase == "finished" else "Ready")

    st.markdown('<div class="main-shell">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="top-panel">
            <div class="call-card">
                <div class="status-title">{phase_label}</div>
                <div class="big-number">{shown_main}</div>
                <div class="progress-track"><div class="progress-fill" style="width:{progress_pct}%;"></div></div>
                <div class="next-call">{next_text}</div>
            </div>

            <div class="stats-grid">
                <div class="stat">
                    <div class="stat-icon stat-green">▷</div>
                    <div>
                        <div class="stat-label">STATUS</div>
                        <div class="stat-value stat-green">{status_word}</div>
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-icon stat-purple">↪</div>
                    <div>
                        <div class="stat-label">COMPLETED</div>
                        <div class="stat-value">{st.session_state.completed}</div>
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-icon stat-blue">⏱</div>
                    <div>
                        <div class="stat-label">ROUND</div>
                        <div class="stat-value">{st.session_state.round} / {total_rounds}</div>
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-icon stat-orange">🏆</div>
                    <div>
                        <div class="stat-label">BEST STREAK</div>
                        <div class="stat-value">{st.session_state.best_streak}</div>
                    </div>
                </div>
            </div>

            <div class="action-panel">
        """,
        unsafe_allow_html=True,
    )

    a1, a2 = st.columns(2)
    with a1:
        if not st.session_state.running:
            if st.button("▶ Start Drill", type="primary", use_container_width=True):
                start_drill()
                st.rerun()
        else:
            if st.button("□ Stop Drill", type="primary", use_container_width=True):
                stop_drill()
                st.rerun()
    with a2:
        if st.button("↻ Reset", use_container_width=True):
            reset_drill()
            st.rerun()

    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="court-section">
            <div class="court-heading">BADMINTON COURT – 6 CORNERS</div>
            <div class="court-subheading">NET / FRONT COURT</div>
            {court_html()}
            <div class="tip-box">ⓘ &nbsp; Move to the called zone as fast as you can and recover back to BASE after each call.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="bottom-quote">Stay light. Move fast. Be consistent. 💪</div>', unsafe_allow_html=True)

    if st.session_state.running:
        time.sleep(0.25)
        st.rerun()


elif st.session_state.page == "History":
    st.markdown('<div class="history-card">', unsafe_allow_html=True)
    st.header("History")

    if not st.session_state.session_log and not st.session_state.history:
        st.info("No completed sessions yet.")
    else:
        if st.session_state.history:
            st.subheader("Current / latest session")
            st.write(f"Completed: **{st.session_state.completed}**")
            st.write(f"Best streak: **{st.session_state.best_streak}**")
            st.write("Last calls: " + " → ".join(str(x) for x in st.session_state.history[-20:]))

            counts = {f"Zone {i}": st.session_state.history.count(i) for i in range(1, 7)}
            st.bar_chart(counts)

        if st.session_state.session_log:
            st.subheader("Saved sessions")
            for item in reversed(st.session_state.session_log[-10:]):
                st.write(f"**{item['date']}** — completed {item['completed']} calls, best streak {item['best_streak']}")

    st.markdown("</div>", unsafe_allow_html=True)


else:
    st.markdown('<div class="about-card">', unsafe_allow_html=True)
    st.header("About")
    st.write(
        """
        This is a badminton footwork drill web app designed for six-corner movement practice.

        It can call zones by number, direction, or both. The goal is simple:
        move quickly to the called zone, recover to base, and repeat with good balance.
        """
    )
    st.subheader("Zone map")
    st.write("1 = Front Left")
    st.write("2 = Front Right")
    st.write("3 = Mid Left")
    st.write("4 = Mid Right")
    st.write("5 = Rear Left")
    st.write("6 = Rear Right")
    st.markdown("</div>", unsafe_allow_html=True)
