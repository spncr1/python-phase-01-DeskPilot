"""
Voice Handler for DeskPilot - Prevents feedback loops
"""

from voice.speaker import speak_and_wait, speak
from voice.listener import listen_command
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.app_launcher import (
        AppLauncher,
        launch_app_by_voice,
        quit_app_by_voice
    )
except ImportError:
    print("⚠️ App launcher not available")
    AppLauncher = None

# GPT integration (optional)
try:
    from gpt import GPTHandler
except Exception:
    GPTHandler = None

# Names from config (optional for fallbacks)
try:
    from config import ASSISTANT_NAME, USER_NAME
except Exception:
    ASSISTANT_NAME, USER_NAME = "DeskPilot", "sir"


class VoiceHandler:
    """Handles the voice interaction flow, delegating app logic to app_launcher.py"""

    def __init__(self):
        self.listening = False
        self.app_launcher = AppLauncher() if AppLauncher else None
        # Lazy GPT handler for dynamic greetings
        self.gpt_handler = GPTHandler() if GPTHandler else None
        # Local rotating greetings as examples/fallbacks
        self._greeting_pool = [
            "DeskPilot, at your service sir.",
            "Ready when you are, sir!",
            "How may I help you today, sir?",
            "What will it be today, sir — opening apps, or shall I show what's currently running?",
        ]
        self._greet_index = 0

    def _get_dynamic_greeting(self):
        """Return a varied greeting using GPT when available, otherwise cycle local examples."""
        # Try GPT-driven dynamic prompt first
        if self.gpt_handler:
            try:
                prompt = self.gpt_handler.get_dynamic_prompt()
                if prompt and isinstance(prompt, str) and prompt.strip():
                    return prompt.strip()
            except Exception as _e:
                print(f"GPT dynamic greeting failed: {_e}")
        # Fallback: simple rotation through local pool
        if not self._greeting_pool:
            return "How may I assist you today, sir?"
        greeting = self._greeting_pool[self._greet_index % len(self._greeting_pool)]
        self._greet_index += 1
        return greeting

    def start_voice_interaction(self):
        """Start voice flow with proper TTS/listen sequence"""
        greet = self._get_dynamic_greeting()
        speak_and_wait(greet)
        self.listen_for_command()

    def start_voice_interaction_with_callback(self):
        """Alternative callback-based voice start"""

        def start_listening():
            print("🎧 Callback triggered - now listening for user...")
            time.sleep(0.2)
            self.listen_for_command()

        greet = self._get_dynamic_greeting()
        speak(
            greet,
            log_to_transcription=True,
            on_finished_callback=start_listening
        )

    def listen_for_command(self):
        """Listen for user command after TTS finishes"""
        if self.listening:
            print("⚠️ Already listening, skipping...")
            return

        self.listening = True

        try:
            command = listen_command(timeout=10, phrase_time_limit=15)

            if command:
                print(f"🎤 Received command: '{command}'")
                self.process_command(command)
            else:
                print("🔇 No command received")
                speak_and_wait("I didn't catch that, sir. Could you please repeat?")
                self.listen_for_command()

        except Exception as e:
            print(f"❌ Listening error: {e}")
            speak_and_wait("Sorry sir, I had trouble hearing you.")
        finally:
            self.listening = False

    def process_command(self, command):
        """Process user command and route to app_launcher.py"""
        print(f"📝 Processing command: {command}")
        command_lower = command.lower().strip()

        # First try GPT interpretation to support conversational phrasing
        if self.gpt_handler:
            try:
                interp = self.gpt_handler.interpret_app_command(command)
                action = (interp.get('action') or 'unknown').lower()
                app = interp.get('app') or 'none'
                if action in ['open', 'launch', 'start', 'run'] and app != 'none':
                    result = launch_app_by_voice(command, self.gpt_handler)
                    speak_and_wait(result['message'])
                    if not result['success']:
                        self.listen_for_command()
                    return
                if action in ['quit', 'close', 'stop', 'exit'] and app != 'none':
                    result = quit_app_by_voice(command, self.gpt_handler)
                    speak_and_wait(result['message'])
                    if not result['success']:
                        self.listen_for_command()
                    return
                if action in ['list'] or ('running' in command_lower and ('app' in command_lower or 'applications' in command_lower or 'apps' in command_lower)):
                    # Treat as running apps inquiry
                    if not self.app_launcher:
                        speak_and_wait("Sorry sir, I can't access running applications right now.")
                        return
            except Exception as _e:
                print(f"GPT pre-parse failed: {_e}")

        # Open/launch/start commands (keyword fallback)
        if any(word in command_lower for word in ["open", "launch", "start", "run", "bring up", "pull up", "fire up", "boot up", "pop open"]):
            result = launch_app_by_voice(command, self.gpt_handler)
            speak_and_wait(result['message'])
            if not result['success']:
                self.listen_for_command()  # Ask again if failed

        # Quit/close/exit/stop commands (keyword fallback)
        elif any(word in command_lower for word in ["quit", "close", "exit", "stop", "shut down", "close out", "end", "terminate", "dismiss", "kill"]):
            result = quit_app_by_voice(command, self.gpt_handler)
            speak_and_wait(result['message'])
            if not result['success']:
                self.listen_for_command()  # Ask again if failed

        # Running apps inquiries (how many / which / is <app> open?)
        elif any(kw in command_lower for kw in ["running", "currently open", "what's running", "what is running", "what's open", "what is open", "applications", "apps", "rundown"]):
            if not self.app_launcher:
                speak_and_wait("Sorry sir, I can't access running applications right now.")
                return

            # 1) Yes/No for specific app: e.g., "is google chrome open?" / "is spotify running?"
            import re as _re
            m = _re.search(r"^is\s+(.+?)\s+(?:currently\s+)?(open|running)\??$", command_lower)
            if m:
                app_phrase = m.group(1).strip()
                result = self.app_launcher.check_app_running_message(app_phrase)
                speak_and_wait(result['message'])
                return

            # 2) How many apps are open?
            if ("how many" in command_lower) and ("app" in command_lower or "application" in command_lower or "applications" in command_lower or "apps" in command_lower):
                summary = self.app_launcher.get_running_apps_summary()
                # Enforce the exact phrasing requested
                speak_and_wait(f"You have {summary['count']} applications open sir")
                return

            # 3) Which/what apps are open?
            list_triggers = [
                "which apps", "which applications", "what apps", "what applications",
                "what's open", "what is open", "what's running", "what is running",
                "show apps", "list apps", "running apps", "running applications", "rundown"
            ]
            if any(t in command_lower for t in list_triggers):
                sentence = self.app_launcher.running_apps_list_sentence()
                speak_and_wait(sentence)
                return

            # Fallback: generic summary
            summary = self.app_launcher.get_running_apps_summary()
            speak_and_wait(summary['message'])

        # Assistant name queries (e.g., "what is your name?")
        elif ("your name" in command_lower) or ("what's your name" in command_lower) or ("what is your name" in command_lower) or ("name?" in command_lower and ("your" in command_lower or command_lower.startswith("name"))):
            try:
                if self.gpt_handler:
                    response = self.gpt_handler.get_name_response()
                else:
                    response = f"My name is {ASSISTANT_NAME}, {USER_NAME}."
                speak_and_wait(response)
            finally:
                self.listen_for_command()

        # Identity / capabilities queries
        elif any(phrase in command_lower for phrase in [
            "who are you", "what can you do", "your capabilities", "capabilities", "functions",
            "what are your functions", "what are your capabilities", "tell me about yourself",
            "introduce yourself", "what do you do", "what are you"
        ]):
            try:
                if self.gpt_handler:
                    response = self.gpt_handler.get_identity_response()
                else:
                    response = (
                        f"I am {ASSISTANT_NAME} {USER_NAME}, an interactive artificial intelligence system serving as your personal assistant to help with your desktop needs on your operating system. "
                        "I can open apps, close apps, or check what's currently running."
                    )
                speak_and_wait(response)
            finally:
                self.listen_for_command()

        # Help/assistance
        elif any(phrase in command_lower for phrase in ["help", "what can you do", "commands", "assist"]):
            speak_and_wait(
                "I can help you open applications, close applications, and check what's currently running, sir. What would you like me to do?"
            )
            self.listen_for_command()

        # Default response
        else:
            speak_and_wait(
                "I'm not sure how to help with that, sir. You can ask me to open apps, close apps, or check what's running."
            )
            self.listen_for_command()


# Convenience functions for easy integration
def start_voice_session():
    """Start a single voice interaction session"""
    handler = VoiceHandler()
    handler.start_voice_interaction()


def continuous_voice_mode():
    """Continuous listening mode"""
    voice_handler = VoiceHandler()

    speak_and_wait("DeskPilot voice mode activated, sir.")

    while True:
        try:
            print("🎧 Listening for wake word or command...")
            command = listen_command(timeout=30, phrase_time_limit=10)

            if not command:
                continue

            # Wake word detection
            if any(wake in command.lower() for wake in ["desk pilot", "deskpilot", "hey pilot"]):
                speak_and_wait("Yes sir?")
                actual_command = listen_command(timeout=10, phrase_time_limit=15)
                if actual_command:
                    voice_handler.process_command(actual_command)

            elif "stop listening" in command.lower():
                speak_and_wait("Voice mode deactivated, sir.")
                break

        except KeyboardInterrupt:
            speak_and_wait("Voice mode stopped, sir.")
            break
        except Exception as e:
            print(f"❌ Continuous mode error: {e}")
            time.sleep(1)