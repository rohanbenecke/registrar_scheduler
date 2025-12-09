"""
LLM interface for natural language interaction with the scheduler
Uses Claude API to answer questions and explain schedules
"""
import anthropic
import json
from typing import List, Dict, Optional
import os


class ScheduleAssistant:
    """Claude-powered assistant for schedule queries and explanations"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Claude client"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.conversation_history = []

    def query_schedule(
        self,
        user_question: str,
        schedule_data: Dict,
        registrars: List[Dict],
        config: Dict
    ) -> str:
        """
        Answer a natural language question about the schedule

        Args:
            user_question: The user's question
            schedule_data: Current schedule with statistics
            registrars: List of all registrars
            config: Configuration including constraints

        Returns:
            Natural language response from Claude
        """
        # Build context about the schedule
        context = self._build_context(schedule_data, registrars, config)

        # Create system prompt
        system_prompt = """You are an intelligent medical scheduling assistant. You help administrators and registrars understand and manage complex medical shift schedules.

Your capabilities:
- Answer questions about who is working when
- Explain why specific scheduling decisions were made
- Identify constraint violations or scheduling issues
- Suggest improvements or alternatives
- Explain scheduling rules and constraints

Be concise, clear, and professional. When explaining scheduling decisions, reference specific constraints or fairness considerations. If asked about specific registrars or shifts, provide detailed information."""

        # Build the user message with context
        user_message = f"""Here is the current schedule context:

{context}

User question: {user_question}

Please provide a helpful, accurate response based on the schedule data provided."""

        # Call Claude API
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            response_text = message.content[0].text
            return response_text

        except Exception as e:
            return f"Error querying Claude API: {str(e)}"

    def explain_constraint_violation(
        self,
        violation: Dict,
        registrars: List[Dict],
        config: Dict
    ) -> str:
        """Generate a detailed explanation of why a constraint was violated"""
        prompt = f"""Explain this scheduling constraint violation in simple terms:

Violation: {json.dumps(violation, indent=2)}

Relevant constraints:
{json.dumps(config['hard_constraints'], indent=2)}

Provide a clear explanation of what went wrong and potential solutions."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Could not generate explanation: {str(e)}"

    def suggest_improvements(
        self,
        schedule_data: Dict,
        statistics: Dict,
        config: Dict
    ) -> str:
        """Suggest improvements to the schedule based on statistics and fairness"""
        fairness = statistics.get("fairness_metrics", {})

        prompt = f"""Analyze this medical shift schedule and suggest improvements:

Schedule Statistics:
- Total shifts: {statistics.get('total_shifts', 0)}
- Successfully scheduled: {statistics.get('scheduled_shifts', 0)}
- Failed to schedule: {statistics.get('unscheduled_shifts', 0)}
- Constraint violations: {len(statistics.get('constraint_violations', []))}

Fairness Metrics:
{json.dumps(fairness, indent=2)}

Constraints:
{json.dumps(config['hard_constraints'], indent=2)}

Provide 3-5 specific, actionable suggestions to improve fairness, coverage, or constraint satisfaction."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Could not generate suggestions: {str(e)}"

    def _build_context(
        self,
        schedule_data: Dict,
        registrars: List[Dict],
        config: Dict
    ) -> str:
        """Build context string for Claude"""
        shifts = schedule_data.get("shifts", [])
        statistics = schedule_data.get("statistics", {})

        context_parts = []

        # Summary
        context_parts.append("SCHEDULE SUMMARY:")
        context_parts.append(f"- Total shifts: {len(shifts)}")
        context_parts.append(f"- Number of registrars: {len(registrars)}")
        context_parts.append(f"- Successfully scheduled shifts: {statistics.get('scheduled_shifts', 0)}")
        context_parts.append(f"- Shifts with coverage issues: {statistics.get('unscheduled_shifts', 0)}")
        context_parts.append("")

        # Registrars summary
        context_parts.append("REGISTRARS:")
        for reg in registrars[:10]:  # Limit to first 10 for context length
            context_parts.append(f"- {reg['name']} ({reg['id']}): {reg['seniority']} - {reg['specialty']}")
        if len(registrars) > 10:
            context_parts.append(f"... and {len(registrars) - 10} more registrars")
        context_parts.append("")

        # Recent shifts (sample)
        context_parts.append("SAMPLE SHIFTS:")
        for shift in shifts[:15]:  # Show first 15 shifts
            assigned_names = [a.get("name", "Unknown") for a in shift.get("assigned_registrars", [])]
            context_parts.append(
                f"- {shift['date']} {shift['shift_type']}: {', '.join(assigned_names) if assigned_names else 'UNASSIGNED'}"
            )
        if len(shifts) > 15:
            context_parts.append(f"... and {len(shifts) - 15} more shifts")
        context_parts.append("")

        # Fairness metrics
        if "fairness_metrics" in statistics:
            context_parts.append("FAIRNESS METRICS:")
            fairness = statistics["fairness_metrics"]

            if "total_shifts_per_registrar" in fairness:
                shifts_per_reg = fairness["total_shifts_per_registrar"]
                if shifts_per_reg:
                    avg_shifts = sum(shifts_per_reg.values()) / len(shifts_per_reg)
                    max_shifts = max(shifts_per_reg.values())
                    min_shifts = min(shifts_per_reg.values())
                    context_parts.append(f"- Average shifts per registrar: {avg_shifts:.1f}")
                    context_parts.append(f"- Range: {min_shifts} to {max_shifts} shifts")

            if "night_shifts_per_registrar" in fairness:
                night_shifts = fairness["night_shifts_per_registrar"]
                if night_shifts:
                    total_nights = sum(night_shifts.values())
                    context_parts.append(f"- Total night shifts distributed: {total_nights}")

        context_parts.append("")

        # Constraints
        context_parts.append("ACTIVE CONSTRAINTS:")
        hard = config["hard_constraints"]
        context_parts.append(f"- Max consecutive shifts: {hard.get('max_consecutive_shifts', 'N/A')}")
        context_parts.append(f"- Min rest hours: {hard.get('min_rest_hours', 'N/A')}")
        context_parts.append(f"- Max weekly hours: {hard.get('max_weekly_hours', 'N/A')}")
        context_parts.append(f"- Max night shifts per week: {hard.get('max_night_shifts_per_week', 'N/A')}")

        return "\n".join(context_parts)

    def chat(
        self,
        user_message: str,
        schedule_data: Dict,
        registrars: List[Dict],
        config: Dict
    ) -> str:
        """
        Maintain a conversation about the schedule

        This version maintains conversation history for more natural interaction
        """
        # Build context (only needed for first message or when context changes)
        context = self._build_context(schedule_data, registrars, config)

        # Add user message to history
        if not self.conversation_history:
            # First message - include full context
            self.conversation_history.append({
                "role": "user",
                "content": f"{context}\n\nUser: {user_message}"
            })
        else:
            # Subsequent messages - just the message
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

        try:
            # Call Claude with conversation history
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system="You are a helpful medical scheduling assistant. Answer questions about the schedule concisely and accurately.",
                messages=self.conversation_history
            )

            response_text = message.content[0].text

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            return response_text

        except Exception as e:
            return f"Error: {str(e)}"

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
