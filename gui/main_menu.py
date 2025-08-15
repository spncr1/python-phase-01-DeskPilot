import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sys
from pathlib import Path

from numpy.ma.core import append

from gui.app_launcher_ui import AppLauncherGUI
from gui.file_summariser_ui import FileSummariserGUI

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import voice and GPT modules when implementing speech functionality
from voice.speaker import speak
from voice.listener import listen_command
from gpt import GPTHandler


class MainMenuGUI:
    def __init__(self, root):
        self.root = root
        self.setup_main_menu()

    def setup_main_menu(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main menu content
        title_label = tk.Label(
            self.root,
            text="DeskPilot",
            font=("Arial", 32, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(50, 30))

        subtitle_label = tk.Label(
            self.root,
            text="Your Desktop Assistant (LOGO GOES BELOW)",
            font=("Arial", 16),
            bg='#f0f0f0',
            fg='#666666'
        )
        subtitle_label.pack(pady=(0, 40))

        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(expand=True)

        button_style = {
            'width': 20,
            'height': 2,
            'font': ('Arial', 14),
            'bg': '#ffffff',
            'fg': '#333333',
            'relief': 'raised',
            'borderwidth': 2
        }

        # App Launcher Button
        launcher_btn = tk.Button(
            button_frame,
            text="App Launcher",
            command=self.open_app_launcher,
            **button_style
        )
        launcher_btn.pack(pady=10)

        # Desktop Organiser Button
        voice_btn = tk.Button(
            button_frame,
            text="Desktop Organiser",
            command=self.open_desktop_organiser,
            **button_style
        )
        voice_btn.pack(pady=10)

        # File Summariser Button
        settings_btn = tk.Button(
            button_frame,
            text="File Summariser",
            command=self.open_file_summariser,
            **button_style
        )
        settings_btn.pack(pady=10)

        # Quit Button
        quit_btn = tk.Button(
            button_frame,
            text="Quit",
            command=self.root.quit,
            **button_style
        )
        quit_btn.pack(pady=10)

    def open_app_launcher(self):
        AppLauncherGUI(self.root, self)

    def open_desktop_organiser(self):
        messagebox.showinfo("Coming Soon", "Functionality coming soon!")

    def open_file_summariser(self):
        FileSummariserGUI(self.root, self)