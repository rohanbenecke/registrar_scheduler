# Medical Registrar Scheduler - Project Summary

## What We Built

A **flexible, AI-powered demo** for medical registrar scheduling that you can use to:
1. Demonstrate automated scheduling capabilities
2. Gather real requirements from stakeholders
3. Show the value of AI-powered interfaces
4. Validate the approach before full development

## Project Structure

```
scheduler/
│
├── 📄 Core Application Files
│   ├── app.py                    # Main Streamlit demo app (18KB)
│   ├── setup.py                  # Quick setup helper script
│   ├── requirements.txt          # Python dependencies
│   └── .env.example             # API key template
│
├── 📚 Documentation
│   ├── CLAUDE.md                 # Complete project guide (14KB)
│   ├── README.md                 # User documentation (6KB)
│   ├── QUICKSTART.md             # 5-minute setup guide
│   └── PROJECT_SUMMARY.md        # This file
│
├── ⚙️ config/
│   └── constraints.yaml          # Flexible constraint configuration (3KB)
│
└── 🐍 src/
    ├── __init__.py              # Package initialization
    ├── data_generator.py        # Generate realistic fake data (7KB)
    ├── scheduler.py             # Core scheduling engine (12KB)
    └── llm_interface.py         # Claude API integration (10KB)
```

## Key Features Built

### 1. Flexible Constraint System ✅
- YAML-based configuration (easy to modify)
- Hard constraints (must satisfy)
- Soft constraints (optimize for)
- Shift type definitions
- Weekly schedule templates

**File:** `config/constraints.yaml`

### 2. Automated Scheduler ✅
- Greedy algorithm with constraint validation
- Fairness optimization
- Work hour limit enforcement
- Coverage requirement checking
- Detailed violation reporting

**File:** `src/scheduler.py`

### 3. Sample Data Generator ✅
- Realistic fake registrar profiles
- Leave requests and preferences
- Multiple specialties and seniority levels
- Shift generation based on config

**File:** `src/data_generator.py`

### 4. AI Assistant (Claude Integration) ✅
- Natural language queries
- Schedule explanations
- Constraint violation analysis
- Improvement suggestions
- Conversational interface

**File:** `src/llm_interface.py`

### 5. Interactive Demo UI ✅
- 4 main tabs:
  - **Generate Schedule**: Create and view schedules
  - **Analysis**: Fairness metrics and visualizations
  - **AI Assistant**: Chat with Claude about the schedule
  - **Registrars**: View staff directory
- Real-time statistics
- Interactive charts (Plotly)
- Filterable schedule calendar
- Color-coded coverage indicators

**File:** `app.py`

## Technologies Used

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **Python 3.11+** | Core language | Best for algorithms & ML |
| **Streamlit** | Web UI | Fast prototyping, interactive |
| **Claude API** | AI interface | Natural language understanding |
| **Pandas** | Data handling | Easy data manipulation |
| **Plotly** | Visualizations | Interactive charts |
| **PyYAML** | Configuration | Human-readable config files |
| **Faker** | Sample data | Realistic test data |

## What Makes This Demo Special

### 1. **Flexibility First**
- Change constraints without coding
- Config-driven design
- Easy to customize for any department

### 2. **AI-Powered**
- Natural language queries
- Intelligent explanations
- Shows cutting-edge capabilities

### 3. **Visual & Interactive**
- Beautiful dashboards
- Real-time updates
- Intuitive interface

### 4. **Production-Ready Path**
- Clean architecture
- Modular design
- Clear upgrade path to full system

## Demo Scenarios

### Scenario 1: Basic Demo
1. Run `streamlit run app.py`
2. Generate a schedule
3. Show fairness metrics
4. Demonstrate constraint flexibility

**Time:** 5-10 minutes

### Scenario 2: AI-Powered Demo
1. Set up API key
2. Generate schedule
3. Ask natural language questions:
   - "Who's working this weekend?"
   - "Why is this schedule fair?"
   - "What constraints are violated?"
4. Show conversational understanding

**Time:** 10-15 minutes

### Scenario 3: Customization Demo
1. Open `config/constraints.yaml`
2. Modify a constraint (e.g., max_weekly_hours: 60)
3. Regenerate schedule
4. Show the impact
5. Discuss what constraints matter for their department

**Time:** 15-20 minutes

## Stakeholder Discussion Guide

### Questions to Ask While Demoing

1. **About Constraints:**
   - What work hour regulations apply?
   - What coverage requirements do you have?
   - What makes a schedule "fair" in your view?

2. **About Preferences:**
   - How do you handle leave requests now?
   - Do people have shift preferences?
   - How are swaps managed?

3. **About Features:**
   - What would make this most useful?
   - What reports do you need?
   - Who needs access to what?

4. **About Integration:**
   - What systems need to connect?
   - What data format do you use?
   - How do you communicate schedules?

### Expected Feedback Types

| Feedback Type | How to Handle |
|--------------|---------------|
| **"We need constraint X"** | Note it - easy to add to YAML |
| **"Fairness should be Y"** | Adjustable in algorithm |
| **"We use system Z"** | Plan for integration later |
| **"Can it do X?"** | If not, add to feature backlog |

## Current Limitations (By Design)

These are intentional for the demo:

1. **Simple Algorithm**: Uses greedy approach, not full optimization
   - *Why:* Faster, easier to explain, good enough for demo
   - *Production:* Upgrade to OR-Tools

2. **No Database**: Uses JSON files
   - *Why:* No setup required, portable
   - *Production:* PostgreSQL

3. **No Authentication**: Single user
   - *Why:* Demo simplicity
   - *Production:* Add auth system

4. **Limited Scale**: ~20 registrars, 4 weeks
   - *Why:* Fast generation, clear visualization
   - *Production:* Can scale to 100+ registrars

5. **Basic UI**: Streamlit
   - *Why:* Rapid development
   - *Production:* Could upgrade to React if needed

## Success Metrics for Demo

### Immediate Goals ✅
- [ ] Demo runs successfully
- [ ] Stakeholders understand the concept
- [ ] Real constraints are surfaced
- [ ] Buy-in for full development

### Next Phase Goals
- [ ] Document actual constraints
- [ ] Collect real (anonymized) data
- [ ] Validate algorithm with domain experts
- [ ] Define success metrics for production

## Path to Production

See `CLAUDE.md` for the complete roadmap, but here's the overview:

1. **Phase 0 (Current)**: Flexible Demo ✅
2. **Phase 1**: Production Scheduler Engine
3. **Phase 2**: Full Web Application
4. **Phase 3**: Advanced Features

**Estimated Timeline:**
- Phase 1: 4-6 weeks
- Phase 2: 6-8 weeks
- Phase 3: Ongoing

## Cost Estimates

### Demo (Current)
- **Development:** Complete ✅
- **Running Cost:** ~$5-10/month (Claude API usage)

### Production
- **Development:** 3-6 months (depending on features)
- **Infrastructure:** ~$50-200/month
  - Database hosting
  - Web hosting
  - API costs
  - Backup/monitoring

## Files You Can Customize

### Easy (No Coding)
- `config/constraints.yaml` - All scheduling rules
- `.env` - Configuration parameters
- `data/` - Sample data (auto-generated)

### Medium (Basic Python)
- `src/data_generator.py` - Sample data characteristics
- `app.py` - UI layout and text

### Advanced (Requires Understanding)
- `src/scheduler.py` - Scheduling algorithm
- `src/llm_interface.py` - AI prompts and logic

## Quick Commands Reference

```bash
# Setup
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env

# Run
streamlit run app.py

# Generate new data
python src/data_generator.py

# Clean and restart
rm -rf data/
streamlit run app.py
```

## Getting Help

1. **Setup Issues**: See `QUICKSTART.md`
2. **Usage Questions**: See `README.md`
3. **Project Planning**: See `CLAUDE.md`
4. **Constraint Questions**: See `config/constraints.yaml` comments

## What to Share After Demo

1. **This folder** - Everything is self-contained
2. **Your notes** - What constraints they mentioned
3. **Feedback** - What features they want
4. **Next steps** - Timeline and expectations

## License & Usage

This is a custom demo for your organization. Feel free to:
- Modify any code
- Share with stakeholders
- Use as basis for production system
- Add features as needed

## Credits

Built with Claude Code using:
- Modern Python best practices
- Industry-standard libraries
- Flexible, maintainable architecture

---

**Ready to demo?** Run: `streamlit run app.py`

**Need to customize?** Edit: `config/constraints.yaml`

**Questions?** Check: `QUICKSTART.md` or `README.md`
