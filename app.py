"""
Student Employability & Placement Analytics Dashboard
=======================================================
Analyzes campus placement data to surface KPIs, trends, drivers,
risks/opportunities and actionable recommendations.

Dataset: Campus Recruitment (Placement_Data_Full_Class.csv)
Source : Kaggle - "Campus Recruitment" by Ben Roshan
         https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement
Run    : streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Employability & Placement Analytics",
    page_icon="🎓",
    layout="wide",
)

PRIMARY = "#4C6EF5"
PLACED_COLOR = "#2F9E44"
NOT_PLACED_COLOR = "#E03131"


# ----------------------------------------------------------------------------
# Data loading & preprocessing
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path: str = "Placement_Data_Full_Class.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # --- Light cleaning / preprocessing ---
    # 1. Drop the row-index column; it carries no analytical value.
    if "sl_no" in df.columns:
        df = df.drop(columns=["sl_no"])

    # 2. Strip whitespace from string columns (defensive; source data is clean
    #    but this guards against re-exports with stray spaces).
    obj_cols = df.select_dtypes(include="object").columns
    for c in obj_cols:
        df[c] = df[c].str.strip()

    # 3. Missing `salary` is NOT missing data - it is structural: students
    #    with status == "Not Placed" were never offered a salary. We leave
    #    these as NaN (do not impute with 0 or mean) and always compute
    #    salary statistics on the placed subset only.

    # 4. Duplicate check (no-op if clean, but kept for transparency/logging).
    df = df.drop_duplicates()

    # 5. Friendly display names for the categorical columns used as filters.
    df = df.rename(
        columns={
            "degree_t": "degree_stream",
            "hsc_s": "hsc_stream",
        }
    )

    # 6. Derived column used across pages.
    df["placed_flag"] = (df["status"] == "Placed").astype(int)

    return df


df_raw = load_data()

# ----------------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------------
st.sidebar.title("🎓 Filters")
st.sidebar.caption("Filters apply to every page of the dashboard.")

gender_opts = sorted(df_raw["gender"].unique())
stream_opts = sorted(df_raw["degree_stream"].unique())
spec_opts = sorted(df_raw["specialisation"].unique())
status_opts = sorted(df_raw["status"].unique())
workex_opts = sorted(df_raw["workex"].unique())

sel_gender = st.sidebar.multiselect("Gender", gender_opts, default=gender_opts)
sel_stream = st.sidebar.multiselect(
    "Degree Stream (Department)", stream_opts, default=stream_opts
)
sel_spec = st.sidebar.multiselect(
    "MBA Specialisation", spec_opts, default=spec_opts
)
sel_status = st.sidebar.multiselect(
    "Placement Status", status_opts, default=status_opts
)
sel_workex = st.sidebar.multiselect(
    "Work Experience", workex_opts, default=workex_opts
)
degree_p_min, degree_p_max = float(df_raw["degree_p"].min()), float(df_raw["degree_p"].max())
sel_degree_range = st.sidebar.slider(
    "Degree Percentage range (closest available proxy for CGPA)",
    min_value=round(degree_p_min, 1),
    max_value=round(degree_p_max, 1),
    value=(round(degree_p_min, 1), round(degree_p_max, 1)),
)

if st.sidebar.button("Reset filters"):
    st.rerun()

df = df_raw[
    df_raw["gender"].isin(sel_gender)
    & df_raw["degree_stream"].isin(sel_stream)
    & df_raw["specialisation"].isin(sel_spec)
    & df_raw["status"].isin(sel_status)
    & df_raw["workex"].isin(sel_workex)
    & df_raw["degree_p"].between(sel_degree_range[0], sel_degree_range[1])
].copy()

st.sidebar.markdown("---")
st.sidebar.metric("Rows after filtering", f"{len(df)} / {len(df_raw)}")

if df.empty:
    st.warning("No students match the current filter selection. Adjust the filters in the sidebar.")
    st.stop()


# ----------------------------------------------------------------------------
# Shared helpers
# ----------------------------------------------------------------------------
def placement_rate(frame: pd.DataFrame) -> float:
    if len(frame) == 0:
        return 0.0
    return 100 * frame["placed_flag"].mean()


def kpi_row(frame: pd.DataFrame):
    total = len(frame)
    placed = int(frame["placed_flag"].sum())
    rate = placement_rate(frame)
    avg_degree = frame["degree_p"].mean()
    workex_rate = 100 * (frame["workex"] == "Yes").mean()
    avg_etest = frame["etest_p"].mean()
    placed_salary = frame.loc[frame["status"] == "Placed", "salary"]
    avg_salary = placed_salary.mean() if len(placed_salary) else np.nan

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", f"{total}")
    c2.metric("Placed Students", f"{placed}")
    c3.metric("Placement Rate", f"{rate:.1f}%")
    c4.metric("Avg. Degree %", f"{avg_degree:.1f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Work-Ex Participation", f"{workex_rate:.1f}%")
    c6.metric("Avg. Employability Test %", f"{avg_etest:.1f}")
    c7.metric(
        "Avg. Package (Placed)",
        f"₹{avg_salary:,.0f}" if not np.isnan(avg_salary) else "N/A",
    )
    top_stream = (
        frame.groupby("degree_stream")["placed_flag"].mean().idxmax()
        if frame["degree_stream"].nunique() > 0
        else "N/A"
    )
    c8.metric("Highest-Placing Stream", top_stream)


# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("🎓 Student Employability & Placement Analytics Dashboard")
st.caption(
    "Campus Recruitment dataset (215 students) — academic performance, "
    "internship/work-experience, specialisation and placement outcomes."
)

tab_overview, tab_academic, tab_employ, tab_stream, tab_salary, tab_insights = st.tabs(
    [
        "📊 Overview",
        "🎓 Academic Analysis",
        "💼 Employability Factors",
        "🏛️ Department / Stream Analysis",
        "💰 Salary Analysis",
        "💡 Insights & Recommendations",
    ]
)

# ----------------------------------------------------------------------------
# TAB 1 — Overview
# ----------------------------------------------------------------------------
with tab_overview:
    st.subheader("Key Performance Indicators")
    kpi_row(df)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Placement Status Distribution**")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig = px.pie(
            status_counts,
            names="status",
            values="count",
            color="status",
            color_discrete_map={"Placed": PLACED_COLOR, "Not Placed": NOT_PLACED_COLOR},
            hole=0.45,
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Placement Rate by Gender**")
        g = df.groupby("gender")["placed_flag"].mean().mul(100).reset_index()
        g.columns = ["gender", "placement_rate"]
        fig = px.bar(
            g, x="gender", y="placement_rate", color="gender",
            text=g["placement_rate"].round(1).astype(str) + "%",
            labels={"placement_rate": "Placement Rate (%)", "gender": "Gender"},
        )
        fig.update_layout(showlegend=False, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Dataset Snapshot**")
    with st.expander("Show raw filtered data"):
        st.dataframe(df, use_container_width=True)
    with st.expander("Data quality summary"):
        dq = pd.DataFrame(
            {
                "column": df_raw.columns,
                "dtype": df_raw.dtypes.astype(str).values,
                "missing_values": df_raw.isnull().sum().values,
                "missing_%": (df_raw.isnull().mean() * 100).round(1).values,
            }
        )
        st.dataframe(dq, use_container_width=True, hide_index=True)
        st.caption(
            "`salary` is the only column with missing values (67 of 215 rows). "
            "This is structural, not a data-quality issue: unplaced students "
            "were never offered a salary, so these rows are excluded from salary "
            "statistics rather than imputed."
        )

# ----------------------------------------------------------------------------
# TAB 2 — Academic Analysis
# ----------------------------------------------------------------------------
with tab_academic:
    st.subheader("Academic Performance")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Degree % Distribution by Placement Status**")
        fig = px.histogram(
            df, x="degree_p", color="status", barmode="overlay", nbins=25,
            color_discrete_map={"Placed": PLACED_COLOR, "Not Placed": NOT_PLACED_COLOR},
            labels={"degree_p": "Degree Percentage"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**Academic Scores: Placed vs Not Placed (avg)**")
        academic_cols = ["ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"]
        avg_by_status = df.groupby("status")[academic_cols].mean().reset_index()
        avg_long = avg_by_status.melt(id_vars="status", var_name="metric", value_name="avg_score")
        fig = px.bar(
            avg_long, x="metric", y="avg_score", color="status", barmode="group",
            color_discrete_map={"Placed": PLACED_COLOR, "Not Placed": NOT_PLACED_COLOR},
            labels={"avg_score": "Average %", "metric": "Academic Stage"},
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**10th vs 12th vs Degree % (by student)**")
        fig = px.scatter(
            df, x="ssc_p", y="degree_p", color="status", size="hsc_p",
            color_discrete_map={"Placed": PLACED_COLOR, "Not Placed": NOT_PLACED_COLOR},
            labels={"ssc_p": "10th %", "degree_p": "Degree %"},
            hover_data=["hsc_p", "specialisation"],
        )
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        st.markdown("**Degree % by Stream**")
        fig = px.box(
            df, x="degree_stream", y="degree_p", color="degree_stream",
            labels={"degree_stream": "Degree Stream", "degree_p": "Degree %"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Correlation: Academic Scores vs Placement**")
    corr = df[academic_cols + ["placed_flag"]].corr()["placed_flag"].drop("placed_flag")
    corr = corr.sort_values(ascending=False).reset_index()
    corr.columns = ["academic_stage", "correlation_with_placement"]
    fig = px.bar(
        corr, x="academic_stage", y="correlation_with_placement",
        color="correlation_with_placement", color_continuous_scale="Blues",
        labels={"correlation_with_placement": "Correlation with being Placed"},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Correlation, not causation: this shows association strength only. "
        "Earlier academic stages (10th, 12th) correlate more strongly with "
        "placement than the MBA/employability-test scores in this dataset."
    )

# ----------------------------------------------------------------------------
# TAB 3 — Employability Factors
# ----------------------------------------------------------------------------
with tab_employ:
    st.subheader("Employability Factors")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Work Experience vs Placement**")
        t = pd.crosstab(df["workex"], df["status"], normalize="index").mul(100).reset_index()
        t_long = t.melt(id_vars="workex", var_name="status", value_name="pct")
        fig = px.bar(
            t_long, x="workex", y="pct", color="status", barmode="stack",
            color_discrete_map={"Placed": PLACED_COLOR, "Not Placed": NOT_PLACED_COLOR},
            labels={"pct": "% of students", "workex": "Prior Work Experience"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**MBA Specialisation vs Placement**")
        t = pd.crosstab(df["specialisation"], df["status"], normalize="index").mul(100).reset_index()
        t_long = t.melt(id_vars="specialisation", var_name="status", value_name="pct")
        fig = px.bar(
            t_long, x="specialisation", y="pct", color="status", barmode="stack",
            color_discrete_map={"Placed": PLACED_COLOR, "Not Placed": NOT_PLACED_COLOR},
            labels={"pct": "% of students", "specialisation": "MBA Specialisation"},
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Employability Test % by Placement Status**")
        fig = px.box(
            df, x="status", y="etest_p", color="status",
            color_discrete_map={"Placed": PLACED_COLOR, "Not Placed": NOT_PLACED_COLOR},
            labels={"etest_p": "Employability Test %"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        st.markdown("**12th (HSC) Stream vs Placement Rate**")
        h = df.groupby("hsc_stream")["placed_flag"].mean().mul(100).reset_index()
        h.columns = ["hsc_stream", "placement_rate"]
        fig = px.bar(
            h, x="hsc_stream", y="placement_rate", color="hsc_stream",
            text=h["placement_rate"].round(1).astype(str) + "%",
            labels={"placement_rate": "Placement Rate (%)", "hsc_stream": "12th Stream"},
        )
        fig.update_layout(showlegend=False, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Note: this dataset does not include separate 'certifications' or "
        "'extracurricular activities' fields — work experience, employability "
        "test score, and academic stream are the closest available proxies "
        "for skill-development signals."
    )

# ----------------------------------------------------------------------------
# TAB 4 — Department / Stream Analysis
# ----------------------------------------------------------------------------
with tab_stream:
    st.subheader("Department / Stream Analysis")
    st.caption(
        "This dataset has a single cohort (one 'department'); the closest "
        "grouping variables are Degree Stream and MBA Specialisation, used here "
        "as department-equivalent segments."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Student Count by Degree Stream**")
        c = df["degree_stream"].value_counts().reset_index()
        c.columns = ["degree_stream", "count"]
        fig = px.bar(c, x="degree_stream", y="count", color="degree_stream")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**Placement Rate by Degree Stream**")
        r = df.groupby("degree_stream")["placed_flag"].mean().mul(100).reset_index()
        r.columns = ["degree_stream", "placement_rate"]
        fig = px.bar(
            r, x="degree_stream", y="placement_rate", color="degree_stream",
            text=r["placement_rate"].round(1).astype(str) + "%",
            labels={"placement_rate": "Placement Rate (%)"},
        )
        fig.update_layout(showlegend=False, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Average Package by Degree Stream (placed students only)**")
    placed_df = df[df["status"] == "Placed"]
    if len(placed_df):
        p = placed_df.groupby("degree_stream")["salary"].mean().round(0).reset_index()
        fig = px.bar(
            p, x="degree_stream", y="salary", color="degree_stream",
            labels={"salary": "Avg. Package (₹)"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No placed students in the current filter selection.")

    st.markdown("**Stream × Specialisation Placement Heatmap**")
    pivot = pd.pivot_table(
        df, index="degree_stream", columns="specialisation",
        values="placed_flag", aggfunc="mean",
    ).mul(100)
    fig = px.imshow(
        pivot, text_auto=".1f", color_continuous_scale="Blues", aspect="auto",
        labels=dict(color="Placement Rate (%)"),
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 5 — Salary Analysis
# ----------------------------------------------------------------------------
with tab_salary:
    st.subheader("Salary / Package Analysis")
    placed_df = df[df["status"] == "Placed"].copy()

    if placed_df.empty:
        st.warning("No placed students in the current filter selection — salary analysis unavailable.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg. Package", f"₹{placed_df['salary'].mean():,.0f}")
        c2.metric("Median Package", f"₹{placed_df['salary'].median():,.0f}")
        c3.metric("Min Package", f"₹{placed_df['salary'].min():,.0f}")
        c4.metric("Max Package", f"₹{placed_df['salary'].max():,.0f}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Package Distribution**")
            fig = px.histogram(placed_df, x="salary", nbins=25, labels={"salary": "Package (₹)"})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("**Package by Gender**")
            fig = px.box(placed_df, x="gender", y="salary", color="gender", labels={"salary": "Package (₹)"})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**Package by Work Experience**")
            fig = px.box(placed_df, x="workex", y="salary", color="workex", labels={"salary": "Package (₹)"})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col4:
            st.markdown("**Package vs Degree %**")
            fig = px.scatter(
                placed_df, x="degree_p", y="salary", color="degree_stream",
                labels={"degree_p": "Degree %", "salary": "Package (₹)"},
            )
            st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Package shows a long right tail driven by a small number of high "
            "outlier offers - median package is a more representative figure "
            "than the mean for most students."
        )

# ----------------------------------------------------------------------------
# TAB 6 — Insights & Recommendations
# ----------------------------------------------------------------------------
with tab_insights:
    st.subheader("💡 Insights & Recommendations")
    st.caption("Auto-generated from the currently filtered data — adjust the sidebar filters to re-run.")

    rate = placement_rate(df)
    workex_yes_rate = placement_rate(df[df["workex"] == "Yes"]) if (df["workex"] == "Yes").any() else np.nan
    workex_no_rate = placement_rate(df[df["workex"] == "No"]) if (df["workex"] == "No").any() else np.nan
    academic_cols = ["ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"]
    corr = df[academic_cols + ["placed_flag"]].corr()["placed_flag"].drop("placed_flag").sort_values(ascending=False)
    strongest_driver = corr.index[0]
    stream_rates = df.groupby("degree_stream")["placed_flag"].mean().mul(100).sort_values(ascending=False)
    spec_rates = df.groupby("specialisation")["placed_flag"].mean().mul(100).sort_values(ascending=False)

    st.markdown("### Trends")
    st.markdown(
        f"- Overall placement rate in the current selection is **{rate:.1f}%** "
        f"({int(df['placed_flag'].sum())} of {len(df)} students)."
    )
    st.markdown(
        f"- **{stream_rates.index[0]}** has the highest placement rate among degree "
        f"streams (**{stream_rates.iloc[0]:.1f}%**), vs **{stream_rates.index[-1]}** "
        f"at **{stream_rates.iloc[-1]:.1f}%**."
    )
    st.markdown(
        f"- **{spec_rates.index[0]}** specialisation placements outperform "
        f"**{spec_rates.index[-1]}** ({spec_rates.iloc[0]:.1f}% vs {spec_rates.iloc[-1]:.1f}%)."
    )

    st.markdown("### Drivers")
    st.markdown(
        f"- Among the numeric factors tracked, **{strongest_driver}** has the "
        f"strongest positive correlation with placement (r = {corr.iloc[0]:.2f})."
    )
    if not np.isnan(workex_yes_rate) and not np.isnan(workex_no_rate):
        st.markdown(
            f"- Prior work experience is associated with a placement rate of "
            f"**{workex_yes_rate:.1f}%**, vs **{workex_no_rate:.1f}%** for students "
            f"without it — the largest single-factor gap in the dataset."
        )
    st.markdown(
        "- Early academic performance (10th/12th) correlates more strongly with "
        "placement than later-stage scores (MBA %, employability test %) in this "
        "cohort — consistent with academic consistency mattering more than a "
        "single late-stage test result."
    )

    st.markdown("### Risks")
    weak_stream = stream_rates.index[-1]
    st.markdown(
        f"- Students in **{weak_stream}** and in the **{spec_rates.index[-1]}** "
        f"specialisation show below-average placement rates and may need "
        f"additional support."
    )
    st.markdown(
        "- A wide package range (large gap between median and mean) means "
        "average-package figures can overstate typical outcomes; a small number "
        "of high offers pull the mean up."
    )

    st.markdown("### Opportunities")
    st.markdown(
        "- Because work experience shows the largest placement-rate gap, "
        "structured pre-placement internships are likely the highest-leverage "
        "intervention available in this dataset."
    )
    st.markdown(
        f"- Reinforcing strong **{stream_rates.index[0]}**-style outcomes in "
        f"lower-performing streams (e.g. shared mentoring, mock interviews) "
        f"could narrow the placement-rate gap."
    )

    st.markdown("### Actionable Recommendations")
    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.markdown("**For Students**")
        st.markdown(
            "- Prioritise securing an internship or work experience before "
            "final placements - it shows the strongest association with "
            "getting placed.\n"
            "- Maintain consistency from 10th/12th grade onward rather than "
            "relying on a late-stage test score to compensate.\n"
            "- Students in lower-placing specialisations should seek targeted "
            "interview preparation and employer outreach."
        )
    with rec_col2:
        st.markdown("**For Institutions**")
        st.markdown(
            "- Expand structured internship/work-experience pipelines, "
            "especially for streams and specialisations with below-average "
            "placement rates.\n"
            "- Track and publish stream-level placement rates so at-risk "
            "cohorts can be identified and supported earlier.\n"
            "- Pair strong- and weak-placement-rate cohorts for peer "
            "mentoring / mock interview practice."
        )

    st.caption(
        "These insights describe associations observed in this dataset and "
        "current filter selection; they are not causal claims."
    )
