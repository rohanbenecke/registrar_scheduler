"""
Simple greedy scheduler with constraint checking
For demo purposes - can be upgraded to OR-Tools for production
"""
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import random


class ScheduleValidator:
    """Validates scheduling constraints"""

    def __init__(self, config: Dict):
        self.config = config
        self.hard_constraints = config["hard_constraints"]

    def is_valid_assignment(
        self,
        registrar: Dict,
        shift: Dict,
        current_schedule: Dict[str, List[Dict]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if assigning a registrar to a shift violates any hard constraints

        Returns: (is_valid, reason_if_invalid)
        """
        registrar_id = registrar["id"]
        registrar_shifts = current_schedule.get(registrar_id, [])

        # Check if registrar is on leave
        if self._is_on_leave(registrar, shift):
            return False, "On approved leave"

        # Check max consecutive shifts
        if self._exceeds_consecutive_shifts(shift, registrar_shifts, registrar):
            return False, f"Exceeds max consecutive shifts ({registrar['max_consecutive_shifts']})"

        # Check minimum rest hours between shifts
        if not self._has_sufficient_rest(shift, registrar_shifts):
            return False, f"Insufficient rest (need {self.hard_constraints['min_rest_hours']} hours)"

        # Check weekly hour limits
        if self._exceeds_weekly_hours(shift, registrar_shifts, registrar):
            return False, f"Exceeds weekly hour limit ({self.hard_constraints['max_weekly_hours']})"

        # Check night shift limits per week
        if shift["shift_type"] in ["night", "weekend_night"]:
            if self._exceeds_weekly_night_shifts(shift, registrar_shifts):
                return False, f"Exceeds weekly night shift limit ({self.hard_constraints['max_night_shifts_per_week']})"

        return True, None

    def _is_on_leave(self, registrar: Dict, shift: Dict) -> bool:
        """Check if registrar has leave during this shift"""
        shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()

        for leave in registrar["preferences"].get("leave_requests", []):
            start = datetime.strptime(leave["start_date"], "%Y-%m-%d").date()
            end = datetime.strptime(leave["end_date"], "%Y-%m-%d").date()
            if start <= shift_date <= end:
                return True
        return False

    def _exceeds_consecutive_shifts(
        self,
        shift: Dict,
        registrar_shifts: List[Dict],
        registrar: Dict
    ) -> bool:
        """Check if this shift would exceed max consecutive shifts"""
        if not registrar_shifts:
            return False

        shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()

        # Count consecutive shifts leading up to this one
        consecutive = 0
        for past_shift in sorted(registrar_shifts, key=lambda s: s["date"], reverse=True):
            past_date = datetime.strptime(past_shift["date"], "%Y-%m-%d").date()
            if (shift_date - past_date).days <= 1:
                consecutive += 1
            else:
                break

        return consecutive >= registrar["max_consecutive_shifts"]

    def _has_sufficient_rest(self, shift: Dict, registrar_shifts: List[Dict]) -> bool:
        """Check if registrar has sufficient rest before this shift"""
        if not registrar_shifts:
            return True

        shift_start = datetime.strptime(shift["start_time"], "%Y-%m-%d %H:%M")
        min_rest_hours = self.hard_constraints["min_rest_hours"]

        for past_shift in registrar_shifts:
            past_end = datetime.strptime(past_shift["end_time"], "%Y-%m-%d %H:%M")
            hours_between = (shift_start - past_end).total_seconds() / 3600

            # If shifts are close together, check rest requirement
            if 0 < hours_between < min_rest_hours:
                return False

        return True

    def _exceeds_weekly_hours(
        self,
        shift: Dict,
        registrar_shifts: List[Dict],
        registrar: Dict
    ) -> bool:
        """Check if this shift would exceed weekly hour limit"""
        shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()

        # Get all shifts in the same week
        week_start = shift_date - timedelta(days=shift_date.weekday())
        week_end = week_start + timedelta(days=6)

        weekly_hours = shift["duration_hours"]
        for past_shift in registrar_shifts:
            past_date = datetime.strptime(past_shift["date"], "%Y-%m-%d").date()
            if week_start <= past_date <= week_end:
                weekly_hours += past_shift["duration_hours"]

        return weekly_hours > self.hard_constraints["max_weekly_hours"]

    def _exceeds_weekly_night_shifts(
        self,
        shift: Dict,
        registrar_shifts: List[Dict]
    ) -> bool:
        """Check if this night shift would exceed weekly night shift limit"""
        shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()
        week_start = shift_date - timedelta(days=shift_date.weekday())
        week_end = week_start + timedelta(days=6)

        night_shifts = 1  # Count this shift
        for past_shift in registrar_shifts:
            past_date = datetime.strptime(past_shift["date"], "%Y-%m-%d").date()
            if week_start <= past_date <= week_end:
                if past_shift["shift_type"] in ["night", "weekend_night"]:
                    night_shifts += 1

        return night_shifts > self.hard_constraints["max_night_shifts_per_week"]


class SimpleScheduler:
    """Simple greedy scheduler for demo purposes"""

    def __init__(self, config: Dict):
        self.config = config
        self.validator = ScheduleValidator(config)

    def generate_schedule(
        self,
        registrars: List[Dict],
        shifts: List[Dict]
    ) -> Tuple[List[Dict], Dict]:
        """
        Generate a schedule using a greedy algorithm

        Returns: (scheduled_shifts, statistics)
        """
        # Initialize schedule tracking
        schedule = defaultdict(list)  # registrar_id -> [shifts]
        scheduled_shifts = []
        statistics = {
            "total_shifts": len(shifts),
            "scheduled_shifts": 0,
            "unscheduled_shifts": 0,
            "constraint_violations": [],
            "fairness_metrics": {}
        }

        # Sort shifts by date and time
        sorted_shifts = sorted(shifts, key=lambda s: s["start_time"])

        # Try to assign registrars to each shift
        for shift in sorted_shifts:
            required_staff = shift["required_staff"]
            assigned = []

            # Score each registrar for this shift
            candidates = []
            for registrar in registrars:
                is_valid, reason = self.validator.is_valid_assignment(
                    registrar, shift, schedule
                )

                if is_valid:
                    score = self._score_assignment(registrar, shift, schedule)
                    candidates.append((registrar, score))

            # Sort by score (higher is better) and assign top candidates
            candidates.sort(key=lambda x: x[1], reverse=True)

            for registrar, score in candidates[:required_staff]:
                shift_copy = shift.copy()
                shift_copy["assigned_registrars"] = shift_copy.get("assigned_registrars", [])
                shift_copy["assigned_registrars"].append({
                    "id": registrar["id"],
                    "name": registrar["name"],
                    "seniority": registrar["seniority"]
                })
                schedule[registrar["id"]].append(shift_copy)
                assigned.append(registrar["id"])

            # Update shift with assignments
            shift["assigned_registrars"] = [
                {"id": reg_id, "name": next(r["name"] for r in registrars if r["id"] == reg_id)}
                for reg_id in assigned
            ]
            scheduled_shifts.append(shift)

            if len(assigned) >= required_staff:
                statistics["scheduled_shifts"] += 1
            else:
                statistics["unscheduled_shifts"] += 1
                statistics["constraint_violations"].append({
                    "shift_id": shift["id"],
                    "shift_type": shift["shift_type"],
                    "date": shift["date"],
                    "required": required_staff,
                    "assigned": len(assigned),
                    "reason": "Insufficient eligible registrars"
                })

        # Calculate fairness metrics
        statistics["fairness_metrics"] = self._calculate_fairness(schedule, registrars)

        return scheduled_shifts, statistics

    def _score_assignment(
        self,
        registrar: Dict,
        shift: Dict,
        schedule: Dict[str, List[Dict]]
    ) -> float:
        """
        Score how good this assignment is (higher = better)
        Considers soft constraints and preferences
        """
        score = 0.0

        # Prefer registrars with fewer total shifts (fairness)
        total_shifts = len(schedule.get(registrar["id"], []))
        score -= total_shifts * 2

        # Prefer registrars who like this type of shift
        if shift["shift_type"] in ["night", "weekend_night"] and registrar.get("prefers_nights"):
            score += 10
        if "weekend" in shift["shift_type"] and registrar.get("prefers_weekends"):
            score += 8

        # Prefer registrars with matching specialty (if needed)
        score += random.uniform(0, 1)  # Add small randomness for variety

        # Check preferred days
        if shift["day_of_week"] in registrar["preferences"].get("preferred_days", []):
            score += 5

        # Penalize if this is a night shift and they just worked
        registrar_shifts = schedule.get(registrar["id"], [])
        if registrar_shifts and shift["shift_type"] in ["night", "weekend_night"]:
            last_shift = registrar_shifts[-1]
            if last_shift["shift_type"] in ["night", "weekend_night"]:
                score -= 15  # Avoid back-to-back nights

        return score

    def _calculate_fairness(
        self,
        schedule: Dict[str, List[Dict]],
        registrars: List[Dict]
    ) -> Dict:
        """Calculate fairness metrics across registrars"""
        metrics = {
            "total_shifts_per_registrar": {},
            "night_shifts_per_registrar": {},
            "weekend_shifts_per_registrar": {},
            "total_hours_per_registrar": {}
        }

        for registrar in registrars:
            reg_id = registrar["id"]
            shifts = schedule.get(reg_id, [])

            metrics["total_shifts_per_registrar"][reg_id] = len(shifts)

            night_shifts = sum(
                1 for s in shifts if s["shift_type"] in ["night", "weekend_night"]
            )
            metrics["night_shifts_per_registrar"][reg_id] = night_shifts

            weekend_shifts = sum(
                1 for s in shifts if "weekend" in s["shift_type"]
            )
            metrics["weekend_shifts_per_registrar"][reg_id] = weekend_shifts

            total_hours = sum(s["duration_hours"] for s in shifts)
            metrics["total_hours_per_registrar"][reg_id] = total_hours

        return metrics


def explain_assignment(registrar: Dict, shift: Dict, schedule: Dict) -> str:
    """Generate human-readable explanation for why a registrar was assigned to a shift"""
    reasons = []

    # Check what made this a good assignment
    if shift["shift_type"] in ["night", "weekend_night"] and registrar.get("prefers_nights"):
        reasons.append("prefers night shifts")

    if "weekend" in shift["shift_type"] and registrar.get("prefers_weekends"):
        reasons.append("prefers weekend work")

    if shift["day_of_week"] in registrar["preferences"].get("preferred_days", []):
        reasons.append(f"requested to work {shift['day_of_week']}s")

    total_shifts = len(schedule.get(registrar["id"], []))
    reasons.append(f"had {total_shifts} shifts assigned (fair distribution)")

    if not reasons:
        return "Available and qualified for this shift"

    return f"Assigned because they {', '.join(reasons)}"
