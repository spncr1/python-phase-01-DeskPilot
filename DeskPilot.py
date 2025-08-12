#!/usr/bin/env python3
"""
DeskPilot - Main Tkinter Application
Simple GUI-based desktop assistant with app launcher functionality
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add project directories to path
project_root = Path(__file__).parent
sys.path.extend([
    str(project_root),
    str(project_root / "voice"),
    str(project_root / "core"),
    str(project_root / "gui")
])

from gui.main_menu import MainMenuGUI

def main():
    """Launch the DeskPilot GUI application"""
    root = tk.Tk()
    root.title("DeskPilot")
    root.geometry("500x600")
    root.resizable(False, False)

    # Set a clean background color
    root.configure(bg='#f0f0f0')

    # Create and start the main menu
    app = MainMenuGUI(root)

    # Start the tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()