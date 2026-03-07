"""Nomophobia (NMP-Q) screening app — Streamlit + Plotly

Deploy-ready for Streamlit Community Cloud:
- entry file name: streamlit_app.py (recommended by Streamlit)
- uses st.session_state for paging (5 questions per page) + results view
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import streamlit as st
import plotly.graph_objects as go


QUESTIONS: List[str] = [
    "1. I would feel uncomfortable without constant access to information through my smartphone.",
    "2. I would be annoyed if I could not look information up on my smartphone when I wanted to do so.",
    "3. Being unable to get the news (e.g., happenings, weather, etc.) on my smartphone would make me nervous.",
    "4. I would be annoyed if I could not use my smartphone and/or its capabilities when I wanted to do so.",
    "5. Running out of battery in my smartphone would scare me.",
    "6. If I were to run out of credits or hit my monthly data limit, I would panic.",
    "7. If I did not have a data signal or could not connect to Wi-Fi, then I would constantly check to see if I had a signal or could find a Wi-Fi network.",
    "8. If I could not use my smartphone, I would be afraid of getting stranded somewhere.",
    "9. If I could not check my smartphone for a while, I would feel a desire to check it.",
    "10. If I did not have my smartphone with me, I would feel anxious because I could not instantly communicate with my family and/or friends.",
    "11. If I did not have my smartphone with me, I would be worried because my family and/or friends could not reach me.",
    "12. If I did not have my smartphone with me, I would feel nervous because I would not be able to receive text messages and calls.",
    "13. If I did not have my smartphone with me, I would be anxious because I could not keep in touch with my family and/or friends.",
    "14. If I did not have my smartphone with me, I would be nervous because I could not know if someone had tried to get a hold of me.",
    "15. If I did not have my smartphone with me, I would feel anxious because my constant connection to my family and friends would be broken.",
    "16. If I did not have my smartphone with me, I would be nervous because I would be disconnected from my online identity.",
    "17. If I did not have my smartphone with me, I would be uncomfortable because I could not stay up-to-date with social media and online networks.",
    "18. If I did not have my smartphone with me, I would feel awkward because I could not check my notifications for updates from my connections and online networks.",
    "19. If I did not have my smartphone with me, I would feel anxious because I could not check my email messages.",
    "20. If I did not have my smartphone with me, I would feel weird because I would not know what to do."
]

LIKERT = [
    (1, "1 (Strongly disagree)"),
    (2, "2"),
    (3, "3"),
    (4, "4 (Neutral)"),
    (5, "5"),
    (6, "6"),
    (7, "7 (Strongly agree)"),
]

SUBSCALES = {
    "Not being able to access information (1–4)": [1, 2, 3, 4],
    "Giving up convenience (5–9)": [5, 6, 7, 8, 9],
    "Not being able to communicate (10–15)": [10, 11, 12, 13, 14, 15],
    "Losing connectedness (16–20)": [16, 17, 18, 19, 20],
}

PAPER_LINK = "https://www.sciencedirect.com/science/article/pii/S0747563215001806"


@dataclass(frozen=True)
class Severity:
    label: str
    color: str
    description: str
    recs: List[str]


SEVERITIES = {
    "Absent": Severity(
        label="Absent",
        color="#2e7d32",
        description="Your score suggests minimal nomophobia-related distress.",
        recs=[
            "Keep your current healthy smartphone habits.",
            "Continue balancing online time with sleep, exercise, and in‑person connection.",
            "Consider occasional 'screen-free' moments to protect focus and wellbeing.",
        ],
    ),
    "Mild": Severity(
        label="Mild",
        color="#f9a825",
        description="Your score suggests mild nomophobia-related discomfort in some situations.",
        recs=[
            "Try short, planned phone-free intervals (e.g., 15–30 minutes).",
            "Disable non-essential notifications and keep only high-priority alerts.",
            "Set 'check-in' times instead of frequent, automatic checking.",
        ],
    ),
    "Moderate": Severity(
        label="Moderate",
        color="#ef6c00",
        description="Your score suggests moderate nomophobia-related distress that may affect daily life.",
        recs=[
            "Use app timers / Focus or Do Not Disturb modes during study/work blocks.",
            "Create a 'charging routine' (battery anxiety is common): charge before leaving and carry a small power bank if needed.",
            "Replace habitual checking with a brief alternative (walk, breathing, stretching).",
            "Track triggers (boredom, stress, loneliness) and plan healthier responses.",
        ],
    ),
    "Severe": Severity(
        label="Severe",
        color="#c62828",
        description="Your score suggests severe nomophobia-related distress. Consider extra support.",
        recs=[
            "If this is causing significant anxiety or impairment, consider speaking with a mental health professional.",
            "Build a gradual reduction plan: start with small, consistent phone-free routines and increase weekly.",
            "Create 'phone-free zones' (bedroom, meals, study desk) and keep the phone out of reach.",
            "If safety is a worry, set up alternatives (printed directions, emergency contacts, agreed check-in times).",
        ],
    ),
}


def classify(total: int) -> str:
    # Common NMP-Q cutoffs:
    # 20 = Absent; 21–59 Mild; 60–99 Moderate; 100–140 Severe
    if total <= 20:
        return "Absent"
    if total < 60:
        return "Mild"
    if total < 100:
        return "Moderate"
    return "Severe"


def total_score(ans: Dict[int, int]) -> int:
    return sum(int(ans.get(i, 0) or 0) for i in range(1, 21))


def subscale_scores(ans: Dict[int, int]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for name, items in SUBSCALES.items():
        out[name] = sum(int(ans.get(i, 0) or 0) for i in items)
    return out


def gauge(total: int, color: str) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=total,
            number={"suffix": " / 140"},
            title={"text": "NMP-Q Total Score"},
            gauge={
                "axis": {"range": [20, 140]},
                "bar": {"color": color},
                "steps": [
                    {"range": [20, 59], "color": "rgba(249,168,37,0.20)"},
                    {"range": [60, 99], "color": "rgba(239,108,0,0.20)"},
                    {"range": [100, 140], "color": "rgba(198,40,40,0.18)"},
                ],
                "threshold": {
                    "line": {"color": color, "width": 4},
                    "thickness": 0.75,
                    "value": total,
                },
            },
        )
    )
    fig.update_layout(margin=dict(l=20, r=20, t=45, b=20), height=280)
    return fig


def subscale_bar(subscores: Dict[str, int]) -> go.Figure:
    names = list(subscores.keys())
    values = [subscores[k] for k in names]
    fig = go.Figure(go.Bar(x=names, y=values))
    fig.update_layout(
        title="Subscale scores (higher = more discomfort)",
        xaxis_title="Dimension",
        yaxis_title="Score",
        margin=dict(l=20, r=20, t=50, b=20),
        height=320,
    )
    fig.update_xaxes(tickangle=15)
    return fig


def inject_css() -> None:
    st.markdown(
        """
        <style>
          :root{
            --bg1:#0b1020; --bg2:#0d1b2a;
            --card: rgba(255,255,255,0.08);
            --card2: rgba(255,255,255,0.10);
            --border: rgba(255,255,255,0.18);
            --text: rgba(255,255,255,0.92);
            --muted: rgba(255,255,255,0.72);
            --shadow: 0 18px 50px rgba(0,0,0,0.35);
            --radius: 18px;
          }
          .stApp{
            background:
              radial-gradient(1200px 600px at 20% 10%, rgba(120, 90, 255, 0.30), transparent 60%),
              radial-gradient(900px 500px at 85% 20%, rgba(0, 190, 255, 0.22), transparent 65%),
              radial-gradient(1000px 700px at 50% 90%, rgba(255, 120, 120, 0.16), transparent 60%),
              linear-gradient(180deg, var(--bg1), var(--bg2));
          }
          h1,h2,h3,p,li,div,span,label{ color: var(--text) !important; }
          a{ color: rgba(160, 220, 255, 0.95) !important; }
          .card{
            border: 1px solid var(--border);
            background: linear-gradient(180deg, var(--card), rgba(255,255,255,0.04));
            box-shadow: var(--shadow);
            border-radius: var(--radius);
            padding: 18px 18px 14px;
            backdrop-filter: blur(10px);
            margin-bottom: 14px;
          }
          .qcard{
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 14px;
            margin-bottom: 14px;
          }
          .muted{ color: var(--muted) !important; font-weight: 600; }
          \.pill{
            display:inline-block;
            border: 1px solid rgba(255,255,255,0.18);
            background: rgba(255,255,255,0.08);
            border-radius: 999px;
            padding: 7px 12px;
            font-weight: 800;
            margin-right: 8px;
            margin-bottom: 8px;
          }

          /* FIX BUTTON VISIBILITY */
          div.stButton > button {
            background: linear-gradient(90deg, #7c5cff, #00bfff) !important;
            color: white !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 0.6rem 1rem !important;
          }

          div.stButton > button:hover {
            background: linear-gradient(90deg, #6848e0, #0099cc) !important;
            color: white !important;
          }

          div.stButton > button:disabled {
            background: rgba(255,255,255,0.2) !important;
            color: rgba(255,255,255,0.6) !important;
          }

          .progress{
            height: 10px;
            border-radius: 999px;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.12);
            overflow:hidden;
            margin: 10px 0 6px;
          }
          .progress > div{
            height: 100%;
            background: linear-gradient(90deg, rgba(120, 90, 255, 0.85), rgba(0, 190, 255, 0.85));
            border-radius: 999px;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    st.session_state.setdefault("page", 1)
    st.session_state.setdefault("answers", {})  # {1..20: 1..7}
    st.session_state.setdefault("view", "survey")  # 'survey' or 'results'


def page_complete(page: int, answers: Dict[int, int]) -> bool:
    start = (page - 1) * 5 + 1
    end = min(page * 5, 20)
    return all(answers.get(i) is not None for i in range(start, end + 1))


def all_complete(answers: Dict[int, int]) -> bool:
    return all(answers.get(i) is not None for i in range(1, 21))


def render_header() -> None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("Nomophobia Screening Tool (NMP-Q)")
    st.markdown("**Made by: Alia Al‑Qadri**")
    st.markdown(
        """
        **Nomophobia** refers to anxiety or discomfort related to not having access to a mobile phone or its services.  
        This app is a **screening tool** to help estimate severity of nomophobia-related feelings; it is **not a diagnostic test**.
        """
    )
    st.markdown(
        f"Validated based on: Yildirim, C., & Correia, A. P. (2015). *Computers in Human Behavior*, 49, 130–137.  \nPaper link: {PAPER_LINK}"
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_progress(page: int, num_pages: int) -> None:
    pct = int((page / num_pages) * 100)
    st.markdown(
        f"""<div class="progress"><div style="width:{pct}%"></div></div>
        <div class="muted">Page {page} of {num_pages}</div>
        """,
        unsafe_allow_html=True,
    )


def render_survey() -> None:
    num_pages = 4
    page = int(st.session_state.page)
    answers: Dict[int, int] = st.session_state.answers

    start = (page - 1) * 5 + 1
    end = min(page * 5, 20)

    page = int(st.session_state.page)
    answers: Dict[int, int] = st.session_state.answers

    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_progress(page, num_pages)

    start = (page - 1) * 5 + 1
    end = min(page * 5, 20)

    values = [v for v, _ in LIKERT]
value_to_label = {v: lbl for v, lbl in LIKERT}

for i in range(start, end + 1):
    st.markdown('<div class="qcard">', unsafe_allow_html=True)
    st.markdown(f"**{QUESTIONS[i-1]}**")

    default = answers.get(i)
    idx = (values.index(default) if default in values else None)

    chosen = st.radio(
        label=f"q{i}",
        options=values,
        index=idx,
        format_func=lambda v: value_to_label.get(v, str(v)),
        label_visibility="collapsed",
        key=f"radio_{i}",
    )

    # Streamlit radios normally always select a value, but keep this safe:
    answers[i] = int(chosen) if chosen is not None else None
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.answers = answers

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        back = st.button("Back", disabled=(page == 1), use_container_width=True)
    with col2:
        next_ = st.button("Next", disabled=(page == num_pages), use_container_width=True)
    with col3:
        submit = st.button("Submit", disabled=(page != num_pages), use_container_width=True)

    if back:
        st.session_state.page = max(1, page - 1)
        st.rerun()

    if next_:
        if not page_complete(page, answers):
            st.warning("Please answer all questions on this page before continuing.")
        else:
            st.session_state.page = min(num_pages, page + 1)
            st.rerun()

    if submit:
        if not page_complete(page, answers) or not all_complete(answers):
            st.warning("Please make sure all 20 questions are answered before submitting.")
        else:
            st.session_state.view = "results"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_results() -> None:
    answers: Dict[int, int] = st.session_state.answers
    total = total_score(answers)
    level = classify(total)
    sev = SEVERITIES[level]
    subs = subscale_scores(answers)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Your Results")
    st.markdown(
        f'<span class="pill" style="border-color:{sev.color}; color:{sev.color};">Nomophobia level: <b>{level}</b></span>'
        f'<span class="pill">Total points: <b>{total}</b></span>',
        unsafe_allow_html=True,
    )
    st.write(sev.description)
    st.markdown("### Recommendations")
    for r in sev.recs:
        st.markdown(f"- {r}")
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(gauge(total, sev.color), use_container_width=True)
    with c2:
        st.plotly_chart(subscale_bar(subs), use_container_width=True)

    c3, c4 = st.columns([1, 1])
    with c3:
        if st.button("Edit answers", use_container_width=True):
            st.session_state.view = "survey"
            st.session_state.page = 1
            st.rerun()
    with c4:
        if st.button("Start over", use_container_width=True):
            st.session_state.view = "survey"
            st.session_state.page = 1
            st.session_state.answers = {}
            for i in range(1, 21):
                st.session_state.pop(f"radio_{i}", None)
            st.rerun()

    st.caption("Reminder: This tool screens for nomophobia-related feelings; it does not diagnose a mental health condition.")


def main() -> None:
    st.set_page_config(page_title="Nomophobia Screening (NMP-Q)", page_icon="📱", layout="centered")
    inject_css()
    init_state()
    render_header()

    if st.session_state.view == "results":
        render_results()
    else:
        render_survey()


if __name__ == "__main__":
    main()
