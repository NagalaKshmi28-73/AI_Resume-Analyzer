"""
AI Resume Analyzer — Streamlit App
Upload a PDF resume, pick a target job role, and get an ATS score,
skill/keyword gap analysis, and AI-generated improvement suggestions.
"""
import streamlit as st
import plotly.graph_objects as go

from src.pdf_parser import extract_text_from_pdf, get_page_count
from src.skill_extractor import extract_skills
from src.ats_scorer import compute_ats_score
from src.job_matcher import list_job_roles, match_job_role
from src.llm_analyzer import generate_ai_feedback
from src.report_generator import generate_pdf_report
from src.database import init_db, save_analysis, get_history, clear_history

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
init_db()


def gauge_chart(value: float, title: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#4C6EF5"},
            "steps": [
                {"range": [0, 50], "color": "#FFE3E3"},
                {"range": [50, 75], "color": "#FFF3BF"},
                {"range": [75, 100], "color": "#D3F9D8"},
            ],
        },
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def main():
    st.title("📄 AI Resume Analyzer")
    st.caption("Upload your resume, pick a target role, and get an instant ATS + AI-powered review.")

    with st.sidebar:
        st.header("⚙️ Settings")
        job_role = st.selectbox("Target Job Role", list_job_roles())
        st.divider()
        st.header("🕘 Recent Analyses")
        history = get_history(limit=10)
        if history:
            for h in history:
                st.caption(f"**{h['filename']}** → {h['job_role']} | ATS {h['ats_score']} | Match {h['match_score']}")
            if st.button("Clear History"):
                clear_history()
                st.rerun()
        else:
            st.caption("No analyses yet.")

    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()

        if st.button("🔍 Analyze Resume", type="primary"):
            with st.spinner("Extracting text from PDF..."):
                resume_text = extract_text_from_pdf(file_bytes)

            if not resume_text.strip():
                st.error("Could not extract any text from this PDF. It may be a scanned image — try a text-based PDF.")
                return

            with st.spinner("Extracting skills..."):
                skills_found = extract_skills(resume_text)

            with st.spinner("Computing ATS score..."):
                ats_result = compute_ats_score(resume_text)

            with st.spinner(f"Matching against '{job_role}'..."):
                match_result = match_job_role(skills_found, resume_text, job_role)

            with st.spinner("Generating AI-powered feedback... (this can take a few seconds)"):
                ai_feedback = generate_ai_feedback(
                    resume_text, job_role,
                    match_result["missing_required"], match_result["missing_preferred"],
                )

            save_analysis(
                uploaded_file.name, job_role,
                ats_result["total_score"], match_result["match_score"],
                skills_found, match_result["missing_required"],
            )

            st.session_state["last_result"] = {
                "filename": uploaded_file.name,
                "job_role": job_role,
                "resume_text": resume_text,
                "skills_found": skills_found,
                "ats_result": ats_result,
                "match_result": match_result,
                "ai_feedback": ai_feedback,
                "page_count": get_page_count(file_bytes),
            }

    if "last_result" in st.session_state:
        render_results(st.session_state["last_result"])


def render_results(result):
    ats = result["ats_result"]
    match = result["match_result"]
    ai = result["ai_feedback"]

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(gauge_chart(ats["total_score"], "ATS Compatibility Score"), use_container_width=True)
    with col2:
        st.plotly_chart(gauge_chart(match["match_score"], f"Match: {match['job_role']}"), use_container_width=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🧩 Skills & Keywords", "📊 ATS Breakdown", "🤖 AI Feedback", "📥 Download Report"])

    with tab1:
        st.subheader("Skills Found in Resume")
        st.write(", ".join(result["skills_found"]) or "No known skills detected.")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("✅ Matched Required Skills")
            st.write(", ".join(match["matched_required"]) or "None")
            st.subheader("❌ Missing Required Skills")
            st.write(", ".join(match["missing_required"]) or "None — great coverage!")
        with c2:
            st.subheader("✅ Matched Preferred Skills")
            st.write(", ".join(match["matched_preferred"]) or "None")
            st.subheader("⚠️ Missing Preferred Skills")
            st.write(", ".join(match["missing_preferred"]) or "None — great coverage!")

    with tab2:
        st.subheader("Score Breakdown")
        for key, item in ats["breakdown"].items():
            label = key.replace("_", " ").title()
            st.progress(item["score"] / item["max"], text=f"{label}: {item['score']} / {item['max']}")
        st.subheader("Contact Info Detected")
        st.json(ats["contact_info"])
        st.subheader("Sections Detected")
        st.write(", ".join(ats["sections_found"]) or "None detected")
        st.caption(f"Page count: {result['page_count']}")

    with tab3:
        st.subheader("Summary")
        st.write(ai.get("summary", ""))
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💪 Strengths")
            for s in ai.get("strengths", []):
                st.markdown(f"- {s}")
        with c2:
            st.subheader("🔧 Areas to Improve")
            for w in ai.get("weaknesses", []):
                st.markdown(f"- {w}")
        st.subheader("📌 Improvement Suggestions")
        for s in ai.get("improvement_suggestions", []):
            st.markdown(f"- {s}")
        rewrites = ai.get("rewrite_examples", [])
        if rewrites:
            st.subheader("✍️ Suggested Rewrites")
            for ex in rewrites:
                st.markdown(f"**Before:** {ex.get('original','')}")
                st.markdown(f"**After:** {ex.get('improved','')}")
                st.divider()

    with tab4:
        st.write("Generate a polished PDF report of this analysis to share or save.")
        pdf_bytes = generate_pdf_report(
            result["filename"], result["job_role"], ats, match, ai
        )
        st.download_button(
            "⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=f"resume_analysis_{result['filename'].rsplit('.',1)[0]}.pdf",
            mime="application/pdf",
        )


if __name__ == "__main__":
    main()
