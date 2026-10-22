# Student Performance Analytics System — Version 2.0

A beginner-friendly Python data-analysis project that reads a student CSV file and produces understandable performance summaries using **Python, NumPy and Pandas**. It follows the EWB Courses *Python with AI* assignment scope; it does not use machine learning.

> **Dataset note:** All 20 names and marks in `data/students.csv` are fictional demonstration data.

## Features

- Loads and validates the student CSV with Pandas.
- Checks required columns, blank fields, duplicate student IDs, numeric values, and valid mark/attendance ranges.
- Calculates each student's total marks, average, letter grade, subjects passed, and pass/fail result.
- Uses NumPy for numerical summaries, including subject averages, highest marks, lowest marks, and counts.
- Reports class average, pass percentage, best/lowest-average subject, top three performers, and department-level summaries.
- Exports four files: detailed student results, subject summary, department summary, and a plain-text class report.
- Includes automated tests for calculations, grading boundaries, pass rules, input validation, summaries, and report generation.

## Project rules

### Grade scale

| Average mark | Grade |
|---:|:---|
| 90–100 | A+ |
| 80–89.99 | A |
| 70–79.99 | B |
| 60–69.99 | C |
| 50–59.99 | D |
| Below 50 | F |

### Pass rule

A student passes only if **every subject mark is at least 40** and **attendance is at least 75%**. These are the rules defined for this implementation; replace them if your trainer has specified a different rule.

## Requirements

- Python 3.10 or newer
- NumPy
- Pandas

## Run the project

From this folder, run:

```bash
python -m pip install -r requirements.txt
python main.py
```

To analyze another CSV or choose a different output folder:

```bash
python main.py --data data/students.csv --output-dir output
```

The input CSV must contain these columns: `Student_ID`, `Name`, `Department`, `Python`, `Mathematics`, `Statistics`, `Communication`, and `Attendance`. Marks and attendance must be numeric values from 0 to 100, and student IDs must be unique.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Folder structure

```text
Student-Performance-Analytics-System-Version-2.0/
├── data/
│   └── students.csv
├── docs/
│   └── Project_Documentation.md
├── output/
│   └── .gitkeep
├── tests/
│   └── test_analysis.py
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Generated output

Running the program creates these files in `output/`:

- `student_analysis_results.csv`
- `subject_summary.csv`
- `department_summary.csv`
- `summary_report.txt`

Generated reports are excluded from Git by default so the repository stays clean. Run the program yourself to generate current results.

## Learning outcomes

This project demonstrates variables, data types, conditions, loops, reusable functions, CSV handling, Pandas DataFrames, NumPy calculations, validation, sorting, grouping, testing, and documentation.

## Documentation and screenshots

See [`docs/Project_Documentation.md`](docs/Project_Documentation.md) for the objective, dataset, implementation, rules, testing, results section, challenges, and GitHub checklist. Add screenshots of your own program output after running it; do not claim screenshots or test results that have not actually been produced.

## Version

**2.0** — rebuilt as a separate project. It does not modify the earlier project folder or the separate internship CRUD repository.
