"""Student Performance Analytics System — Version 2.0.

A beginner-friendly data-analysis project built with Python, NumPy and Pandas.
All sample student records are fictional.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = ROOT / "data" / "students.csv"
DEFAULT_OUTPUT_DIR = ROOT / "output"
SUBJECT_COLUMNS = ["Python", "Mathematics", "Statistics", "Communication"]
REQUIRED_COLUMNS = ["Student_ID", "Name", "Department", *SUBJECT_COLUMNS, "Attendance"]


def load_student_data(file_path: str | Path = DEFAULT_DATA_FILE) -> pd.DataFrame:
    """Load a CSV and validate its required fields and values."""
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The CSV file is empty.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The CSV file could not be parsed. Check its format.") from exc

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")
    if df.empty:
        raise ValueError("The dataset contains column headers but no student records.")

    df = df[REQUIRED_COLUMNS].copy()
    for column in ["Student_ID", "Name", "Department"]:
        df[column] = df[column].astype("string").str.strip()
        if df[column].isna().any() or df[column].eq("").any():
            raise ValueError(f"'{column}' cannot contain blank values.")

    if df["Student_ID"].duplicated().any():
        duplicates = df.loc[df["Student_ID"].duplicated(keep=False), "Student_ID"].unique()
        raise ValueError(f"Student_ID values must be unique. Duplicate(s): {', '.join(duplicates)}")

    for column in [*SUBJECT_COLUMNS, "Attendance"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        if df[column].isna().any():
            raise ValueError(f"'{column}' must contain a valid number in every row.")
        if not np.isfinite(df[column].to_numpy(dtype=float)).all():
            raise ValueError(f"'{column}' cannot contain infinite values.")
        if not df[column].between(0, 100).all():
            raise ValueError(f"'{column}' values must be between 0 and 100.")

    return df


def grade_for_average(average: float) -> str:
    """Return a letter grade using the project grading scale."""
    if average >= 90:
        return "A+"
    if average >= 80:
        return "A"
    if average >= 70:
        return "B"
    if average >= 60:
        return "C"
    if average >= 50:
        return "D"
    return "F"


def add_performance_columns(df: pd.DataFrame, pass_mark: float = 40,
                            minimum_attendance: float = 75) -> pd.DataFrame:
    """Return a copy with total, average, grade, result and subject count."""
    if not 0 <= pass_mark <= 100:
        raise ValueError("pass_mark must be between 0 and 100.")
    if not 0 <= minimum_attendance <= 100:
        raise ValueError("minimum_attendance must be between 0 and 100.")
    missing = [subject for subject in SUBJECT_COLUMNS if subject not in df.columns]
    if missing:
        raise ValueError(f"Cannot calculate performance; missing subject(s): {', '.join(missing)}")

    result = df.copy()
    marks = result[SUBJECT_COLUMNS].apply(pd.to_numeric, errors="coerce")
    if marks.isna().any().any() or not np.isfinite(marks.to_numpy(dtype=float)).all():
        raise ValueError("Subject marks must all be valid finite numbers.")
    if not marks.apply(lambda column: column.between(0, 100).all()).all():
        raise ValueError("Subject marks must be between 0 and 100.")
    if "Attendance" not in result.columns:
        raise ValueError("Attendance column is required to determine pass/fail status.")
    attendance = pd.to_numeric(result["Attendance"], errors="coerce")
    if attendance.isna().any() or not np.isfinite(attendance.to_numpy(dtype=float)).all() or not attendance.between(0, 100).all():
        raise ValueError("Attendance must be numeric and between 0 and 100.")

    result[SUBJECT_COLUMNS] = marks
    result["Total_Marks"] = marks.sum(axis=1).astype(int)
    result["Average_Marks"] = np.round(marks.mean(axis=1), 2)
    result["Grade"] = result["Average_Marks"].map(grade_for_average)
    subject_pass = marks.ge(pass_mark).all(axis=1)
    attendance_pass = attendance.ge(minimum_attendance)
    result["Result"] = np.where(subject_pass & attendance_pass, "Pass", "Fail")
    result["Subjects_Passed"] = marks.ge(pass_mark).sum(axis=1).astype(int)
    return result


def subject_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize each subject using NumPy calculations."""
    rows: list[dict[str, float | int | str]] = []
    for subject in SUBJECT_COLUMNS:
        if subject not in df.columns:
            raise ValueError(f"Missing subject column: {subject}")
        values = pd.to_numeric(df[subject], errors="coerce").dropna().to_numpy(dtype=float)
        if values.size == 0 or not np.isfinite(values).all():
            raise ValueError(f"'{subject}' has no valid numeric values to summarize.")
        rows.append({
            "Subject": subject,
            "Average": round(float(np.mean(values)), 2),
            "Highest": round(float(np.max(values)), 2),
            "Lowest": round(float(np.min(values)), 2),
            "Students_Passed": int(np.count_nonzero(values >= 40)),
        })
    return pd.DataFrame(rows)


def department_summary(analysed_df: pd.DataFrame) -> pd.DataFrame:
    """Compare average performance and pass rate by department."""
    required = {"Department", "Average_Marks", "Result"}
    if not required.issubset(analysed_df.columns):
        raise ValueError("Department summary requires Department, Average_Marks and Result columns.")
    student_count = ("Student_ID", "count") if "Student_ID" in analysed_df else ("Department", "size")
    return (analysed_df.groupby("Department", as_index=False)
            .agg(Students=(student_count[0], student_count[1]),
                 Average_Marks=("Average_Marks", "mean"),
                 Passed=("Result", lambda values: int(values.eq("Pass").sum())))
            .assign(Pass_Percentage=lambda frame: np.round(frame["Passed"] / frame["Students"] * 100, 2),
                    Average_Marks=lambda frame: np.round(frame["Average_Marks"], 2))
            .sort_values("Department"))


def get_top_performers(analysed_df: pd.DataFrame, count: int = 3) -> pd.DataFrame:
    """Return the top students, ordered by average, total and then name."""
    if count < 0:
        raise ValueError("count cannot be negative.")
    required = {"Average_Marks", "Total_Marks", "Name"}
    if not required.issubset(analysed_df.columns):
        raise ValueError("Top performers require Average_Marks, Total_Marks and Name columns.")
    return analysed_df.sort_values(
        ["Average_Marks", "Total_Marks", "Name"], ascending=[False, False, True]
    ).head(count)


def build_insights(analysed_df: pd.DataFrame, subjects: pd.DataFrame) -> dict[str, object]:
    """Create key class-level metrics and plain-language insights."""
    if analysed_df.empty:
        raise ValueError("Cannot build insights for an empty dataset.")
    passed = int(analysed_df["Result"].eq("Pass").sum())
    averages = analysed_df["Average_Marks"]
    return {
        "students_analysed": int(len(analysed_df)),
        "class_average": round(float(averages.mean()), 2),
        "highest_average": round(float(averages.max()), 2),
        "lowest_average": round(float(averages.min()), 2),
        "passed": passed,
        "failed": int(len(analysed_df) - passed),
        "pass_percentage": round(passed / len(analysed_df) * 100, 2),
        "best_subject": str(subjects.loc[subjects["Average"].idxmax(), "Subject"]),
        "needs_attention_subject": str(subjects.loc[subjects["Average"].idxmin(), "Subject"]),
    }


def write_report(analysed_df: pd.DataFrame, subjects: pd.DataFrame,
                 departments: pd.DataFrame, insights: dict[str, object],
                 output_dir: str | Path = DEFAULT_OUTPUT_DIR) -> list[Path]:
    """Export student results and summary tables as CSV, plus a text report."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    student_path = destination / "student_analysis_results.csv"
    subject_path = destination / "subject_summary.csv"
    department_path = destination / "department_summary.csv"
    report_path = destination / "summary_report.txt"
    analysed_df.to_csv(student_path, index=False)
    subjects.to_csv(subject_path, index=False)
    departments.to_csv(department_path, index=False)
    lines = [
        "STUDENT PERFORMANCE ANALYTICS SYSTEM — VERSION 2.0",
        "=" * 58,
        f"Students analysed: {insights['students_analysed']}",
        f"Class average: {insights['class_average']}/100",
        f"Passed: {insights['passed']}",
        f"Failed: {insights['failed']}",
        f"Pass percentage: {insights['pass_percentage']}%",
        f"Highest student average: {insights['highest_average']}/100",
        f"Lowest student average: {insights['lowest_average']}/100",
        f"Best subject by average: {insights['best_subject']}",
        f"Subject needing most attention by average: {insights['needs_attention_subject']}",
        "",
        "GRADING SCALE",
        "A+ >= 90 | A >= 80 | B >= 70 | C >= 60 | D >= 50 | F < 50",
        "Pass rule: every subject mark >= 40 and attendance >= 75%.",
        "",
        "Note: Results are based on fictional demonstration data.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return [student_path, subject_path, department_path, report_path]


def print_report(df: pd.DataFrame, output_dir: str | Path = DEFAULT_OUTPUT_DIR) -> None:
    """Print the analysis and export the results."""
    analysed = add_performance_columns(df)
    subjects = subject_summary(df)
    departments = department_summary(analysed)
    insights = build_insights(analysed, subjects)
    print("\n" + "=" * 58)
    print("STUDENT PERFORMANCE ANALYTICS SYSTEM — VERSION 2.0")
    print("=" * 58)
    for label, key in [
        ("Students analysed", "students_analysed"),
        ("Class average", "class_average"),
        ("Passed", "passed"),
        ("Failed", "failed"),
        ("Pass percentage", "pass_percentage"),
        ("Best subject", "best_subject"),
        ("Subject needing most attention", "needs_attention_subject"),
    ]:
        suffix = "%" if key == "pass_percentage" else ("/100" if key == "class_average" else "")
        print(f"{label}: {insights[key]}{suffix}")
    print("\nINDIVIDUAL STUDENT RESULTS")
    display_columns = ["Student_ID", "Name", "Department", "Total_Marks", "Average_Marks", "Grade", "Result"]
    print(analysed[display_columns].to_string(index=False))
    print("\nSUBJECT-WISE SUMMARY")
    print(subjects.to_string(index=False))
    print("\nDEPARTMENT-WISE SUMMARY")
    print(departments.to_string(index=False))
    print("\nTOP 3 PERFORMERS")
    print(get_top_performers(analysed)[["Student_ID", "Name", "Average_Marks", "Grade"]].to_string(index=False))
    paths = write_report(analysed, subjects, departments, insights, output_dir)
    print("\nFILES CREATED")
    for path in paths:
        print(f"- {path}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze student marks and attendance.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_FILE,
                        help="Path to the student CSV file (default: data/students.csv).")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
                        help="Directory for generated CSV and text reports (default: output/).")
    args = parser.parse_args(argv)
    try:
        data = load_student_data(args.data)
        print_report(data, args.output_dir)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
