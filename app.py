"""Interactive Streamlit dashboard for Student Performance Analytics System 2.0."""
from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from main import (
    add_performance_columns, build_insights, department_summary,
    get_top_performers, load_student_data, subject_summary, write_report,
)

ROOT = Path(__file__).resolve().parent
SAMPLE_CSV = ROOT / "data" / "students.csv"

st.set_page_config(page_title="Student Performance Analytics | v2.0", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1400px}
.hero{padding:1.5rem 1.7rem;border-radius:18px;background:linear-gradient(115deg,#172554,#1d4ed8);color:white;margin-bottom:1.2rem}
.hero h1{color:white;margin-bottom:.3rem}.hero p{color:#dbeafe;margin-bottom:0}
[data-testid="stMetric"]{border:1px solid rgba(128,128,128,.25);padding:1rem;border-radius:14px}
</style>
""", unsafe_allow_html=True)
st.markdown("""<div class="hero"><h1>📊 Student Performance Analytics</h1>
<p>Version 2.0 · Explore marks, attendance, subject trends, and class performance.</p></div>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📁 Your data")
    uploaded = st.file_uploader("Upload student CSV", type=["csv"])
    st.download_button("Download sample CSV", data=SAMPLE_CSV.read_bytes(),
                       file_name="students_sample.csv", mime="text/csv", use_container_width=True)
    st.divider()
    st.header("⚙️ Pass criteria")
    pass_mark = st.slider("Minimum mark per subject", 0, 100, 40)
    minimum_attendance = st.slider("Minimum attendance (%)", 0, 100, 75)
    st.caption("Pass requires every subject to meet the mark threshold and attendance to meet the attendance threshold.")
    st.divider()
    st.caption("Sample records are fictional. Avoid uploading identifiable student data to a public hosted app.")

try:
    if uploaded is not None:
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as temp:
            temp.write(uploaded.getvalue())
            temp_path = Path(temp.name)
        try:
            raw_df = load_student_data(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)
        source = f"Uploaded file · {uploaded.name}"
    else:
        raw_df = load_student_data(SAMPLE_CSV)
        source = "Sample dataset · 20 fictional students"

    analysed = add_performance_columns(raw_df, pass_mark=pass_mark, minimum_attendance=minimum_attendance)
    subjects = subject_summary(raw_df)
    departments = department_summary(analysed)
    insights = build_insights(analysed, subjects)
    st.caption(f"Data source: {source} · {len(analysed)} records")
    a, b, c, d = st.columns(4)
    a.metric("Students", f"{insights['students_analysed']:,}")
    b.metric("Class average", f"{insights['class_average']:.2f} / 100")
    c.metric("Pass rate", f"{insights['pass_percentage']:.1f}%")
    d.metric("Passed / failed", f"{insights['passed']} / {insights['failed']}")

    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Subject averages")
        st.bar_chart(subjects.set_index("Subject")[["Average"]].sort_values("Average", ascending=False))
        st.dataframe(subjects, hide_index=True, use_container_width=True)
    with right:
        st.subheader("Grade distribution")
        grades = analysed["Grade"].value_counts().reindex(["A+", "A", "B", "C", "D", "F"], fill_value=0)
        st.bar_chart(grades.rename_axis("Grade").to_frame("Students"))
        st.subheader("Pass / fail")
        results = analysed["Result"].value_counts().reindex(["Pass", "Fail"], fill_value=0)
        st.bar_chart(results.rename_axis("Result").to_frame("Students"))

    st.subheader("🏅 Top performers")
    top = get_top_performers(analysed, 3)
    st.dataframe(top[["Student_ID", "Name", "Department", "Total_Marks", "Average_Marks", "Grade", "Result"]],
                 hide_index=True, use_container_width=True)
    st.subheader("🏫 Department comparison")
    st.dataframe(departments, hide_index=True, use_container_width=True)

    st.subheader("🔎 Explore student records")
    query = st.text_input("Search by student ID, name, or department", placeholder="Try S001 or CSE")
    filtered = analysed.copy()
    if query.strip():
        match = filtered[["Student_ID", "Name", "Department"]].astype(str).apply(
            lambda col: col.str.contains(query.strip(), case=False, na=False, regex=False)).any(axis=1)
        filtered = filtered[match]
    result_filter = st.selectbox("Filter result", ["All", "Pass", "Fail"])
    if result_filter != "All":
        filtered = filtered[filtered["Result"] == result_filter]
    st.dataframe(filtered, hide_index=True, use_container_width=True)

    st.subheader("⬇️ Export reports")
    with tempfile.TemporaryDirectory() as folder:
        paths = write_report(analysed, subjects, departments, insights, folder)
        columns = st.columns(4)
        labels = ["Student results CSV", "Subject summary CSV", "Department summary CSV", "Text summary"]
        for column, path, label in zip(columns, paths, labels):
            with column:
                column.download_button(f"Download {label}", data=path.read_bytes(), file_name=path.name,
                                       mime="text/plain" if path.suffix == ".txt" else "text/csv",
                                       use_container_width=True)
    with st.expander("ℹ️ Rules and interpretation"):
        st.markdown("""
        - **Grades:** A+ ≥ 90; A ≥ 80; B ≥ 70; C ≥ 60; D ≥ 50; F < 50.
        - **Pass:** every subject meets the selected minimum and attendance meets the selected minimum.
        - **Privacy:** this demo is not intended for sensitive or identifiable education records.
        """)
    st.caption("Built with Python, Pandas, NumPy, and Streamlit · Student Performance Analytics System 2.0")
except (ValueError, OSError, pd.errors.ParserError) as exc:
    st.error(f"Could not analyze this dataset: {exc}")
    st.info("Check the required columns: Student_ID, Name, Department, Python, Mathematics, Statistics, Communication, Attendance. See README for details.")
