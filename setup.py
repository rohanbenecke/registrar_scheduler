"""
Quick setup script for the Medical Registrar Scheduler demo
"""
import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is adequate"""
    if sys.version_info < (3, 11):
        print("[WARNING] Python 3.11+ recommended. You have:", sys.version)
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("[OK] Python version:", sys.version.split()[0])


def setup_directories():
    """Create necessary directories"""
    dirs = ["data", "config", "src"]
    for dir_name in dirs:
        path = Path(dir_name)
        path.mkdir(exist_ok=True)
    print("[OK] Directories created")


def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        if env_example.exists():
            print("[INFO] .env file not found")
            print("   Creating .env from .env.example...")
            env_file.write_text(env_example.read_text())
            print("[OK] .env file created")
            print("   [REMINDER] Add your ANTHROPIC_API_KEY!")
        else:
            print("[ERROR] .env.example not found")
    else:
        print("[OK] .env file exists")

        # Check if API key is set
        env_content = env_file.read_text()
        if "your_api_key_here" in env_content or "ANTHROPIC_API_KEY=" not in env_content:
            print("   [REMINDER] Set your ANTHROPIC_API_KEY in .env!")


def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import streamlit
        import anthropic
        import yaml
        import faker
        print("[OK] Core dependencies installed")
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependencies: {e}")
        print("   Run: pip install -r requirements.txt")
        return False


def generate_sample_data():
    """Generate sample data if it doesn't exist"""
    data_dir = Path("data")
    registrars_file = data_dir / "registrars.json"
    shifts_file = data_dir / "shifts.json"

    if registrars_file.exists() and shifts_file.exists():
        print("[OK] Sample data already exists")
        return

    print("[INFO] Generating sample data...")
    try:
        # Import after ensuring dependencies
        import sys
        sys.path.insert(0, str(Path(__file__).parent))

        from src.data_generator import RegistrarGenerator, ShiftGenerator, save_sample_data
        import yaml
        from datetime import datetime

        # Load config
        with open("config/constraints.yaml", "r") as f:
            config = yaml.safe_load(f)

        # Generate
        reg_gen = RegistrarGenerator()
        shift_gen = ShiftGenerator()

        registrars = reg_gen.generate_registrars(num_registrars=20)
        shifts = shift_gen.generate_shifts_for_period(
            start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            num_weeks=4,
            config=config
        )

        save_sample_data(registrars, shifts, output_dir="data")
        print("[OK] Sample data generated")

    except Exception as e:
        print(f"[ERROR] Error generating sample data: {e}")
        print("   You can generate it later by running: python src/data_generator.py")


def main():
    """Run setup"""
    print("=" * 60)
    print("Medical Registrar Scheduler - Setup")
    print("=" * 60)
    print()

    check_python_version()
    setup_directories()
    check_env_file()

    print()
    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)

    if not check_dependencies():
        print("1. Install dependencies:")
        print("   pip install -r requirements.txt")
        print()
        print("2. Run this setup script again:")
        print("   python setup.py")
    else:
        generate_sample_data()
        print()
        print("[SUCCESS] Ready to run!")
        print()
        print("1. Make sure your .env file has a valid ANTHROPIC_API_KEY")
        print()
        print("2. Start the demo:")
        print("   streamlit run app.py")
        print()
        print("3. Open your browser to: http://localhost:8501")
        print()
        print("See README.md for more information")

    print()


if __name__ == "__main__":
    main()
