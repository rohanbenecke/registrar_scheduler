"""
Stress Testing Suite for Medical Registrar Scheduler

Tests the scheduler under various conditions:
- Different scales (registrars, shifts, time periods)
- Restrictive constraints
- Edge cases
- Performance benchmarks
"""
import time
import yaml
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / "src"))

from data_generator import RegistrarGenerator, ShiftGenerator
from scheduler import SimpleScheduler


class StressTest:
    """Run comprehensive stress tests on the scheduler"""

    def __init__(self):
        self.results = []
        with open("config/constraints.yaml", "r") as f:
            self.base_config = yaml.safe_load(f)

    def run_all_tests(self):
        """Run all stress tests"""
        print("=" * 80)
        print("MEDICAL REGISTRAR SCHEDULER - STRESS TEST SUITE")
        print("=" * 80)
        print()

        # Scale tests
        self.test_scale_registrars()
        self.test_scale_time_periods()

        # Constraint tests
        self.test_restrictive_constraints()
        self.test_high_coverage_requirements()

        # Edge cases
        self.test_insufficient_staff()
        self.test_many_leave_requests()
        self.test_all_prefer_nights()

        # Performance benchmarks
        self.run_performance_benchmarks()

        # Generate report
        self.generate_report()

    def test_scale_registrars(self):
        """Test with different numbers of registrars"""
        print("\n" + "=" * 80)
        print("TEST 1: SCALING - Number of Registrars")
        print("=" * 80)

        scales = [5, 10, 20, 40, 60, 80, 100]

        for num_registrars in scales:
            print(f"\n[Testing with {num_registrars} registrars...]")
            result = self._run_test(
                test_name=f"Scale: {num_registrars} registrars",
                num_registrars=num_registrars,
                num_weeks=2,  # Keep weeks constant
                config=self.base_config.copy()
            )
            self._print_result(result)

    def test_scale_time_periods(self):
        """Test with different time periods"""
        print("\n" + "=" * 80)
        print("TEST 2: SCALING - Time Periods")
        print("=" * 80)

        periods = [1, 2, 4, 8, 12, 26, 52]  # Up to 1 year

        for num_weeks in periods:
            print(f"\n[Testing with {num_weeks} weeks...]")
            result = self._run_test(
                test_name=f"Scale: {num_weeks} weeks",
                num_registrars=20,  # Keep registrars constant
                num_weeks=num_weeks,
                config=self.base_config.copy()
            )
            self._print_result(result)

    def test_restrictive_constraints(self):
        """Test with very restrictive constraints"""
        print("\n" + "=" * 80)
        print("TEST 3: RESTRICTIVE CONSTRAINTS")
        print("=" * 80)

        # Very restrictive hours
        restrictive_config = self.base_config.copy()
        restrictive_config["hard_constraints"]["max_weekly_hours"] = 30
        restrictive_config["hard_constraints"]["max_consecutive_shifts"] = 2
        restrictive_config["hard_constraints"]["max_night_shifts_per_week"] = 1
        restrictive_config["hard_constraints"]["min_rest_hours"] = 16

        print("\n[Testing with restrictive constraints:]")
        print(f"  - Max weekly hours: 30 (vs 48 normal)")
        print(f"  - Max consecutive shifts: 2 (vs 5 normal)")
        print(f"  - Max night shifts/week: 1 (vs 3 normal)")
        print(f"  - Min rest hours: 16 (vs 11 normal)")

        result = self._run_test(
            test_name="Restrictive constraints",
            num_registrars=30,  # More registrars to try to meet requirements
            num_weeks=4,
            config=restrictive_config
        )
        self._print_result(result)

    def test_high_coverage_requirements(self):
        """Test with high coverage requirements"""
        print("\n" + "=" * 80)
        print("TEST 4: HIGH COVERAGE REQUIREMENTS")
        print("=" * 80)

        high_coverage_config = self.base_config.copy()
        high_coverage_config["hard_constraints"]["min_registrars_per_shift"] = {
            "day": 5,  # vs 3 normal
            "evening": 4,  # vs 2 normal
            "night": 4,  # vs 2 normal
            "weekend_day": 4,  # vs 2 normal
            "weekend_night": 3  # vs 2 normal
        }

        print("\n[Testing with high coverage requirements:]")
        print(f"  - Day shifts: 5 registrars (vs 3 normal)")
        print(f"  - Evening shifts: 4 registrars (vs 2 normal)")
        print(f"  - Night shifts: 4 registrars (vs 2 normal)")

        result = self._run_test(
            test_name="High coverage requirements",
            num_registrars=25,
            num_weeks=4,
            config=high_coverage_config
        )
        self._print_result(result)

    def test_insufficient_staff(self):
        """Test edge case: Not enough staff for coverage"""
        print("\n" + "=" * 80)
        print("TEST 5: EDGE CASE - Insufficient Staff")
        print("=" * 80)

        print("\n[Testing with too few registrars for coverage requirements...]")

        result = self._run_test(
            test_name="Insufficient staff",
            num_registrars=5,  # Way too few
            num_weeks=4,
            config=self.base_config.copy()
        )
        self._print_result(result)

    def test_many_leave_requests(self):
        """Test edge case: Many registrars on leave"""
        print("\n" + "=" * 80)
        print("TEST 6: EDGE CASE - Many Leave Requests")
        print("=" * 80)

        print("\n[Testing with 50% of registrars having leave requests...]")

        # Generate registrars with many leave requests
        reg_gen = RegistrarGenerator()
        registrars = reg_gen.generate_registrars(num_registrars=20)

        # Add leave requests to 50% of registrars
        start_date = datetime.now()
        for i, reg in enumerate(registrars):
            if i % 2 == 0:  # 50% of registrars
                reg["preferences"]["leave_requests"] = [{
                    "start_date": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "end_date": (start_date + timedelta(days=14)).strftime("%Y-%m-%d"),
                    "reason": "Annual Leave"
                }]

        result = self._run_test_with_data(
            test_name="Many leave requests (50%)",
            registrars=registrars,
            num_weeks=4,
            config=self.base_config.copy()
        )
        self._print_result(result)

    def test_all_prefer_nights(self):
        """Test edge case: All registrars prefer night shifts"""
        print("\n" + "=" * 80)
        print("TEST 7: EDGE CASE - All Prefer Night Shifts")
        print("=" * 80)

        print("\n[Testing when everyone prefers night shifts...]")

        # Generate registrars who all prefer nights
        reg_gen = RegistrarGenerator()
        registrars = reg_gen.generate_registrars(num_registrars=20)

        for reg in registrars:
            reg["prefers_nights"] = True

        result = self._run_test_with_data(
            test_name="All prefer nights",
            registrars=registrars,
            num_weeks=4,
            config=self.base_config.copy()
        )
        self._print_result(result)

    def run_performance_benchmarks(self):
        """Run performance benchmarks"""
        print("\n" + "=" * 80)
        print("TEST 8: PERFORMANCE BENCHMARKS")
        print("=" * 80)

        benchmarks = [
            ("Small (10 reg, 1 week)", 10, 1),
            ("Medium (20 reg, 4 weeks)", 20, 4),
            ("Large (50 reg, 8 weeks)", 50, 8),
            ("XLarge (100 reg, 12 weeks)", 100, 12),
        ]

        for name, num_registrars, num_weeks in benchmarks:
            print(f"\n[Benchmarking: {name}]")
            result = self._run_test(
                test_name=f"Benchmark: {name}",
                num_registrars=num_registrars,
                num_weeks=num_weeks,
                config=self.base_config.copy()
            )
            self._print_result(result)

    def _run_test(self, test_name, num_registrars, num_weeks, config):
        """Run a single test"""
        # Generate data
        reg_gen = RegistrarGenerator()
        registrars = reg_gen.generate_registrars(num_registrars=num_registrars)

        return self._run_test_with_data(test_name, registrars, num_weeks, config)

    def _run_test_with_data(self, test_name, registrars, num_weeks, config):
        """Run a test with provided registrar data"""
        shift_gen = ShiftGenerator()
        shifts = shift_gen.generate_shifts_for_period(
            start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            num_weeks=num_weeks,
            config=config
        )

        # Run scheduler and measure time
        scheduler = SimpleScheduler(config)
        start_time = time.time()

        try:
            scheduled_shifts, statistics = scheduler.generate_schedule(registrars, shifts)
            execution_time = time.time() - start_time
            success = True
            error = None
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            error = str(e)
            scheduled_shifts = []
            statistics = {}

        # Calculate results
        result = {
            "test_name": test_name,
            "success": success,
            "error": error,
            "execution_time": execution_time,
            "num_registrars": len(registrars),
            "num_weeks": num_weeks,
            "total_shifts": len(shifts),
            "scheduled_shifts": statistics.get("scheduled_shifts", 0),
            "unscheduled_shifts": statistics.get("unscheduled_shifts", 0),
            "violations": len(statistics.get("constraint_violations", [])),
            "coverage_rate": (
                statistics.get("scheduled_shifts", 0) / len(shifts) * 100
                if len(shifts) > 0 else 0
            ),
            "fairness_metrics": statistics.get("fairness_metrics", {})
        }

        self.results.append(result)
        return result

    def _print_result(self, result):
        """Print test result"""
        if result["success"]:
            print(f"\n  [OK] Test completed in {result['execution_time']:.2f}s")
        else:
            print(f"\n  [FAIL] Test failed: {result['error']}")
            print(f"    Execution time: {result['execution_time']:.2f}s")

        print(f"  - Total shifts: {result['total_shifts']}")
        print(f"  - Scheduled: {result['scheduled_shifts']} ({result['coverage_rate']:.1f}%)")
        print(f"  - Unscheduled: {result['unscheduled_shifts']}")
        print(f"  - Violations: {result['violations']}")

        # Fairness metrics summary
        if result["fairness_metrics"]:
            fairness = result["fairness_metrics"]
            if "total_shifts_per_registrar" in fairness:
                shifts_per_reg = fairness["total_shifts_per_registrar"]
                if shifts_per_reg:
                    values = list(shifts_per_reg.values())
                    print(f"  - Shifts per registrar: avg={sum(values)/len(values):.1f}, "
                          f"min={min(values)}, max={max(values)}")

    def generate_report(self):
        """Generate final report"""
        print("\n" + "=" * 80)
        print("STRESS TEST SUMMARY")
        print("=" * 80)

        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])

        print(f"\nTotal tests run: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")

        # Performance summary
        print("\n--- PERFORMANCE SUMMARY ---")
        print(f"Fastest test: {min(r['execution_time'] for r in self.results):.2f}s")
        print(f"Slowest test: {max(r['execution_time'] for r in self.results):.2f}s")
        print(f"Average time: {sum(r['execution_time'] for r in self.results) / total_tests:.2f}s")

        # Coverage summary
        print("\n--- COVERAGE SUMMARY ---")
        avg_coverage = sum(r['coverage_rate'] for r in self.results) / total_tests
        print(f"Average coverage rate: {avg_coverage:.1f}%")

        best_coverage = max(self.results, key=lambda r: r['coverage_rate'])
        worst_coverage = min(self.results, key=lambda r: r['coverage_rate'])

        print(f"\nBest coverage: {best_coverage['coverage_rate']:.1f}% ({best_coverage['test_name']})")
        print(f"Worst coverage: {worst_coverage['coverage_rate']:.1f}% ({worst_coverage['test_name']})")

        # Recommendations
        print("\n--- RECOMMENDATIONS ---")

        if avg_coverage < 90:
            print("[WARNING] Average coverage below 90% - consider:")
            print("  - Increasing number of registrars")
            print("  - Relaxing some constraints")
            print("  - Reducing coverage requirements")
        else:
            print("[OK] Good average coverage rate")

        # Find performance bottlenecks
        slow_tests = [r for r in self.results if r['execution_time'] > 5.0]
        if slow_tests:
            print(f"\n[WARNING] {len(slow_tests)} tests took > 5 seconds:")
            for test in slow_tests:
                print(f"  - {test['test_name']}: {test['execution_time']:.2f}s")
            print("\nConsider upgrading to OR-Tools for better performance with large datasets")
        else:
            print("\n[OK] All tests completed in reasonable time")

        # Scale limits
        print("\n--- SCALE LIMITS ---")
        largest_success = max(
            (r for r in self.results if r['success'] and r['coverage_rate'] > 90),
            key=lambda r: r['num_registrars'] * r['num_weeks'],
            default=None
        )

        if largest_success:
            print(f"Largest successful test (>90% coverage):")
            print(f"  - {largest_success['num_registrars']} registrars")
            print(f"  - {largest_success['num_weeks']} weeks")
            print(f"  - {largest_success['total_shifts']} total shifts")
            print(f"  - {largest_success['execution_time']:.2f}s execution time")

        # Save detailed results
        output_file = "stress_test_results.json"
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n[OK] Detailed results saved to: {output_file}")
        print()


def main():
    """Run stress tests"""
    tester = StressTest()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
