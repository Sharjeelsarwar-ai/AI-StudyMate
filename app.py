import streamlit as st
import os
from pypdf import PdfReader
from groq import Groq
import re


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI StudyMate",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HTML RENDERING HELPER
# ============================================================

def render_html(html, **kwargs):
    """Render trusted app HTML without Markdown code-block parsing."""
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 5% 5%,
                rgba(99, 102, 241, 0.12),
                transparent 28%
            ),
            radial-gradient(
                circle at 95% 5%,
                rgba(168, 85, 247, 0.12),
                transparent 28%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(14, 165, 233, 0.08),
                transparent 35%
            ),
            #f7f8fc;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        position: relative;
        overflow: hidden;

        padding: 50px 30px;

        margin-bottom: 30px;

        text-align: center;

        border-radius: 30px;

        background:
            linear-gradient(
                135deg,
                rgba(255,255,255,0.88),
                rgba(238,242,255,0.76)
            );

        border:
            1px solid rgba(255,255,255,0.95);

        box-shadow:
            0 22px 65px rgba(15,23,42,0.08),
            inset 0 1px 0 rgba(255,255,255,1);

        backdrop-filter: blur(22px);
        -webkit-backdrop-filter: blur(22px);
    }

    .hero::before {
        content: "";

        position: absolute;

        width: 300px;
        height: 300px;

        left: -100px;
        top: -170px;

        border-radius: 50%;

        background:
            rgba(99,102,241,0.16);

        filter: blur(60px);

        pointer-events: none;
    }

    .hero::after {
        content: "";

        position: absolute;

        width: 280px;
        height: 280px;

        right: -100px;
        bottom: -170px;

        border-radius: 50%;

        background:
            rgba(168,85,247,0.14);

        filter: blur(60px);

        pointer-events: none;
    }

    .hero-inner {
        position: relative;
        z-index: 2;
    }

    .hero-icon {
        font-size: 58px;
        line-height: 1;

        margin-bottom: 12px;
    }

    .hero-title {
        margin: 0;

        color: #172033;

        font-size: 50px;

        font-weight: 850;

        letter-spacing: -2px;

        line-height: 1.1;
    }

    .hero-gradient {
        background:
            linear-gradient(
                90deg,
                #4f46e5,
                #7c3aed,
                #2563eb
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        background-clip: text;
    }

    .hero-subtitle {
        margin-top: 15px;

        color: #475569;

        font-size: 20px;

        font-weight: 650;
    }

    .hero-description {
        max-width: 730px;

        margin: 12px auto 0;

        color: #64748b;

        font-size: 16px;

        line-height: 1.7;
    }


    /* ========================================================
       GLASS CARDS
       ======================================================== */

    .glass-card {
        padding: 24px;

        margin-bottom: 18px;

        border-radius: 20px;

        background:
            rgba(255,255,255,0.72);

        border:
            1px solid rgba(255,255,255,0.95);

        box-shadow:
            0 12px 35px rgba(15,23,42,0.06),
            inset 0 1px 0 rgba(255,255,255,0.9);

        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
    }


    /* ========================================================
       FEATURE CARDS
       ======================================================== */

    .feature-card {
        min-height: 165px;

        padding: 24px;

        border-radius: 20px;

        background:
            rgba(255,255,255,0.72);

        border:
            1px solid rgba(255,255,255,0.95);

        box-shadow:
            0 12px 35px rgba(15,23,42,0.05);

        backdrop-filter: blur(18px);
    }

    .feature-icon {
        font-size: 32px;

        margin-bottom: 10px;
    }

    .feature-title {
        color: #172033;

        font-size: 19px;

        font-weight: 750;

        margin-bottom: 8px;
    }

    .feature-text {
        color: #64748b;

        font-size: 14px;

        line-height: 1.6;
    }


    /* ========================================================
       QUESTION CARDS
       ======================================================== */

    .question-card {
        padding: 22px;

        margin-bottom: 15px;

        border-radius: 18px;

        background:
            rgba(255,255,255,0.78);

        border:
            1px solid rgba(99,102,241,0.14);

        border-left:
            5px solid #6366f1;

        box-shadow:
            0 8px 25px rgba(15,23,42,0.05);
    }

    .question-label {
        color: #6366f1;

        font-size: 12px;

        font-weight: 800;

        text-transform: uppercase;

        letter-spacing: 0.8px;

        margin-bottom: 8px;
    }


    /* ========================================================
       ANSWER CARD
       ======================================================== */

    .answer-card {
        padding: 24px;

        margin-top: 18px;

        border-radius: 18px;

        background:
            rgba(240,253,244,0.80);

        border:
            1px solid rgba(34,197,94,0.18);

        border-left:
            5px solid #22c55e;

        box-shadow:
            0 8px 25px rgba(34,197,94,0.06);
    }

    .answer-title {
        color: #166534;

        font-size: 18px;

        font-weight: 750;

        margin-bottom: 12px;
    }


    /* ========================================================
       INFO CARD
       ======================================================== */

    .info-card {
        padding: 18px;

        border-radius: 16px;

        background:
            rgba(239,246,255,0.80);

        border:
            1px solid rgba(59,130,246,0.15);

        color: #1e40af;
    }


    /* ========================================================
       WARNING
       ======================================================== */

    .warning-card {
        padding: 18px;

        margin-top: 15px;

        border-radius: 16px;

        background:
            rgba(255,247,237,0.86);

        border:
            1px solid rgba(249,115,22,0.18);

        color: #9a3412;
    }


    /* ========================================================
       TEXT
       ======================================================== */

    h1, h2, h3, h4 {
        color: #172033 !important;
    }

    p {
        color: #475569;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(248,250,252,0.97),
                rgba(241,245,249,0.94)
            );

        border-right:
            1px solid rgba(148,163,184,0.15);
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        width: 100%;

        min-height: 44px;

        border: none;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                #4f46e5,
                #7c3aed
            );

        color: white !important;

        font-weight: 700;

        box-shadow:
            0 8px 20px rgba(79,70,229,0.20);

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);

        box-shadow:
            0 12px 28px rgba(79,70,229,0.30);
    }


    /* ========================================================
       FILE UPLOADER
       ======================================================== */

    [data-testid="stFileUploader"] {
        padding: 10px;

        border-radius: 18px;

        background:
            rgba(255,255,255,0.62);

        border:
            1px dashed rgba(99,102,241,0.35);
    }


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {
        padding: 18px;

        border-radius: 18px;

        background:
            rgba(255,255,255,0.72);

        border:
            1px solid rgba(255,255,255,0.95);

        box-shadow:
            0 10px 30px rgba(15,23,42,0.05);

        backdrop-filter: blur(15px);
    }

    [data-testid="stMetricLabel"] {
        color: #64748b !important;

        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #172033 !important;

        font-weight: 800;
    }


    /* ========================================================
       TABS
       ======================================================== */

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;

        padding: 7px;

        border-radius: 16px;

        background:
            rgba(255,255,255,0.70);

        border:
            1px solid rgba(255,255,255,0.95);

        box-shadow:
            0 8px 25px rgba(15,23,42,0.05);

        overflow-x: auto;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;

        padding: 10px 15px;

        color: #64748b;

        font-weight: 650;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        margin-top: 50px;

        padding: 30px;

        text-align: center;

        border-top:
            1px solid rgba(148,163,184,0.15);
    }

    .footer-title {
        color: #475569;

        font-size: 15px;

        font-weight: 750;
    }

    .footer-text {
        color: #94a3b8;

        font-size: 13px;

        margin-top: 6px;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 768px) {

        .hero {
            padding: 36px 18px;
        }

        .hero-title {
            font-size: 36px;
        }

        .hero-subtitle {
            font-size: 17px;
        }

        .hero-description {
            font-size: 14px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# GROQ CLIENT
# ============================================================

def get_groq_client():
    try:
        # Colab / local environment
        api_key = os.environ.get("GROQ_API_KEY")

        # Streamlit Cloud fallback
        if not api_key:
            try:
                api_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                api_key = None

        if not api_key:
            st.error("Groq API key is not configured.")
            st.info(
                "In Colab, set GROQ_API_KEY in the environment. "
                "On Streamlit Cloud, add it under App Settings → Secrets."
            )
            return None

        return Groq(api_key=api_key)

    except Exception as e:
        st.error(f"Could not initialize Groq: {e}")
        return None


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "openai/gpt-oss-120b"


# ============================================================
# GROQ GENERATION
# ============================================================

def ask_groq(
    prompt,
    system_message=None,
    max_tokens=2000
):

    client = get_groq_client()

    if client is None:
        return ""

    try:

        messages = []

        if system_message:

            messages.append(
                {
                    "role": "system",
                    "content": system_message
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.2,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    except Exception as e:

        st.error(
            f"Groq API error: {str(e)}"
        )

        return ""


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(uploaded_file):

    try:

        reader = PdfReader(
            uploaded_file
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if text:

                pages.append(
                    f"\n[PAGE {page_number}]\n{text}"
                )

        return "\n".join(pages)

    except Exception as e:

        st.error(
            f"Could not read the PDF: {e}"
        )

        return ""


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = text.replace(
        "\x00",
        " "
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# CHUNK TEXT
# ============================================================

def chunk_text(
    text,
    chunk_size=9000
):

    words = text.split()

    chunks = []

    current = []

    current_length = 0

    for word in words:

        current.append(word)

        current_length += len(word) + 1

        if current_length >= chunk_size:

            chunks.append(
                " ".join(current)
            )

            current = []

            current_length = 0

    if current:

        chunks.append(
            " ".join(current)
        )

    return chunks


# ============================================================
# RELEVANCE SEARCH
# ============================================================

def get_relevant_chunks(
    text,
    question,
    max_chunks=6
):

    chunks = chunk_text(
        text,
        chunk_size=7000
    )

    if not chunks:

        return ""

    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            question.lower()
        )
    )

    scored_chunks = []

    for index, chunk in enumerate(chunks):

        chunk_words = re.findall(
            r"\b[a-zA-Z]{3,}\b",
            chunk.lower()
        )

        chunk_set = set(
            chunk_words
        )

        score = len(
            question_words.intersection(
                chunk_set
            )
        )

        scored_chunks.append(
            (
                score,
                index,
                chunk
            )
        )

    scored_chunks.sort(
        key=lambda x: x[0],
        reverse=True
    )

    selected = scored_chunks[
        :max_chunks
    ]

    selected.sort(
        key=lambda x: x[1]
    )

    return "\n\n".join(
        item[2]
        for item in selected
    )


# ============================================================
# GENERATE SUMMARY
# ============================================================

def generate_summary(text):

    chunks = chunk_text(
        text,
        chunk_size=8000
    )

    # Limit extremely huge documents
    chunks = chunks[:15]

    partial_summaries = []

    for index, chunk in enumerate(
        chunks
    ):

        prompt = f"""
You are helping a university student study.

Summarize this section of lecture material.

Focus on:
- Main ideas
- Important concepts
- Definitions
- Important facts
- Processes
- Exam-relevant information

Do not invent information.

LECTURE SECTION:

{chunk}
"""

        result = ask_groq(
            prompt,
            system_message=(
                "You are an accurate academic study assistant. "
                "Use only the provided material."
            ),
            max_tokens=1200
        )

        if result:

            partial_summaries.append(
                result
            )

    combined = "\n\n".join(
        partial_summaries
    )

    final_prompt = f"""
Create a clear, organized, exam-focused summary
from the following section summaries.

Structure the answer with:

1. Chapter Overview
2. Main Concepts
3. Important Definitions
4. Important Facts
5. Processes / Mechanisms
6. Exam-Focused Points
7. Quick Revision

SECTION SUMMARIES:

{combined}
"""

    return ask_groq(
        final_prompt,
        system_message=(
            "You are an expert university study assistant."
        ),
        max_tokens=3000
    )


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="hero-inner">

            <div class="hero-icon">
                🧠
            </div>

            <div class="hero-title">
                AI <span class="hero-gradient">StudyMate</span>
            </div>

            <div class="hero-subtitle">
                Your Personal AI-Powered Study Assistant
            </div>

            <div class="hero-description">
                Upload your lecture notes or PDF and transform
                them into clear, organized, exam-ready study material.
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "pdf_text" not in st.session_state:

    st.session_state.pdf_text = ""


if "document_name" not in st.session_state:

    st.session_state.document_name = ""


if "quiz_data" not in st.session_state:

    st.session_state.quiz_data = ""


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🧠 AI StudyMate"
    )

    st.caption(
        "Turn your lecture notes into exam-ready material."
    )

    st.divider()

    st.markdown(
        "### 📄 Upload Your Notes"
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        help="Upload a text-based PDF."
    )

    if uploaded_file:

        if (
            st.session_state.document_name
            != uploaded_file.name
        ):

            with st.spinner(
                "Reading your PDF..."
            ):

                text = extract_pdf_text(
                    uploaded_file
                )

                text = clean_text(
                    text
                )

                st.session_state.pdf_text = text

                st.session_state.document_name = (
                    uploaded_file.name
                )

                st.session_state.quiz_data = ""

        if st.session_state.pdf_text:

            st.success(
                "✓ PDF loaded successfully"
            )

            word_count = len(
                st.session_state.pdf_text.split()
            )

            page_count = (
                st.session_state.pdf_text.count(
                    "[PAGE "
                )
            )

            st.metric(
                "📖 Words",
                f"{word_count:,}"
            )

            st.metric(
                "📄 Pages",
                page_count
            )

    st.divider()

    st.markdown(
        "### ⚙️ Study Settings"
    )

    question_count = st.slider(
        "Number of questions",
        min_value=3,
        max_value=15,
        value=5
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Easy",
            "Medium",
            "Hard",
            "University Exam"
        ]
    )

    st.divider()

    render_html(
        """
        <div class="glass-card">

            <b>💡 Study Tip</b>

            <br><br>

            For the best results, upload clear
            lecture notes or textbook PDFs.

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.pdf_text:

    render_html(
        """
        <div class="glass-card">

            <h2>👋 Welcome to AI StudyMate</h2>

            <p>
                Upload your study material from the sidebar
                and transform it into personalized exam preparation.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        render_html(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    📚
                </div>

                <div class="feature-title">
                    Learn
                </div>

                <div class="feature-text">
                    Generate summaries, explanations,
                    definitions and key concepts.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        render_html(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    📝
                </div>

                <div class="feature-title">
                    Practice
                </div>

                <div class="feature-text">
                    Generate MCQs, short questions,
                    long questions and flashcards.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        render_html(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🎯
                </div>

                <div class="feature-title">
                    Prepare
                </div>

                <div class="feature-text">
                    Analyze difficulty and test yourself
                    with exam-style questions.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    render_html(
        """
        <div class="warning-card">

            <b>📌 Important</b>

            <br><br>

            Text-based PDFs work best.
            Image-only scanned PDFs may require OCR.

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# DOCUMENT HEADER
# ============================================================

st.markdown(
    f"### 📄 {st.session_state.document_name}"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "📖 Words",
        f"{len(st.session_state.pdf_text.split()):,}"
    )

with col2:

    st.metric(
        "🔤 Characters",
        f"{len(st.session_state.pdf_text):,}"
    )

with col3:

    st.metric(
        "🎯 Difficulty",
        difficulty
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "📚 Summary",
        "📝 Questions",
        "❓ MCQs",
        "🧠 Flashcards",
        "📖 Long Questions",
        "🎯 Short Questions",
        "🔍 Key Concepts",
        "📊 Difficulty",
        "🧪 Practice Test",
        "💬 Ask PDF"
    ]
)


# ============================================================
# SUMMARY
# ============================================================

with tabs[0]:

    st.header(
        "📚 Chapter Summary"
    )

    st.caption(
        "Generate an organized, exam-focused summary."
    )

    if st.button(
        "✨ Generate Summary",
        key="generate_summary"
    ):

        with st.spinner(
            "AI StudyMate is analyzing your material..."
        ):

            result = generate_summary(
                st.session_state.pdf_text
            )

        if result:

            st.markdown(
                '<div class="answer-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="answer-title">'
                '📚 AI Study Summary'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                result
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ============================================================
# IMPORTANT QUESTIONS
# ============================================================

with tabs[1]:

    st.header(
        "📝 Important Exam Questions"
    )

    st.caption(
        "Generate questions based strictly on your uploaded material."
    )

    if st.button(
        "✨ Generate Important Questions",
        key="important_questions"
    ):

        context = get_relevant_chunks(
            st.session_state.pdf_text,
            "important concepts topics definitions processes exam",
            max_chunks=8
        )

        prompt = f"""
Create {question_count} important university
exam questions from the study material below.

Difficulty:
{difficulty}

Prioritize:
- Core concepts
- Important processes
- Definitions
- Comparisons
- Cause and effect
- Frequently testable concepts

Return numbered questions only.

STUDY MATERIAL:

{context}
"""

        with st.spinner(
            "Finding the most important questions..."
        ):

            result = ask_groq(
                prompt,
                max_tokens=1800
            )

        if result:

            lines = [
                line.strip()
                for line in result.split("\n")
                if line.strip()
            ]

            for index, question in enumerate(
                lines[:question_count]
            ):

                render_html(
                    f"""
                    <div class="question-card">

                        <div class="question-label">
                            Question {index + 1}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write(
                    question
                )


# ============================================================
# MCQS
# ============================================================

with tabs[2]:

    st.header(
        "❓ Multiple Choice Questions"
    )

    st.caption(
        "Generate exam-style MCQs with answers and explanations."
    )

    if st.button(
        "✨ Generate MCQs",
        key="mcqs"
    ):

        context = get_relevant_chunks(
            st.session_state.pdf_text,
            "important facts concepts definitions processes",
            max_chunks=8
        )

        prompt = f"""
Create exactly {question_count} multiple-choice questions
from the study material.

Difficulty:
{difficulty}

For EVERY question use this format:

Question 1:
[question]

A) ...
B) ...
C) ...
D) ...

Correct Answer: [letter]
Explanation: [short explanation]

Do not use information outside the study material.

STUDY MATERIAL:

{context}
"""

        with st.spinner(
            "Generating your MCQs..."
        ):

            result = ask_groq(
                prompt,
                max_tokens=3000
            )

        if result:

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                result
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ============================================================
# FLASHCARDS
# ============================================================

with tabs[3]:

    st.header(
        "🧠 Flashcards"
    )

    st.caption(
        "Turn important concepts into quick revision cards."
    )

    if st.button(
        "✨ Generate Flashcards",
        key="flashcards"
    ):

        context = get_relevant_chunks(
            st.session_state.pdf_text,
            "definitions concepts important terms facts",
            max_chunks=8
        )

        prompt = f"""
Create {question_count} flashcards
from this study material.

Each flashcard must contain:

QUESTION:
ANSWER:

Focus on important concepts,
definitions, processes and facts.

Do not invent information.

STUDY MATERIAL:

{context}
"""

        with st.spinner(
            "Creating your flashcards..."
        ):

            result = ask_groq(
                prompt,
                max_tokens=2200
            )

        if result:

            cards = re.split(
                r"(?=QUESTION:)",
                result
            )

            for index, card in enumerate(
                cards
            ):

                if card.strip():

                    with st.expander(
                        f"🎴 Flashcard {index + 1}"
                    ):

                        st.markdown(
                            card.strip()
                        )


# ============================================================
# LONG QUESTIONS
# ============================================================

with tabs[4]:

    st.header(
        "📖 Long Questions"
    )

    st.caption(
        "Prepare detailed university examination questions."
    )

    if st.button(
        "✨ Generate Long Questions",
        key="long_questions"
    ):

        context = get_relevant_chunks(
            st.session_state.pdf_text,
            "process explain discuss compare analyze describe",
            max_chunks=8
        )

        prompt = f"""
Create {question_count} long-answer university
examination questions.

Difficulty:
{difficulty}

Questions should require detailed answers.

Focus on:
- Explain
- Discuss
- Analyze
- Compare
- Describe processes
- Cause and effect

Return only numbered questions.

STUDY MATERIAL:

{context}
"""

        with st.spinner(
            "Generating long questions..."
        ):

            result = ask_groq(
                prompt,
                max_tokens=1800
            )

        if result:

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                result
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ============================================================
# SHORT QUESTIONS
# ============================================================

with tabs[5]:

    st.header(
        "🎯 Short Questions"
    )

    st.caption(
        "Practice definitions, facts and short conceptual questions."
    )

    if st.button(
        "✨ Generate Short Questions",
        key="short_questions"
    ):

        context = get_relevant_chunks(
            st.session_state.pdf_text,
            "definitions facts terms concepts differences",
            max_chunks=8
        )

        prompt = f"""
Create {question_count} short-answer questions
from this study material.

Focus on:
- Definitions
- Facts
- Important terms
- Differences
- Basic concepts

Return only numbered questions.

STUDY MATERIAL:

{context}
"""

        with st.spinner(
            "Generating short questions..."
        ):

            result = ask_groq(
                prompt,
                max_tokens=1800
            )

        if result:

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                result
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ============================================================
# KEY CONCEPTS
# ============================================================

with tabs[6]:

    st.header(
        "🔍 Key Concepts"
    )

    st.caption(
        "Extract the concepts you should know before your exam."
    )

    if st.button(
        "✨ Extract Key Concepts",
        key="key_concepts"
    ):

        context = get_relevant_chunks(
            st.session_state.pdf_text,
            "main concepts important ideas definitions topics",
            max_chunks=8
        )

        prompt = f"""
Identify the most important concepts
in the study material.

For every concept provide:

CONCEPT:
Short explanation:
Why it matters for the exam:

Create a clear study guide.

STUDY MATERIAL:

{context}
"""

        with st.spinner(
            "Identifying key concepts..."
        ):

            result = ask_groq(
                prompt,
                max_tokens=2600
            )

        if result:

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                result
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ============================================================
# DIFFICULTY
# ============================================================

with tabs[7]:

    st.header(
        "📊 Difficulty Analysis"
    )

    st.caption(
        "Find the topics that may require the most preparation."
    )

    if st.button(
        "✨ Analyze Difficulty",
        key="difficulty_analysis"
    ):

        context = get_relevant_chunks(
            st.session_state.pdf_text,
            "complex difficult advanced conceptual process",
            max_chunks=8
        )

        prompt = f"""
Analyze the difficulty of this study material.

Provide:

1. Overall difficulty
2. Easy topics
3. Medium topics
4. Difficult topics
5. Concepts requiring memorization
6. Concepts requiring deep understanding
7. Topics most likely to challenge students
8. Recommended study priority

Base the analysis only on the material.

STUDY MATERIAL:

{context}
"""

        with st.spinner(
            "Analyzing difficulty..."
        ):

            result = ask_groq(
                prompt,
                max_tokens=2600
            )

        if result:

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                result
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ============================================================
# PRACTICE TEST
# ============================================================

with tabs[8]:

    st.header(
        "🧪 Practice Test"
    )

    st.caption(
        "Generate a complete exam-style practice test."
    )

    if st.button(
        "✨ Generate Practice Test",
        key="practice_test"
    ):

        context = get_relevant_chunks(
            st.session_state.pdf_text,
            "important exam concepts facts definitions processes",
            max_chunks=10
        )

        prompt = f"""
Create exactly {question_count} multiple-choice
practice-test questions.

Difficulty:
{difficulty}

Use this format:

QUESTION 1:
[question]

A) option
B) option
C) option
D) option

CORRECT ANSWER:
[letter]

EXPLANATION:
[explanation]

Do not reveal the answer before the options.

Use only the study material.

STUDY MATERIAL:

{context}
"""

        with st.spinner(
            "Preparing your practice test..."
        ):

            result = ask_groq(
                prompt,
                max_tokens=4000
            )

        if result:

            st.session_state.quiz_data = result

    if st.session_state.quiz_data:

        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            "### 🧪 Your Practice Test"
        )

        st.markdown(
            st.session_state.quiz_data
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# ASK PDF
# ============================================================

with tabs[9]:

    st.header(
        "💬 Ask Questions About Your PDF"
    )

    st.caption(
        "Ask questions and StudyMate will search your uploaded material."
    )

    user_question = st.text_input(
        "Your question",
        placeholder=(
            "e.g. Explain the process of stellar evolution."
        )
    )

    if st.button(
        "🤖 Ask StudyMate",
        key="ask_pdf"
    ):

        if not user_question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            with st.spinner(
                "Searching your PDF and thinking..."
            ):

                relevant_context = get_relevant_chunks(
                    st.session_state.pdf_text,
                    user_question,
                    max_chunks=7
                )

                prompt = f"""
You are an AI study assistant.

Answer the student's question using ONLY
the information in the provided PDF material.

If the answer cannot be found in the material,
say clearly:

"The answer is not available in the uploaded PDF."

Rules:

- Do not invent facts.
- Explain concepts clearly.
- Use examples only when supported by the material.
- Prefer simple university-level language.
- If useful, structure the answer with bullet points.
- Mention important terms from the material.

PDF MATERIAL:

{relevant_context}

STUDENT QUESTION:

{user_question}
"""

                answer = ask_groq(
                    prompt,
                    system_message=(
                        "You are a precise academic tutor. "
                        "You answer questions from provided "
                        "study material and avoid hallucinating."
                    ),
                    max_tokens=2500
                )

            if answer:

                st.markdown(
                    '<div class="answer-card">',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="answer-title">'
                    '🤖 StudyMate Answer'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    answer
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">

        <div class="footer-title">
            🧠 AI StudyMate
        </div>

        <div class="footer-text">
            Your Personal AI-Powered Study Assistant
            <br>
            Powered by Groq • Built with Python & Streamlit
        </div>

    </div>
    """,
    unsafe_allow_html=True
)
