import altair as alt
import pandas as pd
import streamlit as st
import time
from pathlib import Path

from interface.influx.api import get_measurement_data, set_process_data

LEAKAGE_TEST_NUMBER = 2601

# App state
if "manual_setpoint" not in st.session_state:
    st.session_state.manual_setpoint = 100.0
    st.session_state.main_x = "timestamp"
    st.session_state.main_y = "feedback_position_%"
    st.session_state.emergency_close = False
    st.session_state.dpdt_lower_bound = -0.3
    st.session_state.dpdt_upper_bound = 0.3
    st.session_state.dp_sim_running = False
    st.session_state.dp_sim_pending_start = False
    st.session_state.dp_sim_index = 1
    st.session_state.dp_sim_step_s = 0.2
    st.session_state.dp_sim_start_time = None
    st.session_state.actuator_trace = []
    st.session_state.save_plots_requested = False
    st.session_state.dp_series = [
        0.61,
        0.62,
        0.6,
        0.61,
        0.62,
        0.6,
        0.61,
        0.59,
        0.6,
        0.2,
        0.21,
        0.2,
        0.19,
        0.18,
        0.2,
        0.21,
        0.2,
        0.19,
    ] + [0.2] * 50
if "main_x" not in st.session_state:
    st.session_state.main_x = "timestamp"
if "main_y" not in st.session_state:
    st.session_state.main_y = "feedback_position_%"
if "save_plots_requested" not in st.session_state:
    st.session_state.save_plots_requested = False

st.title("Belimo Case")
st.subheader("Leakage Detection: Derivative Bounds on Differential Pressure")
st.caption("by LederhosenDjangos")

st.session_state.manual_setpoint = st.number_input(
    "Normal valve setpoint (%)",
    min_value=0.0,
    max_value=100.0,
    value=float(st.session_state.manual_setpoint),
)

st.session_state.dpdt_lower_bound = st.number_input(
    "Lower bound for d∆p/dt (bar/s)",
    value=float(st.session_state.dpdt_lower_bound),
)
st.session_state.dpdt_upper_bound = st.number_input(
    "Upper bound for d∆p/dt (bar/s)",
    value=float(st.session_state.dpdt_upper_bound),
)

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    if st.button("Start d∆p/dt Example"):
        st.session_state.dp_sim_pending_start = True
        st.session_state.dp_sim_running = False
        st.session_state.dp_sim_index = 1
        st.session_state.emergency_close = False
        st.session_state.actuator_trace = []
with col_b:
    if st.button("Stop d∆p/dt Example"):
        st.session_state.dp_sim_running = False
        st.session_state.dp_sim_pending_start = False
        st.session_state.save_plots_requested = True
with col_c:
    if st.button("EMERGENCY: Close Valve Completely"):
        st.session_state.emergency_close = True
with col_d:
    if st.button("Reset Emergency Mode"):
        st.session_state.emergency_close = False

st.subheader("Real-Time Actuator Plot")
options = [
    "timestamp",
    "feedback_position_%",
    "setpoint_position_%",
    "rotation_direction",
    "internal_temperature_deg_C",
    "motor_torque_Nmm",
    "power_W",
]
col_x, col_y = st.columns(2)
with col_x:
    current_main_x = (
        st.session_state.main_x if st.session_state.main_x in options else "timestamp"
    )
    st.session_state.main_x = st.selectbox(
        "Main plot X variable", options, index=options.index(current_main_x)
    )
with col_y:
    current_main_y = (
        st.session_state.main_y
        if st.session_state.main_y in options
        else "feedback_position_%"
    )
    st.session_state.main_y = st.selectbox(
        "Main plot Y variable", options, index=options.index(current_main_y)
    )

main_chart_placeholder = st.empty()
actuator_window_chart_placeholder = st.empty()
dp_chart_placeholder = st.empty()
dpdt_chart_placeholder = st.empty()
status_placeholder = st.empty()
save_status_placeholder = st.empty()


def save_example_data(actuator_window_df, sim_df, dpdt_long):
    assets_dir = Path(__file__).resolve().parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    actuator_window_df.to_csv(assets_dir / "actuator_position_window.csv", index=False)
    sim_df.to_csv(assets_dir / "delta_p.csv", index=False)
    dpdt_long.to_csv(assets_dir / "delta_p_derivative_bounds.csv", index=False)

    save_status_placeholder.success(
        f"Saved CSV data to {assets_dir} (overwrote previous files)."
    )


while True:
    df = get_measurement_data(n=1500)
    main_df = df.reset_index()
    if "timestamp" in main_df.columns:
        main_df["timestamp"] = pd.to_datetime(main_df["timestamp"], utc=True)
    latest_row = (
        main_df.sort_values("timestamp").iloc[-1]
        if "timestamp" in main_df.columns and len(main_df.index) > 0
        else None
    )

    if st.session_state.dp_sim_pending_start and len(main_df.index) > 0:
        st.session_state.dp_sim_start_time = pd.Timestamp(main_df["timestamp"].max())
        st.session_state.dp_sim_running = True
        st.session_state.dp_sim_pending_start = False
        start_feedback = (
            float(latest_row["feedback_position_%"])
            if latest_row is not None and "feedback_position_%" in main_df.columns
            else float(st.session_state.manual_setpoint)
        )
        st.session_state.actuator_trace = [
            {
                "elapsed_s": 0.0,
                "setpoint_position_%": start_feedback,
                "feedback_position_%": start_feedback,
            }
        ]

    dpdt_value = None
    if st.session_state.dp_sim_running:
        idx = st.session_state.dp_sim_index
        series = st.session_state.dp_series
        if idx < len(series):
            prev_dp = float(series[idx - 1])
            current_dp = float(series[idx])
            dpdt_value = (current_dp - prev_dp) / float(st.session_state.dp_sim_step_s)
            if (
                dpdt_value < st.session_state.dpdt_lower_bound
                or dpdt_value > st.session_state.dpdt_upper_bound
            ):
                st.session_state.emergency_close = True
            st.session_state.dp_sim_index += 1
        else:
            st.session_state.dp_sim_running = False

    command_setpoint = (
        0.0 if st.session_state.emergency_close else float(st.session_state.manual_setpoint)
    )
    set_process_data(command_setpoint, test_number=LEAKAGE_TEST_NUMBER)

    latest_feedback = (
        float(latest_row["feedback_position_%"])
        if latest_row is not None and "feedback_position_%" in main_df.columns
        else None
    )
    latest_setpoint_readout = (
        float(latest_row["setpoint_position_%"])
        if latest_row is not None and "setpoint_position_%" in main_df.columns
        else latest_feedback
    )
    if st.session_state.dp_sim_running:
        trace_elapsed = (st.session_state.dp_sim_index - 1) * float(
            st.session_state.dp_sim_step_s
        )
        st.session_state.actuator_trace.append(
            {
                "elapsed_s": trace_elapsed,
                "setpoint_position_%": latest_setpoint_readout,
                "feedback_position_%": latest_feedback,
            }
        )

    if st.session_state.emergency_close:
        status_text = "Emergency mode active: valve command forced to 0%"
        if dpdt_value is not None:
            status_text += f" (d∆p/dt={dpdt_value:.3f} bar/s)"
        status_placeholder.error(status_text)
    else:
        status_text = "Normal control mode active"
        if dpdt_value is not None:
            status_text += f" (d∆p/dt={dpdt_value:.3f} bar/s)"
        status_placeholder.success(status_text)

    sim_points = max(1, st.session_state.dp_sim_index)
    sim_start = st.session_state.dp_sim_start_time
    if sim_start is None:
        sim_start = pd.Timestamp.now(tz="UTC")

    sim_timestamps = pd.date_range(
        start=sim_start,
        periods=sim_points,
        freq=f"{st.session_state.dp_sim_step_s}s",
    )
    sim_df = pd.DataFrame(
        {
            "timestamp": sim_timestamps,
            "elapsed_s": [i * st.session_state.dp_sim_step_s for i in range(sim_points)],
            "delta_p_bar": st.session_state.dp_series[:sim_points],
        }
    )
    if len(sim_df.index) > 1:
        sim_df["d_delta_p_dt"] = sim_df["delta_p_bar"].diff() / float(
            st.session_state.dp_sim_step_s
        )
    else:
        sim_df["d_delta_p_dt"] = 0.0
    sim_df["upper_bound"] = float(st.session_state.dpdt_upper_bound)
    sim_df["lower_bound"] = float(st.session_state.dpdt_lower_bound)

    main_chart = (
        alt.Chart(main_df)
        .mark_point(color="steelblue")
        .encode(
            x=st.session_state.main_x,
            y=st.session_state.main_y,
        )
    )
    main_chart_placeholder.altair_chart(main_chart, width="stretch")

    actuator_trace_df = pd.DataFrame(st.session_state.actuator_trace)
    actuator_window_df = pd.DataFrame({"elapsed_s": [], "series": [], "value": []})
    if len(actuator_trace_df.index) > 0:
        actuator_window_df = actuator_trace_df.melt(
            id_vars=["elapsed_s"],
            value_vars=["setpoint_position_%", "feedback_position_%"],
            var_name="series",
            value_name="value",
        )
        actuator_window_df["series"] = actuator_window_df["series"].replace(
            {
                "setpoint_position_%": "setpoint position %",
                "feedback_position_%": "feedback position %",
            }
        )

    actuator_window_chart = (
        alt.Chart(actuator_window_df)
        .mark_line()
        .encode(
            x=alt.X("elapsed_s:Q", title="Time since Start d∆p/dt Example [s]"),
            y=alt.Y("value:Q", title="position [%]"),
            color=alt.Color("series:N", legend=alt.Legend(orient="bottom")),
        )
    )
    actuator_window_chart_placeholder.altair_chart(actuator_window_chart, width="stretch")

    dp_chart = (
        alt.Chart(sim_df)
        .mark_line(color="orange")
        .encode(
            x=alt.X("elapsed_s:Q", title="Time since Start d∆p/dt Example [s]"),
            y=alt.Y("delta_p_bar:Q", title="∆p [bar]"),
        )
    )
    dp_chart_placeholder.altair_chart(dp_chart, width="stretch")

    dpdt_long = sim_df.melt(
        id_vars=["elapsed_s"],
        value_vars=["d_delta_p_dt", "upper_bound", "lower_bound"],
        var_name="series",
        value_name="value",
    )
    dpdt_long["series"] = dpdt_long["series"].replace(
        {
            "d_delta_p_dt": "d∆p/dt",
            "upper_bound": "upper bound",
            "lower_bound": "lower bound",
        }
    )
    dpdt_chart = (
        alt.Chart(dpdt_long)
        .mark_line()
        .encode(
            x=alt.X("elapsed_s:Q", title="Time since Start d∆p/dt Example [s]"),
            y=alt.Y("value:Q", title="d∆p/dt [bar/s]"),
            color=alt.Color("series:N", legend=alt.Legend(orient="bottom")),
        )
    )
    dpdt_chart_placeholder.altair_chart(dpdt_chart, width="stretch")

    if st.session_state.save_plots_requested:
        save_example_data(actuator_window_df, sim_df, dpdt_long)
        st.session_state.save_plots_requested = False

    time.sleep(st.session_state.dp_sim_step_s)
