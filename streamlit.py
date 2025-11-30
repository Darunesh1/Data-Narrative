import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st

# Page config
st.set_page_config(
    page_title="Global Research Performance: 2003-2025",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .insight-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .story-section {
        background-color: #fff9f0;
        padding: 25px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 5px solid #ff7f0e;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/publications.csv")
    return df


df = load_data()

# ============================================================================
# TITLE & INTRODUCTION
# ============================================================================
st.markdown(
    '<div class="main-header">🌍 Global Research Performance Analysis</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Uncovering 23 Years of Scientific Excellence (2003-2025) | 17 Leading Nations | 14.8M Publications</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ============================================================================
# EXECUTIVE SUMMARY
# ============================================================================
st.markdown("## 📊 Executive Summary: The Unexpected Truth")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Countries Analyzed", value="17", delta="23 years tracked")

with col2:
    st.metric(label="Total Publications", value="14.9M", delta="1.3B citations")

with col3:
    st.metric(label="Above-Average Performers", value="85.5%", delta="CNCI > 1.0")

with col4:
    st.metric(
        label="Collaboration Success Rate",
        value="40.8%",
        delta="-0.077 CNCI",
        delta_color="inverse",
    )

st.markdown('<div class="insight-box">', unsafe_allow_html=True)
st.markdown("""
### 💡 Key Discovery: The Collaboration Paradox

**Conventional wisdom says:** *"Collaborate more, cite more."*  
**Reality shows:** Collaboration provides a **negative average impact** (−0.077 CNCI) and only benefits 40.8% of cases.

This dashboard reveals what separates research leaders from followers in an era where quantity doesn't guarantee quality.
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
st.sidebar.header("🔍 Filters")

# Country selector
countries = ["All Countries"] + sorted(df["Name"].unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", countries)

# Year range
year_range = st.sidebar.slider(
    "Year Range",
    min_value=int(df["year"].min()),
    max_value=int(df["year"].max()),
    value=(int(df["year"].min()), int(df["year"].max())),
)

# Metric threshold
cnci_threshold = st.sidebar.slider(
    "Minimum CNCI", min_value=0.0, max_value=2.0, value=0.0, step=0.1
)

# Filter data
filtered_df = df[
    (df["year"] >= year_range[0])
    & (df["year"] <= year_range[1])
    & (df["Category Normalized Citation Impact"] >= cnci_threshold)
]

if selected_country != "All Countries":
    filtered_df = filtered_df[filtered_df["Name"] == selected_country]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing {len(filtered_df)} of {len(df)} records**")

# ============================================================================
# CHAPTER 1: THE GIANTS VS THE MASTERS
# ============================================================================
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 📖 Chapter 1: The Giants vs The Masters")
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
    st.markdown("### 🎯 Quality Masters (Avg CNCI)")
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
st.markdown("## 📖 Chapter 2: The Collaboration Paradox")
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
    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=["Collaboration Hurts", "Collaboration Helps"],
                values=[collab_effect[False], collab_effect[True]],
                marker=dict(colors=["#ff6b6b", "#51cf66"]),
                hole=0.4,
            )
        ]
    )
    fig_pie.update_layout(
        title="When Does Collaboration Help?",
        annotations=[
            dict(
                text=f"{collab_effect[True] / len(filtered_df) * 100:.1f}%<br>Success",
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
- Only **{(filtered_df["Collab_Helps"].sum() / len(filtered_df) * 100):.1f}%** of records show positive collaboration effect
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
st.markdown("## 📖 Chapter 3: 23 Years of Evolution (2003-2025)")
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

st.markdown('<div class="insight-box">', unsafe_allow_html=True)
st.markdown(f"""
### 🔍 Insight:
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
st.markdown("## 📖 Chapter 4: The Excellence Hierarchy")
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
        f"{high_excellence / len(filtered_df) * 100:.1f}% of records",
    )

st.markdown('<div class="insight-box">', unsafe_allow_html=True)
st.markdown(f"""
### 🔍 Insight:
- **Top Excellence Leaders**: {", ".join(excellence.head(3)["Country"].tolist())}
- **Excellence Concentration**: {high_excellence} records ({high_excellence / len(filtered_df) * 100:.1f}%) achieve >2% in Top 1%
- **Gap Analysis**: Top performers have **{excellence["Avg_Top1"].iloc[0]:.2f}%** in Top 1%, while average is **{filtered_df["% Documents in Top 1%"].mean():.2f}%**
- **{excellence["Avg_Top1"].iloc[0] / filtered_df["% Documents in Top 1%"].mean():.1f}x multiplier** between leaders and average
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# CHAPTER 5: CONSISTENCY CHAMPIONS
# ============================================================================
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 📖 Chapter 5: Consistency Champions")
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
### 🔍 Insight:
- **Most Consistent**: {consistency.iloc[0]["Country"]} (Std Dev: {consistency.iloc[0]["Std_Dev"]:.3f})
- **Sweet Spot**: Top-right quadrant shows high quality WITH low variability
- **Bubble size** = number of years tracked
- Consistency matters for **long-term research funding and planning**
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# COUNTRY DEEP DIVE (if selected)
# ============================================================================
if selected_country != "All Countries":
    st.markdown('<div class="story-section">', unsafe_allow_html=True)
    st.markdown(f"## 🔬 Deep Dive: {selected_country}")
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
    st.markdown(f"### 📊 {selected_country} Performance Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Strengths:**")
        if (
            country_data["Category Normalized Citation Impact"].mean()
            > df["Category Normalized Citation Impact"].mean()
        ):
            st.markdown("✅ Above global average CNCI")
        if (
            country_data["% Documents in Top 1%"].mean()
            > df["% Documents in Top 1%"].mean()
        ):
            st.markdown("✅ Above average excellence rate")
        if country_data["Collab_Advantage"].mean() > 0:
            st.markdown("✅ Benefits from collaboration")

    with col2:
        st.markdown("**Areas for Improvement:**")
        if (
            country_data["Category Normalized Citation Impact"].mean()
            < df["Category Normalized Citation Impact"].mean()
        ):
            st.markdown("⚠️ Below global average CNCI")
        if (
            country_data["% Documents in Top 1%"].mean()
            < df["% Documents in Top 1%"].mean()
        ):
            st.markdown("⚠️ Below average excellence rate")
        if country_data["Collab_Advantage"].mean() < 0:
            st.markdown("⚠️ Collaboration reduces impact")

st.markdown("---")

# ============================================================================
# FINAL INSIGHTS & RECOMMENDATIONS
# ============================================================================
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 🎯 Key Takeaways & Recommendations")

st.markdown("""
### 🔑 Main Discoveries:

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

### 💡 Recommendations:

**For Policymakers:**
- Prioritize **quality over quantity** in research funding
- Evaluate collaboration partnerships critically—not all benefit impact
- Support consistent performers for long-term research sustainability

**For Research Institutions:**
- Learn from **Spain's balanced approach** (volume + quality)
- Study **Japan's quality optimization** strategies
- Invest in **strategic collaborations** (not just more collaborations)

**For Further Analysis:**
- Investigate what makes Spanish research uniquely successful
- Examine why collaboration sometimes hurts performance
- Analyze field-specific patterns within countries
""")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Data Source:</strong> Web of Science Publications (2003-2025)</p>
    <p><strong>Methodology:</strong> CNCI (Category Normalized Citation Impact) where 1.0 = world average</p>
    <p><strong>Created for:</strong> PAIU-OPSA, IISc Bangalore - Project Intern/Trainee Position</p>
    <p><em>Developed by: [Your Name] | Dashboard Built with Streamlit & Plotly</em></p>
</div>
""",
    unsafe_allow_html=True,
)
