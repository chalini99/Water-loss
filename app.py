import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk

from model.anomaly_detector import detect_anomalies
from utils.explanation import generate_explanation
from utils.live_data import generate_live_data


# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Invisible Loss AI",
    page_icon="💧",
    layout="wide"
)

# ================== LOAD CSS ==================
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ================== ZONE LOCATIONS ==================
ZONE_LOCATIONS = {
    "Z1": [28.6139, 77.2090],   # Delhi
    "Z2": [19.0760, 72.8777],   # Mumbai
    "Z3": [12.9716, 77.5946],   # Bangalore
}

# ================== HEADER ==================
st.markdown(
    """
    <div class="dashboard-title">Invisible Water Loss AI</div>
    <div class="dashboard-subtitle">
        Real-time AI-powered monitoring of hidden water loss
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ================== LOAD DATA ==================
df = pd.read_csv("data/water_usage.csv")
df = generate_live_data(df)
processed_df = detect_anomalies(df)

# ================== KPI COUNTS ==================
high = (processed_df["Risk_Level"] == "High").sum()
medium = (processed_df["Risk_Level"] == "Medium").sum()
low = (processed_df["Risk_Level"] == "Low").sum()

# ================== KPI CARDS ==================
k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">High Risk Zones</div>
        <div class="card-value" style="color:#ef4444">{high}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Medium Risk Zones</div>
        <div class="card-value" style="color:#eab308">{medium}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Low Risk Zones</div>
        <div class="card-value" style="color:#22c55e">{low}</div>
    </div>
    """, unsafe_allow_html=True)

# ================== MAP + AI INSIGHTS ==================
st.markdown('<div class="section-title">Live Water Risk Map</div>', unsafe_allow_html=True)

map_col, insight_col = st.columns([2.3, 1])

# -------- MAP --------
with map_col:
    map_rows = []

    for _, row in processed_df.iterrows():
        zone = row["Zone_ID"]
        if zone in ZONE_LOCATIONS:
            lat, lon = ZONE_LOCATIONS[zone]

            if row["Risk_Level"] == "High":
                color, radius = [239, 68, 68], 70000
            elif row["Risk_Level"] == "Medium":
                color, radius = [234, 179, 8], 50000
            else:
                color, radius = [34, 197, 94], 30000

            map_rows.append({
                "lat": lat,
                "lon": lon,
                "zone": zone,
                "risk": row["Risk_Level"],
                "risk_score": row["risk_score"],
                "color": color,
                "radius": radius
            })

    map_df = pd.DataFrame(map_rows)

    if not map_df.empty:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_fill_color="color",
            get_radius="radius",
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=22.5,
            longitude=78.9,
            zoom=4.3,
            pitch=40
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style=None,
            tooltip={
                "html": """
                <b>Zone:</b> {zone}<br/>
                <b>Risk:</b> {risk}<br/>
                <b>Risk Score:</b> {risk_score}
                """
            }
        )

        st.pydeck_chart(deck, height=450)
    else:
        st.warning("No location data available")

# -------- AI INSIGHTS --------
with insight_col:
    st.markdown('<div class="section-title">AI Insights</div>', unsafe_allow_html=True)

    for _, row in processed_df[processed_df["Risk_Level"] == "High"].head(2).iterrows():
        st.markdown(
            f"""
            <div class="alert-critical">
                <b>CRITICAL – Zone {row['Zone_ID']}</b><br/>
                {generate_explanation(row)}
            </div>
            """,
            unsafe_allow_html=True
        )

    for _, row in processed_df[processed_df["Risk_Level"] == "Medium"].head(1).iterrows():
        st.markdown(
            f"""
            <div class="alert-warning">
                <b>WARNING – Zone {row['Zone_ID']}</b><br/>
                Abnormal water usage detected. Monitor closely.
            </div>
            """,
            unsafe_allow_html=True
        )

# ================== REAL-TIME LOSS DETECTION ==================
st.markdown('<div class="section-title">Real-Time Water Loss Detection</div>', unsafe_allow_html=True)

selected_zone = st.selectbox("Select Zone", processed_df["Zone_ID"].unique())
zone_data = processed_df[processed_df["Zone_ID"] == selected_zone]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=zone_data["Date"],
    y=zone_data["Water_Usage_Liters"],
    mode="lines+markers",
    name="Actual Usage",
    line=dict(color="#22d3ee", width=3)
))

fig.add_trace(go.Scatter(
    x=zone_data["Date"],
    y=zone_data["Water_Usage_Liters"].rolling(2).mean(),
    mode="lines",
    name="Expected Usage",
    line=dict(color="#94a3b8", dash="dash")
))

fig.update_layout(
    template="plotly_dark",
    height=420,
    xaxis_title="Time",
    yaxis_title="Water Usage (Liters)",
    legend=dict(orientation="h", y=1.1)
)

st.plotly_chart(fig, width="stretch")

# ================== WATER LOSS ANALYTICS ==================
st.markdown('<div class="section-title">Water Loss Analytics & Prediction</div>', unsafe_allow_html=True)

col_l, col_r = st.columns([1.4, 1])

# -------- HISTORICAL WATER LOSS --------
with col_l:
    daily_loss = (
        zone_data.groupby("Date")["risk_score"]
        .sum()
        .reset_index()
    )

    hist_fig = go.Figure()
    hist_fig.add_trace(go.Scatter(
        x=daily_loss["Date"],
        y=daily_loss["risk_score"],
        mode="lines+markers",
        name="Water Loss Risk"
    ))

    hist_fig.update_layout(
        template="plotly_dark",
        height=300,
        xaxis_title="Date",
        yaxis_title="Risk Score"
    )

    st.plotly_chart(hist_fig, width="stretch")

# -------- AI PREDICTION --------
with col_r:
    predicted = (
        zone_data["risk_score"]
        .rolling(3)
        .mean()
        .fillna(method="bfill")
    )

    pred_fig = go.Figure()
    pred_fig.add_trace(go.Scatter(
        x=zone_data["Date"],
        y=predicted,
        mode="lines+markers",
        name="Predicted Risk"
    ))

    pred_fig.add_hline(y=predicted.mean(), line_dash="dot")

    pred_fig.update_layout(
        template="plotly_dark",
        height=300,
        xaxis_title="Date",
        yaxis_title="Predicted Risk"
    )

    st.plotly_chart(pred_fig, width="stretch")

# ================== PREVENTIVE ACTIONS ==================
st.markdown('<div class="section-title">Preventive Actions (Water)</div>', unsafe_allow_html=True)

avg_risk = zone_data["risk_score"].mean()

if avg_risk > 0.7:
    action = "Inspect underground pipelines immediately"
elif avg_risk > 0.4:
    action = "Increase pressure & flow monitoring"
else:
    action = "Routine maintenance recommended"

st.markdown(
    f"""
    <div class="card">
        <div class="card-title">Recommended Action</div>
        <div class="card-value">{action}</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">📊 Water Risk Distribution</div>',
    unsafe_allow_html=True
)

risk_counts = zone_data["Risk_Level"].value_counts()

pie_fig = go.Figure(
    data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        hole=0.65,                         # 🔥 better donut thickness
        textinfo="percent",
        textfont=dict(size=16),
        marker=dict(
            colors=["#38bdf8", "#4b2fbb"],
            line=dict(color="#0f172a", width=4)
        )
    )]
)

pie_fig.update_layout(
    template="plotly_dark",
    height=420,                           # 🔥 THIS makes it big
    margin=dict(t=20, b=20, l=20, r=20),  # prevents shrinking
    showlegend=True,
    legend=dict(
        orientation="v",
        y=0.5,
        yanchor="middle",
        font=dict(size=14)
    ),
    annotations=[
        dict(
            text="<b>Risk</b>",
            x=0.5,
            y=0.5,
            font_size=22,
            showarrow=False
        )
    ]
)

st.plotly_chart(pie_fig, use_container_width=True)



st.markdown('<div class="section-title">📉 Daily Water Loss Severity</div>', unsafe_allow_html=True)

daily_risk = (
    zone_data.groupby("Date")["risk_score"]
    .mean()
    .reset_index()
)

bar_fig = go.Figure()

bar_fig.add_bar(
    x=daily_risk["Date"],
    y=daily_risk["risk_score"],
    marker_color="#38bdf8",
    name="Average Risk"
)

bar_fig.update_layout(
    template="plotly_dark",
    height=320,
    xaxis_title="Date",
    yaxis_title="Risk Score"
)

st.plotly_chart(bar_fig, width="stretch")



st.markdown('<div class="section-title">🔬 Usage vs Pressure Correlation</div>', unsafe_allow_html=True)

scatter_fig = go.Figure()

scatter_fig.add_trace(go.Scatter(
    x=zone_data["Pressure"],
    y=zone_data["Water_Usage_Liters"],
    mode="markers",
    marker=dict(
        size=10,
        color=zone_data["risk_score"],
        colorscale="RdYlGn_r",
        showscale=True
    ),
    name="Sensor Readings"
))

scatter_fig.update_layout(
    template="plotly_dark",
    height=350,
    xaxis_title="Pressure",
    yaxis_title="Water Usage (Liters)"
)

st.plotly_chart(scatter_fig, width="stretch")



st.markdown('<div class="section-title">🚦 Severity Distribution</div>', unsafe_allow_html=True)

sev_col, timeline_col = st.columns([1, 1.6])

with sev_col:
    severity_counts = zone_data["Risk_Level"].value_counts()
    total_events = severity_counts.sum()

    def sev_row(label, color):
        count = severity_counts.get(label, 0)
        percent = int((count / total_events) * 100) if total_events > 0 else 0

        st.markdown(f"""
        <div style="margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between;">
                <span>{label}</span>
                <span>{count} ({percent}%)</span>
            </div>
            <div style="background:#1f2937; border-radius:6px; height:8px;">
                <div style="width:{percent}%; background:{color}; height:8px; border-radius:6px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    sev_row("Low", "#22c55e")
    sev_row("Medium", "#eab308")
    sev_row("High", "#fb923c")
    sev_row("Critical", "#ef4444")

st.markdown("### 📅 Event Timeline")

timeline_df = zone_data.copy()

# SAFELY parse datetime
timeline_df["Date"] = pd.to_datetime(
    timeline_df["Date"],
    format="mixed",
    errors="coerce"
)

# If too little data, show info instead of blank chart
if timeline_df["Date"].nunique() < 2:
    st.info("Not enough historical data to display event timeline.")
else:
    timeline_df["Day"] = timeline_df["Date"].dt.day_name()

    days_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    total_events = timeline_df.groupby("Day").size()
    anomaly_events = timeline_df[
        timeline_df["Risk_Level"].isin(["Medium", "High", "Critical"])
    ].groupby("Day").size()

    total_events = total_events.reindex(days_order, fill_value=0)
    anomaly_events = anomaly_events.reindex(days_order, fill_value=0)

    timeline_fig = go.Figure()

    timeline_fig.add_trace(go.Scatter(
        x=days_order,
        y=total_events.values,
        mode="lines+markers",
        name="Total Events",
        line=dict(color="#22d3ee", width=3),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(34,211,238,0.15)"
    ))

    timeline_fig.add_trace(go.Scatter(
        x=days_order,
        y=anomaly_events.values,
        mode="lines+markers",
        name="Anomalies",
        line=dict(color="#fb7185", width=3),
        marker=dict(size=8)
    ))

    timeline_fig.update_layout(
        template="plotly_dark",
        height=360,
        xaxis_title="Day",
        yaxis_title="Events",
        legend=dict(orientation="h", y=-0.25),
        margin=dict(l=20, r=20, t=30, b=40)
    )

    st.plotly_chart(timeline_fig, width="stretch")


st.divider()
st.caption("1M1B – IBM SkillsBuild | AI for Sustainability")
