import tkinter as tk
from gui.main_menu import MainMenuGUI
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))


def main():
    """Main entry point for DeskPilot"""
    try:
        # Just create and start the app
        from gui.main_menu import MainMenuGUI
        app = MainMenuGUI()
        app.run()
    except Exception as e:
        print(f"Error starting DeskPilot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()