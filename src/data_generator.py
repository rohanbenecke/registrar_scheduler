"""
Generate realistic sample data for medical registrar scheduling demo
"""
from faker import Faker
import random
from datetime import datetime, timedelta
from typing import List, Dict
import json

fake = Faker()

class RegistrarGenerator:
    """Generate fake registrar data"""

    SPECIALTIES = [
        "General Medicine",
        "Cardiology",
        "Respiratory",
        "Gastroenterology",
        "Neurology",
        "Endocrinology",
        "Rheumatology"
    ]

    SENIORITY_LEVELS = ["Junior", "Mid-level", "Senior", "Principal"]

    def generate_registrars(self, num_registrars: int = 20) -> List[Dict]:
        """Generate a list of fake registrars"""
        registrars = []

        for i in range(num_registrars):
            registrar = {
                "id": f"REG{i+1:03d}",
                "name": fake.name(),
                "specialty": random.choice(self.SPECIALTIES),
                "seniority": random.choice(self.SENIORITY_LEVELS),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "contract_hours": random.choice([32, 40, 48]),  # Part-time or full-time
                "preferences": self._generate_preferences(),
                "skills": random.sample(self.SPECIALTIES, k=random.randint(1, 3)),
                "max_consecutive_shifts": random.randint(4, 6),
                "prefers_nights": random.random() < 0.2,  # 20% prefer nights
                "prefers_weekends": random.random() < 0.15,  # 15% prefer weekends
            }
            registrars.append(registrar)

        return registrars

    def _generate_preferences(self) -> Dict:
        """Generate random preferences for a registrar"""
        preferences = {
            "preferred_days": [],
            "avoid_days": [],
            "leave_requests": []
        }

        # Some people prefer specific days
        if random.random() < 0.3:
            preferences["preferred_days"] = random.sample(
                ["monday", "tuesday", "wednesday", "thursday", "friday"],
                k=random.randint(1, 2)
            )

        # Generate some leave requests (10-30% chance for each registrar)
        if random.random() < 0.3:
            num_leave_days = random.randint(1, 5)
            start_date = datetime.now() + timedelta(days=random.randint(7, 60))
            preferences["leave_requests"].append({
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": (start_date + timedelta(days=num_leave_days)).strftime("%Y-%m-%d"),
                "reason": random.choice(["Annual Leave", "Conference", "Study", "Personal"])
            })

        return preferences


class ShiftGenerator:
    """Generate shift schedules"""

    def generate_shifts_for_period(
        self,
        start_date: datetime,
        num_weeks: int,
        config: Dict
    ) -> List[Dict]:
        """Generate shifts for a given period based on config"""
        shifts = []
        current_date = start_date
        shift_id = 1

        for week in range(num_weeks):
            for day_offset in range(7):
                date = current_date + timedelta(days=day_offset)
                day_name = date.strftime("%A").lower()

                # Get shift types for this day from config
                weekly_template = config.get("weekly_template", {})
                shift_types_for_day = weekly_template.get(day_name, ["day", "evening", "night"])

                for shift_type in shift_types_for_day:
                    shift_config = config["shift_types"][shift_type]

                    # Calculate shift start and end times
                    start_time = date.replace(
                        hour=shift_config["start_hour"],
                        minute=0,
                        second=0
                    )

                    # Handle overnight shifts
                    end_hour = shift_config["end_hour"]
                    if end_hour < shift_config["start_hour"]:
                        end_time = (date + timedelta(days=1)).replace(
                            hour=end_hour,
                            minute=0,
                            second=0
                        )
                    else:
                        end_time = date.replace(
                            hour=end_hour,
                            minute=0,
                            second=0
                        )

                    shift = {
                        "id": f"SHIFT{shift_id:04d}",
                        "date": date.strftime("%Y-%m-%d"),
                        "day_of_week": day_name,
                        "shift_type": shift_type,
                        "start_time": start_time.strftime("%Y-%m-%d %H:%M"),
                        "end_time": end_time.strftime("%Y-%m-%d %H:%M"),
                        "duration_hours": shift_config["duration_hours"],
                        "required_staff": config["hard_constraints"]["min_registrars_per_shift"].get(
                            shift_type,
                            config["hard_constraints"]["min_registrars_per_shift"].get("day", 3)
                        ),
                        "desirability_score": shift_config["desirability_score"],
                        "assigned_registrars": []  # To be filled by scheduler
                    }
                    shifts.append(shift)
                    shift_id += 1

            current_date += timedelta(days=7)

        return shifts


def save_sample_data(registrars: List[Dict], shifts: List[Dict], output_dir: str = "data"):
    """Save generated data to JSON files"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "registrars.json"), "w") as f:
        json.dump(registrars, f, indent=2)

    with open(os.path.join(output_dir, "shifts.json"), "w") as f:
        json.dump(shifts, f, indent=2)

    print(f"Generated {len(registrars)} registrars and {len(shifts)} shifts")
    print(f"Saved to {output_dir}/")


if __name__ == "__main__":
    import yaml

    # Load config
    with open("config/constraints.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Generate data
    reg_gen = RegistrarGenerator()
    shift_gen = ShiftGenerator()

    registrars = reg_gen.generate_registrars(num_registrars=20)
    shifts = shift_gen.generate_shifts_for_period(
        start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        num_weeks=4,
        config=config
    )

    # Save
    save_sample_data(registrars, shifts)
