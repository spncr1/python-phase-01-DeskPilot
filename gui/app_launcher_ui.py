import tkinter as tk
from tkinterweb import HtmlFrame
import threading
import sys
from pathlib import Path
import json

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.app_launcher import open_vscode, open_safari, quit_spotify


class AppLauncherHTMLGUI:
    """HTML-based App Launcher GUI"""

    def __init__(self, root, main_menu):
        self.root = root
        self.main_menu = main_menu
        self.html_frame = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the HTML-based UI"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create HTML frame
        self.html_frame = HtmlFrame(self.root, messages_enabled=False)
        self.html_frame.pack(fill="both", expand=True)

        # Load the App Launcher HTML content
        # For simplicity, we'll use the main HTML file but focus on the app launcher section
        html_path = Path(__file__).parent.parent / "deskpilot_ui.html"
        if html_path.exists():
            self.html_frame.load_file(str(html_path))

            # After loading, show only the app launcher module
            self.html_frame.evaluate_js("""
                document.getElementById('main-menu').style.display = 'none';
                document.getElementById('launcher-module').classList.add('active');
            """)
        else:
            # Fallback to basic UI if HTML file doesn't exist
            self.setup_fallback_ui()

        # Setup JavaScript API
        self._setup_js_api()

    def _setup_js_api(self):
        """Setup JavaScript API for communication with Python"""
        # Create API object
        api = {
            'execute_command': self.execute_command,
            'start_voice_interaction': self.start_voice_interaction,
            'get_running_apps': self.get_running_apps,
            'show_help': self.show_help,
            'go_back_to_menu': self.go_back_to_menu
        }

        # Make API available to JavaScript
        js_code = f"window.pywebview = {{ api: {json.dumps(api)} }};"
        try:
            self.html_frame.evaluate_js(js_code)
        except Exception as e:
            print(f"Error setting up JS API: {e}")

    def execute_command(self, command):
        """Execute commands from HTML interface"""
        self.add_to_transcription(f"(User) clicked: {command}")

        try:
            if command == "open_vscode":
                success = open_vscode()
                if success:
                    self.add_to_transcription("(System) Opening Visual Studio Code...")
                else:
                    self.add_to_transcription("(System) Failed to open VS Code")

            elif command == "open_safari":
                success = open_safari()
                if success:
                    self.add_to_transcription("(System) Opening Safari...")
                else:
                    self.add_to_transcription("(System) Failed to open Safari")

            elif command == "quit_spotify":
                success = quit_spotify()
                if success:
                    self.add_to_transcription("(System) Quitting Spotify...")
                else:
                    self.add_to_transcription("(System) Spotify is not running")

            elif command == "show_running_apps":
                self.get_running_apps()

        except Exception as e:
            self.add_to_transcription(f"(System) Error: {e}")

    def start_voice_interaction(self):
        """Handle voice interaction"""

        def voice_thread():
            try:
                self.add_to_transcription("(System) Starting voice session...")
                # Use the existing voice handler
                self.voice_handler.start_voice_interaction()
            except Exception as e:
                self.add_to_transcription(f"(System) Voice error: {e}")
            finally:
                # Reset speak button
                self._reset_speak_button()

        # Start in separate thread
        thread = threading.Thread(target=voice_thread, daemon=True)
        thread.start()

    def get_running_apps(self):
        """Get and display running applications"""
        # This would call your actual app_launcher code
        # For now, we'll use a placeholder
        apps = ["Chrome", "VS Code", "Finder", "Spotify"]
        self.update_running_apps_display(apps)

    def update_running_apps_display(self, apps):
        """Update the running apps display in HTML"""
        try:
            js_code = f"updateRunningApps({json.dumps(apps)});"
            self.html_frame.evaluate_js(js_code)
            self.add_to_transcription("(System) Updated running applications list")
        except Exception as e:
            print(f"Error updating running apps display: {e}")

    def _reset_speak_button(self):
        """Reset the speak button state"""
        try:
            self.html_frame.evaluate_js("resetSpeakButton();")
        except:
            pass

    def add_to_transcription(self, text):
        """Add text to the transcription box"""
        try:
            # Escape text for JavaScript
            escaped_text = text.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            js_code = f"addToTranscription('{escaped_text}');"
            self.html_frame.evaluate_js(js_code)
        except Exception as e:
            print(f"Error adding to transcription: {e}")

    def show_help(self):
        """Show help dialog"""
        help_text = """App Launcher Help

You can use this app in two ways:

1. CLICK BUTTONS: Use the buttons above to directly launch apps or check what's running.

2. VOICE COMMANDS: Click the 🎤 button and say things like:
   • "Open Chrome" / "Launch browser"
   • "Open Spotify" / "Start music"
   • "Quit Safari" / "Close Safari"
   • "What's running?" / "List running apps"
   • "Open VS Code" / "Launch code editor"

The transcription box shows our conversation history."""

        try:
            import tkinter.messagebox as messagebox
            messagebox.showinfo("App Launcher Help", help_text)
        except:
            print(help_text)

    def go_back_to_menu(self):
        """Go back to main menu"""
        if self.main_menu:
            self.main_menu.setup_main_menu()

    def setup_fallback_ui(self):
        """Fallback UI if HTML is not available"""
        # Your existing tkinter-based UI code here
        pass


# Compatibility alias
class AppLauncherGUI(AppLauncherHTMLGUI):
    """Maintains compatibility with existing interface"""
    pass