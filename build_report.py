"""Builds project_report.pdf from the analysis. Run once; not part of the app."""
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle,
)

df = pd.read_csv("Placement_Data_Full_Class.csv").rename(
    columns={"degree_t": "degree_stream", "hsc_s": "hsc_stream"}
)
df["placed_flag"] = (df["status"] == "Placed").astype(int)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1c", parent=styles["Heading1"], spaceBefore=18, spaceAfter=8))
styles.add(ParagraphStyle(name="H2c", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name="Bodyc", parent=styles["Normal"], leading=15, spaceAfter=8))
styles.add(ParagraphStyle(name="Bulletc", parent=styles["Normal"], leading=15, leftIndent=14, spaceAfter=4))
styles.add(ParagraphStyle(name="TitleC", parent=styles["Title"], fontSize=22, spaceAfter=6))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], fontSize=12, textColor=colors.grey, spaceAfter=4))

story = []

# ---------- Title page ----------
story.append(Spacer(1, 1.6 * inch))
story.append(Paragraph("Student Employability & Placement Analytics Dashboard", styles["TitleC"]))
story.append(Paragraph("Project Report", styles["Subtitle"]))
story.append(Spacer(1, 0.3 * inch))
story.append(Paragraph("Prepared using the Campus Recruitment dataset (Kaggle, Ben Roshan)", styles["Bodyc"]))
story.append(Paragraph("215 students · 15 original columns", styles["Bodyc"]))
story.append(PageBreak())

def h1(t): story.append(Paragraph(t, styles["H1c"]))
def h2(t): story.append(Paragraph(t, styles["H2c"]))
def p(t): story.append(Paragraph(t, styles["Bodyc"]))
def bullets(items):
    for it in items:
        story.append(Paragraph(f"&bull; {it}", styles["Bulletc"]))

# ---------- 1. Introduction ----------
h1("1. Introduction")
p("Colleges routinely collect data on student academics, work experience, specialisation and "
  "placement outcomes, but this data is rarely converted into decisions anyone can act on. "
  "This project builds a data analytics dashboard that turns raw placement records into KPIs, "
  "trends, drivers, risks, opportunities and concrete recommendations for students and institutions.")

# ---------- 2. Problem Statement ----------
h1("2. Problem Statement")
p("Given student-level academic, demographic and employability-related data, the project answers: "
  "What is the overall placement rate? What factors are associated with placement? How do academic "
  "performance, prior work experience and specialisation relate to outcomes? What drives package/salary "
  "differences among placed students? Which cohorts show weaker outcomes and need more support?")

# ---------- 3. Objectives ----------
h1("3. Objectives")
bullets([
    "Calculate the overall placement rate and supporting KPIs",
    "Identify which academic and employability factors associate with placement",
    "Compare placement outcomes across degree streams and MBA specialisations",
    "Analyze salary/package patterns among placed students",
    "Translate findings into specific, data-backed recommendations",
])

# ---------- 4. Dataset Description ----------
h1("4. Dataset Description")
p("<b>Name:</b> Campus Recruitment (Placement_Data_Full_Class.csv)<br/>"
  "<b>Source:</b> Kaggle — \"Campus Recruitment\" dataset by Ben Roshan "
  "(https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement)<br/>"
  "<b>Size:</b> 215 students, 15 columns (14 after dropping the row-index column)")
p("Columns: gender; ssc_p / ssc_b (10th % / board); hsc_p / hsc_b / hsc_s (12th % / board / stream); "
  "degree_p / degree_t (degree % / stream); workex (prior work experience); etest_p (employability "
  "test %); specialisation (MBA specialisation); mba_p (MBA %); status (Placed / Not Placed); "
  "salary (package offered, placed students only).")
p("<b>Scope note:</b> this dataset represents a single MBA cohort rather than multiple departments, "
  "and has no explicit certifications / extracurriculars field. Degree Stream and MBA Specialisation "
  "are used as the closest available department-equivalent groupings throughout this report and the "
  "dashboard; work experience and the employability test score serve as the closest available "
  "skill-development proxies.")

# ---------- 5. Data Preprocessing ----------
h1("5. Data Preprocessing")
bullets([
    "Loaded the CSV and inspected shape (215 rows × 15 columns), dtypes and column names.",
    "Dropped the sl_no row-index column (no analytical value).",
    "Checked for duplicate records — none found.",
    "Checked for missing values — only `salary` has missing values (67 of 215 rows, 31.2%). "
    "This is structural, not a data-quality defect: students with status = \"Not Placed\" were "
    "never offered a salary. These rows are excluded from salary statistics rather than imputed "
    "with zero or a mean, which would distort the results.",
    "Checked categorical values for consistency (gender, board, stream, specialisation, workex, "
    "status) — all values were clean and consistently coded, no normalization needed.",
])

# ---------- 6. Methodology ----------
h1("6. Methodology")
p("The analysis follows: <b>Data → KPIs → Trends → Drivers → Risks/Opportunities → Actionable "
  "Insights.</b> KPIs are computed directly from the (optionally filtered) dataset. Trends are "
  "identified via group comparisons (cross-tabs, group means). Drivers are identified using Pearson "
  "correlation between numeric academic/test scores and a binary placement flag, and by comparing "
  "placement rates across categorical segments (work experience, stream, specialisation). Findings "
  "are described as associations, not causal claims, since this is observational data.")

# ---------- 7. Exploratory Data Analysis ----------
h1("7. Exploratory Data Analysis")
h2("7.1 Placement Status Distribution")
story.append(Image("chart_placement_dist.png", width=3.6 * inch, height=2.9 * inch))
placed = int(df["placed_flag"].sum()); total = len(df)
p(f"{placed} of {total} students ({placed/total*100:.1f}%) were placed; "
  f"{total-placed} ({(1-placed/total)*100:.1f}%) were not.")

h2("7.2 Academic Scores: Placed vs Not Placed")
academic_cols = ["ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"]
avg_tbl = df.groupby("status")[academic_cols].mean().round(1).reset_index()
table_data = [["Status"] + academic_cols] + avg_tbl.values.tolist()
t = Table(table_data, hAlign="LEFT")
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4C6EF5")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
]))
story.append(t)
story.append(Spacer(1, 10))
p("Placed students score higher on average at every academic stage tracked. The gap is widest at "
  "the 10th-grade stage (ssc_p) and narrows by the MBA stage (mba_p), suggesting early academic "
  "consistency is a stronger placement signal than late-stage performance in this cohort.")

h2("7.3 Correlation with Placement")
story.append(Image("chart_correlation.png", width=3.6 * inch, height=2.9 * inch))
corr = df[academic_cols + ["placed_flag"]].corr()["placed_flag"].drop("placed_flag").sort_values(ascending=False)
p(f"10th-grade percentage (ssc_p) shows the strongest correlation with placement (r = {corr.iloc[0]:.2f}), "
  f"followed by 12th-grade percentage (hsc_p, r = {corr['hsc_p']:.2f}) and degree percentage "
  f"(degree_p, r = {corr['degree_p']:.2f}). The MBA percentage and employability test score show "
  f"much weaker correlation (r = {corr['mba_p']:.2f} and r = {corr['etest_p']:.2f} respectively).")

h2("7.4 Work Experience")
story.append(Image("chart_workex_rate.png", width=3.6 * inch, height=2.9 * inch))
we = df.groupby("workex")["placed_flag"].mean().mul(100)
p(f"Students with prior work experience are placed at {we['Yes']:.1f}%, compared to {we['No']:.1f}% "
  f"for students without it — a gap of {we['Yes']-we['No']:.1f} percentage points, the largest "
  f"single-factor gap found in this dataset.")

h2("7.5 Degree Stream")
story.append(Image("chart_stream_rate.png", width=3.6 * inch, height=2.9 * inch))
stream_rates = df.groupby("degree_stream")["placed_flag"].mean().mul(100).sort_values(ascending=False)
p(f"{stream_rates.index[0]} has the highest placement rate ({stream_rates.iloc[0]:.1f}%), while "
  f"{stream_rates.index[-1]} trails at {stream_rates.iloc[-1]:.1f}%.")

story.append(PageBreak())

# ---------- 8. KPI Summary ----------
h1("8. KPI Summary")
kpi_data = [
    ["KPI", "Value"],
    ["Total Students", f"{total}"],
    ["Placed Students", f"{placed}"],
    ["Placement Rate", f"{placed/total*100:.1f}%"],
    ["Average Degree %", f"{df['degree_p'].mean():.1f}"],
    ["Work Experience Participation", f"{(df['workex']=='Yes').mean()*100:.1f}%"],
    ["Average Employability Test %", f"{df['etest_p'].mean():.1f}"],
    ["Average Package (Placed)", f"₹{df.loc[df['status']=='Placed','salary'].mean():,.0f}"],
    ["Median Package (Placed)", f"₹{df.loc[df['status']=='Placed','salary'].median():,.0f}"],
]
t = Table(kpi_data, hAlign="LEFT", colWidths=[3 * inch, 2.2 * inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4C6EF5")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F3F5")]),
]))
story.append(t)

# ---------- 9. Trend Analysis ----------
h1("9. Trend Analysis")
bullets([
    f"Overall placement rate across the cohort is {placed/total*100:.1f}%.",
    f"{stream_rates.index[0]} outperforms {stream_rates.index[-1]} by "
    f"{stream_rates.iloc[0]-stream_rates.iloc[-1]:.1f} percentage points in placement rate.",
    "Median package (₹%s) is meaningfully lower than mean package (₹%s) — a small number of high "
    "outlier offers pull the average up." % (
        f"{df.loc[df['status']=='Placed','salary'].median():,.0f}",
        f"{df.loc[df['status']=='Placed','salary'].mean():,.0f}",
    ),
])

# ---------- 10. Driver Analysis ----------
h1("10. Driver Analysis")
bullets([
    "Prior work experience is the single strongest categorical driver of placement rate.",
    f"10th-grade percentage is the strongest numeric driver (r = {corr.iloc[0]:.2f}), ahead of "
    "12th-grade and degree percentage.",
    "MBA specialisation and degree stream both show meaningful placement-rate gaps between their "
    "best- and worst-performing categories.",
])

# ---------- 11. Risks ----------
h1("11. Risks")
bullets([
    f"Students in the lowest-placing stream ({stream_rates.index[-1]}) and specialisation are "
    "at higher risk of remaining unplaced.",
    "Package figures reported as a simple average can overstate typical student outcomes because "
    "of right-skew from a small number of high offers.",
    "Students without work experience face a materially lower placement rate and may need "
    "additional support to close that gap.",
])

# ---------- 12. Opportunities ----------
h1("12. Opportunities")
bullets([
    "Structured pre-placement internship programs are the highest-leverage lever available in "
    "this dataset, given the size of the work-experience placement gap.",
    f"Mentoring or mock-interview pairing between {stream_rates.index[0]} and "
    f"{stream_rates.index[-1]} cohorts could help narrow the placement-rate gap.",
    "Publishing stream/specialisation-level placement rates lets institutions identify and "
    "support at-risk cohorts earlier in the year.",
])

# ---------- 13. Actionable Insights ----------
h1("13. Actionable Insights")
bullets([
    "Work experience before final placements is associated with the largest single improvement "
    "in placement likelihood in this dataset.",
    "Early academic consistency (10th/12th grade) matters more to placement outcomes here than a "
    "single late-stage test score — students should not rely on a strong final-year test to "
    "compensate for weaker early academics.",
    "Specialisation and stream choice correlate with materially different placement rates and "
    "should inform where institutions target extra support.",
])

# ---------- 14. Recommendations ----------
h1("14. Recommendations")
h2("For Students")
bullets([
    "Prioritise securing an internship or other work experience ahead of final placements.",
    "Build consistent academic performance from 10th grade onward rather than depending on a "
    "late-stage test score.",
    "If in a lower-placing specialisation or stream, seek targeted interview preparation and "
    "proactive employer outreach.",
])
h2("For Institutions")
bullets([
    "Expand structured internship/work-experience pipelines, particularly for streams and "
    "specialisations with below-average placement rates.",
    "Track and publish stream-level placement rates to identify at-risk cohorts earlier.",
    "Pair strong- and weak-placement-rate cohorts for mentoring and mock-interview practice.",
    "Consider adding certification and extracurricular-activity tracking to future data "
    "collection — neither is captured in the current dataset, limiting analysis depth.",
])

# ---------- 15. Machine Learning Model ----------
h1("15. Machine Learning Model")
p("No prediction model was built for this project. At 215 rows, a classifier would have limited "
  "statistical power and a high risk of overfitting to this specific cohort, and the project's "
  "goal is actionable, explainable insight rather than a black-box prediction. The correlation and "
  "group-comparison analysis in Sections 7 and 10 already identifies the same directional drivers "
  "a simple model would surface (work experience, early academic scores), without the added "
  "complexity and overfitting risk of a formal model on a dataset this small.")

# ---------- 16. Technologies Used ----------
h1("16. Technologies Used")
bullets([
    "Python, Pandas, NumPy — data loading, cleaning and analysis",
    "Plotly — interactive charts in the dashboard",
    "Matplotlib — static charts for this report",
    "Streamlit — interactive web dashboard",
    "ReportLab — this PDF report",
])

# ---------- 17. Dashboard Overview ----------
h1("17. Dashboard Overview")
p("The accompanying Streamlit dashboard (app.py) provides six pages: Overview (KPIs and headline "
  "charts), Academic Analysis, Employability Factors, Department/Stream Analysis, Salary Analysis, "
  "and Insights & Recommendations (auto-generated from whatever filters are currently applied). "
  "Sidebar filters for gender, degree stream, specialisation, placement status, work experience and "
  "degree-percentage range apply live across every page.")

# ---------- 18. Results ----------
h1("18. Results")
p(f"The cohort's overall placement rate is {placed/total*100:.1f}%. Work experience is the single "
  f"strongest categorical driver of placement outcome (86.5% vs 59.6% placement rate), and 10th-grade "
  f"percentage is the strongest numeric driver (r = {corr.iloc[0]:.2f}). {stream_rates.index[0]} and "
  f"Mkt&Fin specialisation post the strongest placement rates among their respective categories. "
  f"Median package (₹{df.loc[df['status']=='Placed','salary'].median():,.0f}) is a more representative "
  f"figure than mean package for typical student outcomes, given the right-skewed package distribution "
  f"shown in the dashboard's Salary Analysis tab.")

# ---------- 19. Conclusion ----------
h1("19. Conclusion")
p("This project demonstrates that a modest, well-understood dataset can still yield concrete, "
  "actionable findings when analyzed with clear KPIs and driver analysis rather than description "
  "alone. Work experience and early academic consistency emerge as the clearest levers available to "
  "students and institutions in this cohort.")

# ---------- 20. Future Scope ----------
h1("20. Future Scope")
bullets([
    "Incorporate multi-year data to analyze placement trends over time rather than a single "
    "cohort snapshot.",
    "Add certification and extracurricular-activity fields to widen the analysis.",
    "Revisit a predictive model once the dataset grows well beyond 215 rows.",
])

# ---------- 21. References / Dataset Source ----------
h1("21. References / Dataset Source")
p("Campus Recruitment dataset, Ben Roshan, Kaggle: "
  "https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement")

doc = SimpleDocTemplate(
    "project_report.pdf", pagesize=letter,
    leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.9 * inch, bottomMargin=0.9 * inch,
)
doc.build(story)
print("Report built.")
