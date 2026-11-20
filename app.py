import base64
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit_antd_components as sac

from db import run_query

# --- Page Config ---
st.set_page_config(
    page_title="K-12 District Performance & ROI Studio",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- State FIPS -> 2-Letter State Postal Initials ---
FIPS_TO_STATE = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA",
    "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
    "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN",
    "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
    "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS",
    "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
    "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
    "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
    "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
    "56": "WY",
}
STATE_TO_FIPS = {v: k for k, v in FIPS_TO_STATE.items()}


def fips_to_abbr(val: str) -> str:
    clean = str(val).strip().zfill(2)
    return FIPS_TO_STATE.get(clean, clean)


# --- Optional Local Font Loader (KG Primary Penmanship) ---
def get_local_font_css() -> str:
    font_path = Path("static/KGPrimaryPenmanship.ttf")
    if font_path.exists():
        b64_font = base64.b64encode(font_path.read_bytes()).decode("utf-8")
        return f"""
        @font-face {{
            font-family: 'KGPrimaryPenmanship';
            src: url(data:font/truetype;charset=utf-8;base64,{b64_font}) format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        """
    return ""


# --- Deep Chalkboard Navy Website Background + Crisp White Chart Cards ---
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
        {get_local_font_css()}

        :root {{
            --school-font: 'KGPrimaryPenmanship', 'Patrick Hand', cursive, sans-serif;
            --ui-font: 'Plus Jakarta Sans', sans-serif;
        }}

        /* Deep Midnight Navy Website Background */
        .stApp {{
            background: radial-gradient(circle at top left, #0d1b3e 0%, #060d1f 55%, #040814 100%) !important;
            font-family: var(--ui-font);
            color: #f8fafc !important;
        }}

        /* Top Toolbar */
        header[data-testid="stHeader"] {{
            background-color: rgba(6, 13, 31, 0.92) !important;
        }}

        /* Dark Navy Sidebar with High-Contrast White Controls */
        [data-testid="stSidebar"] {{
            background-color: #081126 !important;
            border-right: 1px solid rgba(59, 130, 246, 0.35) !important;
        }}
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {{
            color: #f8fafc !important;
            font-weight: 600 !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            background-color: #0f234a !important;
            border: 1.5px solid #3b82f6 !important;
            color: #ffffff !important;
            border-radius: 10px !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="select"] span,
        [data-testid="stSidebar"] div[data-baseweb="select"] div {{
            color: #ffffff !important;
            background-color: transparent !important;
        }}
        ul[data-baseweb="menu"] {{
            background-color: #0f234a !important;
            border: 1px solid #3b82f6 !important;
        }}
        ul[data-baseweb="menu"] li {{
            color: #ffffff !important;
        }}
        ul[data-baseweb="menu"] li:hover {{
            background-color: #1d4ed8 !important;
        }}

        /* Crisp Chalk White Radio Labels on Dark Blue Canvas */
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] p,
        div[data-testid="stRadio"] span {{
            color: #f8fafc !important;
            font-weight: 700 !important;
        }}

        /* Ruled-Paper Primary Penmanship Headers */
        .penmanship-title {{
            font-family: var(--school-font);
            font-size: 2.65rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.15;
            padding: 6px 10px;
            border-top: 2px solid rgba(147, 197, 253, 0.6);
            border-bottom: 2px solid rgba(147, 197, 253, 0.6);
            background-image: linear-gradient(to right, rgba(147, 197, 253, 0.35) 55%, transparent 45%);
            background-position: 0 54%;
            background-size: 14px 2px;
            background-repeat: repeat-x;
            display: inline-block;
            margin-bottom: 0.4rem;
        }}

        .penmanship-section {{
            font-family: var(--school-font);
            font-size: 1.95rem;
            color: #ffffff;
            line-height: 1.2;
            padding: 4px 6px;
            border-bottom: 2px solid rgba(59, 130, 246, 0.55);
            background-image: linear-gradient(to right, rgba(147, 197, 253, 0.3) 55%, transparent 45%);
            background-position: 0 55%;
            background-size: 12px 1.5px;
            background-repeat: repeat-x;
            margin-top: 0.4rem;
            margin-bottom: 0.85rem;
        }}

        /* Dark Navy School-Themed Top KPI Cards */
        .school-card {{
            background: linear-gradient(145deg, #0d1d42 0%, #09142e 100%);
            border-radius: 18px;
            padding: 16px 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
            height: 132px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid rgba(59, 130, 246, 0.42);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .school-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(37, 99, 235, 0.35);
            border-color: #60a5fa;
        }}
        .card-bus {{ border-left: 7px solid #facc15; }}
        .card-apple {{ border-left: 7px solid #f87171; }}
        .card-books {{ border-left: 7px solid #38bdf8; }}
        .card-star {{ border-left: 7px solid #34d399; }}

        .school-card-label {{
            font-family: var(--school-font);
            font-size: 1.38rem;
            color: #e2e8f0;
            line-height: 1.1;
            margin-bottom: 6px;
        }}
        .school-card-value {{
            font-family: var(--ui-font);
            font-size: 1.95rem;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.1;
        }}
        .school-card-icon {{
            font-size: 2.75rem;
            line-height: 1;
            filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.35));
        }}

        /* Cobalt Banner */
        .cobalt-banner {{
            background: #060d1f;
            border: 1.5px solid #facc15;
            border-radius: 14px;
            padding: 10px 16px;
            margin: 12px 0 16px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }}
        .cobalt-banner-highlight {{
            background: #facc15;
            color: #060d1f;
            font-family: var(--school-font);
            font-size: 1.48rem;
            font-weight: 700;
            padding: 4px 14px;
            border-radius: 8px;
            letter-spacing: 0.02em;
        }}
        .cobalt-banner-icons {{
            font-size: 1.45rem;
        }}

        .schema-pill {{
            display: inline-block;
            background: #0f234a;
            border: 1px solid #3b82f6;
            color: #93c5fd;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 2px 10px;
            border-radius: 999px;
            margin-top: 2px;
        }}

        /* Rounded framing on individual white Plotly chart containers */
        div[data-testid="stPlotlyChart"] {{
            background-color: #ffffff;
            border-radius: 16px;
            padding: 8px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
            border: 2px solid rgba(59, 130, 246, 0.35);
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown(
        """
        <div class='penmanship-title' style='font-size:2.05rem;'>K-12 District<br>Performance</div>
        <div><span class='schema-pill'>Live DB: k12_education</span></div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    states_df = run_query("SELECT DISTINCT state_fips FROM k12_education.districts ORDER BY state_fips;")
    raw_fips_list = [str(x).strip().zfill(2) for x in states_df["state_fips"].dropna().tolist()]
    state_abbr_list = sorted({fips_to_abbr(f) for f in raw_fips_list if f in FIPS_TO_STATE})
    state_options = ["All States"] + state_abbr_list

    selected_state_abbr = st.selectbox("Select State", options=state_options, index=0)
    min_enrollment = st.slider(
        "Minimum Student Enrollment",
        min_value=0,
        max_value=10000,
        value=500,
        step=250,
        help="Filters out micro-district outliers using fall_membership.",
    )
    exclude_suppressed = st.toggle("Exclude Privacy-Suppressed Scores", value=True)

# --- Live Filtered Query Builder ---
where_clauses = [
    "f.fall_membership >= :min_enroll",
    "f.fall_membership > 0",
    "f.total_expenditure > 0",
]
query_params = {"min_enroll": min_enrollment}

if selected_state_abbr != "All States":
    target_fips = STATE_TO_FIPS.get(selected_state_abbr, selected_state_abbr)
    where_clauses.append("LPAD(TRIM(d.state_fips), 2, '0') = :state_fips")
    query_params["state_fips"] = target_fips

if exclude_suppressed:
    where_clauses.append("a.is_suppressed = FALSE")

where_sql = " AND ".join(where_clauses)

district_sql = f"""
SELECT
    d.leaid,
    d.district_name,
    LPAD(TRIM(d.state_fips), 2, '0') AS state_fips,
    f.fall_membership,
    f.instructional_expenditure,
    f.total_expenditure,
    ROUND((f.instructional_expenditure / NULLIF(f.fall_membership, 0))::numeric, 2) AS per_pupil_instructional,
    ROUND(((f.instructional_expenditure / NULLIF(f.total_expenditure, 0)) * 100)::numeric, 2) AS classroom_share_pct,
    ROUND(AVG(a.proficiency_rate)::numeric, 2) AS avg_proficiency,
    ROUND(AVG(CASE WHEN a.subject = 'MATH' THEN a.proficiency_rate END)::numeric, 2) AS math_proficiency,
    ROUND(AVG(CASE WHEN a.subject = 'ELA' THEN a.proficiency_rate END)::numeric, 2) AS ela_proficiency
FROM k12_education.districts d
JOIN k12_education.district_finances f ON d.leaid = f.leaid
JOIN k12_education.district_assessments a ON d.leaid = a.leaid
WHERE {where_sql}
GROUP BY
    d.leaid, d.district_name, d.state_fips,
    f.fall_membership, f.instructional_expenditure, f.total_expenditure
HAVING COUNT(a.assessment_id) >= 1;
"""

df = run_query(district_sql, params=query_params)
if not df.empty:
    df["state"] = df["state_fips"].apply(fips_to_abbr)

# --- Top 4 School-Themed KPI Cards ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="school-card card-bus">
            <div>
                <div class="school-card-label">Active Districts</div>
                <div class="school-card-value">{len(df):,}</div>
            </div>
            <div class="school-card-icon">🚌</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    avg_spend = df["per_pupil_instructional"].mean() if not df.empty else 0
    st.markdown(
        f"""
        <div class="school-card card-apple">
            <div>
                <div class="school-card-label">Avg Spending / Pupil</div>
                <div class="school-card-value">${avg_spend:,.0f}</div>
            </div>
            <div class="school-card-icon">🍎</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    avg_share = df["classroom_share_pct"].mean() if not df.empty else 0
    st.markdown(
        f"""
        <div class="school-card card-books">
            <div>
                <div class="school-card-label">Classroom Budget Share</div>
                <div class="school-card-value">{avg_share:.1f}%</div>
            </div>
            <div class="school-card-icon">📚</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    avg_prof = df["avg_proficiency"].mean() if not df.empty else 0
    st.markdown(
        f"""
        <div class="school-card card-star">
            <div>
                <div class="school-card-label">Avg Proficiency Rate</div>
                <div class="school-card-value">{avg_prof:.1f}%</div>
            </div>
            <div class="school-card-icon">⭐</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# --- Segmented Pill Navigation ---
active_tab = sac.segmented(
    items=[
        sac.SegmentedItem(label="Regional Benchmarking", icon="globe-americas"),
        sac.SegmentedItem(label="Educational ROI & Quartiles", icon="star-fill"),
        sac.SegmentedItem(label="Math vs. ELA Subject Splits", icon="book-half"),
    ],
    label="",
    align="center",
    size="lg",
    radius="xl",
    color="#003da5",
    bg_color="#ffffff",
    use_container_width=True,
)

if df.empty:
    st.warning("No school districts match your current sidebar filters. Try lowering the Minimum Student Enrollment slider.")
    st.stop()


def style_white_plotly(fig, height=430):
    """Crisp white individual chart cards with high-contrast slate gridlines."""
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fffef7",
        font=dict(color="#0f172a", family="Plus Jakarta Sans, sans-serif"),
        margin=dict(l=14, r=14, t=24, b=14),
        height=height,
    )
    fig.update_xaxes(
        gridcolor="#e2e8f0",
        zerolinecolor="#cbd5e1",
        linecolor="#94a3b8",
        tickfont=dict(color="#1e293b"),
        title_font=dict(color="#0f172a"),
    )
    fig.update_yaxes(
        gridcolor="#e2e8f0",
        zerolinecolor="#cbd5e1",
        linecolor="#94a3b8",
        tickfont=dict(color="#1e293b"),
        title_font=dict(color="#0f172a"),
    )
    return fig


# Multi-color scale from your screenshot (Teal -> Amber -> Orange -> Crimson)
SCHOOL_SCALE = ["#0d9488", "#eab308", "#ea580c", "#dc2626"]


# ==============================================================================
# TAB 1: REGIONAL BENCHMARKING (Interactive US Map + State District Explorer)
# ==============================================================================
if active_tab == "Regional Benchmarking":
    st.markdown(
        """
        <div class="cobalt-banner">
            <span class="cobalt-banner-highlight">🌍 Geography & Regional Atlas — Interactive US Map & District Benchmarking</span>
            <span class="cobalt-banner-icons">🗺️ 🧭</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    map_metric = st.radio(
        "Map Color Metric:",
        ["Avg Proficiency Rate (%)", "Classroom Budget Share (%)", "Avg Per-Pupil Spending ($)"],
        horizontal=True,
    )
    metric_col_map = {
        "Avg Proficiency Rate (%)": ("avg_proficiency", "Avg Proficiency (%)"),
        "Classroom Budget Share (%)": ("classroom_share_pct", "Classroom Share (%)"),
        "Avg Per-Pupil Spending ($)": ("per_pupil_instructional", "Per-Pupil Spending ($)"),
    }
    col_key, col_label = metric_col_map[map_metric]

    state_map_df = (
        df.groupby("state", as_index=False)
        .agg(
            districts=("leaid", "count"),
            avg_proficiency=("avg_proficiency", "mean"),
            classroom_share_pct=("classroom_share_pct", "mean"),
            per_pupil_instructional=("per_pupil_instructional", "mean"),
            total_students=("fall_membership", "sum"),
        )
    )

    col_map, col_detail = st.columns([1.25, 1])

    with col_map:
        st.markdown(
            f"<div class='penmanship-section'>🗺️ Interactive US Map ({selected_state_abbr})</div>",
            unsafe_allow_html=True,
        )
        fig_us = px.choropleth(
            state_map_df,
            locations="state",
            locationmode="USA-states",
            color=col_key,
            scope="usa",
            color_continuous_scale=["#fef08a", "#34d399", "#0d9488", "#0f766e"],
            hover_name="state",
            hover_data={
                "state": False,
                "districts": ":,",
                "total_students": ":,",
                "avg_proficiency": ":.1f%",
                "classroom_share_pct": ":.1f%",
                "per_pupil_instructional": ":$,.0f",
            },
            labels={col_key: col_label},
        )
        fig_us.update_geos(
            bgcolor="#ffffff",
            lakecolor="#e0f2fe",
            landcolor="#f1f5f9",
            subunitcolor="#334155",
            subunitwidth=1,
            fitbounds="locations" if selected_state_abbr != "All States" else False,
        )
        fig_us.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#0f172a"),
            margin=dict(l=0, r=0, t=10, b=10),
            height=440,
        )
        st.plotly_chart(fig_us, use_container_width=True)

    with col_detail:
        if selected_state_abbr == "All States":
            st.markdown("<div class='penmanship-section'>Top States by Classroom Share (%)</div>", unsafe_allow_html=True)
            top_states = state_map_df.sort_values("classroom_share_pct", ascending=False).head(12)
            fig_bar = px.bar(
                top_states,
                x="classroom_share_pct",
                y="state",
                orientation="h",
                color="avg_proficiency",
                color_continuous_scale=SCHOOL_SCALE,
                labels={
                    "classroom_share_pct": "Avg Classroom Share (%)",
                    "state": "State",
                    "avg_proficiency": "Proficiency (%)",
                },
            )
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(style_white_plotly(fig_bar, height=440), use_container_width=True)
        else:
            st.markdown(
                f"<div class='penmanship-section'>🏫 All {len(df):,} Districts in {selected_state_abbr}</div>",
                unsafe_allow_html=True,
            )
            fig_state_districts = px.scatter(
                df,
                x="per_pupil_instructional",
                y="avg_proficiency",
                size="fall_membership",
                color="classroom_share_pct",
                color_continuous_scale=SCHOOL_SCALE,
                hover_name="district_name",
                hover_data={
                    "fall_membership": ":,",
                    "per_pupil_instructional": ":$,.0f",
                    "classroom_share_pct": ":.1f%",
                    "avg_proficiency": ":.1f%",
                },
                labels={
                    "per_pupil_instructional": "Spending / Pupil ($)",
                    "avg_proficiency": "Proficiency Rate (%)",
                    "classroom_share_pct": "Classroom Share %",
                },
            )
            st.plotly_chart(style_white_plotly(fig_state_districts, height=440), use_container_width=True)

    st.markdown("<div class='penmanship-section'>District Enrollment Size vs. Proficiency</div>", unsafe_allow_html=True)
    df_size = df.copy()
    df_size["district_size_tier"] = pd.cut(
        df_size["fall_membership"],
        bins=[0, 1500, 5000, 15000, float("inf")],
        labels=["Small (<1.5k)", "Mid-Size (1.5k–5k)", "Large (5k–15k)", "Metro (>15k)"],
    )
    fig_box = px.box(
        df_size.dropna(subset=["district_size_tier"]),
        x="district_size_tier",
        y="avg_proficiency",
        color="district_size_tier",
        color_discrete_sequence=["#0d9488", "#eab308", "#ea580c", "#dc2626"],
        labels={
            "district_size_tier": "District Enrollment Tier",
            "avg_proficiency": "Combined Proficiency Rate (%)",
        },
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(style_white_plotly(fig_box, height=340), use_container_width=True)

# ==============================================================================
# TAB 2: EDUCATIONAL ROI & QUARTILES
# ==============================================================================
elif active_tab == "Educational ROI & Quartiles":
    st.markdown(
        """
        <div class="cobalt-banner">
            <span class="cobalt-banner-highlight">🏆 Chalkboard Honor Roll — Does Per-Pupil Classroom Spending Boost Student Proficiency?</span>
            <span class="cobalt-banner-icons">⭐ ✏️</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("<div class='penmanship-section'>Per-Pupil Spending vs. Proficiency Rate</div>", unsafe_allow_html=True)
        spend_cap = df["per_pupil_instructional"].quantile(0.99)
        plot_df = df[df["per_pupil_instructional"] <= spend_cap]

        fig_scatter = px.scatter(
            plot_df,
            x="per_pupil_instructional",
            y="avg_proficiency",
            color="classroom_share_pct",
            color_continuous_scale=SCHOOL_SCALE,
            opacity=0.78,
            hover_name="district_name",
            hover_data={
                "state": True,
                "fall_membership": ":,",
                "per_pupil_instructional": ":$,.0f",
                "avg_proficiency": ":.1f%",
            },
            labels={
                "per_pupil_instructional": "Instructional Spending per Pupil ($)",
                "avg_proficiency": "Avg Proficiency Rate (%)",
                "classroom_share_pct": "Classroom Share %",
            },
        )
        st.plotly_chart(style_white_plotly(fig_scatter, height=430), use_container_width=True)

    with col_right:
        st.markdown("<div class='penmanship-section'>National Spending Quartiles (NTILE 4)</div>", unsafe_allow_html=True)
        df_q = df.copy()
        if len(df_q) >= 4:
            df_q["spending_quartile"] = pd.qcut(
                df_q["per_pupil_instructional"],
                q=4,
                labels=["Q1 (Lowest Spend)", "Q2 (Lower-Mid)", "Q3 (Upper-Mid)", "Q4 (Highest Spend)"],
            )
            q_summary = df_q.groupby("spending_quartile", observed=False, as_index=False).agg(
                avg_spend=("per_pupil_instructional", "mean"),
                avg_proficiency=("avg_proficiency", "mean"),
            )

            fig_q = go.Figure(
                go.Bar(
                    x=q_summary["spending_quartile"],
                    y=q_summary["avg_proficiency"],
                    marker_color=["#0d9488", "#eab308", "#ea580c", "#dc2626"],
                    text=q_summary["avg_proficiency"].round(1).astype(str) + "%",
                    textposition="outside",
                    textfont=dict(color="#0f172a", weight="bold"),
                    hovertemplate="<b>%{x}</b><br>Avg Proficiency: %{y:.1f}%<extra></extra>",
                )
            )
            fig_q.update_layout(
                yaxis_title="Avg Proficiency Rate (%)",
                xaxis_title="Instructional Spending Quartile",
                yaxis=dict(range=[0, max(q_summary["avg_proficiency"].max() * 1.18, 60)]),
            )
            st.plotly_chart(style_white_plotly(fig_q, height=430), use_container_width=True)
        else:
            st.info("Select a broader filter range (at least 4 districts) to compute spending quartiles.")

# ==============================================================================
# TAB 3: MATH VS. ELA SUBJECT SPLITS
# ==============================================================================
elif active_tab == "Math vs. ELA Subject Splits":
    st.markdown(
        """
        <div class="cobalt-banner">
            <span class="cobalt-banner-highlight">📐 Math & Reading Lab — Comparing Mathematics vs. ELA Funding Responsiveness</span>
            <span class="cobalt-banner-icons">📖 🧮</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "📌 **Ready for `queries_subjects.sql`:** Once Cyncier finalizes her subject-split SQL queries, "
        "we can drop her exact SQL query into this tab. Below is a live comparison of Math vs. ELA proficiency from your current filter:"
    )

    subj_df = df.dropna(subset=["math_proficiency", "ela_proficiency"])
    if not subj_df.empty:
        col_m, col_e = st.columns(2)
        with col_m:
            st.markdown("<div class='penmanship-section'>📐 Math vs. ELA District Comparison</div>", unsafe_allow_html=True)
            fig_subj = px.scatter(
                subj_df,
                x="math_proficiency",
                y="ela_proficiency",
                color="per_pupil_instructional",
                color_continuous_scale=SCHOOL_SCALE,
                hover_name="district_name",
                hover_data={"state": True},
                labels={
                    "math_proficiency": "Math Proficiency (%)",
                    "ela_proficiency": "ELA / Reading Proficiency (%)",
                    "per_pupil_instructional": "Spending / Pupil ($)",
                },
            )
            fig_subj.add_shape(type="line", x0=0, y0=0, x1=100, y1=100, line=dict(dash="dash", color="#64748b"))
            st.plotly_chart(style_white_plotly(fig_subj, height=410), use_container_width=True)

        with col_e:
            st.markdown("<div class='penmanship-section'>📖 Subject Proficiency Distribution</div>", unsafe_allow_html=True)
            melted = subj_df.melt(
                value_vars=["math_proficiency", "ela_proficiency"],
                var_name="Subject",
                value_name="Proficiency (%)",
            )
            melted["Subject"] = melted["Subject"].map(
                {"math_proficiency": "📐 Mathematics", "ela_proficiency": "📖 Reading / ELA"}
            )
            fig_violin = px.violin(
                melted,
                x="Subject",
                y="Proficiency (%)",
                color="Subject",
                box=True,
                color_discrete_map={"📐 Mathematics": "#0d9488", "📖 Reading / ELA": "#ea580c"},
            )
            fig_violin.update_layout(showlegend=False)
            st.plotly_chart(style_white_plotly(fig_violin, height=410), use_container_width=True)