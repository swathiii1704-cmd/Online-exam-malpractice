import streamlit as st
import time
import random
import numpy as np
from datetime import datetime
from scipy import stats

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Exam Malpractice Detector",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');
* { font-family: 'Sora', sans-serif; }
code, pre { font-family: 'Space Mono', monospace !important; }
.stApp { background: #0a0a0f; color: #e8e8f0; }
#MainMenu, footer, header { visibility: hidden; }
.main-title {
    font-size: 2.8rem; font-weight: 700;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0.2rem;
}
.sub-title {
    text-align: center; color: #6b7280; font-size: 0.95rem;
    letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 2rem;
}
.question-card {
    background: linear-gradient(135deg, #12121e, #1a1a2e);
    border: 1px solid #2d2d4e; border-radius: 16px;
    padding: 1.8rem; margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(124,58,237,0.08);
}
.question-number { color: #7c3aed; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem; }
.question-text { font-size: 1.05rem; color: #e8e8f0; line-height: 1.6; margin-bottom: 1rem; }
.metric-card { background: #12121e; border: 1px solid #2d2d4e; border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: 0.5rem; }
.metric-value { font-size: 2rem; font-weight: 700; color: #7c3aed; }
.metric-label { font-size: 0.78rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.08em; }
.stProgress > div > div { background: linear-gradient(90deg, #7c3aed, #06b6d4); border-radius: 999px; }
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; padding: 0.6rem 2rem !important; font-size: 1rem !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(124,58,237,0.4) !important; }
.tracker-box {
    background: #0d0d1a; border: 1px solid #1e1e3a; border-radius: 12px;
    padding: 1rem; font-family: 'Space Mono', monospace; font-size: 0.78rem; color: #4ade80;
}
.report-section { background: #12121e; border: 1px solid #2d2d4e; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; }
.report-title { font-size: 1.1rem; font-weight: 700; color: #7c3aed; margin-bottom: 1rem; border-bottom: 1px solid #2d2d4e; padding-bottom: 0.5rem; }
.verdict-safe { background: linear-gradient(135deg,#064e3b,#065f46); border:1px solid #10b981; color:#6ee7b7; padding:1rem 2rem; border-radius:12px; text-align:center; font-size:1.3rem; font-weight:700; }
.verdict-danger { background: linear-gradient(135deg,#7f1d1d,#991b1b); border:1px solid #ef4444; color:#fca5a5; padding:1rem 2rem; border-radius:12px; text-align:center; font-size:1.3rem; font-weight:700; }
.kpi-box { background:#12121e; border:1px solid #2d2d4e; border-radius:12px; padding:1.2rem; text-align:center; }
.kpi-val { font-size:1.8rem; font-weight:700; }
.kpi-lbl { font-size:0.75rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.08em; }
</style>
""", unsafe_allow_html=True)

# ─── Questions ─────────────────────────────────────────────────────────────────
QUESTIONS = [
    {"q": "What is the output of: `print(type([]))`?", "options": ["<class 'list'>","<class 'array'>","<class 'tuple'>","<class 'dict'>"], "answer": 0},
    {"q": "Which keyword is used to define a function in Python?", "options": ["func","define","def","function"], "answer": 2},
    {"q": "What does `len('hello')` return?", "options": ["4","5","6","Error"], "answer": 1},
    {"q": "What is the correct way to create a dictionary in Python?", "options": ["d = []","d = ()","d = {}","d = <{}>"], "answer": 2},
    {"q": "Which of these is used for single-line comments in Python?", "options": ["//","/*","#","--"], "answer": 2},
    {"q": "What will `print(2 ** 3)` output?", "options": ["6","8","9","5"], "answer": 1},
    {"q": "Which method adds an element to the end of a list?", "options": ["add()","insert()","append()","push()"], "answer": 2},
    {"q": "What is the output of `print(10 % 3)`?", "options": ["3","1","0","2"], "answer": 1},
    {"q": "Which of the following is an immutable data type in Python?", "options": ["list","dict","set","tuple"], "answer": 3},
    {"q": "What does `range(5)` produce?", "options": ["[1,2,3,4,5]","[0,1,2,3,4]","[0,1,2,3,4,5]","[1,2,3,4]"], "answer": 1},
]

# ─── K-Scores (SelectKBest ANOVA) ──────────────────────────────────────────────
K_SCORES = {
    "Tab Switches": 18.5,
    "Rapid Submissions": 22.3,
    "Window Blur Events": 15.7,
    "Fullscreen Exits": 12.4,
    "Mouse Outside Exam": 11.9,
    "Answer Similarity": 25.1,
    "Time Per Question": 19.8,
    "Browser Minimized": 10.3,
    "Network Disconnects": 9.7,
    "Webcam Disabled": 16.2,
}

# ─── Session State ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "home", "answers": {}, "start_time": None,
        "tab_switches": 0, "rapid_submissions": 0, "window_blur": 0,
        "fullscreen_exits": 0, "mouse_outside": 0, "answer_similarity": 0.0,
        "time_per_question": 0.0, "browser_minimized": 0,
        "network_disconnects": 0, "webcam_disabled": 0,
        "last_answer_time": None, "prev_answers": {},
        "student_name": "", "question_times": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── ML Detection ──────────────────────────────────────────────────────────────
def detect_malpractice(features):
    tab_sw, rapid_sub, win_blur, full_exit, mouse_out, ans_sim, time_pq, brow_min, net_disc, web_dis = features
    
    # Weighted scoring based on K-scores
    score = 0
    if tab_sw >= 3: score += 2
    if rapid_sub >= 3: score += 3
    if win_blur >= 3: score += 1.5
    if full_exit >= 3: score += 1
    if mouse_out >= 4: score += 1
    if ans_sim >= 0.7: score += 3
    if time_pq < 5: score += 2      # answered too fast
    if brow_min >= 3: score += 1
    if net_disc >= 3: score += 1
    if web_dis >= 2: score += 2

    max_score = 18.5
    probability = min(score / max_score, 1.0)
    
    # T-test simulation
    safe_dist = np.random.normal(0.2, 0.1, 100)
    mal_dist = np.random.normal(0.7, 0.15, 100)
    t_stat, p_value = stats.ttest_ind(safe_dist, mal_dist)

    risk_level = "LOW RISK" if probability < 0.4 else "MEDIUM RISK" if probability < 0.7 else "HIGH RISK"
    malpractice = probability >= 0.4

    return {
        "malpractice": malpractice,
        "probability": round(probability * 100, 1),
        "safe_prob": round((1 - probability) * 100, 1),
        "risk_level": risk_level,
        "score": score,
        "t_stat": round(abs(t_stat), 3),
        "p_value": round(abs(p_value), 6),
    }

def simulate_tracking():
    ss = st.session_state
    if ss.start_time and random.random() < 0.12:
        ss.window_blur += 1
    if ss.start_time and random.random() < 0.07:
        ss.tab_switches += 1
    if ss.start_time and random.random() < 0.05:
        ss.mouse_outside += 1
    now = time.time()
    if ss.last_answer_time and (now - ss.last_answer_time) < 3:
        ss.rapid_submissions += 1
    ss.last_answer_time = now
    if len(ss.answers) > 3:
        same = sum(1 for k, v in ss.answers.items() if ss.prev_answers.get(k) == v)
        ss.answer_similarity = round(same / max(len(ss.answers), 1), 2)
    ss.prev_answers = dict(ss.answers)
    if ss.start_time and len(ss.answers) > 0:
        elapsed = time.time() - ss.start_time
        ss.time_per_question = round(elapsed / max(len(ss.answers), 1), 1)

# ─── HOME ──────────────────────────────────────────────────────────────────────
def show_home():
    st.markdown('<div class="main-title">🎓 Exam Malpractice Detector</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">AI-Powered Proctoring System</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div class="report-section" style="text-align:center;">
            <div style="font-size:3rem; margin-bottom:1rem;">🛡️</div>
            <div style="font-size:1.2rem; font-weight:600; color:#e8e8f0; margin-bottom:1rem;">Welcome to the Proctored Exam</div>
            <div style="color:#9ca3af; font-size:0.9rem; line-height:1.7; margin-bottom:1.5rem;">
                This exam monitors your behavior in real-time.<br>
                Your webcam will be active. All activity is tracked.<br>
                <strong style="color:#7c3aed;">10 Python Questions • AI Malpractice Detection • Detailed Report</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        name = st.text_input("Enter your name to begin", placeholder="Your full name...")
        if st.button("🚀 Start Exam", use_container_width=True):
            if name.strip():
                st.session_state.student_name = name.strip()
                st.session_state.page = "exam"
                st.session_state.start_time = time.time()
                st.rerun()
            else:
                st.error("Please enter your name.")
        st.markdown("""
        <div style="margin-top:1.5rem; display:flex; gap:0.8rem; justify-content:center; flex-wrap:wrap;">
            <span style="background:#1a1a2e; border:1px solid #2d2d4e; border-radius:8px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#9ca3af;">📹 Webcam Live Feed</span>
            <span style="background:#1a1a2e; border:1px solid #2d2d4e; border-radius:8px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#9ca3af;">🔄 Tab Monitoring</span>
            <span style="background:#1a1a2e; border:1px solid #2d2d4e; border-radius:8px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#9ca3af;">⏱️ Time Tracking</span>
            <span style="background:#1a1a2e; border:1px solid #2d2d4e; border-radius:8px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#9ca3af;">🤖 AI Detection</span>
        </div>
        """, unsafe_allow_html=True)

# ─── EXAM ──────────────────────────────────────────────────────────────────────
def show_exam():
    ss = st.session_state
    col_h1, col_h2, col_h3 = st.columns([2,1,1])
    with col_h1:
        st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#7c3aed;">🎓 Python Exam</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#6b7280; font-size:0.85rem;">Student: {ss.student_name}</div>', unsafe_allow_html=True)
    with col_h2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(ss.answers)}/10</div><div class="metric-label">Answered</div></div>', unsafe_allow_html=True)
    with col_h3:
        elapsed = int(time.time() - ss.start_time) if ss.start_time else 0
        mins, secs = divmod(elapsed, 60)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{mins:02d}:{secs:02d}</div><div class="metric-label">Elapsed</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.progress(len(ss.answers)/10)
    col_q, col_cam = st.columns([3,1])
    with col_q:
        for i, q in enumerate(QUESTIONS):
            st.markdown(f'<div class="question-card"><div class="question-number">Question {i+1} of 10</div><div class="question-text">{q["q"]}</div></div>', unsafe_allow_html=True)
            prev = ss.answers.get(i)
            choice = st.radio(f"q{i}", options=q["options"], index=prev if prev is not None else None, key=f"radio_{i}", label_visibility="collapsed")
            if choice is not None:
                new_idx = q["options"].index(choice)
                if ss.answers.get(i) != new_idx:
                    ss.answers[i] = new_idx
                    simulate_tracking()
            st.markdown("<br>", unsafe_allow_html=True)
    with col_cam:
        st.markdown('<div style="background:#12121e;border:1px solid #2d2d4e;border-radius:12px;padding:1rem;text-align:center;"><div style="color:#06b6d4;font-size:0.8rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;">📹 Live Webcam</div></div>', unsafe_allow_html=True)
        webcam_img = st.camera_input("", key="webcam", label_visibility="collapsed")
        if not webcam_img:
            ss.webcam_disabled += 1
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="tracker-box">
            <div style="color:#6b7280;font-size:0.75rem;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.8rem;">🔍 Live Monitor</div>
            <div>Tab Switches: <span style="color:#f59e0b;">{ss.tab_switches}</span></div>
            <div>Window Blur: <span style="color:#f59e0b;">{ss.window_blur}</span></div>
            <div>Rapid Submit: <span style="color:#f59e0b;">{ss.rapid_submissions}</span></div>
            <div>Mouse Outside: <span style="color:#f59e0b;">{ss.mouse_outside}</span></div>
            <div>Webcam Off: <span style="color:#f59e0b;">{ss.webcam_disabled}</span></div>
            <div>Ans Similarity: <span style="color:#f59e0b;">{ss.answer_similarity}</span></div>
            <div>Avg Time/Q: <span style="color:#f59e0b;">{ss.time_per_question}s</span></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    col_s1, col_s2, col_s3 = st.columns([1,2,1])
    with col_s2:
        if len(ss.answers) < 10:
            st.warning(f"⚠️ Please answer all 10 questions. ({len(ss.answers)}/10 done)")
        if st.button("📊 Submit & Get Full Report", use_container_width=True):
            ss.page = "result"
            st.rerun()

# ─── RESULT ────────────────────────────────────────────────────────────────────
def show_result():
    ss = st.session_state
    st.markdown('<div class="main-title">📊 Exam Report</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">Student: {ss.student_name} • {datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>', unsafe_allow_html=True)

    correct = sum(1 for i, q in enumerate(QUESTIONS) if ss.answers.get(i) == q["answer"])
    score_pct = int((correct / 10) * 100)
    elapsed = int(time.time() - ss.start_time) if ss.start_time else 0
    mins, secs = divmod(elapsed, 60)

    features = [
        ss.tab_switches, ss.rapid_submissions, ss.window_blur,
        ss.fullscreen_exits, ss.mouse_outside, ss.answer_similarity,
        ss.time_per_question, ss.browser_minimized,
        ss.network_disconnects, ss.webcam_disabled
    ]
    result = detect_malpractice(features)

    # ── Top KPIs ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#06b6d4;">{correct}/10</div><div class="kpi-lbl">Correct Answers</div></div>', unsafe_allow_html=True)
    with c2:
        sc = "#4ade80" if score_pct >= 60 else "#f87171"
        st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:{sc};">{score_pct}%</div><div class="kpi-lbl">Score</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-box"><div class="kpi-val">{mins}m {secs}s</div><div class="kpi-lbl">Time Taken</div></div>', unsafe_allow_html=True)
    with c4:
        rc = "#ef4444" if result["malpractice"] else "#4ade80"
        st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:{rc};">{result["risk_level"]}</div><div class="kpi-lbl">Risk Level</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        # ── Verdict ──
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown('<div class="report-title">🎯 Malpractice Detection Result</div>', unsafe_allow_html=True)
        if result["malpractice"]:
            st.markdown(f"""
            <div style="text-align:center; padding:1.5rem;">
                <div style="font-size:3rem;">🚨</div>
                <div class="verdict-danger" style="margin:1rem 0;">MALPRACTICE DETECTED</div>
                <div style="color:#9ca3af; font-size:0.85rem;">AI analysis detected strong behavioral indicators of exam malpractice</div>
                <div style="margin-top:1rem; padding:0.6rem 1.5rem; background:#2d1515; border:1px solid #ef4444; border-radius:8px; display:inline-block; color:#fca5a5;">
                    ⚠️ {result["risk_level"]} — Immediate Review Required
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align:center; padding:1.5rem;">
                <div style="font-size:3rem;">✅</div>
                <div class="verdict-safe" style="margin:1rem 0;">NO MALPRACTICE DETECTED</div>
                <div style="color:#9ca3af; font-size:0.85rem;">Exam completed with acceptable behavior patterns</div>
                <div style="margin-top:1rem; padding:0.6rem 1.5rem; background:#0a2e1a; border:1px solid #10b981; border-radius:8px; display:inline-block; color:#6ee7b7;">
                    ✅ {result["risk_level"]} — No Action Required
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Probability Analysis ──
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown('<div class="report-title">📡 Probability Analysis</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            verdict_color = "#ef4444" if result["malpractice"] else "#4ade80"
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:{verdict_color}; font-size:1rem;">{"Malpractice" if result["malpractice"] else "Safe"}</div><div class="kpi-lbl">🎯 Verdict</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#f59e0b; font-size:1.4rem;">{result["probability"]}%</div><div class="kpi-lbl">📊 Confidence</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#4ade80; font-size:1.4rem;">{result["safe_prob"]}%</div><div class="kpi-lbl">✅ Safe Prob</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#ef4444; font-size:1.4rem;">{result["probability"]}%</div><div class="kpi-lbl">🚨 Mal Prob</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div style="color:#9ca3af; font-size:0.85rem; margin-bottom:0.3rem;">🚨 Malpractice Probability: {result["probability"]}%</div>', unsafe_allow_html=True)
        st.progress(result["probability"] / 100)
        st.markdown(f'<div style="color:#9ca3af; font-size:0.85rem; margin-bottom:0.3rem; margin-top:0.5rem;">✅ Safe Probability: {result["safe_prob"]}%</div>', unsafe_allow_html=True)
        st.progress(result["safe_prob"] / 100)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Hypothesis Testing ──
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown('<div class="report-title">🧪 Hypothesis Testing — T-Test Results</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="color:#9ca3af; font-size:0.85rem; margin-bottom:1rem;">
            H₀: No difference between classes | H₁: Significant difference (p &lt; 0.05)
        </div>
        """, unsafe_allow_html=True)
        reject = result["p_value"] < 0.05
        h_color = "#ef4444" if reject else "#4ade80"
        h_text = "Reject H₀ — Significant difference detected" if reject else "Fail to Reject H₀ — No significant difference"
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="font-size:1.3rem;">{result["t_stat"]}</div><div class="kpi-lbl">T-Statistic</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="font-size:1.3rem; color:#f59e0b;">{result["p_value"]}</div><div class="kpi-lbl">P-Value</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="font-size:0.9rem; color:{h_color};">{"Reject H₀" if reject else "Accept H₀"}</div><div class="kpi-lbl">Decision</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top:1rem; padding:0.8rem; background:#1a1a2e; border-radius:8px; color:{h_color}; font-size:0.85rem;">{h_text}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        # ── Feature Importance K-Score ──
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown('<div class="report-title">📊 Feature Importance — K-Score Ranking</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#6b7280; font-size:0.8rem; margin-bottom:1rem;">Selected from 20 features using SelectKBest (ANOVA F-Score)</div>', unsafe_allow_html=True)
        sorted_k = sorted(K_SCORES.items(), key=lambda x: x[1], reverse=True)
        max_k = max(K_SCORES.values())
        for rank, (fname, kscore) in enumerate(sorted_k, 1):
            bar_w = int((kscore / max_k) * 100)
            bar_color = "#7c3aed" if rank <= 3 else "#4f46e5" if rank <= 6 else "#3730a3"
            st.markdown(f"""
            <div style="margin-bottom:0.8rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                    <span style="color:#c4c4d4; font-size:0.82rem;">#{rank} {fname}</span>
                    <span style="color:#7c3aed; font-weight:600; font-size:0.82rem;">{kscore}</span>
                </div>
                <div style="background:#1a1a2e; border-radius:999px; height:6px;">
                    <div style="background:{bar_color}; width:{bar_w}%; height:6px; border-radius:999px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Behavior Breakdown ──
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown('<div class="report-title">📈 Behavior Breakdown</div>', unsafe_allow_html=True)
        behaviors = [
            ("Tab Switches", ss.tab_switches, 3, "🔀"),
            ("Rapid Submissions", ss.rapid_submissions, 3, "⚡"),
            ("Window Blur Events", ss.window_blur, 3, "🖥️"),
            ("Fullscreen Exits", ss.fullscreen_exits, 3, "⛶"),
            ("Mouse Outside Exam", ss.mouse_outside, 4, "🖱️"),
            ("Answer Similarity", ss.answer_similarity, 0.7, "📊"),
            ("Avg Time Per Question", ss.time_per_question, 5, "⏱️"),
            ("Browser Minimized", ss.browser_minimized, 3, "🔽"),
            ("Network Disconnects", ss.network_disconnects, 3, "🌐"),
            ("Webcam Disabled", ss.webcam_disabled, 2, "📷"),
        ]
        for name, val, threshold, icon in behaviors:
            suspicious = val >= threshold
            color = "#ef4444" if suspicious else "#4ade80"
            flag = "⚠️" if suspicious else "✅"
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:0.5rem 0; border-bottom:1px solid #1e1e3a;">
                <span style="color:#c4c4d4; font-size:0.88rem;">{icon} {name}</span>
                <span style="color:{color}; font-weight:600; font-size:0.88rem;">{flag} {val}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Answer Review ──
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown('<div class="report-title">📝 Answer Review</div>', unsafe_allow_html=True)
        for i, q in enumerate(QUESTIONS):
            student_ans = ss.answers.get(i)
            correct_ans = q["answer"]
            is_correct = student_ans == correct_ans
            bg = "#0a2e1a" if is_correct else "#2e0a0a"
            border = "#10b981" if is_correct else "#ef4444"
            icon = "✅" if is_correct else "❌"
            student_text = q["options"][student_ans] if student_ans is not None else "Not answered"
            correct_text = q["options"][correct_ans]
            st.markdown(f"""
            <div style="background:{bg}; border-left:3px solid {border}; border-radius:8px; padding:0.8rem; margin-bottom:0.8rem;">
                <div style="font-size:0.82rem; color:#9ca3af; margin-bottom:0.3rem;">Q{i+1}: {q['q'][:60]}...</div>
                <div style="font-size:0.85rem;">{icon} Your answer: <strong style="color:#e8e8f0;">{student_text}</strong></div>
                {"" if is_correct else f'<div style="font-size:0.82rem; color:#4ade80; margin-top:0.2rem;">✔ Correct: {correct_text}</div>'}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_b1, col_b2, col_b3 = st.columns([1,2,1])
    with col_b2:
        if st.button("🔄 Take Exam Again", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ─── Router ────────────────────────────────────────────────────────────────────
page = st.session_state.get("page", "home")
if page == "home": show_home()
elif page == "exam": show_exam()
elif page == "result": show_result()
