#!/usr/bin/env python3
"""
Standalone Settings GUI Launcher
Quick way to configure API keys and settings without CLI
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Launch the settings GUI"""
    print("Excel Seedream Generator - Settings")
    print("=" * 50)

    try:
        # Check tkinter availability
        try:
            import tkinter as tk
            print("GUI framework available")
        except ImportError:
            print("Error: tkinter not available")
            print("Please install tkinter or edit .env file manually")
            return

        # Import and launch settings GUI
        try:
            from gui.settings_gui import SettingsGUI
            print("Settings module loaded")
        except ImportError as e:
            print(f"Error importing settings module: {e}")
            print("Make sure you're in the project directory")
            return

        print("Launching settings GUI...")
        print("")

        # Create and run GUI
        gui = SettingsGUI()
        gui.run()

        print("Settings GUI closed")

    except KeyboardInterrupt:
        print("\nCancelled by user")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("You can manually edit .env file:")
        print("   1. Copy .env.template to .env")
        print("   2. Edit .env with your API keys")


if __name__ == "__main__":
    main()