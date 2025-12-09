# Medical Registrar Scheduling System

## Project Overview

An intelligent, LLM-powered scheduling system for automating medical registrar scheduling in a large department of medicine (40+ registrars). The system aims to eliminate manual scheduling overhead while managing complex constraints including work hour limits, coverage requirements, personal preferences, and training rotations.

## Problem Statement

**Current State**: Manual scheduling via spreadsheets consuming significant human resources
**Goal**: Fully automated scheduling with intelligent constraint satisfaction and natural language interface
**Scale**: 40+ registrars across multiple sites
**Complexity**: Multi-dimensional constraints (legal, operational, personal, educational)

## Core Constraints to Handle

### Hard Constraints (Must be satisfied)
- Work hour limits and fatigue management (maximum consecutive hours, minimum rest periods)
- Minimum coverage requirements per shift/specialty
- Regulatory compliance (medical board requirements)
- Maximum weekly/monthly hours per registrar
- Mandatory training rotation requirements

### Soft Constraints (Optimize for)
- Personal leave and preference requests
- Fair distribution of night shifts and weekends
- Continuity of care considerations
- Preferred working partnerships
- Commute and work-life balance factors

### Dynamic Constraints
- Last-minute sick leave
- Emergency coverage needs
- Shift swap requests
- Training opportunities

## Architecture

### Technology Stack

**Backend**
- Language: Python 3.11+
- Framework: FastAPI
- Constraint Solver: Google OR-Tools
- LLM: Claude API (Anthropic)
- Database: PostgreSQL

**Frontend** (Phase 2)
- Framework: React + Next.js (or Streamlit for rapid prototyping)
- UI Library: Tailwind CSS or Material-UI
- Mobile: Responsive web design

**DevOps**
- Containerization: Docker
- Version Control: Git
- Testing: pytest
- CI/CD: GitHub Actions (or similar)

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ LLM Chat UI  │  │  Admin UI    │  │ Registrar UI │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Chat Endpoint│  │ Schedule API │  │ Admin API    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                    Business Logic Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ LLM Service  │  │  Scheduler   │  │ Validator    │  │
│  │  (Claude)    │  │  Engine      │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                    Data Layer (PostgreSQL)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Registrars  │  │  Schedules   │  │ Constraints  │  │
│  │  Shifts      │  │  History     │  │ Preferences  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Development Phases

### Phase 0: Flexible Demo (CURRENT FOCUS)
**Goal**: Build a working demo with configurable constraints to pitch to stakeholders

- [ ] Set up lightweight project structure (no database yet)
- [ ] Create sample data generator (realistic fake registrars and shifts)
- [ ] Build flexible constraint system (define constraints in config files)
- [ ] Implement basic scheduler with common medical constraints
- [ ] Integrate Claude API for natural language interface
- [ ] Create simple Streamlit UI for demo
- [ ] Add constraint explanation and "what-if" scenarios
- [ ] Generate sample schedules with explanations

**Deliverable**: Interactive demo that stakeholders can play with to surface real requirements

**Key Features for Demo**:
- Chat interface: "Show me next week's schedule", "Why is Dr. Smith on nights?", "What if we need 3 people on Friday?"
- Constraint viewer: Show which constraints are active and how to modify them
- Schedule visualization: Calendar view of generated schedules
- Flexibility showcase: Demonstrate adding/removing constraints on the fly

### Phase 1: Core Scheduling Engine (Post-Demo)
**Goal**: Build production system with real constraints from stakeholder feedback

- [ ] Set up proper project structure and database
- [ ] Define data models based on learned requirements
- [ ] Implement validated constraint solver
- [ ] Build robust schedule generator
- [ ] Create validation engine
- [ ] Write comprehensive tests

**Deliverable**: Production-ready scheduling engine

### Phase 2: Full Application
**Goal**: Complete system with all required features

- [ ] Build FastAPI backend with all endpoints
- [ ] Create admin dashboard
- [ ] Develop registrar portal
- [ ] Implement notification system
- [ ] Add reporting and analytics
- [ ] Build export functionality
- [ ] Implement audit trail and history
- [ ] Add authentication and authorization

**Deliverable**: Full-featured web application

### Phase 3: Advanced Features (Future)
**Goal**: Optimization and intelligence

- [ ] Machine learning for preference prediction
- [ ] Automated swap matching
- [ ] Predictive analytics for coverage needs
- [ ] Integration with hospital systems
- [ ] Advanced fairness algorithms

## Data Model (Initial)

### Registrar
- ID, name, contact info
- Seniority level
- Specialty/rotation assignments
- Contract hours
- Maximum consecutive hours
- Minimum rest hours
- Skills/certifications

### Shift
- ID, date, start time, end time
- Type (day/night/weekend)
- Location/site
- Required coverage (number of registrars)
- Required skills/specialties
- Difficulty/desirability score

### Constraint
- Type (hard/soft)
- Registrar ID (if applicable)
- Rule definition
- Priority/weight
- Active date range

### Preference
- Registrar ID
- Preference type (leave, preferred shift, avoid shift)
- Date/date range
- Priority
- Reason

### Schedule
- ID, period (start/end date)
- Status (draft/published/archived)
- Generation timestamp
- Assignments (registrar-shift mappings)
- Conflict log
- Optimization score

## Key Algorithms

### Schedule Generation
1. **Constraint Satisfaction**: Use OR-Tools CP-SAT solver
2. **Objective Function**: Minimize soft constraint violations while satisfying all hard constraints
3. **Fairness Metrics**: Balance undesirable shifts, total hours, weekend coverage

### LLM Integration Strategy
- **Query Understanding**: Parse natural language into structured queries
- **Context Management**: Provide relevant schedule data to Claude
- **Action Execution**: Translate LLM suggestions into API calls
- **Explanation Generation**: Use Claude to explain scheduling decisions in plain language

## Success Metrics

- **Automation Rate**: % of schedules generated without manual intervention
- **Constraint Satisfaction**: 100% hard constraints, >90% soft constraints
- **Time Savings**: Hours saved vs. manual scheduling
- **Registrar Satisfaction**: Survey scores on schedule fairness
- **System Uptime**: >99% availability
- **Response Time**: <2s for queries, <30s for schedule generation

## Security & Compliance

- HIPAA compliance considerations (if handling patient data)
- Authentication and role-based access control
- Audit logging for all schedule changes
- Data encryption at rest and in transit
- Backup and disaster recovery

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Anthropic API key
- Git

### Initial Setup
```bash
# Clone repository
git clone <repo-url>
cd scheduler

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb medical_scheduler
python scripts/init_db.py

# Configure environment
cp .env.example .env
# Edit .env with your API keys and database credentials

# Run tests
pytest

# Start development server
python main.py
```

## Project Structure
```
scheduler/
├── CLAUDE.md                 # This file
├── README.md                 # User-facing documentation
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   │
│   ├── models/              # Data models
│   │   ├── registrar.py
│   │   ├── shift.py
│   │   ├── schedule.py
│   │   └── constraint.py
│   │
│   ├── scheduler/           # Core scheduling engine
│   │   ├── solver.py        # OR-Tools constraint solver
│   │   ├── generator.py     # Schedule generation
│   │   ├── validator.py     # Constraint validation
│   │   └── optimizer.py     # Optimization algorithms
│   │
│   ├── llm/                 # LLM integration
│   │   ├── claude_client.py # Claude API wrapper
│   │   ├── prompts.py       # Prompt templates
│   │   ├── parser.py        # NL query parsing
│   │   └── explainer.py     # Schedule explanations
│   │
│   ├── api/                 # FastAPI application
│   │   ├── routes/
│   │   ├── dependencies.py
│   │   └── middleware.py
│   │
│   ├── database/            # Database layer
│   │   ├── connection.py
│   │   ├── repositories/
│   │   └── migrations/
│   │
│   └── utils/               # Utilities
│       ├── config.py
│       └── logger.py
│
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── scripts/                 # Utility scripts
│   ├── init_db.py
│   ├── seed_data.py
│   └── export_schedule.py
│
└── docs/                    # Additional documentation
    ├── api.md
    ├── constraints.md
    └── deployment.md
```

## Next Steps

1. **Clarify Requirements**: Document specific constraint rules for your department
2. **Set Up Project**: Initialize git repository and project structure
3. **Data Collection**: Gather sample data (anonymized if needed) for testing
4. **Build MVP**: Focus on Phase 1 - get basic scheduling working
5. **Iterate**: Test with small dataset, refine constraints
6. **Add LLM**: Integrate Claude for natural language interface
7. **Pilot**: Test with a subset of registrars
8. **Scale**: Roll out to full department

## Resources & References

- Google OR-Tools Documentation: https://developers.google.com/optimization
- Nurse Rostering Problem (similar domain): https://en.wikipedia.org/wiki/Nurse_scheduling_problem
- Claude API Documentation: https://docs.anthropic.com
- Medical Shift Scheduling Papers: [Add relevant academic references]

## Questions to Answer

- [ ] What are the exact work hour regulations for your jurisdiction?
- [ ] How many different shift types exist?
- [ ] What is the scheduling horizon? (weekly, monthly, quarterly)
- [ ] Are there multiple sites/locations to coordinate?
- [ ] What are the training rotation requirements?
- [ ] How are current preferences collected?
- [ ] What is the approval workflow?
- [ ] Who are the stakeholders? (registrars, chief registrar, admin, HR)
- [ ] What existing systems need integration?
- [ ] What reporting is needed?

## Notes

- Start simple: Get basic constraint satisfaction working before adding LLM interface
- Validate with domain experts frequently
- Keep the LLM as an interface layer, not the core logic
- Consider privacy: registrars may not want their constraints visible to others
- Build in flexibility: rules will change as you learn more about the problem
