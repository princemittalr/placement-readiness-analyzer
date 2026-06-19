import streamlit as st
from groq import Groq
import PyPDF2
import os
import re
import io
from datetime import datetime

# ── PDF support ───────────────────────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Placement Readiness Analyzer", page_icon="🎯", layout="wide")
MODEL = "llama-3.3-70b-versatile"

@st.cache_resource
def get_client():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not set.")
        st.stop()
    return Groq(api_key=api_key)

client = get_client()

# ── PROMPTS ───────────────────────────────────────────────────────────────────
ANALYZER_PROMPT = """You are an expert placement counselor for Indian engineering students.
Analyze the student's profile and give brutally honest, specific feedback.

Output EXACTLY in this format (no deviation):

READINESS SCORE: [0-100]/100

CURRENT LEVEL: [Not Ready / Partially Ready / Ready / Highly Ready]

STRONG POINTS:
- [point 1]
- [point 2]
- [point 3]

CRITICAL GAPS:
- [gap 1]
- [gap 2]
- [gap 3]

SKILL RATINGS (rate each 1-10):
DSA: [score]/10
Projects: [score]/10
Core CS: [score]/10
Communication: [score]/10
Resume Quality: [score]/10

COMPANY FIT:
- Service companies (TCS/Infosys/Wipro): [Ready/Not Ready] — [one line reason]
- Mid-tier product (Zoho/Freshworks): [Ready/Not Ready] — [one line reason]
- Top product/FAANG (Google/Microsoft/Amazon): [Ready/Not Ready] — [one line reason]
- Startups: [Ready/Not Ready] — [one line reason]

30-DAY ACTION PLAN:
Week 1: [specific action]
Week 2: [specific action]
Week 3: [specific action]
Week 4: [specific action]

HONEST VERDICT:
[2-3 sentences. Brutally honest. What this student must hear, not what they want to hear.]"""

INTERVIEW_PROMPT_TEMPLATE = """You are an expert interviewer at {company}.
Generate a realistic mock interview for an Indian engineering student.

ROUND: {round} at {company}
DIFFICULTY LEVEL: [Easy/Medium/Hard]
DURATION: [typical duration]

TECHNICAL QUESTIONS:
Q1: [question]
WHAT THEY WANT TO HEAR: [expected answer in 2-3 lines]

Q2: [question]
WHAT THEY WANT TO HEAR: [expected answer]

Q3: [question]
WHAT THEY WANT TO HEAR: [expected answer]

Q4: [question]
WHAT THEY WANT TO HEAR: [expected answer]

Q5: [question]
WHAT THEY WANT TO HEAR: [expected answer]

HR/BEHAVIORAL QUESTIONS:
Q6: [question]
STRONG ANSWER STRUCTURE: [how to answer specifically]

Q7: [question]
STRONG ANSWER STRUCTURE: [how to answer]

Q8: [question]
STRONG ANSWER STRUCTURE: [how to answer]

TRICK QUESTION THIS COMPANY IS KNOWN FOR:
Q9: [trick question]
WHY THEY ASK IT: [real reason]
HOW TO ANSWER: [specific strategy]

COMMON MISTAKES THAT FAIL CANDIDATES AT {company}:
- [mistake 1]
- [mistake 2]
- [mistake 3]

FINAL TIP FOR {company}:
[One paragraph of insider advice specific to this company's culture and hiring process]"""

ROADMAP_PROMPT_TEMPLATE = """You are an expert placement coach for Indian engineering students.
Generate a specific, actionable preparation roadmap for: {company}

TIMELINE TO BE READY: [X months]

MUST-KNOW TOPICS:
- [topic 1] — [why it matters]
- [topic 2] — [why it matters]
- [topic 3] — [why it matters]
- [topic 4] — [why it matters]
- [topic 5] — [why it matters]

LEETCODE STRATEGY:
- Minimum problems needed: [number]
- Focus tags: [specific tags]
- Difficulty split: Easy X% / Medium X% / Hard X%

FREE RESOURCES:
- [resource 1 with link]
- [resource 2 with link]
- [resource 3 with link]

WEEK BY WEEK PLAN (8 weeks):
Week 1-2: [specific action]
Week 3-4: [specific action]
Week 5-6: [specific action]
Week 7-8: [specific action]

RED FLAGS THAT INSTANTLY REJECT YOU AT {company}:
- [red flag 1]
- [red flag 2]
- [red flag 3]

ONE THING MOST STUDENTS IGNORE:
[Single most important insight specific to this company]"""

RESUME_PROMPT = """You are an expert resume reviewer for Indian engineering placements.
Review this resume and give brutally honest, specific feedback.

Output EXACTLY in this format:

RESUME SCORE: [0-100]/100

FIRST IMPRESSION: [one sentence — what a recruiter thinks in 6 seconds]

WHAT'S WORKING:
- [point 1]
- [point 2]

CRITICAL ISSUES:
- [issue 1 with exact fix]
- [issue 2 with exact fix]
- [issue 3 with exact fix]

SECTION-BY-SECTION FEEDBACK:
Education: [feedback]
Skills: [feedback]
Projects: [feedback]
Experience/Internships: [feedback]
Achievements: [feedback]

ATS SCORE: [0-100]/100
ATS ISSUES: [what keywords or formatting will fail Applicant Tracking Systems]

TOP 3 CHANGES TO MAKE RIGHT NOW:
1. [change 1]
2. [change 2]
3. [change 3]

VERDICT: [2 sentences. Honest assessment of this resume's current state.]

Resume Content:
{resume}"""

# ── HELPERS ───────────────────────────────────────────────────────────────────
def extract_score(text, label="READINESS SCORE"):
    match = re.search(rf"{label}:\s*(\d+)", text)
    return int(match.group(1)) if match else None

def stream_response(messages, max_tokens=2000):
    """Stream Groq response, return full text"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            stream=True
        )
        box = st.empty()
        full = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            full += delta
            box.markdown(full + "▌")
        box.markdown(full)
        return full
    except Exception as e:
        st.error(f"AI error: {e}")
        return None

def read_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception:
        return ""

def score_color(score):
    if score >= 75: return "#00b894"
    if score >= 50: return "#fdcb6e"
    if score >= 25: return "#e17055"
    return "#d63031"

def score_label(score):
    if score >= 75: return "Highly Ready 🚀"
    if score >= 50: return "Partially Ready 📈"
    if score >= 25: return "Not Ready Yet ⚠️"
    return "Critical — Start Now 🔴"

def render_score_card(score, label="Readiness Score"):
    color = score_color(score)
    lbl   = score_label(score)
    st.markdown(f"""
    <div style="background:{color};padding:20px;border-radius:12px;text-align:center;margin-bottom:16px">
        <h1 style="color:white;margin:0;font-size:3rem">{score}/100</h1>
        <p style="color:white;margin:4px 0;font-size:1.1rem">{label}</p>
        <p style="color:white;margin:0;font-weight:bold">{lbl}</p>
    </div>
    """, unsafe_allow_html=True)
    st.progress(score / 100)

def generate_pdf_result(name, result_text, section_title):
    if not PDF_AVAILABLE:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story  = []
    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=18,
                                  spaceAfter=4, textColor=colors.HexColor("#1a1a2e"))
    story.append(Paragraph(f"🎯 {section_title}", title_style))
    if name:
        story.append(Paragraph(f"Student: {name}", styles["Normal"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 0.2*inch))
    for line in result_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), styles["Normal"]))
            story.append(Spacer(1, 0.04*inch))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for key in ["analysis_result","interview_result","roadmap_result","resume_result","student_name"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🎯 Placement Readiness Analyzer")
st.caption("Brutally honest AI feedback on your placement preparation — free, specific, actionable.")
st.warning("⚠️ This tool gives HONEST feedback, not flattery. Be ready for truth.")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Profile Analyzer",
    "🎤 Mock Interview",
    "🗺️ Prep Roadmap",
    "📄 Resume Reviewer"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — PROFILE ANALYZER
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    with st.form("profile_form"):
        st.subheader("Your Profile")
        col1, col2 = st.columns(2)
        with col1:
            name     = st.text_input("Your Name")
            branch   = st.selectbox("Branch", ["CSE","CSE (AI/ML)","CSE (Data Science)","ECE","EEE","Mechanical","Civil","Other"])
            year     = st.selectbox("Current Year", ["1st Year","2nd Year","3rd Year","4th Year"])
            cgpa     = st.number_input("CGPA", min_value=0.0, max_value=10.0, step=0.1, value=7.0)
        with col2:
            backlogs   = st.selectbox("Active Backlogs", ["0","1","2","3+"])
            target     = st.multiselect("Target Companies", [
                "Service companies (TCS/Infosys/Wipro)",
                "Mid-tier product (Zoho/Freshworks/Juspay)",
                "Top product/FAANG (Google/Microsoft/Amazon)",
                "Startups"
            ])
            internship = st.selectbox("Internship Experience", ["None","1 internship","2+ internships"])

        st.subheader("Technical Skills")
        col3, col4 = st.columns(2)
        with col3:
            dsa      = st.selectbox("DSA / Problem Solving", [
                "Never practiced",
                "Basics only (arrays, strings)",
                "Medium level (trees, graphs)",
                "Advanced (DP, segment trees)"
            ])
            projects = st.selectbox("Projects Built", [
                "None",
                "1 project (tutorial-based)",
                "1-2 original projects",
                "3+ deployed projects with users"
            ])
        with col4:
            languages = st.multiselect("Programming Languages", ["C","C++","Java","Python","JavaScript","Other"])
            core      = st.multiselect("Core CS Subjects Ready", ["DBMS","OS","CN","OOPs","System Design"])

        st.subheader("Soft Skills & Extras")
        communication = st.selectbox("Communication / English", [
            "Weak — struggle to explain in English",
            "Average — can manage but not confident",
            "Good — can explain clearly",
            "Strong — fluent and confident"
        ])
        extras = st.multiselect("Achievements", [
            "Hackathon participation",
            "Open source contributions",
            "Technical blog/YouTube",
            "Leadership role in college club",
            "Competitive programming (Codeforces/LeetCode rating)",
            "Research paper/publication",
            "None of the above"
        ])
        resume_file = st.file_uploader("Upload Resume PDF (optional)", type="pdf")
        submitted   = st.form_submit_button("🔍 Analyze My Placement Readiness", type="primary", use_container_width=True)

    if submitted:
        resume_text = read_pdf(resume_file) if resume_file else ""
        profile = f"""
Name: {name} | Branch: {branch} | Year: {year} | CGPA: {cgpa} | Backlogs: {backlogs}
Target: {', '.join(target) if target else 'Not specified'} | Internships: {internship}
DSA: {dsa} | Projects: {projects}
Languages: {', '.join(languages) if languages else 'None'} | Core CS: {', '.join(core) if core else 'None'}
Communication: {communication} | Extras: {', '.join(extras) if extras else 'None'}
{"Resume: " + resume_text[:3000] if resume_text else "No resume uploaded."}"""

        st.session_state.student_name = name
        st.divider()
        st.subheader(f"📊 Analysis for {name}")

        with st.spinner("Analyzing your profile..."):
            result = stream_response([
                {"role": "system", "content": ANALYZER_PROMPT},
                {"role": "user",   "content": f"Analyze this student:\n{profile}"}
            ])

        if result:
            st.session_state.analysis_result = result

            # Visual score card
            score = extract_score(result, "READINESS SCORE")
            if score is not None:
                st.divider()
                st.subheader("📈 Your Score")
                render_score_card(score, "Placement Readiness Score")

            # Skill ratings bar chart
            skill_scores = {}
            for skill in ["DSA","Projects","Core CS","Communication","Resume Quality"]:
                m = re.search(rf"{skill}:\s*(\d+)/10", result)
                if m:
                    skill_scores[skill] = int(m.group(1))

            if skill_scores:
                st.subheader("🎯 Skill Breakdown")
                for skill, val in skill_scores.items():
                    col_s, col_b = st.columns([1, 3])
                    col_s.markdown(f"**{skill}**")
                    col_b.progress(val / 10, text=f"{val}/10")

            # Download buttons
            st.divider()
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button("📥 Download Analysis (.txt)",
                    data=result,
                    file_name=f"placement_analysis_{name.replace(' ','_')}.txt",
                    mime="text/plain", use_container_width=True)
            with col_d2:
                if PDF_AVAILABLE:
                    pdf = generate_pdf_result(name, result, "Placement Readiness Analysis")
                    if pdf:
                        st.download_button("📥 Download Analysis (.pdf)",
                            data=pdf,
                            file_name=f"placement_analysis_{name.replace(' ','_')}.pdf",
                            mime="application/pdf", use_container_width=True)

    # Show previous result
    elif st.session_state.analysis_result:
        st.info("Showing your last analysis. Fill the form again to re-analyze.")
        st.markdown(st.session_state.analysis_result)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — MOCK INTERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🎤 Mock Interview Question Generator")
    st.write("Get personalized interview questions based on your target company and round.")

    col_a, col_b = st.columns(2)
    with col_a:
        interview_company = st.selectbox("Target Company:", [
            "TCS / Infosys / Wipro (Service)",
            "Zoho / Freshworks (Mid-tier Product)",
            "Amazon / Microsoft / Google (FAANG)",
            "Early-stage Startup"
        ])
    with col_b:
        interview_round = st.selectbox("Interview Round:", [
            "Aptitude / Online Assessment",
            "Technical Round 1",
            "Technical Round 2",
            "HR Round"
        ])

    if st.button("🎯 Generate Mock Interview", type="primary", use_container_width=True):
        prompt = INTERVIEW_PROMPT_TEMPLATE.format(
            company=interview_company,
            round=interview_round
        )
        st.divider()
        st.subheader(f"Mock Interview — {interview_round} at {interview_company}")
        with st.spinner("Generating your mock interview..."):
            result = stream_response([{"role":"user","content":prompt}])
        if result:
            st.session_state.interview_result = result
            st.success("✅ Practice answering each question OUT LOUD before your real interview!")

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button("📥 Download Questions (.txt)",
                    data=result,
                    file_name=f"mock_interview_{interview_company[:10].replace(' ','_')}.txt",
                    mime="text/plain", use_container_width=True)
            with col_d2:
                if PDF_AVAILABLE:
                    pdf = generate_pdf_result(
                        st.session_state.student_name, result,
                        f"Mock Interview — {interview_company}"
                    )
                    if pdf:
                        st.download_button("📥 Download Questions (.pdf)",
                            data=pdf,
                            file_name=f"mock_interview_{interview_company[:10].replace(' ','_')}.pdf",
                            mime="application/pdf", use_container_width=True)

    elif st.session_state.interview_result:
        st.info("Showing your last generated interview. Click button to generate new one.")
        st.markdown(st.session_state.interview_result)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — PREP ROADMAP
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🗺️ Company-Specific Preparation Roadmap")
    st.write("Get exact preparation strategy, topics, and week-by-week plan.")

    roadmap_company = st.selectbox("Target Company:", [
        "TCS / Infosys / Wipro (Service)",
        "Zoho / Freshworks / Juspay (Mid-tier Product)",
        "Amazon / Microsoft / Google (FAANG)",
        "Early-stage Startup"
    ], key="roadmap_co")

    if st.button("🗺️ Generate Preparation Roadmap", type="primary", use_container_width=True):
        prompt = ROADMAP_PROMPT_TEMPLATE.format(company=roadmap_company)
        st.divider()
        st.subheader(f"Preparation Roadmap — {roadmap_company}")
        with st.spinner("Building your roadmap..."):
            result = stream_response([{"role":"user","content":prompt}])
        if result:
            st.session_state.roadmap_result = result

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button("📥 Download Roadmap (.txt)",
                    data=result,
                    file_name=f"roadmap_{roadmap_company[:10].replace(' ','_')}.txt",
                    mime="text/plain", use_container_width=True)
            with col_d2:
                if PDF_AVAILABLE:
                    pdf = generate_pdf_result(
                        st.session_state.student_name, result,
                        f"Placement Roadmap — {roadmap_company}"
                    )
                    if pdf:
                        st.download_button("📥 Download Roadmap (.pdf)",
                            data=pdf,
                            file_name=f"roadmap_{roadmap_company[:10].replace(' ','_')}.pdf",
                            mime="application/pdf", use_container_width=True)

    elif st.session_state.roadmap_result:
        st.info("Showing your last roadmap. Click button to generate new one.")
        st.markdown(st.session_state.roadmap_result)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — RESUME REVIEWER
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📄 AI Resume Reviewer")
    st.write("Upload your resume and get brutally honest, section-by-section feedback with ATS score.")

    resume_upload = st.file_uploader("Upload your Resume (PDF)", type="pdf", key="resume_tab")

    col_name, _ = st.columns([1, 2])
    with col_name:
        reviewer_name = st.text_input("Your Name (for report)", key="rev_name",
                                       value=st.session_state.student_name)

    if st.button("📄 Analyze My Resume", type="primary", use_container_width=True):
        if not resume_upload:
            st.warning("Please upload your resume PDF first.")
        else:
            resume_text = read_pdf(resume_upload)
            if not resume_text.strip():
                st.error("Could not read PDF. Make sure it's not scanned/image-based.")
            else:
                prompt = RESUME_PROMPT.format(resume=resume_text[:4000])
                st.divider()
                st.subheader("📊 Resume Analysis")
                with st.spinner("Reviewing your resume..."):
                    result = stream_response([{"role":"user","content":prompt}], max_tokens=1500)
                if result:
                    st.session_state.resume_result = result

                    # Visual resume score
                    score = extract_score(result, "RESUME SCORE")
                    if score is not None:
                        st.divider()
                        render_score_card(score, "Resume Score")

                    # ATS score
                    ats = extract_score(result, "ATS SCORE")
                    if ats is not None:
                        st.subheader("🤖 ATS Score")
                        st.progress(ats / 100, text=f"ATS Score: {ats}/100")
                        if ats < 50:
                            st.error("⚠️ Low ATS score — your resume may get filtered before a human sees it!")
                        elif ats < 75:
                            st.warning("🟡 Medium ATS score — improve keywords and formatting.")
                        else:
                            st.success("✅ Good ATS score — your resume should pass automated filters.")

                    # Downloads
                    st.divider()
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.download_button("📥 Download Review (.txt)",
                            data=result,
                            file_name=f"resume_review_{reviewer_name.replace(' ','_')}.txt",
                            mime="text/plain", use_container_width=True)
                    with col_d2:
                        if PDF_AVAILABLE:
                            pdf = generate_pdf_result(reviewer_name, result, "Resume Review Report")
                            if pdf:
                                st.download_button("📥 Download Review (.pdf)",
                                    data=pdf,
                                    file_name=f"resume_review_{reviewer_name.replace(' ','_')}.pdf",
                                    mime="application/pdf", use_container_width=True)

    elif st.session_state.resume_result:
        st.info("Showing your last resume review.")
        st.markdown(st.session_state.resume_result)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
c1, c2, c3 = st.columns(3)
c1.caption("🎯 Placement Readiness Analyzer")
c2.caption("🤖 Powered by Groq (LLaMA 3.3 70B) — Free")
c3.caption("Built for Indian engineering students | Honest feedback only")
