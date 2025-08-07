# GUI for summariser
import tkinter as tk
from tkinter import filedialog, messagebox # what are these used for (find out)?
import openai
import fitz
import docx

#^^^ placeholder for importing the logic module

def build_summariser_ui(root):
    # Clear existing widgets from root window
    for widget in root.winfo_children():
        widget.destroy()

# BACK BUTTON
#from gui.main_menu import build_main_menu
#tk.Button(root, text="Back to Menu", command=lambda: build_main_menu(root)).pack(pady=20)