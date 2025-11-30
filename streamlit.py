import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st

warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="Global Research Performance Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_csv("data/publications.csv")
    return df


df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

countries = ["All Countries"] + sorted(df["Name"].unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", countries)

year_range = st.sidebar.slider(
    "Select Year Range",
    int(df["year"].min()),
    int(df["year"].max()),
    (int(df["year"].min()), int(df["year"].max())),
)

cnci_min = st.sidebar.slider("Minimum CNCI", 0.0, 2.0, 0.0, 0.1)

# Filter dataframe based on sidebar picks
filtered_df = df[
    (df["year"] >= year_range[0])
    & (df["year"] <= year_range[1])
    & (df["Category Normalized Citation Impact"] >= cnci_min)
]

if selected_country != "All Countries":
    filtered_df = filtered_df[filtered_df["Name"] == selected_country]

filtered_df = filtered_df.copy()  # Avoid SettingWithCopyWarning

# Add Collaboration Advantage column
filtered_df["Collab_Advantage"] = (
    filtered_df["Collab-CNCI"] - filtered_df["Category Normalized Citation Impact"]
)

# ----------- Title and introductory section -----------

st.title("Global Research Performance Analysis: 2003–2025")
st.markdown(
    """
This analysis covers 17 leading countries’ research output and impact over 23 years.  
The focus is on understanding **what drives research excellence** beyond the popular assumptions.
"""
)

st.markdown("---")

# ----------- Story Chapter 1: The Collaboration Paradox -----------

st.header("1. The Collaboration Paradox")

st.subheader("Finding")
st.markdown(
    """
While collaboration is widely considered a key success factor, our data reveals a surprising finding: more than half of international collaborations do **not** increase normalized impact.
"""
)

st.subheader("Hypothesis")
st.markdown(
    """
The quality and strategic nature of collaborations matter more than the mere quantity of partnerships. Some collaborations may dilute focus or spread resources thin.
"""
)

st.subheader("Proof")
# Histogram of Collaboration Impact Difference
fig_collab = px.histogram(
    filtered_df,
    x="Collab_Advantage",
    nbins=50,
    title="Distribution of Collaboration Impact on Normalized Citation Impact (CNCI)",
    labels={"Collab_Advantage": "Collaboration CNCI Advantage (Collab-CNCI - CNCI)"},
    color_discrete_sequence=["#377eb8"],
)
fig_collab.add_vline(
    x=0,
    line_dash="dash",
    line_color="red",
    annotation_text="No Impact",
    annotation_position="top right",
)
st.plotly_chart(fig_collab, use_container_width=True)

# Collaboration effect summary
collab_helpful_pct = (filtered_df["Collab_Advantage"] > 0).mean() * 100
avg_collab_adv = filtered_df["Collab_Advantage"].mean()

st.markdown(
    f"""
- Only **{collab_helpful_pct:.1f}%** of collaborations actually improve normalized impact (CNCI).  
- On average, collaboration reduces CNCI by **{abs(avg_collab_adv):.3f}**, indicating many partnerships may be counterproductive.
"""
)

st.subheader("Answer")
st.markdown(
    """
This finding challenges conventional wisdom: instead of pursuing more collaborations, research leaders should **focus on forming high-quality, strategically aligned partnerships**.
"""
)

st.markdown("---")

# ----------- Story Chapter 2: Quality vs Quantity -----------

st.header("2. Quality vs Quantity in Research Output")

st.subheader("Finding")
st.markdown(
    """
Publishing more papers doesn't necessarily correlate with greater normalized impact. Some countries have smaller output but higher research quality.
"""
)

st.subheader("Hypothesis")
st.markdown(
    """
Research excellence depends on prioritizing quality over sheer volume. High output alone may dilute average impact.
"""
)

st.subheader("Proof")
country_metrics = (
    filtered_df.groupby("Name")
    .agg(
        total_papers=pd.NamedAgg(column="Web of Science Documents", aggfunc="sum"),
        total_citations=pd.NamedAgg(column="Times Cited", aggfunc="sum"),
        avg_cnci=pd.NamedAgg(
            column="Category Normalized Citation Impact", aggfunc="mean"
        ),
        avg_top10=pd.NamedAgg(column="% Documents in Top 10%", aggfunc="mean"),
    )
    .reset_index()
)

fig_quality_quantity = px.scatter(
    country_metrics,
    x="total_papers",
    y="avg_cnci",
    size="total_citations",
    color="avg_top10",
    hover_name="Name",
    labels={
        "total_papers": "Total Publications",
        "avg_cnci": "Average CNCI (Normalized Impact)",
        "total_citations": "Total Citations",
        "avg_top10": "% Papers in Top 10%",
    },
    title="Research Quality vs Quantity Across Countries",
    color_continuous_scale="Viridis",
)
fig_quality_quantity.add_hline(
    y=1, line_dash="dash", line_color="red", annotation_text="World Avg CNCI"
)
st.plotly_chart(fig_quality_quantity, use_container_width=True)

st.subheader("Answer")
st.markdown(
    """
Countries like Japan and Italy demonstrate that prioritizing quality leads to sustainable impact even with moderate publication volume, unlike some high-output countries with lower normalized impact.
"""
)

st.markdown("---")

# ----------- Story Chapter 3: Temporal Trends -----------

st.header("3. Research Evolution Over 23 Years")

st.subheader("Finding")
st.markdown(
    """
Between 2003-2005 and 2023-2025, total research output decreased slightly, but average impact remained stable.
"""
)

st.subheader("Hypothesis")
st.markdown(
    """
This suggests an emphasis on sustaining quality throughout changing research volumes, possibly reflecting strategic prioritization.
"""
)

st.subheader("Proof")
yearly_metrics = (
    filtered_df.groupby("year")
    .agg(
        total_papers=pd.NamedAgg(column="Web of Science Documents", aggfunc="sum"),
        total_citations=pd.NamedAgg(column="Times Cited", aggfunc="sum"),
        avg_cnci=pd.NamedAgg(
            column="Category Normalized Citation Impact", aggfunc="mean"
        ),
        avg_top10=pd.NamedAgg(column="% Documents in Top 10%", aggfunc="mean"),
    )
    .reset_index()
)

fig_trends = make_subplots(
    rows=2,
    cols=1,
    subplot_titles=[
        "Research Output and Citations Over Time",
        "Normalized Impact Over Time",
    ],
    vertical_spacing=0.15,
)

fig_trends.add_trace(
    go.Bar(
        x=yearly_metrics["year"],
        y=yearly_metrics["total_papers"],
        name="Total Publications",
        marker_color="lightblue",
    ),
    row=1,
    col=1,
)
fig_trends.add_trace(
    go.Bar(
        x=yearly_metrics["year"],
        y=yearly_metrics["total_citations"],
        name="Total Citations",
        marker_color="lightgreen",
    ),
    row=1,
    col=1,
)
fig_trends.add_trace(
    go.Scatter(
        x=yearly_metrics["year"],
        y=yearly_metrics["avg_cnci"],
        name="Average CNCI",
        mode="lines+markers",
        line=dict(color="darkblue", width=3),
    ),
    row=2,
    col=1,
)
fig_trends.add_hline(y=1, line_dash="dash", line_color="red", row=2, col=1)

fig_trends.update_layout(height=700, showlegend=True)
fig_trends.update_xaxes(title_text="Year", row=2, col=1)
fig_trends.update_yaxes(title_text="Count", row=1, col=1)
fig_trends.update_yaxes(title_text="CNCI", row=2, col=1)

st.plotly_chart(fig_trends, use_container_width=True)

st.subheader("Answer")
st.markdown(
    """
The stability of CNCI despite changes in output volume underscores a mature research system that can maintain consistent quality, possibly by focusing on impactful studies.
"""
)

st.markdown("---")

# ----------- Story Chapter 4: Excellence Concentration -----------

st.header("4. Concentration of Research Excellence")

st.subheader("Finding")
st.markdown(
    """
Only 40% of the analyzed records have greater than 2% of their papers in the top 1% of citation percentiles, yet these contribute to nearly 40% of total output.
"""
)

st.subheader("Hypothesis")
st.markdown(
    """
Research excellence is highly concentrated: a minority of records account for a large share of top-tier publications.
"""
)

st.subheader("Proof")
high_excellence = filtered_df[filtered_df["% Documents in Top 1%"] > 2]
excellence_share = (
    high_excellence["Web of Science Documents"].sum()
    / filtered_df["Web of Science Documents"].sum()
) * 100

st.markdown(
    f"""
- Number of high-excellence records: {len(high_excellence)} ({len(high_excellence) / len(filtered_df) * 100:.1f}%).  
- These contribute {excellence_share:.1f}% to the total publications.
"""
)

fig_excellence = px.histogram(
    filtered_df,
    x="% Documents in Top 1%",
    nbins=40,
    title="Distribution of Top 1% Citation Excellence",
    labels={"% Documents in Top 1%": "% Papers in Top 1%"},
    color_discrete_sequence=["#1b9e77"],
)
st.plotly_chart(fig_excellence, use_container_width=True)

st.subheader("Answer")
st.markdown(
    """
Strategic investment in nurturing and sustaining high-excellence groups yields disproportionate impact on national research outcomes.
"""
)

st.markdown("---")

# ----------- Story Chapter 5: Country Deep Dive -----------

if selected_country != "All Countries":
    st.header(f"5. In-Depth Analysis: {selected_country}")

    country_data = filtered_df[filtered_df["Name"] == selected_country]
    st.markdown(
        f"Analyzing research output and impact trends of {selected_country} over the selected years."
    )

    # Summary metrics
    st.subheader("Summary Statistics")
    st.markdown(
        f"""
- Total Publications: {country_data["Web of Science Documents"].sum():,}  
- Total Citations: {country_data["Times Cited"].sum():,}  
- Average CNCI: {country_data["Category Normalized Citation Impact"].mean():.3f}  
- Percentage Papers in Top 1%: {country_data["% Documents in Top 1%"].mean():.2f}%  
- Years Tracked: {country_data["year"].nunique()}
"""
    )

    yearly_country = (
        country_data.groupby("year")
        .agg(
            total_pubs=pd.NamedAgg(column="Web of Science Documents", aggfunc="sum"),
            avg_cnci=pd.NamedAgg(
                column="Category Normalized Citation Impact", aggfunc="mean"
            ),
            top1_pct=pd.NamedAgg(column="% Documents in Top 1%", aggfunc="mean"),
        )
        .reset_index()
    )

    fig_country_trends = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=[
            f"{selected_country} Publications Over Time",
            f"{selected_country} CNCI Over Time",
        ],
        vertical_spacing=0.15,
    )

    fig_country_trends.add_trace(
        go.Bar(
            x=yearly_country["year"],
            y=yearly_country["total_pubs"],
            name="Total Publications",
            marker_color="darkblue",
        ),
        row=1,
        col=1,
    )

    fig_country_trends.add_trace(
        go.Scatter(
            x=yearly_country["year"],
            y=yearly_country["avg_cnci"],
            name="Average CNCI",
            mode="lines+markers",
            line=dict(color="orange", width=3),
        ),
        row=2,
        col=1,
    )
    fig_country_trends.add_hline(y=1, line_dash="dash", line_color="red", row=2, col=1)

    fig_country_trends.update_xaxes(title_text="Year", row=2, col=1)
    fig_country_trends.update_yaxes(title_text="Publications", row=1, col=1)
    fig_country_trends.update_yaxes(title_text="CNCI", row=2, col=1)
    fig_country_trends.update_layout(height=700, showlegend=True)

    st.plotly_chart(fig_country_trends, use_container_width=True)

    st.subheader("Summary Conclusion")
    st.markdown(
        f"""
{selected_country}'s research impact and output display notable trends over time. This detailed view can help policymakers and research leaders target improvement areas or sustain success.
"""
    )

st.markdown("---")

# ----------- Footer -----------

st.markdown(
    """
<div style="text-align:center; font-size:0.8rem; color:#777;">
    Data Source: Web of Science (2003-2025) |  
    Methodology: CNCI (Category Normalized Citation Impact, 1.0 is world average) |  
    Developed for PAIU-OPSA, IISc Bangalore
</div>
""",
    unsafe_allow_html=True,
)
