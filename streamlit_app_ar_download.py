"""Nomophobia (NMP-Q) screening app — Streamlit + Plotly
Streamlit Community Cloud entry point: streamlit_app.py

Updates:
- Arabic/English UI toggle (including Arabic question wording)
- Download results (CSV + TXT; PDF if reportlab is installed)
- Scroll-to-top on navigation using streamlit-scroll-to-top
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import BytesIO, StringIO
from typing import Dict, List, Tuple
import csv

import plotly.graph_objects as go
import streamlit as st

# Scroll helper (add to requirements.txt: streamlit-scroll-to-top)
from streamlit_scroll_to_top import scroll_to_here


QUESTIONS_EN: List[str] = [
    "1. I would feel uncomfortable without constant access to information through my smartphone.",
    "2. I would be annoyed if I could not look information up on my smartphone when I wanted to do so.",
    "3. Being unable to get the news (e.g., happenings, weather, etc.) on my smartphone would make me nervous.",
    "4. I would be annoyed if I could not use my smartphone and/or its capabilities when I wanted to do so.",
    "5. Running out of battery in my smartphone would scare me.",
    "6. If I were to run out of credits or hit my monthly data limit, I would panic.",
    "7. If I did not have a data signal or could not connect to Wi‑Fi, then I would constantly check to see if I had a signal or could find a Wi‑Fi network.",
    "8. If I could not use my smartphone, I would be afraid of getting stranded somewhere.",
    "9. If I could not check my smartphone for a while, I would feel a desire to check it.",
    "10. If I did not have my smartphone with me, I would feel anxious because I could not instantly communicate with my family and/or friends.",
    "11. If I did not have my smartphone with me, I would be worried because my family and/or friends could not reach me.",
    "12. If I did not have my smartphone with me, I would feel nervous because I would not be able to receive text messages and calls.",
    "13. If I did not have my smartphone with me, I would be anxious because I could not keep in touch with my family and/or friends.",
    "14. If I did not have my smartphone with me, I would be nervous because I could not know if someone had tried to get a hold of me.",
    "15. If I did not have my smartphone with me, I would feel anxious because my constant connection to my family and friends would be broken.",
    "16. If I did not have my smartphone with me, I would be nervous because I would be disconnected from my online identity.",
    "17. If I did not have my smartphone with me, I would be uncomfortable because I could not stay up‑to‑date with social media and online networks.",
    "18. If I did not have my smartphone with me, I would feel awkward because I could not check my notifications for updates from my connections and online networks.",
    "19. If I did not have my smartphone with me, I would feel anxious because I could not check my email messages.",
    "20. If I did not have my smartphone with me, I would feel weird because I would not know what to do.",
]

# Original Arabic rendering for UI convenience (screening use)
QUESTIONS_AR: List[str] = [
    "1. سأشعر بعدم الارتياح إذا لم يكن لدي وصولٌ مستمر للمعلومات عبر هاتفي الذكي.",
    "2. سأشعر بالانزعاج إذا لم أستطع البحث عن المعلومات عبر هاتفي الذكي عندما أريد ذلك.",
    "3. عدم قدرتي على متابعة الأخبار (مثل الأحداث والطقس وغيرها) عبر هاتفي الذكي سيجعلني متوتراً.",
    "4. سأشعر بالانزعاج إذا لم أستطع استخدام هاتفي الذكي و/أو إمكاناته عندما أريد ذلك.",
    "5. نفاد بطارية هاتفي الذكي سيُخيفني.",
    "6. إذا نفدت رصيدي أو وصلت إلى حد باقة البيانات الشهرية فسأشعر بالهلع.",
    "7. إذا لم تكن لدي إشارة بيانات أو لم أستطع الاتصال بشبكة Wi‑Fi فسأتحقق باستمرار مما إذا كانت هناك إشارة أو شبكة متاحة.",
    "8. إذا لم أستطع استخدام هاتفي الذكي فسأخاف من أن أعلق في مكان ما دون مساعدة.",
    "9. إذا لم أستطع تفقد هاتفي الذكي لفترة فسأشعر برغبة قوية في تفقده.",
    "10. إذا لم يكن هاتفي الذكي معي فسأشعر بالقلق لأنني لن أتمكن من التواصل فوراً مع عائلتي و/أو أصدقائي.",
    "11. إذا لم يكن هاتفي الذكي معي فسأشعر بالقلق لأن عائلتي و/أو أصدقائي لن يتمكنوا من الوصول إليّ.",
    "12. إذا لم يكن هاتفي الذكي معي فسأشعر بالتوتر لأنني لن أتمكن من تلقي الرسائل النصية والمكالمات.",
    "13. إذا لم يكن هاتفي الذكي معي فسأشعر بالقلق لأنني لن أستطيع البقاء على تواصل مع عائلتي و/أو أصدقائي.",
    "14. إذا لم يكن هاتفي الذكي معي فسأشعر بالتوتر لأنني لن أعرف إن كان هناك من حاول التواصل معي.",
    "15. إذا لم يكن هاتفي الذكي معي فسأشعر بالقلق لأن اتصالي الدائم بعائلتي وأصدقائي سينقطع.",
    "16. إذا لم يكن هاتفي الذكي معي فسأشعر بالتوتر لأنني سأكون منفصلاً عن هويتي على الإنترنت.",
    "17. إذا لم يكن هاتفي الذكي معي فسأشعر بعدم الارتياح لأنني لن أستطيع متابعة شبكات التواصل الاجتماعي والمنصات عبر الإنترنت.",
    "18. إذا لم يكن هاتفي الذكي معي فسأشعر بالحرج لأنني لن أستطيع تفقد الإشعارات لمعرفة التحديثات من اتصالاتي وشبكات الإنترنت.",
    "19. إذا لم يكن هاتفي الذكي معي فسأشعر بالقلق لأنني لن أستطيع تفقد رسائل البريد الإلكتروني.",
    "20. إذا لم يكن هاتفي الذكي معي فسأشعر بغرابة لأنني لن أعرف ماذا أفعل.",
]

LIKERT_VALUES = [1, 2, 3, 4, 5, 6, 7]
LIKERT_LABELS_EN = {
    1: "1 (Strongly disagree)",
    2: "2",
    3: "3",
    4: "4 (Neutral)",
    5: "5",
    6: "6",
    7: "7 (Strongly agree)",
}
LIKERT_LABELS_AR = {
    1: "1 (لا أوافق بشدة)",
    2: "2",
    3: "3",
    4: "4 (محايد)",
    5: "5",
    6: "6",
    7: "7 (أوافق بشدة)",
}

SUBSCALES_EN = {
    "Not being able to access information (1–4)": [1, 2, 3, 4],
    "Giving up convenience (5–9)": [5, 6, 7, 8, 9],
    "Not being able to communicate (10–15)": [10, 11, 12, 13, 14, 15],
    "Losing connectedness (16–20)": [16, 17, 18, 19, 20],
}
SUBSCALES_AR = {
    "عدم القدرة على الوصول للمعلومات (1–4)": [1, 2, 3, 4],
    "التخلي عن الراحة/السهولة (5–9)": [5, 6, 7, 8, 9],
    "عدم القدرة على التواصل (10–15)": [10, 11, 12, 13, 14, 15],
    "فقدان الاتصال/الترابط (16–20)": [16, 17, 18, 19, 20],
}

PAPER_LINK = "https://www.sciencedirect.com/science/article/pii/S0747563215001806"


@dataclass(frozen=True)
class Severity:
    label: str
    color: str
    description: str
    recs: List[str]


SEVERITIES_EN = {
    "Absent": Severity(
        label="Absent",
        color="#2e7d32",
        description="Your score suggests minimal nomophobia-related distress.",
        recs=[
            "Keep your current healthy smartphone habits.",
            "Balance screen time with sleep, exercise, and in‑person connection.",
            "Try occasional short 'screen‑free' moments to protect focus.",
        ],
    ),
    "Mild": Severity(
        label="Mild",
        color="#f9a825",
        description="Your score suggests mild nomophobia-related discomfort in some situations.",
        recs=[
            "Try short, planned phone‑free intervals (15–30 minutes).",
            "Disable non‑essential notifications.",
            "Use scheduled check‑in times instead of frequent automatic checking.",
        ],
    ),
    "Moderate": Severity(
        label="Moderate",
        color="#ef6c00",
        description="Your score suggests moderate nomophobia-related distress that may affect daily life.",
        recs=[
            "Use Focus / Do Not Disturb during study/work blocks.",
            "Charge before leaving; consider a small power bank if needed.",
            "Replace habitual checking with a brief alternative (walk, breathing, stretching).",
            "Track triggers (stress, boredom) and plan healthier responses.",
        ],
    ),
    "Severe": Severity(
        label="Severe",
        color="#c62828",
        description="Your score suggests severe nomophobia-related distress. Consider extra support.",
        recs=[
            "If this causes significant anxiety or impairment, consider speaking with a mental health professional.",
            "Build a gradual reduction plan: start small and increase weekly.",
            "Create phone‑free zones (bedroom, meals, study desk).",
            "If safety is a worry, prepare alternatives (printed directions, agreed check‑ins).",
        ],
    ),
}

SEVERITIES_AR = {
    "Absent": Severity(
        label="غير موجود",
        color="#2e7d32",
        description="تشير درجتك إلى حدٍ أدنى من الضيق المرتبط برهاب فقدان الهاتف.",
        recs=[
            "حافظ/ي على عاداتك الصحية الحالية في استخدام الهاتف.",
            "وازِن/ي وقت الشاشة مع النوم والرياضة والتواصل المباشر.",
            "جرّب/ي فترات قصيرة بدون هاتف لحماية التركيز.",
        ],
    ),
    "Mild": Severity(
        label="خفيف",
        color="#f9a825",
        description="تشير درجتك إلى انزعاج خفيف في بعض المواقف.",
        recs=[
            "جرّب/ي فترات مخططة بدون هاتف (15–30 دقيقة).",
            "أوقف/ي الإشعارات غير الضرورية.",
            "حدّد/ي أوقات تفقد بدلاً من التفقد المتكرر.",
        ],
    ),
    "Moderate": Severity(
        label="متوسط",
        color="#ef6c00",
        description="تشير درجتك إلى ضيق متوسط قد يؤثر على الحياة اليومية.",
        recs=[
            "استخدم/ي وضع التركيز أو عدم الإزعاج أثناء الدراسة/العمل.",
            "اشحن/ي الهاتف قبل الخروج؛ ويمكن حمل شاحن متنقل صغير عند الحاجة.",
            "استبدل/ي التفقد المعتاد بنشاط قصير (مشي، تنفس، تمدد).",
            "لاحظ/ي المحفزات (الملل، التوتر) وخطط/ي لاستجابات صحية.",
        ],
    ),
    "Severe": Severity(
        label="شديد",
        color="#c62828",
        description="تشير درجتك إلى ضيق شديد. قد يكون من المفيد الحصول على دعم إضافي.",
        recs=[
            "إذا سبب ذلك قلقاً شديداً أو أثر على الوظائف اليومية، ففكر/ي بالتحدث مع مختص نفسي.",
            "ضع/ي خطة تقليل تدريجية: ابدأ/ي بخطوات صغيرة وزد/ي أسبوعياً.",
            "أنشئ/ي مناطق بلا هاتف (غرفة النوم، وقت الطعام، مكتب الدراسة).",
            "إذا كان القلق مرتبطاً بالسلامة، حضّر/ي بدائل (اتفاقيات تواصل، خرائط مطبوعة).",
        ],
    ),
}


def t(lang: str, en: str, ar: str) -> str:
    return ar if lang == "العربية" else en


def classify(total: int) -> str:
    if total <= 20:
        return "Absent"
    if total < 60:
        return "Mild"
    if total < 100:
        return "Moderate"
    return "Severe"


def total_score(ans: Dict[int, int]) -> int:
    return sum(int(ans.get(i, 0) or 0) for i in range(1, 21))


def subscale_scores(ans: Dict[int, int], subscales: Dict[str, List[int]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for name, items in subscales.items():
        out[name] = sum(int(ans.get(i, 0) or 0) for i in items)
    return out


def fig_gauge(total: int, color: str, title: str) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=total,
            number={"suffix": " / 140"},
            title={"text": title},
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


def fig_subscale_bar(subscores: Dict[str, int], title: str, x_title: str, y_title: str) -> go.Figure:
    names = list(subscores.keys())
    values = [subscores[n] for n in names]
    fig = go.Figure(go.Bar(x=names, y=values))
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        margin=dict(l=20, r=20, t=50, b=20),
        height=330,
    )
    fig.update_xaxes(tickangle=12)
    return fig


def inject_css() -> None:
    st.markdown(
        """
        <style>
          :root{
            --bg1:#0b1020; --bg2:#0d1b2a;
            --card: rgba(255,255,255,0.08);
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

          .pill{
            display:inline-block;
            border: 1px solid rgba(255,255,255,0.18);
            background: rgba(255,255,255,0.08);
            border-radius: 999px;
            padding: 7px 12px;
            font-weight: 800;
            margin-right: 8px;
            margin-bottom: 8px;
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

          div.stButton > button {
            background: linear-gradient(90deg, #7c5cff, #00bfff) !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            border-radius: 12px !important;
            border: none !important;
          }
          div.stButton > button:hover {
            background: linear-gradient(90deg, #6848e0, #0099cc) !important;
            color: #ffffff !important;
          }
          div.stButton > button:disabled {
            background: rgba(255,255,255,0.18) !important;
            color: rgba(255,255,255,0.60) !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    st.session_state.setdefault("page", 1)
    st.session_state.setdefault("view", "survey")
    st.session_state.setdefault("answers", {})
    st.session_state.setdefault("lang", "English")
    st.session_state.setdefault("participant", "")
    st.session_state.setdefault("scroll_to_top", False)


def maybe_scroll_top() -> None:
    if st.session_state.get("scroll_to_top"):
        scroll_to_here(0, key="top")
        st.session_state.scroll_to_top = False


def render_header(lang: str) -> None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title(t(lang, "Nomophobia Screening Tool (NMP-Q)", "أداة فحص رهاب فقدان الهاتف (NMP‑Q)"))
    st.markdown(t(lang, "**Made by: Alia Al‑Qadri**", "**إعداد: Alia Al‑Qadri**"))
    st.markdown(
        t(
            lang,
            "**Nomophobia** refers to anxiety or discomfort related to not having access to a mobile phone or its services.  \n"
            "This app is a **screening tool**; it is **not a diagnostic test**.",
            "**رهاب فقدان الهاتف (Nomophobia)** هو قلق أو انزعاج مرتبط بعدم توفر الهاتف المحمول أو خدماته.  \n"
            "هذا التطبيق **للفحص/التحري** وليس **أداة تشخيص**."
        )
    )
    st.markdown(
        t(
            lang,
            f"Validated based on: Yildirim, C., & Correia, A. P. (2015). *Computers in Human Behavior*, 49, 130–137.  \nPaper link: {PAPER_LINK}",
            f"معتمدة بناءً على: Yildirim, C., & Correia, A. P. (2015). *Computers in Human Behavior*, 49, 130–137.  \nرابط الدراسة: {PAPER_LINK}",
        )
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_progress(lang: str, page: int, num_pages: int) -> None:
    pct = int((page / num_pages) * 100)
    st.markdown(
        f"""<div class="progress"><div style="width:{pct}%"></div></div>
        <div class="muted">{t(lang, f"Page {page} of {num_pages}", f"الصفحة {page} من {num_pages}")}</div>
        """,
        unsafe_allow_html=True,
    )


def page_complete(page: int, answers: Dict[int, int]) -> bool:
    s = (page - 1) * 5 + 1
    e = min(page * 5, 20)
    return all(answers.get(i) is not None for i in range(s, e + 1))


def all_complete(answers: Dict[int, int]) -> bool:
    return all(answers.get(i) is not None for i in range(1, 21))


def make_results_csv(participant: str, answers: Dict[int, int]) -> bytes:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["participant", participant])
    writer.writerow(["timestamp", datetime.utcnow().isoformat() + "Z"])
    writer.writerow([])
    writer.writerow(["item", "response_1to7"])
    for i in range(1, 21):
        writer.writerow([i, answers.get(i, "")])
    writer.writerow([])
    writer.writerow(["total_score", total_score(answers)])
    writer.writerow(["severity", classify(total_score(answers))])
    return output.getvalue().encode("utf-8")


def make_results_txt(lang: str, participant: str, answers: Dict[int, int]) -> bytes:
    total = total_score(answers)
    level = classify(total)
    subs = subscale_scores(answers, SUBSCALES_AR if lang == "العربية" else SUBSCALES_EN)
    sev = (SEVERITIES_AR if lang == "العربية" else SEVERITIES_EN)[level]

    lines: List[str] = []
    lines.append(t(lang, "Nomophobia Screening Tool (NMP-Q)", "أداة فحص رهاب فقدان الهاتف (NMP‑Q)"))
    lines.append(t(lang, "Made by: Alia Al-Qadri", "إعداد: Alia Al‑Qadri"))
    if participant.strip():
        lines.append(t(lang, f"Participant: {participant}", f"المشارك/ة: {participant}"))
    lines.append(t(lang, f"Timestamp (UTC): {datetime.utcnow().isoformat()}Z", f"الوقت (UTC): {datetime.utcnow().isoformat()}Z"))
    lines.append("")
    lines.append(t(lang, f"Total score: {total}/140", f"المجموع: {total}/140"))
    lines.append(t(lang, f"Severity: {level}", f"الشدة: {sev.label}"))
    lines.append("")
    lines.append(t(lang, "Subscale scores:", "درجات الأبعاد:"))
    for k, v in subs.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append(t(lang, "Recommendations:", "توصيات:"))
    for r in sev.recs:
        lines.append(f"- {r}")
    return ("\n".join(lines)).encode("utf-8")


def make_results_pdf(lang: str, participant: str, answers: Dict[int, int]) -> Tuple[bytes | None, str | None]:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception:
        return None, t(lang, "PDF export needs 'reportlab' in requirements.txt.", "تصدير PDF يحتاج إضافة 'reportlab' في requirements.txt.")

    total = total_score(answers)
    level = classify(total)
    sev = SEVERITIES_EN[level]
    subs = subscale_scores(answers, SUBSCALES_EN)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Nomophobia Screening Tool (NMP-Q)")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(50, y, "Made by: Alia Al-Qadri")
    y -= 18
    if participant.strip():
        c.drawString(50, y, f"Participant: {participant}")
        y -= 18
    c.drawString(50, y, f"Timestamp (UTC): {datetime.utcnow().isoformat()}Z")
    y -= 26

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Total score: {total}/140")
    y -= 16
    c.drawString(50, y, f"Severity: {level}")
    y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Subscale scores:")
    y -= 16
    c.setFont("Helvetica", 11)
    for k, v in subs.items():
        c.drawString(60, y, f"- {k}: {v}")
        y -= 14
        if y < 80:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 11)

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Recommendations:")
    y -= 16
    c.setFont("Helvetica", 11)
    for r in sev.recs:
        c.drawString(60, y, f"- {r}")
        y -= 14
        if y < 80:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 11)

    c.showPage()
    c.save()
    return buf.getvalue(), None


def render_survey(lang: str) -> None:
    maybe_scroll_top()

    num_pages = 4
    page = int(st.session_state.page)
    answers: Dict[int, int] = st.session_state.answers

    questions = QUESTIONS_AR if lang == "العربية" else QUESTIONS_EN
    value_to_label = LIKERT_LABELS_AR if lang == "العربية" else LIKERT_LABELS_EN

    start = (page - 1) * 5 + 1
    end = min(page * 5, 20)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_progress(lang, page, num_pages)

    for i in range(start, end + 1):
        st.markdown('<div class="qcard">', unsafe_allow_html=True)
        st.markdown(f"**{questions[i-1]}**")

        if i not in answers:
            answers[i] = 4

        default = answers.get(i, 4)
        if default not in LIKERT_VALUES:
            default = 4
        idx = LIKERT_VALUES.index(default)

        chosen = st.radio(
            label=f"q{i}",
            options=LIKERT_VALUES,
            index=idx,
            format_func=lambda v: value_to_label.get(v, str(v)),
            label_visibility="collapsed",
            key=f"radio_{i}",
        )

        answers[i] = int(chosen)
        st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.answers = answers

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        back = st.button(t(lang, "Back", "رجوع"), disabled=(page == 1), use_container_width=True)
    with col2:
        next_ = st.button(t(lang, "Next", "التالي"), disabled=(page == num_pages), use_container_width=True)
    with col3:
        submit = st.button(t(lang, "Submit", "إرسال"), disabled=(page != num_pages), use_container_width=True)

    if back:
        st.session_state.page = max(1, page - 1)
        st.session_state.scroll_to_top = True
        st.rerun()

    if next_:
        if not page_complete(page, answers):
            st.warning(t(lang, "Please answer all questions on this page before continuing.", "يرجى الإجابة على جميع أسئلة هذه الصفحة قبل المتابعة."))
        else:
            st.session_state.page = min(num_pages, page + 1)
            st.session_state.scroll_to_top = True
            st.rerun()

    if submit:
        if not all_complete(answers):
            st.warning(t(lang, "Please make sure all 20 questions are answered before submitting.", "يرجى التأكد من الإجابة على جميع الأسئلة (20) قبل الإرسال."))
        else:
            st.session_state.view = "results"
            st.session_state.scroll_to_top = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_results(lang: str) -> None:
    maybe_scroll_top()

    answers: Dict[int, int] = st.session_state.answers
    participant: str = st.session_state.participant or ""
    total = total_score(answers)
    level = classify(total)

    sev_map = SEVERITIES_AR if lang == "العربية" else SEVERITIES_EN
    sev = sev_map[level]

    sub_map = SUBSCALES_AR if lang == "العربية" else SUBSCALES_EN
    subs = subscale_scores(answers, sub_map)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t(lang, "Your Results", "نتائجك"))
    st.markdown(
        f'<span class="pill" style="border-color:{sev.color}; color:{sev.color};">{t(lang, "Nomophobia level", "مستوى الرهاب")}: <b>{sev.label if lang=="العربية" else level}</b></span>'
        f'<span class="pill">{t(lang, "Total points", "المجموع")}: <b>{total}</b></span>',
        unsafe_allow_html=True,
    )
    st.write(sev.description)

    st.markdown("### " + t(lang, "Recommendations", "توصيات"))
    for r in sev.recs:
        st.markdown(f"- {r}")
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(fig_gauge(total, sev.color, t(lang, "NMP-Q Total Score", "المجموع الكلي")), use_container_width=True)
    with c2:
        st.plotly_chart(
            fig_subscale_bar(
                subs,
                t(lang, "Subscale scores (higher = more discomfort)", "درجات الأبعاد (الأعلى = انزعاج أكثر)"),
                t(lang, "Dimension", "البعد"),
                t(lang, "Score", "الدرجة"),
            ),
            use_container_width=True,
        )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t(lang, "Download your results", "تحميل النتائج"))

    csv_bytes = make_results_csv(participant, answers)
    st.download_button(
        t(lang, "Download CSV", "تحميل CSV"),
        data=csv_bytes,
        file_name="nmpq_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

    txt_bytes = make_results_txt(lang, participant, answers)
    st.download_button(
        t(lang, "Download TXT summary", "تحميل ملخص TXT"),
        data=txt_bytes,
        file_name="nmpq_results.txt",
        mime="text/plain",
        use_container_width=True,
    )

    pdf_bytes, pdf_err = make_results_pdf(lang, participant, answers)
    if pdf_bytes:
        st.download_button(
            t(lang, "Download PDF (English)", "تحميل PDF (بالإنجليزية)"),
            data=pdf_bytes,
            file_name="nmpq_results.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.info(pdf_err or t(lang, "PDF export unavailable.", "تصدير PDF غير متاح."))

    st.markdown("</div>", unsafe_allow_html=True)

    c3, c4 = st.columns([1, 1])
    with c3:
        if st.button(t(lang, "Edit answers", "تعديل الإجابات"), use_container_width=True):
            st.session_state.view = "survey"
            st.session_state.page = 1
            st.session_state.scroll_to_top = True
            st.rerun()
    with c4:
        if st.button(t(lang, "Start over", "بدء من جديد"), use_container_width=True):
            st.session_state.view = "survey"
            st.session_state.page = 1
            st.session_state.answers = {}
            for i in range(1, 21):
                st.session_state.pop(f"radio_{i}", None)
            st.session_state.scroll_to_top = True
            st.rerun()

    st.caption(
        t(
            lang,
            "Reminder: This tool screens for nomophobia-related feelings; it does not diagnose a mental health condition.",
            "تنبيه: هذه الأداة للفحص/التحري وليست أداة تشخيص لحالة نفسية.",
        )
    )


def main() -> None:
    st.set_page_config(page_title="Nomophobia Screening (NMP-Q)", page_icon="📱", layout="centered")
    inject_css()
    init_state()

    with st.sidebar:
        st.session_state.lang = st.selectbox("Language / اللغة", ["English", "العربية"], index=0 if st.session_state.lang == "English" else 1)
        st.session_state.participant = st.text_input(
            t(st.session_state.lang, "Participant ID (optional)", "معرّف المشارك/ة (اختياري)"),
            value=st.session_state.participant,
        )
        st.markdown("---")
        st.caption(t(st.session_state.lang, "Deployment notes:", "ملاحظات النشر:"))
        st.caption("requirements.txt: streamlit, plotly, streamlit-scroll-to-top")
        st.caption(t(st.session_state.lang, "For PDF export add: reportlab", "لتصدير PDF أضف: reportlab"))

    lang = st.session_state.lang
    render_header(lang)

    if st.session_state.view == "results":
        render_results(lang)
    else:
        render_survey(lang)


if __name__ == "__main__":
    main()
