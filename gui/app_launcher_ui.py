import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import sys
from pathlib import Path
import time

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

# voice + core + gpt
from voice import speaker as speaker_module
from voice.speaker import speak
from voice.listener import listen_command
from voice.voice_handler import VoiceHandler, start_voice_session
from core.app_launcher import (
    AppLauncher,
    open_vscode,
    open_safari,
    quit_spotify,
    launch_app_by_voice,
    quit_app_by_voice,
)
from gpt import GPTHandler

class AppLauncherGUI:
    def __init__(self, root, main_menu):
        self.root = root
        self.main_menu = main_menu
        self.app_launcher = AppLauncher()
        self.gpt_handler = GPTHandler()
        self.is_listening = False
        self.setup_ui()
        self.voice_handler = VoiceHandler()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#f0f0f0")

        # Title
        title_label = tk.Label(
            self.root,
            text="App Launcher",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        )
        title_label.pack(pady=(20, 10))

        # Subtitle
        subtitle_label = tk.Label(
            self.root,
            text="You can ask me to...",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666666",
        )
        subtitle_label.pack(pady=(0, 10))

        # Button frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(padx=24, pady=6, fill="x")

        # Button style
        btn_style = {
            "width": 20,
            "height": 2,
            "font": ("Arial", 14),
            "bg": "#ffffff",
            "fg": "#333333",
            "relief": "raised",
            "borderwidth": 2,
        }

        # Example App Functions (BUTTONS)
        open_vscode_btn = tk.Button(
            button_frame,
            text="Open VS Code",
            command=lambda: self._run_and_log(open_vscode, "Open VS Code"),
            **btn_style,
        )
        open_vscode_btn.pack(pady=10)

        open_safari_btn = tk.Button(
            button_frame,
            text="Open Safari",
            command=lambda: self._run_and_log(open_safari, "Open Safari"),
            **btn_style,
        )
        open_safari_btn.pack(pady=10)

        quit_spotify_btn = tk.Button(
            button_frame,
            text="Quit Spotify",
            command=lambda: self._run_and_log(quit_spotify, "Quit Spotify"),
            **btn_style
        )
        quit_spotify_btn.pack(pady=10)

        currently_running_btn = tk.Button(
            button_frame,
            text="Applications Currently Open",
            command=lambda: self._run_and_log(self.app_launcher.speak_running_apps, "List Running Apps"),
            **btn_style
        )
        currently_running_btn.pack(pady=10)

        # Transcription box - Limited height and proper packing
        transcription_frame = tk.Frame(self.root, bg="#f0f0f0")
        transcription_frame.pack(fill="x", padx=20, pady=(12, 6))

        self.transcription_box = scrolledtext.ScrolledText(
            transcription_frame,
            height=6,
            width=50,
            font=("Courier", 10),
            bg="#ffffff",
            fg="#333333",
            wrap=tk.WORD,
            borderwidth=2,
            state="disabled",
        )
        self.transcription_box.pack(fill="x")

        # Bottom controls: help (left), speak (right)
        controls_frame = tk.Frame(self.root, bg="#f0f0f0")
        controls_frame.pack(fill="x", padx=20, pady=(8, 18))

        # HELP BUTTON
        help_btn = tk.Button(
            controls_frame,
            text="?",
            font=("Arial", 20, "bold"),
            bg="#2196F3",
            fg="white",
            width=3,
            height=1,
            relief="raised",
            borderwidth=2,
            command=self.show_help,
        )
        help_btn.pack(side="left")

        # SPEAK BUTTON
        self.speak_btn = tk.Button(
            controls_frame,
            text="🎤",
            font=("Arial", 20),
            bg="#4CAF50",
            fg="white",
            width=3,
            height=1,
            relief="raised",
            borderwidth=2,
            command=self.on_speak_button_clicked,
        )
        self.speak_btn.pack(side="right")

        # BACK BUTTON
        back_btn = tk.Button(
            self.root,
            text="BACK TO\nMAIN\nMENU",
            command=self.go_back,
            font=("Arial", 10, "bold"),
            bg="#dddddd",
            fg="#333333",
            relief="raised",
            borderwidth=1,
        )
        back_btn.pack(pady=(0, 12))

        # Hook speaker's transcription log if available
        try:
            speaker_module.TRANSCRIPTION_LOG = self.transcription_box
        except Exception:
            pass

    def show_help(self):
        """Show help dialog with usage instructions"""
        help_text = """App Launcher Help

You can use this app in two ways:

1. CLICK BUTTONS: Use the buttons above to directly launch apps or check what's running.

2. VOICE COMMANDS: Click the 🗣 button and say things like:
   • "Open Chrome" / "Launch browser"
   • "Open Spotify" / "Start music" 
   • "Quit Safari" / "Close Safari"
   • "What's running?" / "List running apps"
   • "Open VS Code" / "Launch code editor"
   • Ask general questions and I'll help!

VOICE EXAMPLES:
   • "Open Visual Studio Code"
   • "Launch my web browser"
   • "Close Spotify"
   • "What applications are currently running?"
   • "Start the calculator"
   • "Open terminal"

I'll address you as 'sir' and provide voice confirmations for all actions.
The transcription box shows our conversation history."""

        messagebox.showinfo("App Launcher Help", help_text)

    def on_speak_button_clicked(self):
        """FIXED speak button handler - no more feedback!"""
        print("🎤 Speak button clicked")

        # Use the fixed voice handler
        self.voice_handler.start_voice_interaction()

    def _run_and_log(self, func, action_name):
        """Helper to run an action and log + speak with proper feedback"""
        self.add_to_transcription(f"(User) clicked: {action_name}")

        def runner():
            try:
                # The function should handle its own speaking now
                success = func()

                if success is False:
                    # Only speak error if the function didn't already handle it
                    self.add_to_transcription(f"(System) Action failed: {action_name}")
                else:
                    # Success case - function should have already spoken
                    self.add_to_transcription(f"(System) Action completed: {action_name}")

            except Exception as e:
                self.add_to_transcription(f"(System) Error: {e}")
                speak(f"Sorry sir, an error occurred: {e}")

        threading.Thread(target=runner, daemon=True).start()

    def toggle_listen_flow(self):
        """Start the speak -> listen -> process loop in a thread"""
        if self.is_listening:
            return
        self.is_listening = True
        self.speak_btn.config(bg="#f44336", text="🔴")  # Change to red with recording symbol
        threading.Thread(target=self._speak_listen_process, daemon=True).start()

    def _speak_listen_process(self):
        """
        Enhanced voice flow with GPT integration:
          1. Get a dynamic prompt from GPT
          2. Speak it aloud
          3. Listen for user's command
          4. Log both sides to transcription
          5. Process command intelligently using GPT + app launcher
        """
        try:
            # 1. Get dynamic prompt from GPT
            try:
                dynamic_prompt = self.gpt_handler.get_dynamic_prompt()
            except Exception as e:
                print(f"GPT prompt generation failed: {e}")
                dynamic_prompt = "How can I assist you today, sir?"

            # 2. Speak the prompt and log
            self.add_to_transcription(f"(DeskPilot) says: {dynamic_prompt}")
            speak(dynamic_prompt)

            # 3. Listen for command
            self.add_to_transcription("(System) Listening for voice command...")
            print("🎤 Starting to listen...")

            try:
                command = listen_command(timeout=8, phrase_time_limit=12)
                print(f"🎤 Received command: '{command}'")
            except Exception as listen_error:
                print(f"Listen error: {listen_error}")
                command = ""

            # 4. Handle no command or empty command
            if not command or command.strip() == "":
                self.add_to_transcription("(System) No command detected")
                speak("I didn't catch that, sir. Please try again.")
                return

            # 5. Log user's command
            self.add_to_transcription(f"(User) says: {command}")
            print(f"📝 Processing command: {command}")

            # 6. Process command with enhanced logic
            try:
                processed = self._process_voice_command(command)
                print(f"✅ Command processed: {processed}")

                if not processed:
                    # Fallback to GPT for general questions
                    print("🤖 Using GPT for general response")
                    self.add_to_transcription("(System) Using GPT for general response")

                    try:
                        response = self.gpt_handler.get_response(command)
                        self.add_to_transcription(f"(DeskPilot) says: {response}")
                        speak(response)
                    except Exception as gpt_error:
                        print(f"GPT response failed: {gpt_error}")
                        fallback_response = "I'm sorry sir, I'm having trouble processing that request at the moment."
                        self.add_to_transcription(f"(DeskPilot) says: {fallback_response}")
                        speak(fallback_response)

            except Exception as process_error:
                print(f"Command processing error: {process_error}")
                error_response = "I encountered an error processing your command, sir."
                self.add_to_transcription(f"(DeskPilot) says: {error_response}")
                speak(error_response)

        except Exception as e:
            print(f"❌ Voice flow error: {e}")
            self.add_to_transcription(f"(System) Error during voice flow: {e}")
            speak("Sorry sir, I encountered an error while processing your request.")
        finally:
            # Reset UI
            self.is_listening = False
            time.sleep(0.5)
            try:
                self.speak_btn.config(bg="#4CAF50", text="🎤")
            except:
                pass

    def _process_voice_command(self, command):
        """
        Process voice commands with intelligent parsing using GPT

        Args:
            command (str): The voice command to process

        Returns:
            bool: True if command was processed, False otherwise
        """
        if not command or not command.strip():
            return False

        command_lower = command.lower().strip()
        print(f"🔍 Processing command: '{command_lower}'")

        # 1. Check for app opening commands
        open_triggers = ["open", "launch", "start", "run"]
        if any(word in command_lower for word in open_triggers):
            print("🚀 Detected app opening command")
            try:
                success = launch_app_by_voice(command, self.gpt_handler)
                if success:
                    self.add_to_transcription("(System) Application launched successfully")

                else:
                    self.add_to_transcription("(System) Application launch failed or not found")
                return True  # Command was handled, regardless of success
            except Exception as e:
                print(f"App launch error: {e}")
                speak("Sorry sir, I had trouble launching that application.")
                return True

        # 2. Check for app quitting commands
        quit_triggers = ["quit", "close", "stop", "exit", "kill"]
        if any(word in command_lower for word in quit_triggers):
            print("🛑 Detected app quitting command")
            try:
                success = quit_app_by_voice(command, self.gpt_handler)
                if success:
                    self.add_to_transcription("(System) Application quit successfully")
                else:
                    self.add_to_transcription("(System) Application quit failed or not found")
                return True  # Command was handled
            except Exception as e:
                print(f"App quit error: {e}")
                speak("Sorry sir, I had trouble quitting that application.")
                return True

        # 3. Check for running apps query
        running_phrases = [
            "running", "what's open", "what is open", "what's running",
            "what is running", "list apps", "show apps", "current apps",
            "what applications", "running applications", "apps running"
        ]
        if any(phrase in command_lower for phrase in running_phrases):
            print("📱 Detected running apps query")
            try:
                success = self.app_launcher.speak_running_apps()
                if success:
                    self.add_to_transcription("(System) Listed running applications")
                else:
                    self.add_to_transcription("(System) Failed to list running applications")
                return True
            except Exception as e:
                print(f"Running apps error: {e}")
                speak("Sorry sir, I had trouble checking your running applications.")
                return True

        # 4. Check for system commands
        help_phrases = ["help", "what can you do", "commands", "what can i do"]
        if any(phrase in command_lower for phrase in help_phrases):
            print("❓ Detected help command")
            help_text = ("I can help you open applications, quit applications, "
                         "and show what's currently running, sir. Just tell me what you'd like to do!")
            speak(help_text)
            self.add_to_transcription(f"(DeskPilot) says: {help_text}")
            return True

        # 5. Check for greeting
        greeting_phrases = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if any(phrase in command_lower for phrase in greeting_phrases):
            print("👋 Detected greeting")
            greeting_response = "Hello sir, how can I assist you today?"
            speak(greeting_response)
            self.add_to_transcription(f"(DeskPilot) says: {greeting_response}")
            return True

        print("❓ Command not recognized by specific handlers")
        # Command not recognized by specific handlers
        return False

    def add_to_transcription(self, text):
        """Add text to the transcription box safely on the Tk main thread"""

        def append():
            self.transcription_box.config(state="normal")
            self.transcription_box.insert(tk.END, text + "\n")
            self.transcription_box.see(tk.END)
            self.transcription_box.config(state="disabled")

        try:
            self.root.after(0, append)
        except Exception:
            append()

    def go_back(self):
        self.main_menu.setup_main_menu()