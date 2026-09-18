# Student Employability & Placement Analytics Dashboard

## Overview

An interactive Streamlit dashboard that turns raw campus placement data into
KPIs, trends, drivers, risks/opportunities and actionable recommendations for
students and institutions. The project follows the pipeline:

**Data → Cleaning → Analysis → KPIs → Trends → Drivers → Insights → Recommendations**

## Problem Statement

Colleges collect a lot of data on academics, internships, specialisations and
placement outcomes, but it rarely gets converted into decisions anyone can
act on. This dashboard analyzes that data to answer questions like: What
drives placement? Which cohorts are under-performing? What should a student
or institution actually do differently?

## Objectives

- Calculate the overall placement rate and the KPIs behind it
- Identify which academic and employability factors are associated with
  placement
- Compare outcomes across degree streams and specialisations
- Analyze salary/package patterns among placed students
- Surface actionable, data-backed recommendations (not just charts)

## Dataset

- **Name:** Campus Recruitment ("Placement_Data_Full_Class.csv")
- **Source:** Kaggle — [Campus Recruitment](https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement)
  by Ben Roshan (mirrored copy used here is included in this repo)
- **Records / Features:** 215 students, 15 columns (14 after dropping the
  row-index column)
- **Key columns:**
  - `gender`, `ssc_p`/`ssc_b` (10th % / board), `hsc_p`/`hsc_b`/`hsc_s`
    (12th % / board / stream), `degree_p`/`degree_t` (degree % / stream),
    `workex` (prior work experience), `etest_p` (employability test %),
    `specialisation` (MBA specialisation), `mba_p` (MBA %), `status`
    (Placed / Not Placed), `salary` (package offered, placed students only)

> **Note on scope:** This dataset represents a single MBA cohort rather than
> multiple college departments, and has no explicit "certifications" or
> "extracurriculars" columns. Degree Stream and MBA Specialisation are used
> as the closest available department-equivalent groupings; work experience
> and the employability test score are used as the closest available
> skill-development proxies. This is called out directly in the dashboard.

## Technologies Used

- Python, Pandas, NumPy
- Plotly (interactive charts)
- Streamlit (dashboard/UI)

## Features

- **KPI dashboard:** total students, placed students, placement rate,
  average degree %, work-experience participation, average employability
  test %, average package, top-placing stream
- **6 analysis pages:** Overview, Academic Analysis, Employability Factors,
  Department/Stream Analysis, Salary Analysis, Insights & Recommendations
- **Interactive filters:** gender, degree stream, specialisation, placement
  status, work experience, degree-percentage range — all KPIs and charts
  recompute live from the filtered data
- **Auto-generated insights:** trends, drivers (correlation-based), risks,
  opportunities and recommendations, computed from whatever is currently
  filtered rather than hard-coded

No machine-learning prediction model is included — at 215 rows the dataset
is better suited to descriptive/diagnostic analysis than a generalizable
predictive model, and the objective here is actionable insight rather than
prediction.

## Project Workflow

1. **Data:** load `Placement_Data_Full_Class.csv`
2. **Cleaning:** drop the row-index column, strip whitespace, drop exact
   duplicates (none found); missing `salary` values are left as-is because
   they are structural (unplaced students never receive an offer), not a
   data-quality defect
3. **Analysis:** cross-tabs and correlations between academic/employability
   factors and placement outcome
4. **KPIs:** computed live from the (filtered) dataset
5. **Trends / Drivers:** computed on the Insights tab from correlation and
   group comparisons
6. **Insights → Recommendations:** presented on the final dashboard tab,
   separated for students vs. institutions

## Installation

```bash
pip install -r requirements.txt
```

## How to Run

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (typically `http://localhost:8501`).

## Results (headline findings on the full dataset)

- Overall placement rate: **68.8%** (148 of 215 students)
- Prior work experience shows the largest single-factor gap: **86.5%**
  placement rate for students with work experience vs. **59.6%** without it
- 10th-grade percentage (`ssc_p`) has the strongest correlation with
  placement (r ≈ 0.61) among all academic/test scores tracked — stronger
  than the MBA percentage or the employability test score
- Mkt&Fin specialisation placements (79.2%) outperform Mkt&HR (55.8%)
- Median package (₹265,000) is meaningfully lower than the mean
  (₹288,655) — a small number of high offers pull the average up, so
  median is the more representative figure

Full breakdowns, correlations, and filterable charts are in the dashboard
itself.

## Future Scope

- Add year-over-year data if/when available, to track placement-rate trends
  over time rather than a single cohort snapshot
- Add a genuine "certifications" and "extracurriculars" field if the
  institution starts collecting it, since none exists in the current source
  data
- Revisit an ML prediction model if the dataset grows well beyond 215 rows

## Dataset Source

https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement
