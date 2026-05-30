import streamlit as st
import time
import random
import numpy as np
import pickle
import os
from datetime import datetime

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

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

.main-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.2rem;
}
.sub-title {
    text-align: center;
    color: #6b7280;
    font-size: 0.95rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Question Card */
.question-card {
    background: linear-gradient(135deg, #12121e, #1a1a2e);
    border: 1px solid #2d2d4e;
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(124,58,237,0.08);
}
.question-number {
    color: #7c3aed;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.question-text {
    font-size: 1.05rem;
    color: #e8e8f0;
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* Status Badge */
.status-safe {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border: 1px solid #10b981;
    color: #6ee7b7;
    padding: 0.4rem 1rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}
.status-danger {
    background: linear-gradient(135deg, #7f1d1d, #991b1b);
    border: 1px solid #ef4444;
    color: #fca5a5;
    padding: 0.4rem 1rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}

/* Metric Card */
.metric-card {
    background: #12121e;
    border: 1px solid #2d2d4e;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #7c3aed;
}
.metric-label {
    font-size: 0.78rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Progress bar */
.stProgress > div > div { background: linear-gradient(90deg, #7c3aed, #06b6d4); border-radius: 999px; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
    font-size: 1rem !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(124,58,237,0.4) !important;
}

/* Radio buttons */
.stRadio > div { gap: 0.5rem; }
.stRadio label { color: #c4c4d4 !important; }

/* Webcam section */
.webcam-box {
    background: #12121e;
    border: 1px solid #2d2d4e;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.webcam-title {
    color: #06b6d4;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* Tracker box */
.tracker-box {
    background: #0d0d1a;
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    padding: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #4ade80;
}
.tracker-title {
    color: #6b7280;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

/* Report card */
.report-section {
    background: #12121e;
    border: 1px solid #2d2d4e;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
}
.report-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #7c3aed;
    margin-bottom: 1rem;
    border-bottom: 1px solid #2d2d4e;
    padding-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Python MCQ Questions ──────────────────────────────────────────────────────
QUESTIONS = [
    {
        "q": "What is the output of: `print(type([]))`?",
        "options": ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'dict'>"],
        "answer": 0
    },
    {
        "q": "Which keyword is used to define a function in Python?",
        "options": ["func", "define", "def", "function"],
        "answer": 2
    },
    {
        "q": "What does `len('hello')` return?",
        "options": ["4", "5", "6", "Error"],
        "answer": 1
    },
    {
        "q": "What is the correct way to create a dictionary in Python?",
        "options": ["d = []", "d = ()", "d = {}", "d = <{}>"],
        "answer": 2
    },
    {
        "q": "Which of these is used for single-line comments in Python?",
        "options": ["//", "/*", "#", "--"],
        "answer": 2
    },
    {
        "q": "What will `print(2 ** 3)` output?",
        "options": ["6", "8", "9", "5"],
        "answer": 1
    },
    {
        "q": "Which method adds an element to the end of a list?",
        "options": ["add()", "insert()", "append()", "push()"],
        "answer": 2
    },
    {
        "q": "What is the output of `print(10 % 3)`?",
        "options": ["3", "1", "0", "2"],
        "answer": 1
    },
    {
        "q": "Which of the following is an immutable data type in Python?",
        "options": ["list", "dict", "set", "tuple"],
        "answer": 3
    },
    {
        "q": "What does `range(5)` produce?",
        "options": ["[1,2,3,4,5]", "[0,1,2,3,4]", "[0,1,2,3,4,5]", "[1,2,3,4]"],
        "answer": 1
    }
]

# ─── Session State Init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "home",           # home | exam | result
        "answers": {},
        "start_time": None,
        "tab_switches": 0,
        "rapid_submissions": 0,
        "window_blur": 0,
        "fullscreen_exits": 0,
        "mouse_outside": 0,
        "answer_similarity": 0.0,
        "copy_paste_count": 0,
        "browser_minimized": 0,
        "network_disconnects": 0,
        "webcam_disabled": 0,
        "last_answer_time": None,
        "prev_answers": {},
        "submitted": False,
        "student_name": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── Malpractice Detection Logic ───────────────────────────────────────────────
def detect_malpractice(features):
    """
    Simple rule-based detection if no model is available.
    Replace with your actual model prediction here.
    """
    tab_switches, rapid_submissions, window_blur, fullscreen_exits, \
    mouse_outside, answer_similarity, copy_paste_count, \
    browser_minimized, network_disconnects, webcam_disabled = features

    score = 0
    if tab_switches >= 3: score += 2
    if rapid_submissions >= 3: score += 2
    if window_blur >= 3: score += 1
    if fullscreen_exits >= 3: score += 1
    if mouse_outside >= 4: score += 1
    if answer_similarity >= 0.7: score += 3
    if copy_paste_count >= 3: score += 2
    if browser_minimized >= 3: score += 1
    if network_disconnects >= 3: score += 1
    if webcam_disabled >= 2: score += 2

    return 1 if score >= 5 else 0, score

def simulate_behavior_tracking():
    """Simulate some automatic behavior detection during exam"""
    ss = st.session_state
    
    # Simulate random minor events (in real app, these come from JS)
    if ss.start_time and random.random() < 0.15:
        ss.window_blur += 1
    if ss.start_time and random.random() < 0.08:
        ss.tab_switches += 1
    if ss.start_time and random.random() < 0.05:
        ss.mouse_outside += 1

    # Detect rapid submissions
    now = time.time()
    if ss.last_answer_time:
        if now - ss.last_answer_time < 3:
            ss.rapid_submissions += 1
    ss.last_answer_time = now

    # Detect answer similarity (if many answers same as previous)
    if len(ss.answers) > 3:
        same = sum(1 for k, v in ss.answers.items()
                   if ss.prev_answers.get(k) == v)
        ss.answer_similarity = round(same / max(len(ss.answers), 1), 2)

    ss.prev_answers = dict(ss.answers)

# ─── HOME PAGE ─────────────────────────────────────────────────────────────────
def show_home():
    st.markdown('<div class="main-title">🎓 Exam Malpractice Detector</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">AI-Powered Proctoring System</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="report-section" style="text-align:center;">
            <div style="font-size:3rem; margin-bottom:1rem;">🛡️</div>
            <div style="font-size:1.2rem; font-weight:600; color:#e8e8f0; margin-bottom:1rem;">
                Welcome to the Proctored Exam
            </div>
            <div style="color:#9ca3af; font-size:0.9rem; line-height:1.7; margin-bottom:1.5rem;">
                This exam monitors your behavior in real-time.<br>
                Your webcam will be active. All activity is tracked.<br>
                <strong style="color:#7c3aed;">10 Python Questions • No Time Limit • Detailed Report</strong>
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
                st.error("Please enter your name to proceed.")

        st.markdown("""
        <div style="margin-top:1.5rem; display:flex; gap:1rem; justify-content:center; flex-wrap:wrap;">
            <span style="background:#1a1a2e; border:1px solid #2d2d4e; border-radius:8px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#9ca3af;">📹 Webcam Live Feed</span>
            <span style="background:#1a1a2e; border:1px solid #2d2d4e; border-radius:8px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#9ca3af;">🖱️ Mouse Tracking</span>
            <span style="background:#1a1a2e; border:1px solid #2d2d4e; border-radius:8px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#9ca3af;">📋 Paste Detection</span>
            <span style="background:#1a1a2e; border:1px solid #2d2d4e; border-radius:8px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#9ca3af;">🔄 Tab Monitoring</span>
        </div>
        """, unsafe_allow_html=True)

# ─── EXAM PAGE ──────────────────────────────────────────────────────────────────
def show_exam():
    ss = st.session_state

    # Header
    col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
    with col_h1:
        st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#7c3aed;">🎓 Python Exam</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#6b7280; font-size:0.85rem;">Student: {ss.student_name}</div>', unsafe_allow_html=True)
    with col_h2:
        answered = len(ss.answers)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{answered}/10</div><div class="metric-label">Answered</div></div>', unsafe_allow_html=True)
    with col_h3:
        elapsed = int(time.time() - ss.start_time) if ss.start_time else 0
        mins, secs = divmod(elapsed, 60)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{mins:02d}:{secs:02d}</div><div class="metric-label">Elapsed</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Progress
    progress = len(ss.answers) / 10
    st.progress(progress)
    st.markdown(f'<div style="color:#6b7280; font-size:0.8rem; margin-bottom:1rem;">{int(progress*100)}% Complete</div>', unsafe_allow_html=True)

    # Two column layout: Questions | Webcam + Tracker
    col_q, col_cam = st.columns([3, 1])

    with col_q:
        for i, q in enumerate(QUESTIONS):
            with st.container():
                st.markdown(f"""
                <div class="question-card">
                    <div class="question-number">Question {i+1} of 10</div>
                    <div class="question-text">{q['q']}</div>
                </div>
                """, unsafe_allow_html=True)

                prev = ss.answers.get(i)
                choice = st.radio(
                    f"q{i}",
                    options=q["options"],
                    index=prev if prev is not None else None,
                    key=f"radio_{i}",
                    label_visibility="collapsed"
                )
                if choice is not None:
                    new_idx = q["options"].index(choice)
                    if ss.answers.get(i) != new_idx:
                        ss.answers[i] = new_idx
                        simulate_behavior_tracking()

                st.markdown("<br>", unsafe_allow_html=True)

    with col_cam:
        # Webcam
        st.markdown('<div class="webcam-box"><div class="webcam-title">📹 Live Webcam Feed</div></div>', unsafe_allow_html=True)
        webcam_img = st.camera_input("", key="webcam", label_visibility="collapsed")
        if not webcam_img:
            st.markdown('<div style="color:#6b7280; font-size:0.75rem; text-align:center; margin-top:0.5rem;">⚠️ Allow camera access</div>', unsafe_allow_html=True)
            ss.webcam_disabled += 1

        st.markdown("<br>", unsafe_allow_html=True)

        # Live tracker
        st.markdown(f"""
        <div class="tracker-box">
            <div class="tracker-title">🔍 Live Behavior Monitor</div>
            <div>Tab Switches: <span style="color:#f59e0b;">{ss.tab_switches}</span></div>
            <div>Window Blur: <span style="color:#f59e0b;">{ss.window_blur}</span></div>
            <div>Rapid Submit: <span style="color:#f59e0b;">{ss.rapid_submissions}</span></div>
            <div>Copy-Paste: <span style="color:#f59e0b;">{ss.copy_paste_count}</span></div>
            <div>Mouse Outside: <span style="color:#f59e0b;">{ss.mouse_outside}</span></div>
            <div>Webcam Off: <span style="color:#f59e0b;">{ss.webcam_disabled}</span></div>
            <div>Answer Sim: <span style="color:#f59e0b;">{ss.answer_similarity}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # JS to track tab switches and copy-paste
        st.components.v1.html("""
        <script>
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                fetch('/?tab_switch=1').catch(()=>{});
            }
        });
        document.addEventListener('copy', function() {
            fetch('/?copy=1').catch(()=>{});
        });
        document.addEventListener('paste', function() {
            fetch('/?paste=1').catch(()=>{});
        });
        </script>
        """, height=0)

    st.markdown("---")

    # Submit Button
    col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
    with col_s2:
        if len(ss.answers) < 10:
            st.warning(f"⚠️ You have answered {len(ss.answers)}/10 questions. Please answer all before submitting.")
        
        if st.button("📊 Submit & Get Report", use_container_width=True):
            ss.page = "result"
            ss.submitted = True
            st.rerun()

# ─── RESULT PAGE ───────────────────────────────────────────────────────────────
def show_result():
    ss = st.session_state

    st.markdown('<div class="main-title">📊 Exam Report</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">Student: {ss.student_name} • {datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>', unsafe_allow_html=True)

    # Calculate score
    correct = sum(1 for i, q in enumerate(QUESTIONS) if ss.answers.get(i) == q["answer"])
    total = 10
    score_pct = int((correct / total) * 100)

    # Run malpractice detection
    features = [
        ss.tab_switches, ss.rapid_submissions, ss.window_blur,
        ss.fullscreen_exits, ss.mouse_outside, ss.answer_similarity,
        ss.copy_paste_count, ss.browser_minimized,
        ss.network_disconnects, ss.webcam_disabled
    ]
    malpractice, risk_score = detect_malpractice(features)

    # ── Top Summary ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#06b6d4;">{correct}/{total}</div><div class="metric-label">Correct Answers</div></div>', unsafe_allow_html=True)
    with col2:
        color = "#4ade80" if score_pct >= 60 else "#f87171"
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color};">{score_pct}%</div><div class="metric-label">Score</div></div>', unsafe_allow_html=True)
    with col3:
        elapsed = int(time.time() - ss.start_time) if ss.start_time else 0
        mins, secs = divmod(elapsed, 60)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{mins}m {secs}s</div><div class="metric-label">Time Taken</div></div>', unsafe_allow_html=True)
    with col4:
        risk_color = "#ef4444" if malpractice else "#4ade80"
        risk_label = "HIGH RISK" if malpractice else "LOW RISK"
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{risk_color};">{risk_label}</div><div class="metric-label">Malpractice Risk</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        # Malpractice Verdict
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown('<div class="report-title">🔍 Malpractice Detection Result</div>', unsafe_allow_html=True)
        if malpractice:
            st.markdown("""
            <div style="text-align:center; padding:1.5rem;">
                <div style="font-size:3rem;">🚨</div>
                <div class="status-danger" style="font-size:1rem; padding:0.6rem 2rem; margin:1rem 0; display:inline-block;">
                    MALPRACTICE DETECTED
                </div>
                <div style="color:#fca5a5; font-size:0.9rem; margin-top:0.5rem;">
                    Suspicious behavior patterns were identified during this exam.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:1.5rem;">
                <div style="font-size:3rem;">✅</div>
                <div class="status-safe" style="font-size:1rem; padding:0.6rem 2rem; margin:1rem 0; display:inline-block;">
                    NO MALPRACTICE DETECTED
                </div>
                <div style="color:#6ee7b7; font-size:0.9rem; margin-top:0.5rem;">
                    Exam was completed with acceptable behavior patterns.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Risk score bar
        st.markdown(f'<div style="color:#9ca3af; font-size:0.85rem; margin-top:1rem;">Risk Score: {risk_score}/18</div>', unsafe_allow_html=True)
        st.progress(min(risk_score / 18, 1.0))
        st.markdown('</div>', unsafe_allow_html=True)

        # Behavior Breakdown
        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.markdown('<div class="report-title">📈 Behavior Breakdown</div>', unsafe_allow_html=True)
        
        behaviors = [
            ("Tab Switches", ss.tab_switches, 3, "🔀"),
            ("Rapid Submissions", ss.rapid_submissions, 3, "⚡"),
            ("Window Blur Events", ss.window_blur, 3, "🖥️"),
            ("Fullscreen Exits", ss.fullscreen_exits, 3, "⛶"),
            ("Mouse Outside Exam", ss.mouse_outside, 4, "🖱️"),
            ("Copy-Paste Count", ss.copy_paste_count, 3, "📋"),
            ("Browser Minimized", ss.browser_minimized, 3, "🔽"),
            ("Network Disconnects", ss.network_disconnects, 3, "🌐"),
            ("Webcam Disabled", ss.webcam_disabled, 2, "📷"),
            ("Answer Similarity", ss.answer_similarity, 0.7, "📊"),
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

    with col_right:
        # Answer Review
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
            <div style="background:{bg}; border-left:3px solid {border}; border-radius:8px;
                        padding:0.8rem; margin-bottom:0.8rem;">
                <div style="font-size:0.82rem; color:#9ca3af; margin-bottom:0.3rem;">Q{i+1}: {q['q'][:60]}...</div>
                <div style="font-size:0.85rem;">{icon} Your answer: <strong style="color:#e8e8f0;">{student_text}</strong></div>
                {"" if is_correct else f'<div style="font-size:0.82rem; color:#4ade80; margin-top:0.2rem;">✔ Correct: {correct_text}</div>'}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        if st.button("🔄 Take Exam Again", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ─── Router ────────────────────────────────────────────────────────────────────
page = st.session_state.get("page", "home")
if page == "home":
    show_home()
elif page == "exam":
    show_exam()
elif page == "result":
    show_result()
