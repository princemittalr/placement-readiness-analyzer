# 🎯 Placement Readiness Analyzer

<div align="center">

**Brutally honest AI feedback on your placement preparation — free, specific, actionable.**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge)](https://placement-readiness-analyzer.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 🔥 The Problem

Every year, **1.5 million engineering students** in India sit for campus placements.

Most of them prepare blindly — grinding random LeetCode problems, listing every technology on their resume, and walking into interviews with no idea what a specific company actually expects.

**The result:** Students who could get placed at Zoho prepare for TCS. Students who could crack Amazon waste months on wrong topics. Qualified candidates get rejected for fixable gaps they never knew existed.

> **This tool gives every student access to the honest, personalized feedback that only students with expensive coaching or well-connected mentors usually get.**

---

## ✨ What It Does

A student fills a profile form — branch, CGPA, DSA level, projects, target companies — and gets a complete placement readiness assessment across **4 tools in one app:**

---

## 🛠️ 4 Tools in One

### 📊 Tab 1 — Profile Analyzer
- **Readiness Score** (0–100) with visual score card
- Current level: Not Ready → Highly Ready
- Strong points + critical gaps
- **5-skill breakdown** with progress bars (DSA, Projects, Core CS, Communication, Resume)
- Company fit assessment for Service / Mid-tier Product / FAANG / Startups
- Personalized 30-day action plan
- Brutally honest verdict
- Download as TXT or PDF

### 🎤 Tab 2 — Mock Interview Generator
- Realistic interview questions by company + round type
- "What they want to hear" for every technical question
- Strong answer structure for every HR question
- The trick question this specific company is known for
- Common mistakes that fail candidates
- Insider tip for company culture

### 🗺️ Tab 3 — Prep Roadmap
- Week-by-week 8-week preparation plan
- Must-know topics with reasons
- LeetCode strategy: problem count, tags, difficulty split
- Free resource links
- Red flags that instantly reject candidates
- The one thing most students ignore

### 📄 Tab 4 — AI Resume Reviewer
- **Resume Score** (0–100) with visual card
- **ATS Score** — will your resume survive automated filters?
- First impression in 6 seconds (what a recruiter actually thinks)
- Section-by-section feedback: Education, Skills, Projects, Experience
- Top 3 changes to make right now
- Download review as TXT or PDF

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| **Streaming Responses** | AI answers appear word-by-word — no waiting for full response |
| **Visual Score Cards** | Color-coded readiness scores — not just text |
| **Skill Progress Bars** | 5-dimension skill breakdown visualized |
| **ATS Score** | Checks if resume will pass automated filtering |
| **Company-Specific** | Different questions, roadmaps, and tips per company type |
| **PDF Export** | Download any analysis as formatted PDF report |
| **Session Persistence** | Switch tabs without losing your results |
| **Resume Upload** | Upload PDF resume for personalized analysis |

---

## 🏗️ Tech Stack

```
Frontend      →  Streamlit (4-tab layout)
AI Engine     →  Groq API (LLaMA 3.3 70B) — streaming
Resume Parse  →  PyPDF2
PDF Export    →  ReportLab
Language      →  Python 3.10+
Deployment    →  Streamlit Community Cloud
```

---

## 🚀 Run Locally

```bash
# Clone
git clone https://github.com/princemittalr/placement-readiness-analyzer.git
cd placement-readiness-analyzer

# Install
pip install streamlit groq PyPDF2 reportlab

# Set API key
export GROQ_API_KEY="your_groq_api_key"   # Free at console.groq.com

# Run
streamlit run app.py
```

---

## 📁 Project Structure

```
placement-readiness-analyzer/
├── app.py              # Main application (4-tab layout)
├── requirements.txt    # Dependencies
└── README.md
```

---

## 💡 Design Decisions

**Why 4 tabs instead of 4 separate apps?**
A student's placement journey is one continuous workflow — profile → mock interview → roadmap → resume. Keeping everything in one app with persistent session state means no re-entering data, no switching between tools.

**Why "brutally honest" framing?**
Most placement prep tools give generic positive feedback to keep users engaged. This tool is built on the opposite principle — students need to hear what's wrong, not what's right, to actually improve before placements.

**Why company-specific outputs?**
The gap between TCS and Amazon preparation is enormous. A student targeting Zoho needs a fundamentally different roadmap than one targeting Google. Generic advice fails both.

---

## 🗺️ Roadmap

- [ ] Progress tracker — re-analyze monthly, track improvement
- [ ] Peer comparison — anonymized benchmarking against similar profiles
- [ ] College-specific placement data integration
- [ ] WhatsApp bot for quick profile checks
- [ ] Vernacular language support (Tamil, Hindi)

---

## 🌍 Who This Is For

- 3rd and 4th year engineering students preparing for campus placements
- Students without access to paid coaching or placement mentors
- First-generation engineers with no family guidance on placements
- Students in Tier-2 and Tier-3 colleges with limited placement support

---

## 👨‍💻 Author

**Prince Mittal**
B.Tech CSE (AI/ML) · Dayananda Sagar University

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/princemittalr)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/princemittalr)

---

## 📄 License

MIT License — free to use, modify, and deploy.

---

<div align="center">

*Built for the engineering student who works hard but doesn't know what to work on.*

</div>