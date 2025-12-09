"""
Medical Registrar Scheduler - Interactive Demo
Streamlit application for demonstrating the scheduling system
"""
import streamlit as st
import yaml
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent / "src"))

from data_generator import RegistrarGenerator, ShiftGenerator, save_sample_data
from scheduler import SimpleScheduler, ScheduleValidator
from llm_interface import ScheduleAssistant

# Page configuration
st.set_page_config(
    page_title="Medical Registrar Scheduler",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def load_config():
    """Load constraints configuration"""
    config_path = Path(__file__).parent / "config" / "constraints.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_or_generate_data(config):
    """Load existing data or generate new data"""
    data_dir = Path(__file__).parent / "data"
    registrars_file = data_dir / "registrars.json"
    shifts_file = data_dir / "shifts.json"

    if registrars_file.exists() and shifts_file.exists():
        with open(registrars_file, "r") as f:
            registrars = json.load(f)
        with open(shifts_file, "r") as f:
            shifts = json.load(f)
        return registrars, shifts
    else:
        # Generate new data
        num_registrars = int(os.getenv("NUM_REGISTRARS", "20"))
        num_weeks = int(os.getenv("NUM_WEEKS", "4"))

        reg_gen = RegistrarGenerator()
        shift_gen = ShiftGenerator()

        registrars = reg_gen.generate_registrars(num_registrars=num_registrars)
        shifts = shift_gen.generate_shifts_for_period(
            start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            num_weeks=num_weeks,
            config=config
        )

        # Save for future use
        data_dir.mkdir(exist_ok=True)
        save_sample_data(registrars, shifts, output_dir=str(data_dir))

        return registrars, shifts


def init_session_state():
    """Initialize session state variables"""
    if "schedule_generated" not in st.session_state:
        st.session_state.schedule_generated = False
    if "scheduled_shifts" not in st.session_state:
        st.session_state.scheduled_shifts = None
    if "statistics" not in st.session_state:
        st.session_state.statistics = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "assistant" not in st.session_state:
        # Check if API key is available
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            st.session_state.assistant = ScheduleAssistant(api_key)
        else:
            st.session_state.assistant = None


def display_schedule_statistics(statistics):
    """Display schedule statistics in metrics"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Shifts",
            statistics["total_shifts"],
            help="Total number of shifts in the schedule"
        )

    with col2:
        st.metric(
            "Successfully Scheduled",
            statistics["scheduled_shifts"],
            delta=f"{(statistics['scheduled_shifts']/statistics['total_shifts']*100):.1f}%",
            help="Shifts with adequate coverage"
        )

    with col3:
        st.metric(
            "Coverage Issues",
            statistics["unscheduled_shifts"],
            delta=f"{(statistics['unscheduled_shifts']/statistics['total_shifts']*100):.1f}%",
            delta_color="inverse",
            help="Shifts that couldn't meet minimum coverage requirements"
        )

    with col4:
        violations = len(statistics.get("constraint_violations", []))
        st.metric(
            "Constraint Violations",
            violations,
            delta_color="inverse",
            help="Number of shifts with constraint issues"
        )


def display_fairness_metrics(fairness_metrics, registrars):
    """Display fairness metrics with visualizations"""
    st.markdown('<p class="sub-header">Fairness Analysis</p>', unsafe_allow_html=True)

    if not fairness_metrics:
        st.info("No fairness metrics available yet. Generate a schedule first.")
        return

    # Create tabs for different metrics
    tab1, tab2, tab3 = st.tabs(["Total Shifts", "Night Shifts", "Work Hours"])

    with tab1:
        if "total_shifts_per_registrar" in fairness_metrics:
            shifts_data = fairness_metrics["total_shifts_per_registrar"]
            if shifts_data:
                # Create DataFrame
                df = pd.DataFrame([
                    {
                        "Registrar": next((r["name"] for r in registrars if r["id"] == reg_id), reg_id),
                        "ID": reg_id,
                        "Shifts": count
                    }
                    for reg_id, count in shifts_data.items()
                ])
                df = df.sort_values("Shifts", ascending=False)

                # Bar chart
                fig = px.bar(
                    df,
                    x="Registrar",
                    y="Shifts",
                    title="Total Shifts per Registrar",
                    color="Shifts",
                    color_continuous_scale="Blues"
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)

                # Statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average", f"{df['Shifts'].mean():.1f}")
                with col2:
                    st.metric("Std Dev", f"{df['Shifts'].std():.1f}")
                with col3:
                    st.metric("Range", f"{df['Shifts'].min()}-{df['Shifts'].max()}")

    with tab2:
        if "night_shifts_per_registrar" in fairness_metrics:
            night_data = fairness_metrics["night_shifts_per_registrar"]
            if night_data:
                df = pd.DataFrame([
                    {
                        "Registrar": next((r["name"] for r in registrars if r["id"] == reg_id), reg_id),
                        "Night Shifts": count
                    }
                    for reg_id, count in night_data.items()
                ])
                df = df.sort_values("Night Shifts", ascending=False)

                fig = px.bar(
                    df,
                    x="Registrar",
                    y="Night Shifts",
                    title="Night Shifts Distribution",
                    color="Night Shifts",
                    color_continuous_scale="Reds"
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if "total_hours_per_registrar" in fairness_metrics:
            hours_data = fairness_metrics["total_hours_per_registrar"]
            if hours_data:
                df = pd.DataFrame([
                    {
                        "Registrar": next((r["name"] for r in registrars if r["id"] == reg_id), reg_id),
                        "Hours": hours
                    }
                    for reg_id, hours in hours_data.items()
                ])
                df = df.sort_values("Hours", ascending=False)

                fig = px.bar(
                    df,
                    x="Registrar",
                    y="Hours",
                    title="Total Work Hours per Registrar",
                    color="Hours",
                    color_continuous_scale="Greens"
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)


def display_schedule_calendar(shifts):
    """Display schedule in calendar format"""
    st.markdown('<p class="sub-header">Schedule Calendar</p>', unsafe_allow_html=True)

    # Convert to DataFrame
    df_data = []
    for shift in shifts:
        assigned_names = [a.get("name", "Unknown") for a in shift.get("assigned_registrars", [])]
        df_data.append({
            "Date": shift["date"],
            "Day": shift["day_of_week"].capitalize(),
            "Shift Type": shift["shift_type"].replace("_", " ").title(),
            "Start": shift["start_time"].split()[1],
            "End": shift["end_time"].split()[1],
            "Duration (hrs)": shift["duration_hours"],
            "Required Staff": shift["required_staff"],
            "Assigned Staff": len(shift.get("assigned_registrars", [])),
            "Registrars": ", ".join(assigned_names) if assigned_names else "UNASSIGNED"
        })

    df = pd.DataFrame(df_data)

    # Add filtering
    col1, col2 = st.columns(2)
    with col1:
        selected_dates = st.multiselect(
            "Filter by Date",
            options=sorted(df["Date"].unique()),
            default=sorted(df["Date"].unique())[:7]  # Default to first week
        )
    with col2:
        selected_shift_types = st.multiselect(
            "Filter by Shift Type",
            options=df["Shift Type"].unique(),
            default=df["Shift Type"].unique()
        )

    # Filter DataFrame
    filtered_df = df[
        (df["Date"].isin(selected_dates)) &
        (df["Shift Type"].isin(selected_shift_types))
    ]

    # Color code by coverage status
    def color_coverage(row):
        if row["Assigned Staff"] < row["Required Staff"]:
            return "background-color: #ffcccc"  # Red for under-staffed
        elif row["Assigned Staff"] == row["Required Staff"]:
            return "background-color: #ccffcc"  # Green for adequate
        else:
            return "background-color: #ccf"  # Blue for over-staffed

    styled_df = filtered_df.style.apply(lambda x: [color_coverage(x)] * len(x), axis=1)

    st.dataframe(styled_df, use_container_width=True, height=400)

    # Legend
    st.caption("🟢 Green: Adequate coverage | 🔴 Red: Under-staffed | 🔵 Blue: Over-staffed")


def chat_interface(config, registrars):
    """Display chat interface for LLM interaction"""
    st.markdown('<p class="sub-header">Ask Questions About the Schedule</p>', unsafe_allow_html=True)

    if st.session_state.assistant is None:
        st.warning("⚠️ Claude API key not configured. Please set ANTHROPIC_API_KEY in your .env file.")
        st.info("To enable the AI assistant:\n1. Copy `.env.example` to `.env`\n2. Add your Anthropic API key\n3. Restart the app")
        return

    if not st.session_state.schedule_generated:
        st.info("Generate a schedule first, then you can ask questions about it!")
        return

    # Example questions
    with st.expander("Example Questions You Can Ask"):
        st.markdown("""
        - Who is working next Monday?
        - Why was Dr. Smith assigned to night shifts?
        - How many shifts does each person have?
        - Are there any fairness issues with this schedule?
        - What constraints are being violated?
        - How can we improve this schedule?
        - Who has the most night shifts?
        - Show me weekend coverage
        """)

    # Chat input
    user_question = st.chat_input("Ask a question about the schedule...")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle new question
    if user_question:
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        # Get response from assistant
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                schedule_data = {
                    "shifts": st.session_state.scheduled_shifts,
                    "statistics": st.session_state.statistics
                }

                response = st.session_state.assistant.query_schedule(
                    user_question=user_question,
                    schedule_data=schedule_data,
                    registrars=registrars,
                    config=config
                )

                st.markdown(response)

                # Add assistant response to chat
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })


def main():
    """Main application"""
    init_session_state()

    # Header
    st.markdown('<p class="main-header">🏥 Medical Registrar Scheduler</p>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Scheduling Demo** - Flexible, Intelligent, Fair")

    # Load configuration and data
    config = load_config()
    registrars, shifts = load_or_generate_data(config)

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        st.subheader("Data")
        st.info(f"📊 {len(registrars)} registrars\n\n📅 {len(shifts)} shifts")

        if st.button("🔄 Regenerate Sample Data", use_container_width=True):
            # Delete existing data files
            data_dir = Path(__file__).parent / "data"
            for file in data_dir.glob("*.json"):
                file.unlink()
            st.session_state.schedule_generated = False
            st.rerun()

        st.divider()

        st.subheader("Constraints")
        with st.expander("View Hard Constraints"):
            st.json(config["hard_constraints"])

        with st.expander("View Soft Constraints"):
            st.json(config["soft_constraints"])

        st.caption("Edit `config/constraints.yaml` to modify constraints")

        st.divider()

        st.subheader("About")
        st.markdown("""
        This is a **proof-of-concept** medical scheduler demonstrating:
        - Flexible constraint system
        - Automated schedule generation
        - AI-powered explanations
        - Fairness optimization

        Perfect for pitching to stakeholders and gathering real requirements!
        """)

    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Generate Schedule", "📊 Analysis", "💬 AI Assistant", "👥 Registrars"])

    with tab1:
        st.markdown("### Schedule Generation")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("Click the button to generate an optimized schedule based on current constraints")
        with col2:
            if st.button("🚀 Generate Schedule", type="primary", use_container_width=True):
                with st.spinner("Generating schedule..."):
                    scheduler = SimpleScheduler(config)
                    scheduled_shifts, statistics = scheduler.generate_schedule(registrars, shifts)

                    st.session_state.scheduled_shifts = scheduled_shifts
                    st.session_state.statistics = statistics
                    st.session_state.schedule_generated = True

                st.success("✅ Schedule generated successfully!")
                st.rerun()

        if st.session_state.schedule_generated:
            st.divider()

            # Display statistics
            display_schedule_statistics(st.session_state.statistics)

            st.divider()

            # Display calendar
            display_schedule_calendar(st.session_state.scheduled_shifts)

    with tab2:
        if not st.session_state.schedule_generated:
            st.info("Generate a schedule first to see analysis")
        else:
            display_fairness_metrics(
                st.session_state.statistics.get("fairness_metrics", {}),
                registrars
            )

            # Constraint violations
            violations = st.session_state.statistics.get("constraint_violations", [])
            if violations:
                st.divider()
                st.markdown('<p class="sub-header">⚠️ Constraint Violations</p>', unsafe_allow_html=True)

                for v in violations:
                    with st.expander(f"❌ {v['date']} - {v['shift_type']}"):
                        st.error(f"**Issue:** {v['reason']}")
                        st.write(f"Required: {v['required']} registrars")
                        st.write(f"Assigned: {v['assigned']} registrars")

    with tab3:
        chat_interface(config, registrars)

    with tab4:
        st.markdown("### Registrar Directory")

        # Display registrars in a nice format
        for registrar in registrars:
            with st.expander(f"👤 {registrar['name']} ({registrar['id']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Specialty:** {registrar['specialty']}")
                    st.write(f"**Seniority:** {registrar['seniority']}")
                    st.write(f"**Contract Hours:** {registrar['contract_hours']}/week")
                with col2:
                    st.write(f"**Email:** {registrar['email']}")
                    st.write(f"**Phone:** {registrar['phone']}")

                if registrar.get("preferences", {}).get("leave_requests"):
                    st.write("**Leave Requests:**")
                    for leave in registrar["preferences"]["leave_requests"]:
                        st.write(f"- {leave['start_date']} to {leave['end_date']}: {leave['reason']}")


if __name__ == "__main__":
    main()
