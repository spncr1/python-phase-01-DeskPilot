# GUI for app launcher
import tkinter as tk
from tkinter import messagebox
#from gui.main_menu import build_main_menu
from core.app_launcher import open_chrome, open_vscode, open_safari, open_notes

# when the button is clicked from main menu, this is what will be shown, giving user access to some basic functions defined below using GUI logic
def build_app_launcher_ui(root):
    # Clear existing widgets from root window
    for widget in root.winfo_children():
        widget.destroy()

    # Title and Instructions
    tk.Label(root, text="App Launcher", font=("Calibri", 16)).pack(pady=10)
    tk.Label(root, text="You can ask me to...", font=("Calibri", 16)).pack(pady=10)

    # Example CMDs
    tk.Button(root, text="Open Chrome", command=open_chrome).pack(pady=5)
    tk.Button(root, text="Open Visual Studio Code", command=open_vscode).pack(pady=5)
    tk.Button(root, text="Open Safari", command=open_safari).pack(pady=5)
    tk.Button(root, text="Open Notes", command=open_notes).pack(pady=5)

    # BACK BUTTON
    from gui.main_menu import build_main_menu
    tk.Button(root, text="Back to Menu", command=lambda: build_main_menu(root)).pack(pady=20)