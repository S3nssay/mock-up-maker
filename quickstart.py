#!/usr/bin/env python3
"""
Quick Start Script for Mock Up Maker

This script demonstrates basic usage and helps you get started quickly.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from processors.excel_processor import ExcelProcessor


def create_sample_excel():
    """Create a sample Excel file to get started"""
    print("Creating sample Excel file...")

    try:
        import pandas as pd

        # Create output directory if it doesn't exist
        examples_dir = Path("examples")
        examples_dir.mkdir(exist_ok=True)

        # Create sample data directly
        sample_data = {
            "product_name": ["Elegant Black Evening Dress", "Summer Beach Sandals", "Professional Blazer"],
            "prompt": [
                "Professional model wearing elegant black dress in modern office",
                "Model showcasing comfortable beach sandals on sandy beach",
                "Business professional wearing navy blazer in corporate setting"
            ],
            "brand_name": ["StyleCorp", "BeachWear Co", "BusinessPro"],
            "product_price": ["$149.99", "$49.99", "$299.99"],
            "product_url": [
                "https://stylecorp.com/dress-001",
                "https://beachwear.com/sandals-summer",
                "https://businesspro.com/blazer-navy"
            ],
            "product_url_1": ["", "", ""],
            "product_url_2": ["", "", ""],
            "product_url_3": ["", "", ""],
            "model_url": ["", "", ""],
            "add_product_overlay": [True, True, True],
            "overlay_position": ["bottom-left", "bottom-right", "top-left"]
        }

        # Create DataFrame and save to Excel
        df = pd.DataFrame(sample_data)
        output_path = examples_dir / "sample_products.xlsx"
        df.to_excel(str(output_path), index=False)

        print(f"Sample Excel created: {output_path}")
        print("\nNext steps:")
        print("1. Edit the sample Excel file with your product data")
        print("2. Set up your API keys in .env file")
        print("3. Run: python src/main.py process examples/sample_products.xlsx")

        return str(output_path)

    except Exception as e:
        print(f"Error creating sample: {str(e)}")
        return None


def check_environment():
    """Check if environment is properly configured"""
    print("Checking environment...")

    issues = []

    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        issues.append(".env file not found. Copy .env.template to .env and configure your API keys.")
    else:
        print(".env file found")

    # Check Python version
    if sys.version_info < (3, 9):
        issues.append(f"Python {sys.version_info.major}.{sys.version_info.minor} detected. Python 3.9+ required.")
    else:
        print(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Check required packages
    required_packages = [
        ("pandas", "pandas"),
        ("requests", "requests"),
        ("click", "click"),
        ("rich", "rich"),
        ("Pillow", "PIL")
    ]
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"{package_name} installed")
        except ImportError:
            issues.append(f"{package_name} not installed. Run: pip install -r requirements.txt")

    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  {issue}")
        return False

    print("\nEnvironment looks good!")
    return True


def main():
    """Main quickstart function"""
    print("=" * 60)
    print("MOCK UP MAKER - QUICK START")
    print("=" * 60)

    # Check environment
    if not check_environment():
        print("\nPlease fix the environment issues above before continuing.")
        sys.exit(1)

    print("\n" + "="*60)

    # Create sample Excel
    sample_file = create_sample_excel()

    if sample_file:
        print("\n" + "="*60)
        print("QUICK SETUP & USAGE")
        print("="*60)

        print("\n1. Configure API keys (GUI):")
        print("   python settings_launcher.py")
        print("   OR: python src/main.py settings")

        print("\n2. Configure API keys (manual):")
        print("   python src/main.py config-manager --create-env")
        print("   # Then edit .env file with your API keys")

        print("\n3. Validate configuration:")
        print("   python src/main.py validate-config")

        print("\n4. Test with sample data (dry run):")
        print(f"   python src/main.py process {sample_file} --dry-run")

        print("\n5. Generate images:")
        print(f"   python src/main.py process {sample_file} --output-dir ./my_campaign")

        print("\n6. Advanced processing:")
        print(f"   python src/main.py process {sample_file} --enable-overlays --concurrent 3")

        print("\n" + "="*60)
        print("SETTINGS & CONFIGURATION:")
        print("   python settings_launcher.py  # Easy GUI setup")
        print("   python src/main.py settings  # Settings via CLI")
        print("   python src/main.py config-manager --help  # Config management")
        print("\nFor detailed help, see USAGE_GUIDE.md or README.md")
        print("="*60)


if __name__ == "__main__":
    main()