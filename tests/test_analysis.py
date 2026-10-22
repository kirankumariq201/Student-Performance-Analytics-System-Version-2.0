"""Automated tests for Student Performance Analytics System 2.0."""
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from main import (
    add_performance_columns, build_insights, department_summary,
    get_top_performers, grade_for_average, load_student_data,
    subject_summary, write_report,
)


class TestStudentPerformanceAnalytics(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame([
            {"Student_ID": "T01", "Name": "Asha", "Department": "CSE", "Python": 90,
             "Mathematics": 80, "Statistics": 70, "Communication": 100, "Attendance": 90},
            {"Student_ID": "T02", "Name": "Bala", "Department": "IT", "Python": 30,
             "Mathematics": 80, "Statistics": 70, "Communication": 100, "Attendance": 90},
            {"Student_ID": "T03", "Name": "Chitra", "Department": "CSE", "Python": 80,
             "Mathematics": 80, "Statistics": 80, "Communication": 80, "Attendance": 70},
        ])

    def test_total_average_and_grade(self):
        result = add_performance_columns(self.df)
        self.assertEqual(result.loc[0, "Total_Marks"], 340)
        self.assertEqual(result.loc[0, "Average_Marks"], 85.0)
        self.assertEqual(result.loc[0, "Grade"], "A")

    def test_grade_boundaries(self):
        self.assertEqual(grade_for_average(90), "A+")
        self.assertEqual(grade_for_average(80), "A")
        self.assertEqual(grade_for_average(70), "B")
        self.assertEqual(grade_for_average(60), "C")
        self.assertEqual(grade_for_average(50), "D")
        self.assertEqual(grade_for_average(49.99), "F")

    def test_pass_requires_all_subjects_and_attendance(self):
        result = add_performance_columns(self.df)
        self.assertEqual(result.loc[0, "Result"], "Pass")
        self.assertEqual(result.loc[1, "Result"], "Fail")
        self.assertEqual(result.loc[2, "Result"], "Fail")

    def test_exact_thresholds_pass(self):
        row = self.df.iloc[[0]].copy()
        row.loc[:, ["Python", "Mathematics", "Statistics", "Communication"]] = 40
        row.loc[:, "Attendance"] = 75
        self.assertEqual(add_performance_columns(row).iloc[0]["Result"], "Pass")

    def test_subject_summary(self):
        summary = subject_summary(self.df)
        self.assertEqual(summary.loc[0, "Highest"], 90.0)
        self.assertEqual(summary.loc[0, "Lowest"], 30.0)
        self.assertEqual(summary.loc[0, "Students_Passed"], 2)

    def test_top_performer(self):
        result = add_performance_columns(self.df)
        self.assertEqual(get_top_performers(result, 1).iloc[0]["Name"], "Asha")

    def test_negative_top_count_is_rejected(self):
        with self.assertRaises(ValueError):
            get_top_performers(add_performance_columns(self.df), -1)

    def test_department_summary(self):
        result = department_summary(add_performance_columns(self.df))
        cse = result.loc[result["Department"].eq("CSE")].iloc[0]
        self.assertEqual(cse["Students"], 2)
        self.assertEqual(cse["Passed"], 1)

    def test_input_validation_rejects_duplicate_ids(self):
        bad = self.df.copy()
        bad.loc[1, "Student_ID"] = "T01"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            bad.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "unique"):
                load_student_data(path)

    def test_input_validation_rejects_marks_outside_range(self):
        bad = self.df.copy()
        bad.loc[0, "Python"] = 101
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            bad.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "between 0 and 100"):
                load_student_data(path)

    def test_insights_and_report_exports(self):
        analysed = add_performance_columns(self.df)
        subjects = subject_summary(self.df)
        departments = department_summary(analysed)
        insights = build_insights(analysed, subjects)
        self.assertEqual(insights["students_analysed"], 3)
        self.assertEqual(insights["passed"], 1)
        with tempfile.TemporaryDirectory() as folder:
            files = write_report(analysed, subjects, departments, insights, folder)
            self.assertEqual(len(files), 4)
            self.assertTrue(all(path.exists() for path in files))


if __name__ == "__main__":
    unittest.main(verbosity=2)
