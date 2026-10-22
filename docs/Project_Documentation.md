# Project Documentation

## 1. Project Title

**Student Performance Analytics System — Version 2.0**

Student name: [Enter your name]  
Course: EWB Courses — Python with AI  
GitHub repository: https://github.com/kirankumariq201/Student-Performance-Analytics-System-Version-2.0

## 2. Objective

The objective is to build a Python program that organizes student marks and attendance, calculates individual and class-level performance, identifies pass/fail status using clearly stated rules, and presents results in a form that is easy to understand.

## 3. Technologies Used

- Python 3.10+
- Pandas for CSV loading, DataFrames, grouping, sorting, and exporting
- NumPy for numerical calculations and summaries
- Python `unittest` for automated tests

No machine-learning model is used or required.

## 4. Dataset Description

The sample dataset contains 20 fictional student records. Its fields are:

- `Student_ID`: unique identifier for each student
- `Name`: student display name
- `Department`: department or course group
- `Python`, `Mathematics`, `Statistics`, `Communication`: marks out of 100
- `Attendance`: attendance percentage from 0 to 100

The data is for demonstration only and is not real student information.

## 5. Implementation

1. `load_student_data()` reads the CSV using Pandas and validates required columns, blank fields, duplicate IDs, numeric values, and ranges.
2. `add_performance_columns()` calculates totals, averages, grades, subjects passed, and pass/fail results.
3. `grade_for_average()` applies the documented grade scale.
4. `subject_summary()` uses NumPy to calculate subject averages, highest and lowest marks, and the number of marks meeting the pass mark.
5. `department_summary()` groups records by department and calculates student counts, average marks, and pass percentages.
6. `get_top_performers()` sorts students by average marks, total marks, and name.
7. `build_insights()` creates class-level metrics and identifies the best and lowest-average subjects.
8. `write_report()` exports the detailed student table and summary files as CSV, plus a readable text report.
9. The command-line entry point catches common input errors and returns a clear error message instead of continuing with invalid data.

## 6. Key Features

- Individual student analysis
- Total and average marks
- Letter grades
- Pass/fail status
- Subject-wise performance
- Top three performers
- Department-wise comparison
- Input validation
- Exportable results
- Automated unit tests

## 7. Output / Screenshots

After running `python main.py`, insert your own screenshots here:

1. The terminal showing class statistics and individual results.
2. The subject-wise and department-wise summaries.
3. The generated `output/` report files.

Do not insert screenshots until you have run the project and verified the output.

## 8. Final Outcome

The completed program is designed to transform a student CSV dataset into individual results, class-level statistics, subject summaries, department comparisons, top-performer rankings, and exportable reports. Fill in the actual run results after testing the project locally.

## 9. Challenges & Learning

Possible learning points to describe after you have run and reviewed the code:

- Validating CSV data before calculating statistics
- Using Pandas to organize and group tabular records
- Using NumPy for numerical summaries
- Applying conditions and loops to analysis tasks
- Testing boundary cases and invalid inputs
- Exporting results so they can be reviewed without reading the source code

Add any real errors you encountered and how you fixed them; do not claim a challenge you did not experience.

## 10. GitHub Repository

Repository URL: https://github.com/kirankumariq201/Student-Performance-Analytics-System-Version-2.0

### Final checklist

- [ ] `main.py` uploaded
- [ ] `data/students.csv` uploaded
- [ ] `README.md` uploaded
- [ ] `docs/Project_Documentation.md` uploaded
- [ ] `tests/test_analysis.py` uploaded
- [ ] Requirements file uploaded
- [ ] Program runs successfully
- [ ] Automated tests pass
- [ ] Repository URL opens while signed out
- [ ] Final URL copied into the correct submission form, if required

## Rules used in this version

**Grade scale:** A+ for averages of 90 and above; A for 80–89.99; B for 70–79.99; C for 60–69.99; D for 50–59.99; F below 50.

**Pass rule:** every subject mark must be at least 40 and attendance must be at least 75%. These are implementation choices, not a claim that EWB requires this exact grading scheme.
