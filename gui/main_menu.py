# builds the GUI main menu

import tkinter as tk
#from gui.app_launcher_ui import #(function) - placeholder
#from gui.organise_ui import #(function) - placeholder
#from gui.summarise_ui import #(function) - placeholder

def build_main_menu(root):
    # Clear the root in case it's being reused
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="DeskPilot - Main Menu", font=("Arial", 16)).pack(pady=20) # placeholder font, can maybe choose a better font later

    #placeholders for simple window generation:
    #tk.Button(root, text="Desktop Organiser", width=20, command=organise_ui).pack(pady=5)
    #tk.Button(root, text="App Launcher", width=20, command=app_launcher_ui).pack(pady=5)
    #tk.Button(root, text="File Summariser", width=20, command=summarise_ui).pack(pady=5)
