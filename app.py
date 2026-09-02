"""
AI StudyMate Pro
=================
Flat single-row tab layout (matches the original UI), with the graded
interactive Test and Analytics features folded in as regular tabs.

Requires: streamlit>=1.45.0, groq, pypdf
"""

import streamlit as st
from pypdf import PdfReader
from groq import Groq
import re
import json
import os
from datetime import datetime
from collections import Counter, defaultdict

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI StudyMate Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# HTML HELPER  (avoids the markdown-code-block bug entirely)
# ============================================================

def html(content: str):
    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown("\n".join(line.lstrip() for line in content.splitlines()),
                     unsafe_allow_html=True)


# ============================================================
# CSS  -- richer color, left-aligned to dodge markdown code fences
# ============================================================

html("""
<style>
:root {
  --bg: #eef0fb;
  --ink: #10142a;
  --ink-soft: #454e68;
  --ink-faint: #7d84a0;
  --accent1: #4f46e5;
  --accent2: #7c3aed;
  --accent3: #0ea5e9;
  --accent4: #db2777;
  --accent5: #f59e0b;
  --gold: #d6a92c;
  --good: #16a34a;
  --bad: #dc2626;
  --glass-bg: rgba(255,255,255,0.58);
  --glass-bg-soft: rgba(255,255,255,0.44);
  --glass-border: rgba(255,255,255,0.75);
  --glass-shadow: 0 10px 40px rgba(31,25,90,0.14), inset 0 1px 0 rgba(255,255,255,0.65);
}

/* PREMIUM MESH BACKGROUND */
.stApp {
  background:
    radial-gradient(circle at 8% 0%, rgba(99,102,241,0.28), transparent 34%),
    radial-gradient(circle at 92% 4%, rgba(219,39,119,0.20), transparent 32%),
    radial-gradient(circle at 50% 30%, rgba(14,165,233,0.16), transparent 40%),
    radial-gradient(circle at 20% 95%, rgba(214,169,44,0.16), transparent 32%),
    radial-gradient(circle at 85% 90%, rgba(124,58,237,0.18), transparent 34%),
    linear-gradient(160deg, #eef0fb 0%, #eaeefc 45%, #f3ecfb 100%);
  background-attachment: fixed;
}
.main .block-container { max-width: 1450px; padding-top: 1.6rem; padding-bottom: 3rem; }

/* HERO -- deep glass with a gold shimmer edge */
.sm-hero {
  position: relative; overflow: hidden;
  padding: 48px 30px; margin-bottom: 26px; border-radius: 30px; text-align: center;
  background: linear-gradient(135deg, rgba(255,255,255,0.75), rgba(238,242,255,0.55) 60%, rgba(253,242,255,0.6));
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  backdrop-filter: blur(26px) saturate(170%);
  -webkit-backdrop-filter: blur(26px) saturate(170%);
}
.sm-hero::before {
  content: ""; position: absolute; inset: 0; border-radius: 30px; padding: 1px;
  background: linear-gradient(120deg, rgba(214,169,44,0.55), rgba(124,58,237,0.25), rgba(14,165,233,0.35));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude; pointer-events: none;
}
.sm-hero h1 { margin: 0; font-size: 47px; font-weight: 850; color: var(--ink); letter-spacing: -1.5px; }
.sm-hero .grad {
  background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent4), var(--gold));
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.sm-hero p.sub { color: var(--ink-soft); font-size: 18px; font-weight: 650; margin-top: 8px; }
.sm-hero p.desc { color: var(--ink-faint); max-width: 700px; margin: 10px auto 0; font-size: 15px; }

/* GLASS CARD BASE -- reused everywhere below */
.sm-card, .sm-feature, .sm-metric, .sm-question, .sm-answer, .sm-warning, .sm-score-hero {
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
}

.sm-card {
  padding: 24px; border-radius: 20px; background: var(--glass-bg);
  border: 1px solid var(--glass-border); box-shadow: var(--glass-shadow);
  margin-bottom: 16px; color: var(--ink);
}
.sm-card h2, .sm-card h3, .sm-card p, .sm-card li, .sm-card b { color: var(--ink); }
.sm-card p { color: var(--ink-soft); }

.sm-feature {
  padding: 22px; border-radius: 20px; background: var(--glass-bg);
  border: 1px solid var(--glass-border); min-height: 155px;
  box-shadow: var(--glass-shadow);
  transition: transform .2s ease;
}
.sm-feature:hover { transform: translateY(-3px); }
.sm-feature .icon { font-size: 30px; margin-bottom: 8px; }
.sm-feature .title { font-weight: 750; color: var(--ink); font-size: 18px; margin-bottom: 6px; }
.sm-feature .text { color: var(--ink-soft); font-size: 14px; line-height: 1.55; }

/* METRIC CHIPS -- colored icon badge + big number, premium glass finish */
.sm-metric {
  padding: 20px 22px; border-radius: 20px; background: var(--glass-bg);
  border: 1px solid var(--glass-border); box-shadow: var(--glass-shadow);
}
.sm-metric .row { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.sm-metric .chip {
  width: 28px; height: 28px; border-radius: 9px; display: flex; align-items: center;
  justify-content: center; font-size: 14px; font-weight: 800;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}
.sm-metric .label { color: var(--ink-soft); font-weight: 650; font-size: 15px; }
.sm-metric .value { color: var(--ink); font-weight: 850; font-size: 32px; }
.chip-blue   { background: linear-gradient(135deg, #c7d2fe, #a5b4fc); color: #3730a3; }
.chip-cyan   { background: linear-gradient(135deg, #bae6fd, #7dd3fc); color: #075985; }
.chip-orange { background: linear-gradient(135deg, #fed7aa, #fdba74); color: #9a3412; }

/* QUESTION / ANSWER / WARNING -- glass with colored left rail */
.sm-question {
  padding: 20px; margin-bottom: 14px; border-radius: 18px; background: var(--glass-bg-soft);
  border: 1px solid rgba(79,70,229,0.18); border-left: 5px solid var(--accent1);
  box-shadow: var(--glass-shadow);
}
.sm-question .label { color: var(--accent1); font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .6px; margin-bottom: 6px; }

.sm-answer {
  padding: 22px; margin-top: 14px; border-radius: 18px; background: rgba(220,252,231,0.55);
  border: 1px solid rgba(34,197,94,0.25); border-left: 5px solid var(--good);
  box-shadow: var(--glass-shadow);
}
.sm-answer .title { color: #14532d; font-weight: 750; font-size: 17px; margin-bottom: 10px; }

.sm-warning {
  padding: 16px; border-radius: 16px; background: rgba(255,237,213,0.6);
  border: 1px solid rgba(249,115,22,0.28); color: #7c2d12;
  box-shadow: var(--glass-shadow);
}

/* QUIZ */
.sm-quiz-progress { color: var(--ink-faint); font-size: 13px; font-weight: 750; text-transform: uppercase; letter-spacing: .5px; }
.sm-quiz-topic {
  display: inline-block; padding: 4px 13px; border-radius: 999px; font-size: 12px; font-weight: 750;
  background: linear-gradient(135deg, rgba(219,39,119,0.16), rgba(124,58,237,0.14));
  color: var(--accent4); margin-bottom: 10px; border: 1px solid rgba(219,39,119,0.2);
}
.sm-quiz-q { font-size: 20px; font-weight: 750; color: var(--ink); margin-bottom: 6px; }
.sm-result-correct { color: var(--good); font-weight: 750; }
.sm-result-wrong { color: var(--bad); font-weight: 750; }

.sm-score-hero {
  text-align: center; padding: 40px; border-radius: 26px;
  background: linear-gradient(135deg, rgba(220,252,231,0.55), rgba(238,242,255,0.55), rgba(253,242,255,0.55));
  border: 1px solid var(--glass-border); box-shadow: var(--glass-shadow);
}
.sm-score-hero .big {
  font-size: 60px; font-weight: 850;
  background: linear-gradient(90deg, var(--accent1), var(--gold));
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.sm-score-hero .pct { font-size: 21px; font-weight: 750; color: var(--accent1); }

.sm-tag-weak { background: rgba(220,38,38,0.12); color: var(--bad); padding: 4px 12px; border-radius: 999px; font-size: 13px; font-weight: 750; margin: 3px; display: inline-block; border: 1px solid rgba(220,38,38,0.2); }
.sm-tag-strong { background: rgba(22,163,74,0.12); color: var(--good); padding: 4px 12px; border-radius: 999px; font-size: 13px; font-weight: 750; margin: 3px; display: inline-block; border: 1px solid rgba(22,163,74,0.2); }

/* BUTTONS -- premium gradient with gold-tinted glow */
.stButton > button {
  width: 100%; min-height: 46px; border: none; border-radius: 13px; font-weight: 750; color: white !important;
  background: linear-gradient(135deg, var(--accent1) 0%, var(--accent2) 55%, var(--accent4) 100%);
  box-shadow: 0 10px 24px rgba(124,58,237,0.30), 0 0 0 1px rgba(255,255,255,0.15) inset;
  transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 16px 32px rgba(124,58,237,0.38), 0 0 0 1px rgba(214,169,44,0.4) inset; }

/* SIDEBAR -- frosted glass panel */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255,255,255,0.75), rgba(238,240,251,0.7));
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
  border-right: 1px solid rgba(255,255,255,0.5);
}
[data-testid="stFileUploader"] {
  padding: 8px; border-radius: 18px; background: rgba(255,255,255,0.5);
  border: 1.5px dashed rgba(124,58,237,0.4); backdrop-filter: blur(10px);
}
[data-testid="stMetric"] {
  padding: 14px; border-radius: 16px; background: rgba(255,255,255,0.6);
  border: 1px solid var(--glass-border); backdrop-filter: blur(14px);
}

/* FLAT SCROLLABLE TAB ROW -- glass pill bar */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px; padding: 7px; border-radius: 18px; background: var(--glass-bg);
  border: 1px solid var(--glass-border); box-shadow: var(--glass-shadow);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  overflow-x: auto; flex-wrap: nowrap;
}
.stTabs [data-baseweb="tab"] { border-radius: 11px; padding: 10px 16px; font-weight: 700; color: var(--ink-soft); white-space: nowrap; }
.stTabs [aria-selected="true"] {
  color: white !important;
  background: linear-gradient(135deg, var(--accent1), var(--accent2)) !important;
}

@media (max-width: 768px) {
  .sm-hero { padding: 32px 16px; }
  .sm-hero h1 { font-size: 32px; }
}
</style>
""")

# ============================================================
# GROQ CLIENT
# ============================================================

MODEL_CANDIDATES = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            api_key = None
    if not api_key:
        st.error("Groq API key is not configured. Set GROQ_API_KEY as an env var or in Streamlit Secrets.")
        return None
    return Groq(api_key=api_key)


def ask_groq(prompt, system_message=None, max_tokens=2000):
    client = get_groq_client()
    if client is None:
        return ""
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    last_error = None
    for model in MODEL_CANDIDATES:
        try:
            response = client.chat.completions.create(
                model=model, messages=messages, temperature=0.2, max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            continue
    st.error(f"Groq API error: {last_error}")
    return ""


# ============================================================
# PDF EXTRACTION / CLEANING / CHUNKING
# ============================================================

def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        pages = []
        for n, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                pages.append(f"\n[PAGE {n}]\n{text}")
        return "\n".join(pages)
    except Exception as e:
        st.error(f"Could not read the PDF: {e}")
        return ""


def clean_text(text):
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text, chunk_size=7000):
    words = text.split()
    chunks, current, length = [], [], 0
    for w in words:
        current.append(w)
        length += len(w) + 1
        if length >= chunk_size:
            chunks.append(" ".join(current))
            current, length = [], 0
    if current:
        chunks.append(" ".join(current))
    return chunks


def get_relevant_chunks(text, query, max_chunks=8):
    chunks = chunk_text(text, chunk_size=7000)
    if not chunks:
        return ""
    query_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", query.lower()))
    scored = []
    for i, chunk in enumerate(chunks):
        chunk_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", chunk.lower()))
        scored.append((len(query_words & chunk_words), i, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = sorted(scored[:max_chunks], key=lambda x: x[1])
    return "\n\n".join(c for _, _, c in selected)


# ============================================================
# JSON QUIZ GENERATION (structured, not regex-parsed)
# ============================================================

QUIZ_SYSTEM_MSG = (
    "You are a quiz generation engine. Respond with ONLY valid JSON — "
    "no markdown, no code fences, no commentary. The JSON must be a list of objects "
    'with keys: "question" (string), "options" (object with keys A,B,C,D), '
    '"correct" (one of "A","B","C","D"), "explanation" (string), '
    '"topic" (short 2-4 word label). Base everything strictly on the material given.'
)

def _strip_json_fences(raw):
    raw = raw.strip()
    raw = re.sub(r"^```(json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return raw


def generate_quiz_questions(text, count, difficulty):
    context = get_relevant_chunks(text, "important exam concepts facts definitions processes", max_chunks=10)
    prompt = f"""Create exactly {count} multiple-choice questions at {difficulty} difficulty
from the study material below. Return ONLY the JSON array described in the system message.

STUDY MATERIAL:
{context}
"""
    raw = ask_groq(prompt, system_message=QUIZ_SYSTEM_MSG, max_tokens=4000)
    if not raw:
        return None
    try:
        data = json.loads(_strip_json_fences(raw))
        cleaned = [q for q in data if all(k in q for k in ("question", "options", "correct", "explanation", "topic"))
                   and all(k in q["options"] for k in ("A", "B", "C", "D"))]
        return cleaned or None
    except Exception as e:
        st.error(f"Couldn't parse the generated quiz as JSON: {e}")
        with st.expander("Raw model output (for debugging)"):
            st.code(raw)
        return None


# ============================================================
# SCORE HISTORY (local JSON — resets on Streamlit Cloud restart)
# ============================================================

HISTORY_FILE = "study_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_attempt(document_name, score, total, topic_results):
    history = load_history()
    history.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "document": document_name, "score": score, "total": total, "topics": topic_results,
    })
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        st.warning(f"Couldn't save this attempt to history: {e}")
    return history


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "pdf_text": "", "document_name": "",
    "quiz_questions": None, "quiz_index": 0, "quiz_answers": [],
    "quiz_locked": False, "quiz_finished": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_quiz():
    st.session_state.quiz_questions = None
    st.session_state.quiz_index = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_locked = False
    st.session_state.quiz_finished = False


def metric_card(chip_class, icon, label, value):
    html(f"""
    <div class="sm-metric">
      <div class="row"><span class="chip {chip_class}">{icon}</span><span class="label">{label}</span></div>
      <div class="value">{value}</div>
    </div>
    """)


# ============================================================
# HERO
# ============================================================

html("""
<div class="sm-hero">
  <div style="font-size:54px;">🧠</div>
  <h1>AI <span class="grad">StudyMate Pro</span></h1>
  <p class="sub">Your Personal AI-Powered Study Assistant</p>
  <p class="desc">Upload your lecture notes or PDF and transform them into clear,
  organized, exam-ready study material — then test yourself and track your progress.</p>
</div>
""")

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 📄 Upload Your Notes")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

    if uploaded_file:
        if st.session_state.document_name != uploaded_file.name:
            with st.spinner("Reading your PDF..."):
                text = clean_text(extract_pdf_text(uploaded_file))
                st.session_state.pdf_text = text
                st.session_state.document_name = uploaded_file.name
                reset_quiz()
        if st.session_state.pdf_text:
            st.success("✓ PDF loaded successfully")
            word_count = len(st.session_state.pdf_text.split())
            page_count = st.session_state.pdf_text.count("[PAGE ")
            st.metric("📖 Words", f"{word_count:,}")
            st.metric("📄 Pages", page_count)

    st.divider()
    st.markdown("### ⚙️ Study Settings")
    question_count = st.slider("Number of questions", 3, 15, 5)
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "University Exam"])

    st.divider()
    if st.button("🔄 Reset Test"):
        reset_quiz()
        st.rerun()

    st.divider()
    html("""
    <div class="sm-card">
      <b>💡 Study Tip</b><br><br>
      For the best results, upload clear lecture notes or textbook PDFs.
    </div>
    """)

# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.pdf_text:
    html("""
    <div class="sm-card">
      <h2>👋 Welcome to AI StudyMate</h2>
      <p>Upload your study material from the sidebar and transform it into personalized exam preparation.</p>
    </div>
    """)
    c1, c2, c3 = st.columns(3)
    for col, icon, title, text in [
        (c1, "📚", "Learn", "Generate summaries, explanations, definitions and key concepts."),
        (c2, "📝", "Practice", "Generate MCQs, short questions, long questions and flashcards."),
        (c3, "🎯", "Prepare", "Analyze difficulty and test yourself with a graded exam-style test."),
    ]:
        with col:
            html(f'<div class="sm-feature"><div class="icon">{icon}</div><div class="title">{title}</div><div class="text">{text}</div></div>')
    html('<div class="sm-warning"><b>📌 Important</b><br><br>Text-based PDFs work best. Image-only scanned PDFs may require OCR.</div>')
    st.stop()

# ============================================================
# DOCUMENT HEADER  (Words / Characters / Difficulty — restored)
# ============================================================

html(f'<div style="display:flex; align-items:center; gap:10px; font-size:26px; font-weight:800; color:var(--ink); margin-bottom:14px;">📄 {st.session_state.document_name}</div>')

m1, m2, m3 = st.columns(3)
with m1:
    metric_card("chip-blue", "📖", "Words", f"{len(st.session_state.pdf_text.split()):,}")
with m2:
    metric_card("chip-cyan", "🔤", "Characters", f"{len(st.session_state.pdf_text):,}")
with m3:
    metric_card("chip-orange", "🎯", "Difficulty", difficulty)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# FLAT TAB ROW — everything in one scrollable line
# ============================================================

tabs = st.tabs([
    "📚 Summary", "📝 Questions", "❓ MCQs", "🎴 Flashcards",
    "📖 Long Questions", "🎯 Short Questions", "🔍 Key Concepts",
    "📊 Difficulty", "🧪 Practice Test", "📈 Analytics", "💬 Ask PDF",
])

# ---------------- SUMMARY ----------------
with tabs[0]:
    st.header("📚 Chapter Summary")
    st.caption("Generate an organized, exam-focused summary.")
    if st.button("✨ Generate Summary", key="gen_summary"):
        context = get_relevant_chunks(st.session_state.pdf_text, "overview main ideas important concepts", max_chunks=10)
        prompt = f"""Create a clear, organized, exam-focused summary of this material.
Structure it with: 1. Chapter Overview 2. Main Concepts 3. Important Definitions
4. Important Facts 5. Processes / Mechanisms 6. Exam-Focused Points 7. Quick Revision.

STUDY MATERIAL:
{context}"""
        with st.spinner("AI StudyMate is analyzing your material..."):
            result = ask_groq(prompt, max_tokens=2600)
        if result:
            html(f'<div class="sm-answer"><div class="title">📚 AI Study Summary</div></div>')
            st.markdown(result)

# ---------------- IMPORTANT QUESTIONS ----------------
with tabs[1]:
    st.header("📝 Important Exam Questions")
    st.caption("Generate questions based strictly on your uploaded material.")
    if st.button("✨ Generate Important Questions", key="gen_iq"):
        context = get_relevant_chunks(st.session_state.pdf_text, "important concepts topics definitions processes exam", max_chunks=8)
        prompt = f"""Create {question_count} important university exam questions from the material below.
Difficulty: {difficulty}. Prioritize core concepts, processes, definitions, comparisons, cause and effect.
Return numbered questions only.

STUDY MATERIAL:
{context}"""
        with st.spinner("Finding the most important questions..."):
            result = ask_groq(prompt, max_tokens=1800)
        if result:
            lines = [l.strip() for l in result.split("\n") if l.strip()]
            for i, q in enumerate(lines[:question_count]):
                html(f'<div class="sm-question"><div class="label">Question {i+1}</div></div>')
                st.write(q)

# ---------------- MCQS (interactive JSON, browsable) ----------------
with tabs[2]:
    st.header("❓ Multiple Choice Questions")
    st.caption("Generate exam-style MCQs with answers and explanations.")
    if st.button("✨ Generate MCQs", key="gen_mcq"):
        with st.spinner("Generating your MCQs..."):
            questions = generate_quiz_questions(st.session_state.pdf_text, question_count, difficulty)
        if questions:
            for i, q in enumerate(questions, 1):
                with st.expander(f"Q{i}. {q['question']}"):
                    for letter, opt in q["options"].items():
                        st.write(f"**{letter})** {opt}")
                    st.success(f"Correct Answer: {q['correct']} — {q['explanation']}")

# ---------------- FLASHCARDS ----------------
with tabs[3]:
    st.header("🎴 Flashcards")
    st.caption("Turn important concepts into quick revision cards.")
    if st.button("✨ Generate Flashcards", key="gen_flash"):
        with st.spinner("Creating your flashcards..."):
            questions = generate_quiz_questions(st.session_state.pdf_text, question_count, difficulty)
        if questions:
            for i, q in enumerate(questions, 1):
                with st.expander(f"🎴 Flashcard {i}: {q['topic']}"):
                    st.write(f"**Q:** {q['question']}")
                    st.write(f"**A:** {q['options'][q['correct']]}")
                    st.caption(q["explanation"])

# ---------------- LONG QUESTIONS ----------------
with tabs[4]:
    st.header("📖 Long Questions")
    st.caption("Prepare detailed university examination questions.")
    if st.button("✨ Generate Long Questions", key="gen_long"):
        context = get_relevant_chunks(st.session_state.pdf_text, "process explain discuss compare analyze describe", max_chunks=8)
        prompt = f"""Create {question_count} long-answer university examination questions.
Difficulty: {difficulty}. Focus on Explain / Discuss / Analyze / Compare / Describe processes / Cause and effect.
Return only numbered questions.

STUDY MATERIAL:
{context}"""
        with st.spinner("Generating long questions..."):
            result = ask_groq(prompt, max_tokens=1800)
        if result:
            html('<div class="sm-card"></div>')
            st.markdown(result)

# ---------------- SHORT QUESTIONS ----------------
with tabs[5]:
    st.header("🎯 Short Questions")
    st.caption("Practice definitions, facts and short conceptual questions.")
    if st.button("✨ Generate Short Questions", key="gen_short"):
        context = get_relevant_chunks(st.session_state.pdf_text, "definitions facts terms concepts differences", max_chunks=8)
        prompt = f"""Create {question_count} short-answer questions from this study material.
Focus on Definitions / Facts / Important terms / Differences / Basic concepts.
Return only numbered questions.

STUDY MATERIAL:
{context}"""
        with st.spinner("Generating short questions..."):
            result = ask_groq(prompt, max_tokens=1800)
        if result:
            html('<div class="sm-card"></div>')
            st.markdown(result)

# ---------------- KEY CONCEPTS ----------------
with tabs[6]:
    st.header("🔍 Key Concepts")
    st.caption("Extract the concepts you should know before your exam.")
    if st.button("✨ Extract Key Concepts", key="gen_concepts"):
        context = get_relevant_chunks(st.session_state.pdf_text, "main concepts important ideas definitions topics", max_chunks=8)
        prompt = f"""Identify the most important concepts in the study material.
For every concept provide: CONCEPT / Short explanation / Why it matters for the exam.

STUDY MATERIAL:
{context}"""
        with st.spinner("Identifying key concepts..."):
            result = ask_groq(prompt, max_tokens=2600)
        if result:
            html('<div class="sm-card"></div>')
            st.markdown(result)

# ---------------- DIFFICULTY ANALYSIS ----------------
with tabs[7]:
    st.header("📊 Difficulty Analysis")
    st.caption("Find the topics that may require the most preparation.")
    if st.button("✨ Analyze Difficulty", key="gen_diff"):
        context = get_relevant_chunks(st.session_state.pdf_text, "complex difficult advanced conceptual process", max_chunks=8)
        prompt = f"""Analyze the difficulty of this study material. Provide:
1. Overall difficulty 2. Easy topics 3. Medium topics 4. Difficult topics
5. Concepts requiring memorization 6. Concepts requiring deep understanding
7. Topics most likely to challenge students 8. Recommended study priority.

STUDY MATERIAL:
{context}"""
        with st.spinner("Analyzing difficulty..."):
            result = ask_groq(prompt, max_tokens=2600)
        if result:
            html('<div class="sm-card"></div>')
            st.markdown(result)

# ---------------- PRACTICE TEST (graded, interactive) ----------------
with tabs[8]:
    st.header("🧪 Practice Test")
    st.caption("Answers are hidden until you submit each question — no peeking.")

    if st.session_state.quiz_questions is None:
        if st.button("🚀 Start New Test", key="start_test"):
            with st.spinner("Preparing your practice test..."):
                questions = generate_quiz_questions(st.session_state.pdf_text, question_count, difficulty)
            if questions:
                st.session_state.quiz_questions = questions
                st.session_state.quiz_index = 0
                st.session_state.quiz_answers = []
                st.session_state.quiz_locked = False
                st.session_state.quiz_finished = False
                st.rerun()

    elif not st.session_state.quiz_finished:
        questions = st.session_state.quiz_questions
        idx = st.session_state.quiz_index
        q = questions[idx]

        html(f'<div class="sm-quiz-progress">Question {idx + 1} of {len(questions)}</div>')
        html(f'<div class="sm-quiz-topic">{q["topic"]}</div>')
        html(f'<div class="sm-quiz-q">{q["question"]}</div>')

        option_labels = [f"{letter}) {text}" for letter, text in q["options"].items()]
        choice = st.radio("Choose an answer:", option_labels, key=f"choice_{idx}",
                           disabled=st.session_state.quiz_locked, label_visibility="collapsed")
        chosen_letter = choice.split(")")[0] if choice else None

        if not st.session_state.quiz_locked:
            if st.button("✅ Submit Answer", key=f"submit_{idx}"):
                is_correct = chosen_letter == q["correct"]
                st.session_state.quiz_answers.append({
                    "topic": q["topic"], "correct": is_correct,
                    "chosen": chosen_letter, "answer": q["correct"],
                })
                st.session_state.quiz_locked = True
                st.rerun()
        else:
            last = st.session_state.quiz_answers[-1]
            if last["correct"]:
                st.markdown('<span class="sm-result-correct">✔ Correct!</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="sm-result-wrong">✘ Not quite — correct answer: {q["correct"]}</span>', unsafe_allow_html=True)
            st.caption(q["explanation"])

            if idx + 1 < len(questions):
                if st.button("➡️ Next Question", key=f"next_{idx}"):
                    st.session_state.quiz_index += 1
                    st.session_state.quiz_locked = False
                    st.rerun()
            else:
                if st.button("🏁 Finish Test", key="finish_test"):
                    st.session_state.quiz_finished = True
                    st.rerun()

    else:
        answers = st.session_state.quiz_answers
        score = sum(1 for a in answers if a["correct"])
        total = len(answers)
        pct = round((score / total) * 100) if total else 0

        topic_stats = defaultdict(lambda: {"correct": 0, "wrong": 0})
        for a in answers:
            topic_stats[a["topic"]]["correct" if a["correct"] else "wrong"] += 1

        if st.session_state.get("last_saved_index") != id(answers):
            save_attempt(st.session_state.document_name, score, total, dict(topic_stats))
            st.session_state["last_saved_index"] = id(answers)

        verdict = "Excellent! 🔥" if pct >= 80 else "Good work 👍" if pct >= 60 else "Keep practicing 💪"
        html(f'<div class="sm-score-hero"><div class="big">{score}/{total}</div><div class="pct">{pct}% — {verdict}</div></div>')

        weak = [t for t, s in topic_stats.items() if s["wrong"] > s["correct"]]
        strong = [t for t, s in topic_stats.items() if s["correct"] > s["wrong"]]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Weak topics**")
            html("".join(f'<span class="sm-tag-weak">{t}</span>' for t in weak) or "<i>None — nice.</i>")
        with col2:
            st.markdown("**Strong topics**")
            html("".join(f'<span class="sm-tag-strong">{t}</span>' for t in strong) or "<i>None yet.</i>")

        if st.button("🔄 Take Another Test", key="retake"):
            reset_quiz()
            st.rerun()

# ---------------- ANALYTICS ----------------
with tabs[9]:
    st.header("📈 Study Analytics")
    history = load_history()
    doc_history = [h for h in history if h["document"] == st.session_state.document_name]

    if not doc_history:
        html('<div class="sm-card"><p>No test attempts yet for this document. Take a Practice Test to see your analytics here.</p></div>')
    else:
        scores_pct = [round((h["score"] / h["total"]) * 100) for h in doc_history]
        st.markdown("#### Score History")
        st.line_chart(scores_pct)

        all_topics = Counter()
        weak_topics = Counter()
        for h in doc_history:
            for topic, stats in h["topics"].items():
                all_topics[topic] += stats["correct"] + stats["wrong"]
                if stats["wrong"] > stats["correct"]:
                    weak_topics[topic] += 1

        st.markdown("#### Topics needing the most work")
        if weak_topics:
            for topic, count in weak_topics.most_common(5):
                st.write(f"- **{topic}** — missed more than answered in {count} attempt(s)")
        else:
            st.write("No consistently weak topics detected yet.")

        st.markdown("#### Recommended revision order")
        recommended = [t for t, _ in weak_topics.most_common()] or [t for t, _ in all_topics.most_common(3)]
        for i, t in enumerate(recommended[:5], 1):
            st.write(f"{i}. {t}")

        st.caption("Note: history is stored locally to this app instance and resets if the app restarts or redeploys.")

# ---------------- ASK PDF ----------------
with tabs[10]:
    st.header("💬 Ask Questions About Your PDF")
    st.caption("Ask questions and StudyMate will search your uploaded material.")
    user_question = st.text_input("Your question", placeholder="e.g. Explain the process of stellar evolution.")
    if st.button("🤖 Ask StudyMate", key="ask_pdf"):
        if not user_question.strip():
            st.warning("Please enter a question first.")
        else:
            context = get_relevant_chunks(st.session_state.pdf_text, user_question, max_chunks=7)
            prompt = f"""Answer the student's question using ONLY the information in the provided PDF material.
If the answer cannot be found, say clearly: "The answer is not available in the uploaded PDF."
Do not invent facts. Explain clearly, use bullet points if useful.

PDF MATERIAL:
{context}

STUDENT QUESTION:
{user_question}"""
            with st.spinner("Searching your PDF and thinking..."):
                answer = ask_groq(prompt, max_tokens=2500)
            if answer:
                html('<div class="sm-answer"><div class="title">🤖 StudyMate Answer</div></div>')
                st.markdown(answer)

# ============================================================
# FOOTER
# ============================================================

html("""
<div style="margin-top:44px; padding:26px; text-align:center; color:#94a3b8; font-size:13px; border-top:1px solid rgba(20,20,40,0.08);">
  🧠 AI StudyMate Pro — Powered by Groq · Built with Python & Streamlit
</div>
""")
