# GUI for desktop organiser
import tkinter as tk
from tkinter import messagebox
import os # why do i need this?
#from core.organiser import organise_deskop
#^^^ placeholder for importing the logic module

def build_desktop_organiser_ui(root):
    # Clear existing widgets from root window
    for widget in root.winfo_children():
        widget.destroy()

# BACK BUTTON
#from gui.main_menu import (build_main_menu)
#tk.Button(root, text="Back to Menu", command=lambda: build_main_menu(root)).pack(pady=20)