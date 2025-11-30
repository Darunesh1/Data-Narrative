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


st.markdown("##  General Findings (Filtered Data)")

if len(filtered_df) == 0:
    st.warning(
        "No data available for the current filter selection. Please adjust the filters in the sidebar."
    )
else:
    total_records = len(filtered_df)
    unique_countries = filtered_df["Name"].nunique()
    total_publications = filtered_df["Web of Science Documents"].sum()
    total_citations = filtered_df["Times Cited"].sum()
    avg_citations_per_doc = (
        total_citations / total_publications if total_publications > 0 else 0
    )
    avg_cnci = filtered_df["Category Normalized Citation Impact"].mean()
    above_avg_count = (filtered_df["Category Normalized Citation Impact"] > 1.0).sum()
    above_avg_pct = above_avg_count / total_records * 100

    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.markdown(f"**Records in View:** {total_records:,}")
        st.markdown(f"**Countries in View:** {unique_countries}")
    with col_g2:
        st.markdown(f"**Total Publications (filtered):** {total_publications:,}")
        st.markdown(f"**Total Citations (filtered):** {total_citations:,}")
    with col_g3:
        st.markdown(f"**Avg Citations per Paper:** {avg_citations_per_doc:.2f}")
        st.markdown(f"**Avg CNCI (filtered):** {avg_cnci:.3f}")
        st.markdown(f"**Above World Avg CNCI:** {above_avg_pct:.1f}% of records")

    st.markdown(
        """
These figures update automatically with your filter selections and provide context on  
how much of the full dataset is currently being examined and how strong its impact is.
"""
    )

st.markdown("---")

# ============================================================================
# CHAPTER 1: THE GIANTS VS THE MASTERS
# ============================================================================
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("##  Chapter 1: The Giants vs The Masters")
st.markdown("""
**Question:** *Does publishing more papers lead to higher impact?*

Let's compare countries by **volume (total citations)** vs **quality (average CNCI)**.
""")
st.markdown("</div>", unsafe_allow_html=True)

# Aggregate by country
country_agg = (
    filtered_df.groupby("Name")
    .agg(
        {
            "Web of Science Documents": "sum",
            "Times Cited": "sum",
            "Category Normalized Citation Impact": "mean",
            "% Documents in Top 1%": "mean",
            "% Documents in Top 10%": "mean",
            "Collab-CNCI": "mean",
            "year": "count",
        }
    )
    .reset_index()
)

country_agg.columns = [
    "Country",
    "Total_Docs",
    "Total_Citations",
    "Avg_CNCI",
    "Avg_Top1",
    "Avg_Top10",
    "Avg_Collab_CNCI",
    "Years_Tracked",
]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏋️ Volume Champions (Total Citations)")
    top_citations = country_agg.nlargest(10, "Total_Citations")[
        ["Country", "Total_Citations", "Avg_CNCI"]
    ]
    top_citations["Total_Citations"] = top_citations["Total_Citations"].apply(
        lambda x: f"{x:,.0f}"
    )
    top_citations["Avg_CNCI"] = top_citations["Avg_CNCI"].round(3)
    st.dataframe(top_citations, hide_index=True, use_container_width=True)

with col2:
    st.markdown("###  Quality Masters (Avg CNCI)")
    top_quality = country_agg.nlargest(10, "Avg_CNCI")[
        ["Country", "Avg_CNCI", "Total_Docs"]
    ]
    top_quality["Total_Docs"] = top_quality["Total_Docs"].apply(lambda x: f"{x:,.0f}")
    top_quality["Avg_CNCI"] = top_quality["Avg_CNCI"].round(3)
    st.dataframe(top_quality, hide_index=True, use_container_width=True)

# Scatter plot: Volume vs Quality
fig_scatter = px.scatter(
    country_agg,
    x="Total_Docs",
    y="Avg_CNCI",
    size="Total_Citations",
    color="Avg_Top10",
    hover_name="Country",
    hover_data={"Total_Docs": ":,.0f", "Avg_CNCI": ":.3f", "Total_Citations": ":,.0f"},
    labels={
        "Total_Docs": "Total Publications",
        "Avg_CNCI": "Average CNCI (Quality)",
        "Avg_Top10": "% in Top 10%",
    },
    title="Quality vs Quantity: The Research Performance Matrix",
    color_continuous_scale="Viridis",
)
fig_scatter.add_hline(
    y=1.0,
    line_dash="dash",
    line_color="red",
    annotation_text="World Average (CNCI=1.0)",
)
fig_scatter.update_layout(height=500)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown('<div class="insight-box">', unsafe_allow_html=True)
st.markdown(f"""
### 🔍 Insight:
- **Spain, Switzerland, Brazil** dominate in total citations (volume)
- **Japan, Italy, Spain** lead in normalized impact (quality)
- **Spain** uniquely balances both: highest citations AND top-3 quality
- Countries above the red line exceed world-average performance
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# CHAPTER 2: THE COLLABORATION PARADOX
# ============================================================================
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("##  Chapter 2: The Collaboration Paradox")
st.markdown("""
**Conventional Wisdom:** *"International collaboration boosts research impact."*  
**Our Data Says:** Not always. Let's investigate.
""")
st.markdown("</div>", unsafe_allow_html=True)

# Collaboration analysis
filtered_df["Collab_Advantage"] = (
    filtered_df["Collab-CNCI"] - filtered_df["Category Normalized Citation Impact"]
)
filtered_df["Collab_Helps"] = filtered_df["Collab_Advantage"] > 0

col1, col2 = st.columns(2)

with col1:
    # Pie chart: Collaboration effect distribution
    collab_effect = filtered_df["Collab_Helps"].value_counts()
    if len(collab_effect) == 2:
        hurts = collab_effect[False]
        helps = collab_effect[True]
    else:
        # Handle edge case when all True or all False
        helps = collab_effect.get(True, 0)
        hurts = collab_effect.get(False, 0)
    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=["Collaboration Hurts", "Collaboration Helps"],
                values=[hurts, helps],
                marker=dict(colors=["#ff6b6b", "#51cf66"]),
                hole=0.4,
            )
        ]
    )
    success_pct = helps / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    fig_pie.update_layout(
        title="When Does Collaboration Help?",
        annotations=[
            dict(
                text=f"{success_pct:.1f}%<br>Success",
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False,
            )
        ],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Bar chart: Collab advantage by country
    collab_by_country = (
        filtered_df.groupby("Name")["Collab_Advantage"].mean().sort_values()
    )
    fig_collab = go.Figure(
        data=[
            go.Bar(
                x=collab_by_country.values,
                y=collab_by_country.index,
                orientation="h",
                marker=dict(
                    color=collab_by_country.values, colorscale="RdYlGn", cmid=0
                ),
            )
        ]
    )
    fig_collab.add_vline(x=0, line_dash="dash", line_color="black")
    fig_collab.update_layout(
        title="Collaboration Impact by Country",
        xaxis_title="CNCI Advantage (Collab - Solo)",
        yaxis_title="",
        height=500,
    )
    st.plotly_chart(fig_collab, use_container_width=True)

st.markdown('<div class="insight-box">', unsafe_allow_html=True)
st.markdown(f"""
### 🔍 Insight:
- Only **{(filtered_df["Collab_Helps"].sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0):.1f}%** of records show positive collaboration effect
- Average collaboration impact: **{filtered_df["Collab_Advantage"].mean():.3f}** (negative!)
- **Winners**: Countries on the right benefit from international partnerships
- **Losers**: Countries on the left see diminished impact with collaboration
- **Hypothesis**: Quality of collaboration matters more than quantity
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# CHAPTER 3: EVOLUTION OVER TWO DECADES
# ============================================================================
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("##  Chapter 3: 23 Years of Evolution (2003-2025)")
st.markdown("""
**Question:** *Has research quality improved, declined, or stayed stable?*
""")
st.markdown("</div>", unsafe_allow_html=True)

# Yearly trends
yearly_trends = (
    filtered_df.groupby("year")
    .agg(
        {
            "Web of Science Documents": "sum",
            "Times Cited": "sum",
            "Category Normalized Citation Impact": "mean",
            "% Documents in Top 10%": "mean",
            "% Documents in Top 1%": "mean",
        }
    )
    .reset_index()
)

# Multi-axis plot
fig_trends = make_subplots(
    rows=2,
    cols=1,
    subplot_titles=(
        "Research Output & Citations Over Time",
        "Quality Metrics Over Time",
    ),
    vertical_spacing=0.15,
)

# Row 1: Output and Citations
fig_trends.add_trace(
    go.Scatter(
        x=yearly_trends["year"],
        y=yearly_trends["Web of Science Documents"],
        name="Publications",
        line=dict(color="#1f77b4", width=3),
    ),
    row=1,
    col=1,
)
fig_trends.add_trace(
    go.Scatter(
        x=yearly_trends["year"],
        y=yearly_trends["Times Cited"],
        name="Citations",
        line=dict(color="#ff7f0e", width=3),
        yaxis="y2",
    ),
    row=1,
    col=1,
)

# Row 2: Quality metrics
fig_trends.add_trace(
    go.Scatter(
        x=yearly_trends["year"],
        y=yearly_trends["Category Normalized Citation Impact"],
        name="Avg CNCI",
        line=dict(color="#2ca02c", width=3),
    ),
    row=2,
    col=1,
)
fig_trends.add_trace(
    go.Scatter(
        x=yearly_trends["year"],
        y=yearly_trends["% Documents in Top 10%"],
        name="% in Top 10%",
        line=dict(color="#d62728", width=3),
        yaxis="y4",
    ),
    row=2,
    col=1,
)

fig_trends.add_hline(
    y=1.0,
    line_dash="dash",
    line_color="gray",
    row=2,
    col=1,
    annotation_text="World Average",
)

fig_trends.update_xaxes(title_text="Year", row=2, col=1)
fig_trends.update_yaxes(title_text="Publications", row=1, col=1)
fig_trends.update_yaxes(title_text="CNCI", row=2, col=1)
fig_trends.update_layout(height=700, showlegend=True)

st.plotly_chart(fig_trends, use_container_width=True)

# Calculate trends
early_years = yearly_trends[yearly_trends["year"] <= 2007]
recent_years = yearly_trends[yearly_trends["year"] >= 2021]

if len(early_years) > 0 and len(recent_years) > 0:
    output_change = (
        (
            recent_years["Web of Science Documents"].mean()
            / early_years["Web of Science Documents"].mean()
        )
        - 1
    ) * 100
    quality_change = (
        recent_years["Category Normalized Citation Impact"].mean()
        - early_years["Category Normalized Citation Impact"].mean()
    )
else:
    output_change = 0
    quality_change = 0

st.markdown('<div class="insight-box">', unsafe_allow_html=True)
st.markdown(f"""
###  Insight:
- **Output Trend**: {"Increased" if output_change > 0 else "Decreased"} by **{abs(output_change):.1f}%** (2003-07 vs 2021-25)
- **Quality Trend**: CNCI {"improved" if quality_change > 0 else "declined" if quality_change < 0 else "remained stable"} (**{quality_change:+.3f}**)
- **Key Finding**: Despite {"declining" if output_change < 0 else "growing"} output, quality has **remained remarkably stable** around world average
- **Interpretation**: Countries are prioritizing **sustainable excellence** over volume expansion
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# CHAPTER 4: THE EXCELLENCE HIERARCHY
# ============================================================================
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("##  Chapter 4: The Excellence Hierarchy")
st.markdown("""
**Question:** *Who consistently produces top-tier research?*

Examining % of papers in **Top 1%** and **Top 10%** citation percentiles.
""")
st.markdown("</div>", unsafe_allow_html=True)

# Excellence metrics by country
excellence = country_agg.sort_values("Avg_Top1", ascending=False).head(15)

fig_excellence = go.Figure()

fig_excellence.add_trace(
    go.Bar(
        name="% in Top 1%",
        x=excellence["Country"],
        y=excellence["Avg_Top1"],
        marker_color="gold",
    )
)

fig_excellence.add_trace(
    go.Bar(
        name="% in Top 10%",
        x=excellence["Country"],
        y=excellence["Avg_Top10"],
        marker_color="silver",
    )
)

fig_excellence.update_layout(
    title="Research Excellence: Top-Tier Publication Rates",
    xaxis_title="Country",
    yaxis_title="Percentage (%)",
    barmode="group",
    height=500,
)

st.plotly_chart(fig_excellence, use_container_width=True)

# Excellence distribution
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Avg % in Top 1%",
        f"{filtered_df['% Documents in Top 1%'].mean():.2f}%",
        f"Max: {filtered_df['% Documents in Top 1%'].max():.2f}%",
    )

with col2:
    st.metric(
        "Avg % in Top 10%",
        f"{filtered_df['% Documents in Top 10%'].mean():.2f}%",
        f"Max: {filtered_df['% Documents in Top 10%'].max():.2f}%",
    )

with col3:
    high_excellence = (filtered_df["% Documents in Top 1%"] > 2.0).sum()
    st.metric(
        "High Excellence (>2% in Top 1%)",
        f"{high_excellence}",
        f"{high_excellence / len(filtered_df) * 100 if len(filtered_df) > 0 else 0:.1f}% of records",
    )

st.markdown('<div class="insight-box">', unsafe_allow_html=True)
st.markdown(f"""
###  Insight:
- **Top Excellence Leaders**: {", ".join(excellence.head(3)["Country"].tolist())}
- **Excellence Concentration**: {high_excellence} records ({high_excellence / len(filtered_df) * 100 if len(filtered_df) > 0 else 0:.1f}%) achieve >2% in Top 1%
- **Gap Analysis**: Top performers have **{excellence["Avg_Top1"].iloc[0]:.2f}%** in Top 1%, while average is **{filtered_df["% Documents in Top 1%"].mean():.2f}%**
- **{excellence["Avg_Top1"].iloc[0] / filtered_df["% Documents in Top 1%"].mean() if filtered_df["% Documents in Top 1%"].mean() > 0 else 0:.1f}x multiplier** between leaders and average
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# CHAPTER 5: CONSISTENCY CHAMPIONS
# ============================================================================
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("##  Chapter 5: Consistency Champions")
st.markdown("""
**Question:** *Who maintains stable excellence over time?*

Analyzing performance variability (standard deviation of CNCI).
""")
st.markdown("</div>", unsafe_allow_html=True)

# Consistency analysis (countries with at least 10 records)
consistency = (
    filtered_df.groupby("Name")
    .agg({"Category Normalized Citation Impact": ["mean", "std", "count"]})
    .reset_index()
)
consistency.columns = ["Country", "Avg_CNCI", "Std_Dev", "Records"]
consistency = consistency[consistency["Records"] >= 10]
consistency["Consistency_Score"] = consistency["Avg_CNCI"] / (
    consistency["Std_Dev"] + 0.01
)  # Avoid division by zero
consistency = consistency.sort_values("Std_Dev")

fig_consistency = go.Figure()

fig_consistency.add_trace(
    go.Scatter(
        x=consistency["Avg_CNCI"],
        y=consistency["Std_Dev"],
        mode="markers+text",
        marker=dict(
            size=consistency["Records"] * 2,
            color=consistency["Avg_CNCI"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Avg CNCI"),
        ),
        text=consistency["Country"],
        textposition="top center",
        hovertemplate="<b>%{text}</b><br>Avg CNCI: %{x:.3f}<br>Std Dev: %{y:.3f}<extra></extra>",
    )
)

fig_consistency.update_layout(
    title="Consistency Matrix: High Quality + Low Variability = Champions",
    xaxis_title="Average CNCI (Quality)",
    yaxis_title="Standard Deviation (Variability)",
    height=500,
    annotations=[
        dict(
            x=consistency["Avg_CNCI"].max(),
            y=consistency["Std_Dev"].max(),
            text="High Quality<br>High Variability",
            showarrow=False,
            font=dict(color="gray"),
        ),
        dict(
            x=consistency["Avg_CNCI"].max(),
            y=consistency["Std_Dev"].min(),
            text="🏆 Champions<br>High Quality<br>Low Variability",
            showarrow=False,
            font=dict(color="green", size=12),
        ),
    ],
)

st.plotly_chart(fig_consistency, use_container_width=True)

st.markdown("### 🏆 Most Consistent Performers")
consistent_top = consistency.head(10)[["Country", "Avg_CNCI", "Std_Dev", "Records"]]
consistent_top["Avg_CNCI"] = consistent_top["Avg_CNCI"].round(3)
consistent_top["Std_Dev"] = consistent_top["Std_Dev"].round(3)
st.dataframe(consistent_top, hide_index=True, use_container_width=True)

st.markdown('<div class="insight-box">', unsafe_allow_html=True)
st.markdown(f"""
###  Insight:
- **Most Consistent**: {consistency.iloc[0]["Country"] if len(consistency) > 0 else "N/A"}{f" (Std Dev: {consistency.iloc[0]['Std_Dev']:.3f})" if len(consistency) > 0 else ""}
- **Sweet Spot**: Top-right quadrant shows high quality WITH low variability
- **Bubble size** = number of years tracked
- Consistency matters for **long-term research funding and planning**
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# COUNTRY DEEP DIVE (if selected)
# ============================================================================
if selected_country != "All Countries" and len(filtered_df) > 0:
    st.markdown('<div class="story-section">', unsafe_allow_html=True)
    st.markdown(f"##  Deep Dive: {selected_country}")
    st.markdown("</div>", unsafe_allow_html=True)

    country_data = filtered_df

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Publications",
            f"{country_data['Web of Science Documents'].sum():,.0f}",
        )
    with col2:
        st.metric("Total Citations", f"{country_data['Times Cited'].sum():,.0f}")
    with col3:
        st.metric(
            "Avg CNCI",
            f"{country_data['Category Normalized Citation Impact'].mean():.3f}",
        )
    with col4:
        st.metric("Years Tracked", f"{country_data['year'].nunique()}")

    # Country timeline
    country_timeline = (
        country_data.groupby("year")
        .agg(
            {
                "Category Normalized Citation Impact": "mean",
                "Web of Science Documents": "sum",
                "% Documents in Top 10%": "mean",
            }
        )
        .reset_index()
    )

    fig_country = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            f"{selected_country}: CNCI Over Time",
            f"{selected_country}: Output & Excellence",
        ),
    )

    fig_country.add_trace(
        go.Scatter(
            x=country_timeline["year"],
            y=country_timeline["Category Normalized Citation Impact"],
            name="CNCI",
            line=dict(color="blue", width=3),
        ),
        row=1,
        col=1,
    )
    fig_country.add_hline(y=1.0, line_dash="dash", line_color="red", row=1, col=1)

    fig_country.add_trace(
        go.Bar(
            x=country_timeline["year"],
            y=country_timeline["Web of Science Documents"],
            name="Publications",
            marker_color="lightblue",
        ),
        row=2,
        col=1,
    )
    fig_country.add_trace(
        go.Scatter(
            x=country_timeline["year"],
            y=country_timeline["% Documents in Top 10%"],
            name="% Top 10%",
            line=dict(color="orange", width=3),
            yaxis="y3",
        ),
        row=2,
        col=1,
    )

    fig_country.update_layout(height=700, showlegend=True)
    st.plotly_chart(fig_country, use_container_width=True)

    # Performance summary
    st.markdown(f"###  {selected_country} Performance Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Strengths:**")
        if (
            country_data["Category Normalized Citation Impact"].mean()
            > df["Category Normalized Citation Impact"].mean()
        ):
            st.markdown(" Above global average CNCI")
        if (
            country_data["% Documents in Top 1%"].mean()
            > df["% Documents in Top 1%"].mean()
        ):
            st.markdown(" Above average excellence rate")
        if (
            "Collab_Advantage" in country_data.columns
            and country_data["Collab_Advantage"].mean() > 0
        ):
            st.markdown(" Benefits from collaboration")

    with col2:
        st.markdown("**Areas for Improvement:**")
        if (
            country_data["Category Normalized Citation Impact"].mean()
            < df["Category Normalized Citation Impact"].mean()
        ):
            st.markdown(" Below global average CNCI")
        if (
            country_data["% Documents in Top 1%"].mean()
            < df["% Documents in Top 1%"].mean()
        ):
            st.markdown(" Below average excellence rate")
        if (
            "Collab_Advantage" in country_data.columns
            and country_data["Collab_Advantage"].mean() < 0
        ):
            st.markdown(" Collaboration reduces impact")

st.markdown("---")

# ============================================================================
# FINAL INSIGHTS & RECOMMENDATIONS
# ============================================================================
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("##  Key Takeaways & Recommendations")

st.markdown("""
###  Main Discoveries:

1. **The 85% Elite Club** 
   - 85.5% of country-year records maintain above-world-average impact (CNCI > 1.0)
   - This represents exceptional global research performance

2. **The Collaboration Paradox**
   - Collaboration only helps in 40.8% of cases
   - Average collaboration effect is **negative** (−0.077 CNCI)
   - **Lesson**: Quality of partnerships matters more than quantity

3. **Quantity ≠ Quality**
   - Spain achieves both volume leadership AND top-3 quality
   - Japan leads in quality with moderate output
   - Output declined 4.7% but quality remained stable

4. **Consistency Matters**
   - Brazil demonstrates most consistent performance (lowest variability)
   - Consistency signals sustainable research infrastructure

5. **The Excellence Gap**
   - Top performers achieve ~2% in Top 1% citations
   - 40% of records exceed this benchmark
   - Excellence is concentrated but achievable


""")
st.markdown("</div>", unsafe_allow_html=True)
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
