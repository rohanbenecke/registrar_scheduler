# Quick Start Guide

Get the demo running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Make sure you're in the scheduler directory
cd scheduler

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Set Up API Key (Optional but Recommended)

The AI assistant requires an Anthropic API key.

1. Get a free API key from: https://console.anthropic.com/
2. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
3. Edit `.env` and replace `your_api_key_here` with your actual key

**Note:** The demo will work without an API key, but the AI assistant features won't be available.

## Step 3: Run Setup (Optional)

```bash
python setup.py
```

This will:
- Check your Python version
- Create necessary directories
- Generate sample data
- Verify everything is ready

## Step 4: Launch the Demo

```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`

## Step 5: Try It Out!

1. **Generate a Schedule**
   - Go to "Generate Schedule" tab
   - Click "Generate Schedule" button
   - View the results!

2. **Explore the Analysis**
   - Check the "Analysis" tab
   - See fairness metrics
   - View distribution charts

3. **Ask Questions** (if you have API key set up)
   - Go to "AI Assistant" tab
   - Try: "Who is working next Monday?"
   - Try: "How many night shifts does each person have?"

4. **Modify Constraints**
   - Edit `config/constraints.yaml`
   - Change values like `max_weekly_hours` or `min_rest_hours`
   - Regenerate the schedule to see the impact

## Common Issues

### "Module not found" error
```bash
# Make sure you installed dependencies
pip install -r requirements.txt
```

### "API key not configured" warning
- This is OK! The demo works without it
- AI assistant just won't be available
- To enable: add your key to `.env` file

### Schedule generation looks weird
- This is a simple demo algorithm
- Try adjusting constraints in `config/constraints.yaml`
- The algorithm prioritizes fairness over perfect coverage

## What to Show Stakeholders

1. **Flexibility**: Change a constraint in the YAML file and regenerate
2. **Visualization**: Show the fairness charts and coverage metrics
3. **AI Interface**: Ask natural language questions about the schedule
4. **Customization**: Explain how constraints can match their exact needs

## Next Steps

After the demo, gather feedback on:
- What constraints matter most for your department?
- What shift types do you need?
- What fairness metrics are important?
- What features would be most valuable?

Document these in `CLAUDE.md` and you'll have a clear roadmap for building the production system!

## Need Help?

- Check `README.md` for detailed documentation
- See `CLAUDE.md` for the full project plan
- Review `config/constraints.yaml` for configuration options
