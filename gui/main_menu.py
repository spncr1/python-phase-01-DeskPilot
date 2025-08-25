import tkinter as tk
from tkinterweb import HtmlFrame
import sys
from pathlib import Path
import webview
import threading
import subprocess
import platform
import psutil

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import your module GUIs
from gui.app_launcher_ui import AppLauncherHTMLGUI
from gui.file_summariser_ui import FileSummariserGUI
from core.desktop_organiser import DesktopOrganiserUI
from core.app_launcher import (
    open_chrome, open_safari, open_firefox, open_vscode, open_spotify,
    open_notes, open_terminal, open_calculator, open_calendar,
    quit_chrome, quit_safari, quit_vscode, quit_spotify, quit_notes,
    quit_terminal, quit_calculator, quit_mail, quit_calendar
)

class MainMenuGUI:
    def __init__(self):
        self.window = None

    def run(self):
        """Run the application using webview"""
        import webview

        # Create an API object that will be exposed to JavaScript
        class API:
            def __init__(self, main_app):
                self.main_app = main_app

            def execute_command(self, command, *args):
                """Execute a command from JavaScript"""
                if hasattr(self.main_app, command):
                    func = getattr(self.main_app, command)
                    return func(*args)
                return f"Command '{command}' not found"

        # Create and show the webview window
        self.window = webview.create_window(
            'DeskPilot',
            'deskpilot_ui.html',
            width=1200,
            height=800,
            js_api=API(self),  # Pass the API instance to JavaScript
            text_select=False,
        )

        # Start the webview with minimal output
        webview.start(debug=True)  # Keep debug=True temporarily to see any JS errors

    # App Launcher Commands
    def open_app(self, app_name):
        """Open an application by name"""
        try:
            if app_name == 'chrome':
                open_chrome()
            elif app_name == 'safari':
                open_safari()
            elif app_name == 'firefox':
                open_firefox()
            elif app_name == 'vscode':
                open_vscode()
            elif app_name == 'spotify':
                open_spotify()
            elif app_name == 'notes':
                open_notes()
            elif app_name == 'terminal':
                open_terminal()
            elif app_name == 'calculator':
                open_calculator()
            elif app_name == 'calendar':
                open_calendar()
            return {'status': 'success', 'message': f'Opened {app_name}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def quit_app(self, app_name):
        """Quit an application by name"""
        try:
            if app_name == 'chrome':
                quit_chrome()
            elif app_name == 'safari':
                quit_safari()
            elif app_name == 'vscode':
                quit_vscode()
            elif app_name == 'spotify':
                quit_spotify()
            elif app_name == 'notes':
                quit_notes()
            elif app_name == 'terminal':
                quit_terminal()
            elif app_name == 'calculator':
                quit_calculator()
            elif app_name == 'calendar':
                quit_calendar()
            return {'status': 'success', 'message': f'Quit {app_name}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def setup_main_menu(self):
        """Setup the main menu interface using HTML"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Use HtmlFrame
        self.html_frame = HtmlFrame(self.root, messages_enabled=False)
        self.html_frame.pack(fill="both", expand=True)

        # Load the HTML file
        html_path = Path(__file__).parent.parent / "deskpilot_ui.html"
        if html_path.exists():
            self.html_frame.load_file(str(html_path))
            # Apply dark theme
            self.root.configure(bg='#1a1c25')
        else:
            self.setup_fallback_menu()
            return

        # Set up JavaScript to Python communication
        self.setup_js_bindings()

    def setup_js_bindings(self):
        """Set up JavaScript to Python communication"""
        try:
            # Create API object for JavaScript to call
            class API:
                def __init__(self, main_menu):
                    self.main_menu = main_menu

                def open_module(self, module_name):
                    """Open a specific module from JavaScript"""
                    if module_name == "organizer":
                        self.main_menu.open_desktop_organizer()
                    elif module_name == "launcher":
                        self.main_menu.open_app_launcher()
                    elif module_name == "summarizer":
                        self.main_menu.open_file_summarizer()

            # Make API available to JavaScript
            api = API(self)
            js_code = f"window.pywebview = {{ api: {api} }};"
            self.html_frame.evaluate_js(js_code)

        except Exception as e:
            print(f"Error setting up JS bindings: {e}")

    def setup_fallback_menu(self):
        """Fallback menu if HTML file is not available"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main menu frame
        main_frame = tk.Frame(self.root, bg="#1a1c25")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="DeskPilot - Main Menu",
            font=("Segoe UI", 20, "bold"),
            bg="#1a1c25",
            fg="#9feaf9"
        )
        title_label.pack(pady=(40, 20))

        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Your Personal Desktop Assistant",
            font=("Segoe UI", 12),
            bg="#1a1c25",
            fg="#6c7bff"
        )
        subtitle_label.pack(pady=(0, 40))

        # Button frame
        button_frame = tk.Frame(main_frame, bg="#1a1c25")
        button_frame.pack(pady=20)

        # Button style
        btn_style = {
            "width": 25,
            "height": 3,
            "font": ("Segoe UI", 12, "bold"),
            "bg": "#2d3246",
            "fg": "#e6e9f0",
            "relief": "flat",
            "borderwidth": 0,
            "cursor": "hand2",
            "highlightthickness": 0
        }

        # Menu buttons
        desktop_organizer_btn = tk.Button(
            button_frame,
            text="Desktop Organizer",
            command=self.open_desktop_organizer,
            **btn_style
        )
        desktop_organizer_btn.pack(pady=15)

        app_launcher_btn = tk.Button(
            button_frame,
            text="App Launcher",
            command=self.open_app_launcher,
            **btn_style
        )
        app_launcher_btn.pack(pady=15)

        file_summarizer_btn = tk.Button(
            button_frame,
            text="File Summarizer",
            command=self.open_file_summarizer,
            **btn_style
        )
        file_summarizer_btn.pack(pady=15)

        # Exit button
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit,
            width=15,
            height=2,
            font=("Segoe UI", 10),
            bg="#ff6b6b",
            fg="white",
            relief="flat",
            borderwidth=0,
            cursor="hand2"
        )
        exit_btn.pack(pady=(30, 0))

    def open_desktop_organizer(self):
        """Open Desktop Organizer module"""
        try:
            # Clear current widgets
            for widget in self.root.winfo_children():
                widget.destroy()

            # Create Desktop Organizer UI
            self.desktop_organizer = DesktopOrganiserUI(self.root, self)
        except Exception as e:
            print(f"Error opening Desktop Organizer: {e}")
            self.setup_main_menu()

    def open_app_launcher(self):
        """Open App Launcher module"""
        try:
            # Clear current widgets
            for widget in self.root.winfo_children():
                widget.destroy()

            # Create App Launcher UI
            self.app_launcher = AppLauncherHTMLGUI(self.root, self)
        except Exception as e:
            print(f"Error opening App Launcher: {e}")
            self.setup_main_menu()

    def open_file_summariser(self):
        """Open File Summariser module"""
        try:
            # Clear current widgets
            for widget in self.root.winfo_children():
                widget.destroy()

            # Create File Summarizer UI
            self.file_summariser = FileSummariserGUI(self.root, self)
        except Exception as e:
            print(f"Error opening File Summariser: {e}")
            self.setup_main_menu()

    def load_ui(self, html_file):
        """Load HTML UI from file"""
        html_path = Path(__file__).parent.parent / html_file
        if html_path.exists():
            # Clear current widgets
            for widget in self.root.winfo_children():
                widget.destroy()

            # Create HTML frame
            html_frame = HtmlFrame(self.root, messages_enabled=False)
            html_frame.pack(fill="both", expand=True)
            html_frame.load_file(str(html_path))
        else:
            print(f"HTML file not found: {html_file}")