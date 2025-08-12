# Logic for all app launching functions
import subprocess
import platform
import psutil
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from voice.speaker import speak
except ImportError:
    # Fallback if voice module not available
    def speak(text):
        print(f"DeskPilot says: {text}")


class AppLauncher:
    """Handle launching, quitting, and managing applications with voice feedback"""

    def __init__(self):
        self.system = platform.system()

    def open_application(self, app_name, speak_feedback=True):
        """
        Open an application by name with voice feedback

        Args:
            app_name (str): Name of the application to open
            speak_feedback (bool): Whether to provide voice feedback

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
            elif self.system == "Windows":
                subprocess.Popen([app_name])
            elif self.system == "Linux":
                subprocess.Popen([app_name.lower()])

            print(f"Opening {app_name}...")
            if speak_feedback:
                speak(f"Opening {app_name} for you, sir.")
            return True

        except Exception as e:
            print(f"Error launching {app_name}: {e}")
            if speak_feedback:
                speak(f"Sorry sir, I couldn't open {app_name}. Please check if it's installed.")
            return False

    def quit_application(self, app_name, speak_feedback=True):
        """
        Quit an application by name with voice feedback

        Args:
            app_name (str): Name of the application to quit
            speak_feedback (bool): Whether to provide voice feedback

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            found_process = False
            # Find and terminate the process
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    found_process = True
                    print(f"Quit {app_name}")
                    if speak_feedback:
                        speak(f"I've quit {app_name} for you, sir.")
                    return True

            if not found_process:
                print(f"{app_name} is not currently running")
                if speak_feedback:
                    speak(f"Sir, {app_name} doesn't appear to be running at the moment.")
                return False

        except Exception as e:
            print(f"Error quitting {app_name}: {e}")
            if speak_feedback:
                speak(f"Sorry sir, I encountered an error while trying to quit {app_name}.")
            return False

    def get_running_apps(self):
        """
        Get list of currently running applications

        Returns:
            list: List of running application names
        """
        try:
            running_apps = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    app_name = proc.info['name']
                    if app_name and app_name not in running_apps and not self._is_system_process(app_name):
                        running_apps.append(app_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return sorted(running_apps)

        except Exception as e:
            print(f"Error getting running apps: {e}")
            speak("Sorry sir, I'm having trouble checking your running applications.")
            return []

    def speak_running_apps(self, limit=5):
        """
        Speak the currently running applications with proper voice feedback

        Args:
            limit (int): Maximum number of apps to mention
        """
        try:
            running_apps = self.get_running_apps()

            if not running_apps:
                speak("No user applications are currently running, sir.")
                return True

            # Filter and limit results
            user_apps = [app for app in running_apps if not self._is_system_process(app)]

            if len(user_apps) == 0:
                speak("No user applications are currently running, sir.")
            elif len(user_apps) == 1:
                speak(f"You have {user_apps[0]} running, sir.")
            elif len(user_apps) <= 3:
                apps_text = ", ".join(user_apps[:-1]) + f" and {user_apps[-1]}"
                speak(f"You have {apps_text} running, sir.")
            elif len(user_apps) <= limit:
                apps_text = ", ".join(user_apps[:-1]) + f" and {user_apps[-1]}"
                speak(f"Sir, you have {len(user_apps)} applications running: {apps_text}.")
            else:
                top_apps = user_apps[:limit - 1]
                apps_text = ", ".join(top_apps)
                remaining = len(user_apps) - (limit - 1)
                speak(
                    f"Sir, you have {len(user_apps)} applications running, including {apps_text}, and {remaining} others.")

            return True

        except Exception as e:
            print(f"Error speaking running apps: {e}")
            speak("Sorry sir, I encountered an error while checking your running applications.")
            return False

    def _is_system_process(self, app_name):
        """
        Check if an application is a system process

        Args:
            app_name (str): Application name to check

        Returns:
            bool: True if it's likely a system process
        """
        system_processes = [
            'kernel_task', 'launchd', 'WindowServer', 'Finder',
            'System Preferences', 'Activity Monitor', 'Dock', 'loginwindow',
            'svchost.exe', 'explorer.exe', 'winlogon.exe', 'csrss.exe',
            'systemd', 'kthreadd', 'ksoftirqd', 'Python', 'python3',
            # Add more system processes as needed
        ]

        return any(sys_proc.lower() in app_name.lower() for sys_proc in system_processes)


# Pre-configured application shortcuts with voice feedback:

def open_chrome():
    """Open Google Chrome"""
    launcher = AppLauncher()
    return launcher.open_application("Google Chrome")


def open_safari():
    """Open Safari"""
    launcher = AppLauncher()
    return launcher.open_application("Safari")


def open_firefox():
    """Open Firefox"""
    launcher = AppLauncher()
    return launcher.open_application("Firefox")


def open_vscode():
    """Open Visual Studio Code"""
    launcher = AppLauncher()
    return launcher.open_application("Visual Studio Code")


def open_spotify():
    """Open Spotify"""
    launcher = AppLauncher()
    return launcher.open_application("Spotify")


def open_notes():
    """Open Notes app"""
    launcher = AppLauncher()
    return launcher.open_application("Notes")


def open_terminal():
    """Open Terminal"""
    launcher = AppLauncher()
    if platform.system() == "Darwin":
        return launcher.open_application("Terminal")
    elif platform.system() == "Windows":
        return launcher.open_application("cmd")
    else:
        return launcher.open_application("gnome-terminal")


def open_calculator():
    """Open Calculator"""
    launcher = AppLauncher()
    return launcher.open_application("Calculator")


def open_calendar():
    """Open Calendar application"""
    launcher = AppLauncher()
    return launcher.open_application("Calendar")


# Quitting applications
def quit_chrome():
    """Quit Google Chrome"""
    launcher = AppLauncher()
    return launcher.quit_application("Google Chrome")


def quit_safari():
    """Quit Safari"""
    launcher = AppLauncher()
    return launcher.quit_application("Safari")


def quit_vscode():
    """Quit Visual Studio Code"""
    launcher = AppLauncher()
    return launcher.quit_application("Visual Studio Code")


def quit_spotify():
    """Quit Spotify"""
    launcher = AppLauncher()
    return launcher.quit_application("Spotify")


def quit_notes():
    """Quit Notes app"""
    launcher = AppLauncher()
    return launcher.quit_application("Notes")


def quit_terminal():
    """Quit Terminal"""
    launcher = AppLauncher()
    if platform.system() == "Darwin":
        return launcher.quit_application("Terminal")
    elif platform.system() == "Windows":
        return launcher.quit_application("cmd")
    else:
        return launcher.quit_application("gnome-terminal")


def quit_calculator():
    """Quit Calculator"""
    launcher = AppLauncher()
    return launcher.quit_application("Calculator")


def quit_mail():
    """Quit Mail application"""
    launcher = AppLauncher()
    return launcher.quit_application("Mail")


def quit_calendar():
    """Quit Calendar application"""
    launcher = AppLauncher()
    return launcher.quit_application("Calendar")


# Enhanced voice command processing
def launch_app_by_voice(command, gpt_handler=None):
    """
    Parse voice command and launch appropriate application with GPT assistance

    Args:
        command (str): Voice command containing app name
        gpt_handler: Optional GPT handler for intelligent parsing

    Returns:
        bool: True if app was launched successfully
    """
    command_lower = command.lower()
    launcher = AppLauncher()

    # Enhanced app mappings with more variations
    app_mappings = {
        # Browsers
        'chrome': 'Google Chrome',
        'google chrome': 'Google Chrome',
        'browser': 'Google Chrome',
        'web browser': 'Google Chrome',
        'safari': 'Safari',
        'firefox': 'Firefox',

        # Development
        'vscode': 'Visual Studio Code',
        'vs code': 'Visual Studio Code',
        'visual studio code': 'Visual Studio Code',
        'code': 'Visual Studio Code',
        'editor': 'Visual Studio Code',

        # Media
        'spotify': 'Spotify',
        'music': 'Spotify',
        'tunes': 'Spotify',

        # Utilities
        'notes': 'Notes',
        'note': 'Notes',
        'notepad': 'Notes',
        'terminal': 'Terminal',
        'command line': 'Terminal',
        'shell': 'Terminal',
        'calculator': 'Calculator',
        'calc': 'Calculator',
        'math': 'Calculator',
        'mail': 'Mail',
        'email': 'Mail',
        'calendar': 'Calendar',
        'schedule': 'Calendar'
    }

    # Try direct mapping first
    for key, app_name in app_mappings.items():
        if key in command_lower:
            success = launcher.open_application(app_name)
            if success:
                return True

    # If GPT handler available, use it for intelligent parsing
    if gpt_handler:
        try:
            interpretation = gpt_handler.interpret_app_command(command)
            if interpretation['action'] == 'open' and interpretation['app'] != 'none':
                app_name = interpretation['app']
                success = launcher.open_application(app_name)
                if success:
                    return True
                elif interpretation['confidence'] == 'high':
                    # App not found but GPT was confident - get suggestion
                    suggestion = gpt_handler.get_app_suggestion(app_name)
                    speak(suggestion)
                    return False
        except Exception as e:
            print(f"GPT interpretation failed: {e}")

    # Fallback: try to extract app name from command
    if any(trigger in command_lower for trigger in ['open', 'launch', 'start', 'run']):
        words = command_lower.split()
        for trigger in ['open', 'launch', 'start', 'run']:
            if trigger in words:
                trigger_index = words.index(trigger)
                if trigger_index + 1 < len(words):
                    app_name = ' '.join(words[trigger_index + 1:]).title()
                    success = launcher.open_application(app_name)
                    if success:
                        return True

    # If nothing worked
    speak("I'm not sure which application you want to open, sir. Could you please be more specific?")
    return False


def quit_app_by_voice(command, gpt_handler=None):
    """
    Parse voice command and quit appropriate application with GPT assistance

    Args:
        command (str): Voice command containing app name to quit
        gpt_handler: Optional GPT handler for intelligent parsing

    Returns:
        bool: True if app was quit successfully
    """
    command_lower = command.lower()
    launcher = AppLauncher()

    # If GPT handler available, use it for intelligent parsing
    if gpt_handler:
        try:
            interpretation = gpt_handler.interpret_app_command(command)
            if interpretation['action'] == 'quit' and interpretation['app'] != 'none':
                app_name = interpretation['app']
                return launcher.quit_application(app_name)
        except Exception as e:
            print(f"GPT interpretation failed: {e}")

    # Fallback: simple parsing
    quit_triggers = ['quit', 'close', 'stop', 'exit', 'kill']
    words = command_lower.split()

    for trigger in quit_triggers:
        if trigger in words:
            trigger_index = words.index(trigger)
            if trigger_index + 1 < len(words):
                app_name = ' '.join(words[trigger_index + 1:]).title()
                return launcher.quit_application(app_name)

    speak("I'm not sure which application you want to quit, sir. Could you please specify?")
    return False