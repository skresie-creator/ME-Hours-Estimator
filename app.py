import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="ME Hours Estimator", page_icon="⚙️", layout="wide")

# --- Header ---
st.title("⚙️ Mechanical Engineering Labor Estimator")
st.markdown("Generate probabilistic labor estimates based on hardware complexity metrics.")
st.divider()

# --- Input Section ---
st.sidebar.header("BOM Parameters")
st.sidebar.markdown("Enter expected part counts and assembly metrics:")

# Using the LSY_13354 data as default values
mts_qty = st.sidebar.number_input("Custom Parts (MTS Qty)", min_value=0, value=185, step=10)
ots_qty = st.sidebar.number_input("Off-the-Shelf Parts (OTS Qty)", min_value=0, value=802, step=10)
fastener_qty = st.sidebar.number_input("Fastener Qty (Subset of OTS)", min_value=0, value=394, step=10)
sub_assembly_count = st.sidebar.number_input("Sub-assembly Count", min_value=1, value=18, step=1)
max_bom_depth = st.sidebar.number_input("Max BOM Depth", min_value=1, value=5, step=1)

# Auto-calculated inputs
total_parts = mts_qty + ots_qty
mts_ots_ratio = round(mts_qty / ots_qty, 4) if ots_qty > 0 else mts_qty

st.sidebar.divider()
st.sidebar.metric("Calculated Total Parts", f"{total_parts:,}")
st.sidebar.metric("Calculated MTS:OTS Ratio", mts_ots_ratio)

# --- Mock Prediction Logic ---
# (In the final version, this will be replaced by joblib loading your Gradient Boosting models)
def generate_mock_predictions():
    # Simulated baseline weights (e.g., 3.5 hours per custom part, 0.2 hours per OTS part)
    base_hours = (mts_qty * 3.5) + (ots_qty * 0.2) + (sub_assembly_count * 8.0)
    
    # Complexity multipliers
    depth_multiplier = 1 + (max_bom_depth * 0.05)
    fastener_penalty = (fastener_qty * 0.05)
    
    median_estimate = (base_hours * depth_multiplier) + fastener_penalty
    
    # Generate quantile spread
    lower_bound = median_estimate * 0.72  # 10th Percentile (Best case)
    upper_bound = median_estimate * 1.45  # 90th Percentile (Worst case)
    
    return int(lower_bound), int(median_estimate), int(upper_bound)

p10, p50, p90 = generate_mock_predictions()

# --- Output Section ---
st.subheader("Model Predictions")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Optimistic (10% Likelihood)", value=f"{p10} hrs", delta="- Best Case Scenario", delta_color="normal")
with col2:
    st.metric(label="Most Likely (50% Likelihood)", value=f"{p50} hrs", delta="Median Estimate", delta_color="off")
with col3:
    st.metric(label="Conservative (90% Likelihood)", value=f"{p90} hrs", delta="+ High Complexity Buffer", delta_color="inverse")

st.divider()

# --- Visualization ---
st.subheader("Estimation Confidence Range")

# Bullet chart to visualize the probabilistic spread
fig = go.Figure(go.Indicator(
    mode = "number+gauge",
    value = p50,
    number = {'suffix': " hrs", 'font': {'size': 40}},
    title = {'text': "Projected ME Labor Spread"},
    gauge = {
        'shape': "bullet",
        'axis': {'range': [None, p90 * 1.2]},
        'threshold': {
            'line': {'color': "red", 'width': 3},
            'thickness': 0.75,
            'value': p90
        },
        'steps': [
            {'range': [0, p10], 'color': "#e0f2f1"},           # Best case zone
            {'range': [p10, p50], 'color': "#80cbc4"},         # Likely zone lower
            {'range': [p50, p90], 'color': "#26a69a"}          # Likely zone upper
        ],
        'bar': {'color': "#004d40"}
    }
))

fig.update_layout(height=250, margin={'t': 40, 'b': 20, 'l': 0, 'r': 0})
st.plotly_chart(fig, use_container_width=True)

# --- Feature Importance Placeholder ---
with st.expander("View Model Diagnostics (Feature Drivers)"):
    st.markdown("*(Simulated data for UI demonstration)*")
    st.progress(0.65, text="MTS Quantity (65% impact)")
    st.progress(0.15, text="Sub-assembly Count (15% impact)")
    st.progress(0.10, text="Max BOM Depth (10% impact)")
    st.progress(0.10, text="OTS Quantity (10% impact)")