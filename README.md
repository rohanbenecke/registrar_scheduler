# Medical Registrar Scheduler - Demo

An intelligent, AI-powered scheduling system for medical registrar shift management. This demo showcases flexible constraint-based scheduling with natural language querying capabilities.

## Features

- **Flexible Constraint System**: Configure scheduling rules via YAML files
- **Automated Schedule Generation**: Intelligent algorithm balances fairness and coverage
- **AI Assistant**: Ask questions about schedules in natural language using Claude
- **Visual Analytics**: Interactive dashboards showing fairness metrics and coverage
- **Sample Data Generation**: Realistic fake data for demonstrations

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Anthropic API key (for AI features)

### Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment**
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env

   # Edit .env and add your Anthropic API key
   # Get your key from: https://console.anthropic.com/
   ```

5. **Generate sample data (optional - will auto-generate on first run)**
   ```bash
   python src/data_generator.py
   ```

6. **Run the demo**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## Usage

### Generating a Schedule

1. Open the **Generate Schedule** tab
2. Click **Generate Schedule**
3. View the generated schedule in calendar format
4. See coverage statistics and fairness metrics

### Modifying Constraints

Edit `config/constraints.yaml` to customize:
- Work hour limits
- Coverage requirements
- Shift definitions
- Fairness preferences

Example:
```yaml
hard_constraints:
  max_consecutive_shifts: 5
  min_rest_hours: 11
  max_weekly_hours: 48
```

### Asking Questions (AI Assistant)

With an API key configured, you can ask natural language questions:

- "Who is working next Monday?"
- "Why was Dr. Smith assigned to night shifts?"
- "How many shifts does each person have?"
- "Are there any fairness issues?"
- "What constraints are being violated?"

### Customizing Demo Data

Edit the data parameters in your `.env` file:

```env
NUM_REGISTRARS=20
NUM_WEEKS=4
```

Then regenerate data using the button in the sidebar.

## Project Structure

```
scheduler/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── CLAUDE.md                # Project guide and documentation
│
├── config/
│   └── constraints.yaml     # Scheduling constraints configuration
│
├── src/
│   ├── data_generator.py   # Sample data generation
│   ├── scheduler.py         # Scheduling engine
│   └── llm_interface.py    # Claude API integration
│
└── data/                    # Generated sample data (auto-created)
    ├── registrars.json
    └── shifts.json
```

## Demo Workflow

This is a **proof-of-concept** designed to:

1. **Demonstrate capabilities** to stakeholders
2. **Surface real requirements** through discussion
3. **Validate approach** before full development

### For Pitching to Stakeholders

1. Run the demo and generate a sample schedule
2. Show the visual dashboards and fairness metrics
3. Demonstrate the AI assistant answering questions
4. Modify constraints in real-time to show flexibility
5. Gather feedback on what constraints matter most

### Next Steps After Demo

Once you have stakeholder buy-in and real requirements:

1. Document actual constraints from your department
2. Collect real registrar data (anonymized for testing)
3. Upgrade to production database (PostgreSQL)
4. Implement OR-Tools for more sophisticated optimization
5. Add authentication and multi-user features
6. Build mobile-friendly interface

See `CLAUDE.md` for the full development roadmap.

## Configuration Examples

### Increasing Night Shift Capacity

```yaml
hard_constraints:
  max_night_shifts_per_week: 4  # Increase from 3
```

### Adding a New Shift Type

```yaml
shift_types:
  late_evening:
    start_hour: 17
    end_hour: 1  # Next day
    duration_hours: 8
    desirability_score: -4

weekly_template:
  monday:
    - day
    - evening
    - late_evening  # Add to schedule
    - night
```

### Adjusting Fairness Priorities

```yaml
soft_constraints:
  respect_leave_requests:
    weight: 10  # Highest priority

  balance_weekend_shifts:
    enabled: true
    weight: 8  # High priority
```

## Troubleshooting

### API Key Issues

If you see "Claude API key not configured":
1. Check that `.env` file exists (not `.env.example`)
2. Verify `ANTHROPIC_API_KEY` is set correctly
3. Restart the Streamlit app

### No Schedule Generated

If schedule generation fails:
1. Check constraints aren't too restrictive
2. Ensure adequate registrars for coverage needs
3. Look at constraint violations in the Analysis tab

### Import Errors

If you get module import errors:
```bash
# Make sure you're in the virtual environment
pip install -r requirements.txt --upgrade
```

## Technologies Used

- **Streamlit**: Interactive web interface
- **Claude API**: Natural language processing
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **Faker**: Realistic sample data
- **PyYAML**: Configuration management

## Contributing

This is a demo project. For production use:
- Add comprehensive testing
- Implement proper error handling
- Add input validation
- Set up continuous integration
- Add logging and monitoring

## License

This is a demonstration project. Customize as needed for your organization.

## Support

For questions about the demo or scheduling requirements, refer to `CLAUDE.md` for detailed documentation.
