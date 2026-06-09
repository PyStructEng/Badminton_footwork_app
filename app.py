import random
import time
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Badminton Footwork Drill",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="collapsed",
)


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

DEFAULTS = {
    "page": "Drill",
    "running": False,
    "phase": "idle",
    "current_zone": 1,
    "round": 0,
    "completed": 0,
    "best_streak": 0,
    "streak": 0,
    "history": [],
    "session_log": [],
    "phase_start": time.time(),
    "next_call_start": time.time(),
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------
# Global Streamlit styling
# --------------------------
st.markdown(
    """
<style>
.stApp {
    background: radial-gradient(circle at top, #142333 0%, #08111b 45%, #050a10 100%);
    color: #f8fafc;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #162231 0%, #0b1420 100%);
    border-right: 1px solid rgba(255,255,255,0.12);
}

[data-testid="stSidebar"] * {
    color: #f8fafc;
}

[data-testid="stSidebar"] .stSelectbox div,
[data-testid="stSidebar"] .stNumberInput input {
    background: #263443 !important;
    color: #f8fafc !important;
    border-color: rgba(255,255,255,0.12) !important;
}

div[data-testid="stButton"] > button {
    min-height: 50px;
    border-radius: 8px;
    font-weight: 900;
    border: 1px solid rgba(255,255,255,0.18);
    background: linear-gradient(180deg, #313d4b, #202b36);
    color: white;
}

div[data-testid="stButton"] > button:hover {
    border-color: #38a3ff;
    color: white;
}

.stButton button[kind="primary"] {
    background: linear-gradient(180deg, #ff4a40, #ef2d24) !important;
    color: white !important;
}

.sidebar-title {
    font-size: 30px;
    font-weight: 950;
    line-height: 1.15;
    margin: 8px 0 34px 0;
}

.control-label {
    font-size: 13px;
    color: #cbd5e1;
    margin: 18px 0 8px 0;
    font-weight: 800;
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

/* Mobile-first Streamlit shell tweaks */
.block-container {
    padding-top: 0.5rem;
    padding-left: 0.75rem;
    padding-right: 0.75rem;
    max-width: 1250px;
}
.mobile-title {
    text-align: center;
    font-size: 28px;
    font-weight: 950;
    line-height: 1.15;
    margin: 4px 0 8px 0;
}
@media (max-width: 768px) {
    .block-container {
        padding-top: 0.25rem;
        padding-left: 0.35rem;
        padding-right: 0.35rem;
    }
    div[data-testid="stButton"] > button {
        min-height: 44px;
        font-size: 14px;
        padding-left: 4px;
        padding-right: 4px;
    }
    .mobile-title {
        font-size: 23px;
        margin-bottom: 6px;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 0.35rem;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


def speak(text: str):
    safe_text = str(text).replace('"', '\\"')
    components.html(
        f"""
<script>
const msg = new SpeechSynthesisUtterance("{safe_text}");
msg.rate = 1.0;
msg.pitch = 1.0;
window.speechSynthesis.cancel();
window.speechSynthesis.speak(msg);
</script>
""",
        height=0,
    )


def reset_drill():
    st.session_state.running = False
    st.session_state.phase = "idle"
    st.session_state.current_zone = 1
    st.session_state.round = 0
    st.session_state.completed = 0
    st.session_state.best_streak = 0
    st.session_state.streak = 0
    st.session_state.history = []
    st.session_state.phase_start = time.time()
    st.session_state.next_call_start = time.time()


def start_drill():
    reset_drill()
    st.session_state.running = True
    st.session_state.phase = "prepare"
    st.session_state.phase_start = time.time()
    st.session_state.next_call_start = time.time()


def save_session():
    if st.session_state.history:
        st.session_state.session_log.append(
            {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "completed": st.session_state.completed,
                "best_streak": st.session_state.best_streak,
                "history": list(st.session_state.history),
            }
        )


def stop_drill():
    save_session()
    st.session_state.running = False
    st.session_state.phase = "finished"


def call_text(zone: int, call_type: str):
    if call_type == "Number only":
        return str(zone)
    if call_type == "Direction only":
        return ZONES[zone]
    return f"{zone} - {ZONES[zone]}"


def tick(active_zones, interval, prepare_time, rest_time, total_rounds, call_type, voice_on):
    if not st.session_state.running:
        return

    now = time.time()

    if st.session_state.phase == "prepare":
        if now - st.session_state.phase_start >= prepare_time:
            st.session_state.phase = "active"
            st.session_state.phase_start = now
            st.session_state.next_call_start = now

    if st.session_state.phase == "active":
        if st.session_state.round >= total_rounds:
            stop_drill()
            return

        if st.session_state.round == 0 or now - st.session_state.next_call_start >= interval:
            zone = random.choice(active_zones)
            st.session_state.current_zone = zone
            st.session_state.round += 1
            st.session_state.completed += 1
            st.session_state.streak += 1
            st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
            st.session_state.history.append(zone)
            st.session_state.next_call_start = now

            if voice_on:
                speak(call_text(zone, call_type))

            if rest_time > 0:
                st.session_state.phase = "rest"
                st.session_state.phase_start = now

    elif st.session_state.phase == "rest":
        if now - st.session_state.phase_start >= rest_time:
            st.session_state.phase = "active"
            st.session_state.next_call_start = now


def card_values(interval, prepare_time, rest_time):
    now = time.time()

    if st.session_state.phase == "idle":
        return "READY", "▶", "Press Start Drill", 0

    if st.session_state.phase == "prepare":
        remaining = max(0, prepare_time - (now - st.session_state.phase_start))
        pct = 100 * (1 - remaining / max(prepare_time, 1))
        return "GET READY", str(int(round(remaining))), f"Starting in {remaining:.1f} sec", pct

    if st.session_state.phase == "active":
        remaining = max(0, interval - (now - st.session_state.next_call_start))
        pct = 100 * (1 - remaining / max(interval, 0.1))
        return "GO", str(st.session_state.current_zone), f"Next call in {remaining:.1f} sec", pct

    if st.session_state.phase == "rest":
        remaining = max(0, rest_time - (now - st.session_state.phase_start))
        pct = 100 * (1 - remaining / max(rest_time, 1))
        return "REST", str(st.session_state.current_zone), f"Rest {remaining:.1f} sec", pct

    return "FINISHED", str(st.session_state.current_zone), "Drill complete", 100


def dashboard_html(phase_label, main_call, next_text, progress_pct, total_rounds):
    status = "Running" if st.session_state.running else ("Finished" if st.session_state.phase == "finished" else "Ready")
    current_zone = st.session_state.current_zone if st.session_state.running or st.session_state.phase == "finished" else None

    def badge(zone, left, top, colour):
        active = " active" if current_zone == zone and st.session_state.phase in ["active", "rest", "finished"] else ""
        return f'<div class="zone-badge {colour}{active}" style="left:{left}%; top:{top}%;">{zone}</div>'

    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    color: #f8fafc;
    background: transparent;
}}

.shell {{
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 8px;
    background: rgba(17,28,40,0.84);
    box-shadow: 0 18px 45px rgba(0,0,0,0.28);
    overflow: hidden;
}}

.top-panel {{
    display: grid;
    grid-template-columns: 1.2fr 1.5fr;
    gap: 34px;
    align-items: center;
    padding: 22px 32px;
    border-bottom: 1px solid rgba(255,255,255,0.13);
}}

.call-card {{
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 8px;
    padding: 24px 30px 18px;
    min-height: 185px;
    text-align: center;
    background: rgba(9,18,28,0.45);
}}

.status-title {{
    color: #ffb000;
    font-weight: 950;
    font-size: 20px;
    margin-bottom: 12px;
}}

.big-number {{
    font-size: 76px;
    font-weight: 950;
    line-height: 1;
    color: white;
    text-shadow: 0 4px 18px rgba(0,0,0,0.35);
}}

.progress-track {{
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,0.1);
    margin: 22px 0 12px;
    border-radius: 999px;
    overflow: hidden;
}}

.progress-fill {{
    height: 100%;
    width: {progress_pct:.1f}%;
    background: #ffd60a;
    border-radius: 999px;
}}

.next-call {{
    color: #e5e7eb;
    font-size: 17px;
}}

.stats-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px 70px;
}}

.stat {{
    display: grid;
    grid-template-columns: 52px 1fr;
    align-items: center;
}}

.stat-icon {{
    font-size: 34px;
}}

.stat-label {{
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 850;
}}

.stat-value {{
    font-size: 22px;
    font-weight: 950;
    margin-top: 4px;
}}

.green {{ color: #39d353; }}
.blue {{ color: #38a3ff; }}
.purple {{ color: #bf5af2; }}
.orange {{ color: #ff9f0a; }}

.court-section {{
    padding: 22px 28px 28px;
}}

.court-heading {{
    text-align: center;
    font-size: 24px;
    font-weight: 950;
    margin-bottom: 8px;
}}

.court-subheading {{
    text-align: center;
    font-size: 18px;
    font-weight: 900;
    margin-bottom: 6px;
}}

.court-wrap {{
    max-width: 1160px;
    margin: 0 auto;
    perspective: 900px;
}}

.court {{
    position: relative;
    height: 460px;
    background: linear-gradient(90deg, #367a3b, #438f45, #367a3b);
    border: 1px solid rgba(255,255,255,0.55);
    box-shadow: inset 0 0 40px rgba(255,255,255,0.08), 0 18px 25px rgba(0,0,0,0.3);
    clip-path: polygon(7% 0%, 93% 0%, 100% 100%, 0% 100%);
    transform: rotateX(7deg);
    transform-origin: bottom center;
    border-radius: 5px;
}}

.line {{
    position: absolute;
    background: rgba(255,255,255,0.92);
    z-index: 3;
}}

.top-line {{ top: 4%; left: 9%; width: 82%; height: 3px; }}
.bottom-line {{ bottom: 4%; left: 4%; width: 92%; height: 3px; }}
.left-line {{ top: 4%; left: 9%; width: 3px; height: 92%; }}
.right-line {{ top: 4%; right: 9%; width: 3px; height: 92%; }}
.net-line {{ top: 4%; left: 50%; width: 3px; height: 92%; }}
.left-service {{ top: 5%; left: 30%; width: 3px; height: 90%; }}
.right-service {{ top: 5%; right: 30%; width: 3px; height: 90%; }}
.front-service {{ top: 35%; left: 7%; width: 86%; height: 3px; }}
.rear-service {{ bottom: 23%; left: 4.5%; width: 91%; height: 3px; }}

.center-dash {{
    position: absolute;
    top: 6%;
    bottom: 4%;
    left: 50%;
    border-left: 2px dashed rgba(255,255,255,0.85);
    z-index: 4;
}}

.zone-badge {{
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
}}

.yellow {{ background: #ffeb00; color: #000; }}
.white {{ background: #f8fafc; color: #000; }}

.active {{
    background: #38a3ff !important;
    color: white !important;
    box-shadow: 0 0 25px rgba(56,163,255,0.95), 0 4px 12px rgba(0,0,0,0.4);
    transform: scale(1.16);
}}

.zone-label {{
    position: absolute;
    color: white;
    font-size: 17px;
    font-weight: 950;
    z-index: 7;
    text-shadow: 0 2px 8px rgba(0,0,0,0.55);
}}

.base {{
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
}}

.feet {{
    display: block;
    font-size: 34px;
    line-height: 1;
    margin-bottom: 3px;
}}

.back-label {{
    text-align: center;
    font-size: 20px;
    font-weight: 950;
    margin-top: 8px;
}}

.tip-box {{
    max-width: 1160px;
    margin: 14px auto 0;
    border: 1px solid rgba(56,163,255,0.75);
    background: linear-gradient(90deg, rgba(18,55,92,0.62), rgba(18,38,61,0.54));
    border-radius: 6px;
    padding: 17px 22px;
    color: #dbeafe;
    font-size: 16px;
}}

.bottom-quote {{
    text-align: center;
    color: #cbd5e1;
    margin: 16px 0 0;
    font-size: 16px;
}}


@media (max-width: 768px) {{
    .shell {{ border-radius: 10px; }}
    .top-panel {{
        grid-template-columns: 1fr;
        gap: 10px;
        padding: 10px;
    }}
    .call-card {{
        min-height: 130px;
        padding: 14px 14px 12px;
    }}
    .status-title {{ font-size: 15px; margin-bottom: 7px; }}
    .big-number {{ font-size: clamp(42px, 16vw, 66px); }}
    .progress-track {{ margin: 12px 0 7px; }}
    .next-call {{ font-size: 14px; }}
    .stats-grid {{
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        background: rgba(8,17,27,0.35);
        border-radius: 10px;
        padding: 10px;
    }}
    .stat {{ grid-template-columns: 30px 1fr; }}
    .stat-icon {{ font-size: 23px; }}
    .stat-label {{ font-size: 10px; }}
    .stat-value {{ font-size: 16px; }}
    .court-section {{ padding: 10px 8px 14px; }}
    .court-heading {{ font-size: 17px; margin-bottom: 4px; }}
    .court-subheading {{ font-size: 13px; margin-bottom: 4px; }}
    .court {{
        height: min(72vh, 500px);
        min-height: 410px;
        clip-path: polygon(4% 0%, 96% 0%, 100% 100%, 0% 100%);
        transform: none;
    }}
    .top-line {{ left: 6%; width: 88%; }}
    .bottom-line {{ left: 3%; width: 94%; }}
    .left-line {{ left: 6%; }}
    .right-line {{ right: 6%; }}
    .front-service {{ left: 5%; width: 90%; }}
    .rear-service {{ left: 4%; width: 92%; }}
    .zone-badge {{ width: 41px; height: 41px; font-size: 22px; }}
    .zone-label {{ font-size: 11px; }}
    .base {{ font-size: 16px; }}
    .feet {{ font-size: 25px; }}
    .back-label {{ font-size: 14px; }}
    .tip-box {{ font-size: 13px; padding: 10px; margin-top: 8px; }}
    .bottom-quote {{ font-size: 13px; }}
}}
@media (max-width: 430px) {{
    .court {{ height: 405px; min-height: 405px; }}
    .zone-badge {{ width: 38px; height: 38px; font-size: 20px; }}
    .zone-label {{ font-size: 10.5px; }}
    .tip-box {{ display: none; }}
}}

@media (max-width: 900px) {{
    .top-panel {{ grid-template-columns: 1fr; }}
    .court {{ height: 350px; }}
}}
</style>
</head>
<body>
<div class="shell">
    <div class="top-panel">
        <div class="call-card">
            <div class="status-title">{phase_label}</div>
            <div class="big-number">{main_call}</div>
            <div class="progress-track"><div class="progress-fill"></div></div>
            <div class="next-call">{next_text}</div>
        </div>

        <div class="stats-grid">
            <div class="stat">
                <div class="stat-icon green">▷</div>
                <div>
                    <div class="stat-label">STATUS</div>
                    <div class="stat-value green">{status}</div>
                </div>
            </div>
            <div class="stat">
                <div class="stat-icon purple">↪</div>
                <div>
                    <div class="stat-label">COMPLETED</div>
                    <div class="stat-value">{st.session_state.completed}</div>
                </div>
            </div>
            <div class="stat">
                <div class="stat-icon blue">⏱</div>
                <div>
                    <div class="stat-label">ROUND</div>
                    <div class="stat-value">{st.session_state.round} / {total_rounds}</div>
                </div>
            </div>
            <div class="stat">
                <div class="stat-icon orange">🏆</div>
                <div>
                    <div class="stat-label">BEST STREAK</div>
                    <div class="stat-value">{st.session_state.best_streak}</div>
                </div>
            </div>
        </div>
    </div>

    <div class="court-section">
        <div class="court-heading">BADMINTON COURT – 6 CORNERS</div>
        <div class="court-subheading">NET / FRONT COURT</div>

        <div class="court-wrap">
            <div class="court">
                <div class="line top-line"></div>
                <div class="line bottom-line"></div>
                <div class="line left-line"></div>
                <div class="line right-line"></div>
                <div class="line net-line"></div>
                <div class="line left-service"></div>
                <div class="line right-service"></div>
                <div class="line front-service"></div>
                <div class="line rear-service"></div>
                <div class="center-dash"></div>

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

        <div class="tip-box">ⓘ &nbsp; Move to the called zone as fast as you can and recover back to BASE after each call.</div>
    </div>
</div>
<div class="bottom-quote">Stay light. Move fast. Be consistent. 💪</div>
</body>
</html>
"""
    return html


# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">Badminton<br>Footwork Drill 🏸</div>', unsafe_allow_html=True)

    st.markdown('<div class="control-label">DRILL MODE</div>', unsafe_allow_html=True)
    drill_mode = st.selectbox("Drill mode", list(DRILL_MODES.keys()), label_visibility="collapsed")

    st.markdown('<div class="control-label">CALL TYPE (ON SCREEN & VOICE)</div>', unsafe_allow_html=True)
    call_type = st.radio(
        "Call type",
        ["Number only", "Direction only", "Number + Direction"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="control-label">INTERVAL (SEC)</div>', unsafe_allow_html=True)
    interval = st.number_input("Interval", min_value=0.5, max_value=10.0, value=3.0, step=0.5, label_visibility="collapsed")

    st.markdown('<div class="control-label">PREPARE TIME (SEC)</div>', unsafe_allow_html=True)
    prepare_time = st.number_input("Prepare time", min_value=0, max_value=20, value=3, step=1, label_visibility="collapsed")

    st.markdown('<div class="control-label">REST TIME (SEC)</div>', unsafe_allow_html=True)
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
        <li>Recover back to base</li>
        <li>Get ready for next call</li>
    </ol>
</div>
<p style="margin-top:28px;color:#cbd5e1;">Made with ❤️ for badminton players</p>
""",
        unsafe_allow_html=True,
    )


# --------------------------
# Navigation and controls
# --------------------------
st.markdown('<div class="mobile-title">Badminton Footwork Drill 🏸</div>', unsafe_allow_html=True)
nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
with nav_mid:
    n1, n2, n3 = st.columns(3)
    if n1.button("▷ Drill", use_container_width=True):
        st.session_state.page = "Drill"
    if n2.button("⌁ History", use_container_width=True):
        st.session_state.page = "History"
    if n3.button("ⓘ About", use_container_width=True):
        st.session_state.page = "About"

st.divider()

active_zones = DRILL_MODES[drill_mode]

if st.session_state.page == "Drill":
    tick(active_zones, interval, prepare_time, rest_time, total_rounds, call_type, voice_on)
    phase_label, main_call, next_text, progress_pct = card_values(interval, prepare_time, rest_time)

    action_left, action_center, action_right = st.columns([1.1, 2.2, 1.1])
    with action_left:
        if st.session_state.running:
            if st.button("□ Stop Drill", type="primary", use_container_width=True):
                stop_drill()
                st.rerun()
        else:
            if st.button("▶ Start Drill", type="primary", use_container_width=True):
                start_drill()
                st.rerun()

    with action_right:
        if st.button("↻ Reset", use_container_width=True):
            reset_drill()
            st.rerun()

    components.html(
        dashboard_html(phase_label, main_call, next_text, progress_pct, total_rounds),
        height=760,
        scrolling=False,
    )

    if st.session_state.running:
        time.sleep(0.25)
        st.rerun()

elif st.session_state.page == "History":
    st.header("History")

    if not st.session_state.history and not st.session_state.session_log:
        st.info("No session history yet.")
    else:
        if st.session_state.history:
            st.subheader("Latest session")
            st.write(f"Completed calls: **{st.session_state.completed}**")
            st.write(f"Best streak: **{st.session_state.best_streak}**")
            st.write("Last calls: " + " → ".join(str(x) for x in st.session_state.history[-20:]))

            counts = {f"Zone {i}": st.session_state.history.count(i) for i in range(1, 7)}
            st.bar_chart(counts)

        if st.session_state.session_log:
            st.subheader("Saved sessions")
            for item in reversed(st.session_state.session_log[-10:]):
                st.write(f"**{item['date']}** — completed {item['completed']} calls, best streak {item['best_streak']}")

else:
    st.header("About")
    st.write(
        """
        This app is a six-corner badminton footwork trainer.

        Start from BASE, move to the called zone, recover to BASE, and repeat.
        You can train by number, direction, or both.
        """
    )

    st.subheader("Zone map")
    for zone, label in ZONES.items():
        st.write(f"**{zone}** = {label}")
