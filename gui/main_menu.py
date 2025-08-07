# builds the GUI main menu
import tkinter as tk
from gui.app_launcher_ui import build_app_launcher_ui
from gui.desktop_organiser_ui import build_desktop_organiser_ui
from gui.summariser_ui import build_summariser_ui

def build_main_menu(root):
    # Clear the root in case it's being reused
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="DeskPilot Main Menu", font=("Calibri", 16)).pack(pady=20) # placeholder font, can maybe choose a better font later

    #placeholders for simple window generation:
    tk.Button(root, text="App Launcher", width=20, command=lambda: build_app_launcher_ui(root)).pack(pady=5)
    tk.Button(root, text="Desktop Organiser", width=20, command=lambda: build_desktop_organiser_ui(root)).pack(pady=5)
    tk.Button(root, text="File Summariser", width=20, command=lambda: build_summariser_ui(root)).pack(pady=5)

    # QUIT BUTTON
    tk.Button(root, text="Quit", command=root.quit).pack(pady=20)
