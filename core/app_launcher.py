# Logic for all app launching functions
import subprocess
import platform
import psutil
import sys
import os
import time
import re
import difflib
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# No more voice imports - app_launcher stays silent


class AppLauncher:
    """Handle launching, quitting, and managing applications WITHOUT voice feedback"""

    def __init__(self):
        self.system = platform.system()

    def open_application(self, app_name):
        """
        Open an application by name (silent operation)

        Args:
            app_name (str): Name of the application to open (user-friendly name or alias)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Darwin":  # macOS
                # Resolve app to a known installed application
                resolved = self._resolve_application(app_name)
                if resolved:
                    display_name, app_path, _score = resolved
                    # If already running, bring to front instead of reopening
                    if self._is_app_running(display_name):
                        self.activate_application(display_name)
                        print(f"Focusing {display_name} (already running)...")
                        return True
                    try:
                        # Prefer opening by exact bundle path for reliability
                        subprocess.Popen(["open", app_path])
                        print(f"Opening {display_name}...")
                        return True
                    except Exception:
                        # Fallback to using -a with display name
                        subprocess.Popen(["open", "-a", display_name])
                        print(f"Opening {display_name}...")
                        return True
                else:
                    # Last resort: try to open what user said
                    subprocess.Popen(["open", "-a", app_name])
                    print(f"Opening {app_name}...")
                    return True

            elif self.system == "Windows":
                subprocess.Popen([app_name])
                print(f"Opening {app_name}...")
                return True

            elif self.system == "Linux":
                subprocess.Popen([app_name.lower()])
                print(f"Opening {app_name}...")
                return True

        except Exception as e:
            print(f"Error launching {app_name}: {e}")
            return False

    def quit_application(self, app_name):
        """
        Quit an application by name (silent operation)

        Args:
            app_name (str): Name of the application to quit

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Resolve the intended app for better matching
            resolved = self._resolve_application(app_name)
            target_name = resolved[0] if resolved else app_name

            # Prefer graceful termination on macOS via osascript; fallback to psutil
            if self.system == "Darwin":
                if self._is_app_running(target_name):
                    try:
                        subprocess.run([
                            "osascript", "-e", f'tell application "{target_name}" to quit'
                        ], check=False)
                        # Give it a moment then verify
                        time.sleep(0.5)
                        if not self._is_app_running(target_name):
                            print(f"Quit {target_name}")
                            return True
                    except Exception:
                        pass

            # Generic fallback: find and terminate process
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = (proc.info['name'] or '').lower()
                    if self._matches_process_name(proc_name, target_name):
                        proc.terminate()
                        print(f"Quit {target_name} (process: {proc.info['name']})")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            print(f"{target_name} is not currently running")
            return False

        except Exception as e:
            print(f"Error quitting {app_name}: {e}")
            return False

    # ----------------- Dynamic App Discovery & Resolution (macOS focused) -----------------
    def _app_search_locations(self):
        if self.system != "Darwin":
            return []
        home = str(Path.home())
        return [
            "/Applications",
            "/Applications/Utilities",
            "/System/Applications",
            "/System/Applications/Utilities",
            f"{home}/Applications",
        ]

    def _normalize(self, name: str) -> str:
        s = name.lower().strip()
        s = re.sub(r"[\._]", " ", s)
        s = re.sub(r"\b(app|application|the)\b", " ", s)
        s = s.replace("&", " and ")
        s = s.replace("ms ", "microsoft ")
        s = s.replace("vs code", "visual studio code")
        s = re.sub(r"[^a-z0-9]+", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _collect_aliases(self, display_name: str):
        base = self._normalize(display_name)
        aliases = {base}
        aliases.add(base.replace(" ", ""))
        aliases.add(base.replace(" and ", "&"))
        # Special short forms
        if base.startswith("microsoft "):
            aliases.add(base.replace("microsoft ", "ms "))
        if base.endswith(" player"):
            aliases.add(base.replace(" player", ""))
        return aliases

    def _scan_installed_apps(self):
        if getattr(self, "_apps_cache", None) and (time.time() - getattr(self, "_apps_cache_time", 0) < 60):
            return self._apps_cache

        apps = {}
        if self.system == "Darwin":
            for loc in self._app_search_locations():
                p = Path(loc)
                if not p.exists():
                    continue
                # Use rglob to find .app bundles
                try:
                    for app in p.rglob("*.app"):
                        display = app.stem
                        aliases = self._collect_aliases(display)
                        for alias in aliases:
                            # Keep the first encountered path for an alias
                            apps.setdefault(alias, (display, str(app)))
                except Exception:
                    continue
        else:
            # For other OS, we can't reliably scan generically; leave empty
            pass

        self._apps_cache = apps
        self._apps_cache_time = time.time()
        return apps

    def _resolve_application(self, query: str):
        if not query:
            return None
        norm_q = self._normalize(query)
        apps = self._scan_installed_apps()

        # 1. Exact alias match
        if norm_q in apps:
            display, path = apps[norm_q]
            return (display, path, 1.0)

        # 2. Try relaxed keys (no spaces)
        key2 = norm_q.replace(" ", "")
        if key2 in apps:
            display, path = apps[key2]
            return (display, path, 0.95)

        # 3. Word containment score
        candidates = []
        q_words = norm_q.split()
        for alias, (display, path) in apps.items():
            score = sum(1 for w in q_words if w in alias) / max(1, len(q_words))
            if score >= 0.6:  # threshold
                candidates.append((score, display, path))

        if candidates:
            candidates.sort(reverse=True)
            score, display, path = candidates[0]
            return (display, path, score)

        # 4. Fuzzy fallback with difflib against display names
        display_names = list({v[0] for v in apps.values()})
        matches = difflib.get_close_matches(query, display_names, n=1, cutoff=0.6)
        if matches:
            # find path for matched display
            target = matches[0]
            for alias, (display, path) in apps.items():
                if display == target:
                    return (display, path, 0.7)

        return None

    def _is_app_running(self, name: str) -> bool:
        """
        Determine if an application is running.
        - On macOS, prefer System Events via AppleScript for precise GUI app checks.
        - Fallback to psutil for other OSes or if AppleScript fails.
        """
        try:
            if self.system == 'Darwin':
                # Use System Events to check for an application process by display name
                script = f'tell application "System Events" to (exists application process "{name}")'
                res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                out = (res.stdout or '').strip().lower()
                if out in ('true', 'false'):
                    return out == 'true'
                # If AppleScript didn't return a boolean, fall back to psutil below
        except Exception:
            # Fall back to psutil path if AppleScript fails
            pass

        name_l = name.lower()
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = (proc.info['name'] or '').lower()
                if self._matches_process_name(proc_name, name_l):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def _matches_process_name(self, proc_name: str, target_name: str) -> bool:
        tn = target_name.lower()
        variants = {tn, tn.replace(" ", ""), tn.split()[0]}
        return any(v and v in proc_name for v in variants)

    def activate_application(self, app_name: str) -> bool:
        """
        Bring an already running application to the foreground/focus.
        On macOS, uses AppleScript 'activate'. On other OSes, this is a no-op (returns False).
        """
        try:
            if self.system == "Darwin":
                # Resolve to proper display name for AppleScript
                resolved = self._resolve_application(app_name)
                target_name = resolved[0] if resolved else app_name
                try:
                    subprocess.run([
                        "osascript", "-e", f'tell application "{target_name}" to activate'
                    ], check=False)
                    return True
                except Exception:
                    return False
            # TODO: Implement focusing on Windows/Linux if desired
            return False
        except Exception:
            return False

    def running_apps_list_sentence(self):
        """
        Build a single sentence listing the currently running user applications.
        This is intended for GUI display (no TTS).

        Returns:
            str: e.g., "sir you currently have Google Chrome, Safari and Spotify open"
        """
        apps = [a for a in self.speak_running_apps() if not self._is_system_process(a)]
        if not apps:
            return "sir, you currently have no applications open"
        # De-duplicate while preserving order
        seen = set()
        unique_apps = []
        for a in apps:
            al = a.lower()
            if al not in seen:
                seen.add(al)
                unique_apps.append(a)
        if len(unique_apps) == 1:
            apps_text = unique_apps[0]
        else:
            apps_text = ", ".join(unique_apps[:-1]) + f" and {unique_apps[-1]}"
        return f"sir you currently have {apps_text} open"

    def check_app_running_message(self, app_phrase: str):
        """
        Given a phrase for an app, resolve and report if it's running.

        Args:
            app_phrase (str): user-provided app phrase
        Returns:
            dict: { 'success': bool, 'app_name': str, 'running': bool, 'message': str }
        """
        if not app_phrase:
            return {
                'success': False,
                'app_name': 'unknown',
                'running': False,
                'message': "I'm not sure which application you mean, sir."
            }
        resolved = self._resolve_application(app_phrase)
        target = resolved[0] if resolved else app_phrase
        is_running = self._is_app_running(target)
        if is_running:
            return {
                'success': True,
                'app_name': target,
                'running': True,
                'message': f"Yes sir, {target} is currently running."
            }
        else:
            return {
                'success': True,
                'app_name': target,
                'running': False,
                'message': f"No sir, {target} is not currently running."
            }

    def _get_running_apps_macos(self):
        """
        macOS-specific: return names of GUI application processes (non-background) using System Events.
        """
        try:
            script = 'tell application "System Events" to get the name of every application process whose background only is false'
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            output = (res.stdout or '').strip()
            if not output:
                return []
            # osascript joins list with ", ", sometimes newlines; split on commas
            parts = [p.strip() for p in re.split(r",\s*|\n+", output) if p.strip()]
            # preserve order, de-dup
            seen = set()
            ordered = []
            for p in parts:
                pl = p.lower()
                if pl not in seen:
                    seen.add(pl)
                    ordered.append(p)
            # Filter obvious non-user items just in case
            banned = {"Dock", "WindowServer", "loginwindow"}
            return [p for p in ordered if p not in banned]
        except Exception as e:
            print(f"AppleScript running apps failed: {e}")
            return []

    def speak_running_apps(self):
        """
        Get list of currently running applications (user-facing GUI apps preferred on macOS)

        Returns:
            list: List of running application names
        """
        try:
            if self.system == 'Darwin':
                apps = self._get_running_apps_macos()
                if apps:
                    return sorted(apps)
                # Fall back to psutil if AppleScript returned nothing
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
            return []

    def get_running_apps_summary(self, limit=5):
        """
        Get a formatted summary of running applications for voice handler to speak

        Args:
            limit (int): Maximum number of apps to include in summary

        Returns:
            dict: Summary with 'success', 'count', 'message' keys
        """
        try:
            running_apps = self.speak_running_apps()

            if not running_apps:
                return {
                    'success': True,
                    'count': 0,
                    'message': "No user applications are currently running, sir."
                }

            # Filter and limit results
            user_apps = [app for app in running_apps if not self._is_system_process(app)]

            if len(user_apps) == 0:
                return {
                    'success': True,
                    'count': 0,
                    'message': "No user applications are currently running, sir."
                }
            elif len(user_apps) == 1:
                return {
                    'success': True,
                    'count': 1,
                    'message': f"You have {user_apps[0]} running, sir."
                }
            elif len(user_apps) <= 3:
                apps_text = ", ".join(user_apps[:-1]) + f" and {user_apps[-1]}"
                return {
                    'success': True,
                    'count': len(user_apps),
                    'message': f"You have {apps_text} running, sir."
                }
            elif len(user_apps) <= limit:
                apps_text = ", ".join(user_apps[:-1]) + f" and {user_apps[-1]}"
                return {
                    'success': True,
                    'count': len(user_apps),
                    'message': f"Sir, you have {len(user_apps)} applications running: {apps_text}."
                }
            else:
                top_apps = user_apps[:limit - 1]
                apps_text = ", ".join(top_apps)
                remaining = len(user_apps) - (limit - 1)
                return {
                    'success': True,
                    'count': len(user_apps),
                    'message': f"Sir, you have {len(user_apps)} applications running, including {apps_text}, and {remaining} others."
                }

        except Exception as e:
            print(f"Error getting running apps summary: {e}")
            return {
                'success': False,
                'count': 0,
                'message': "Sorry sir, I encountered an error while checking your running applications."
            }

    def _is_system_process(self, app_name):
        """
        Heuristic check if an item is a system/background process rather than a user app.
        Note: On macOS, when using System Events to fetch GUI apps, this is rarely needed.
        """
        system_processes = [
            # macOS core/background
            'kernel_task', 'launchd', 'WindowServer', 'Dock', 'loginwindow',
            # Windows core
            'svchost.exe', 'explorer.exe', 'winlogon.exe', 'csrss.exe',
            # Linux core
            'systemd', 'kthreadd', 'ksoftirqd',
        ]
        # Do NOT filter Finder or common GUI utilities; user expects to see them.
        name_l = app_name.lower()
        return any(sys_proc.lower() == name_l or sys_proc.lower() in name_l for sys_proc in system_processes)


# Pre-configured application shortcuts (silent operations):

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


# Quitting applications (silent operations)
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


# Enhanced voice command processing (silent operations - returns results for voice_handler to speak)
def launch_app_by_voice(command, gpt_handler=None):
    """
    Parse voice command and launch appropriate application (SILENT - no voice feedback)

    Args:
        command (str): Voice command containing app name
        gpt_handler: Optional GPT handler for intelligent parsing

    Returns:
        dict: {'success': bool, 'app_name': str, 'message': str} for voice_handler to process
    """
    launcher = AppLauncher()
    text = command.strip()
    lower = text.lower()

    # --- HARD-CODED GUARD FOR RUNNING-APPS STYLE QUERIES (prevents misrouting due to 'open'/'run' substrings) ---
    # If the phrase is actually asking about currently running apps, handle here and return early.
    try:
        import re as _re
        # 1) Yes/No for a specific app being open/running
        m = _re.search(r"^\s*is\s+(.+?)\s+(?:currently\s+)?(open|running)\??\s*$", lower)
        if m:
            app_phrase = m.group(1).strip()
            check = launcher.check_app_running_message(app_phrase)
            # Return as if we 'handled' the request (no app launch)
            return {
                'success': True,
                'app_name': check.get('app_name', app_phrase),
                'message': check.get('message', '')
            }

        # 2) How many apps are open/running?
        if ("how many" in lower) and ("app" in lower or "application" in lower or "applications" in lower or "apps" in lower) and ("open" in lower or "running" in lower or "currently open" in lower):
            summary = launcher.get_running_apps_summary()
            return {
                'success': True,
                'app_name': 'running apps',
                # Exact phrasing requested
                'message': f"You have {summary['count']} applications open sir"
            }

        # 3) Which/what apps are open/running? Or general running apps list/rundown
        list_triggers = [
            "which apps", "which applications", "what apps", "what applications",
            "what's open", "what is open", "what's running", "what is running",
            "show apps", "list apps", "running apps", "running applications", "currently running apps", "rundown"
        ]
        if any(t in lower for t in list_triggers):
            sentence = launcher.running_apps_list_sentence()
            return {
                'success': True,
                'app_name': 'running apps',
                'message': sentence
            }
    except Exception as _guard_e:
        print(f"Running-apps guard failed: {_guard_e}")
    # --- END GUARD ---

    # Prefer GPT interpretation if available
    app_phrase = None
    if gpt_handler:
        try:
            interp = gpt_handler.interpret_app_command(text)
            if interp.get('action') == 'open' and interp.get('app') and interp.get('app') != 'none':
                app_phrase = interp['app']
        except Exception as e:
            print(f"GPT interpretation failed: {e}")

    # Basic extraction if GPT didn't provide
    if not app_phrase:
        # Remove common polite/filler phrases to better isolate the app name
        fillers_pattern = r"\b(could you|would you|can you|please|be a dear and|go ahead and|would you mind|do me a favour and|do me a favor and|for me|for my deskpilot|deskpilot|the|my|a|an|app|application)\b"
        cleaned = re.sub(fillers_pattern, " ", lower)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Support multi-word triggers via regex
        patterns = [
            r"\b(open|launch|start|run)\s+(.+)$",
            r"\b(bring up|pull up|fire up|boot up|pop open)\s+(.+)$",
        ]
        for pat in patterns:
            m = re.search(pat, cleaned)
            if m:
                app_phrase = m.group(2).strip()
                break

        # Simple token fallback
        if not app_phrase:
            triggers = ['open', 'launch', 'start', 'run']
            words = cleaned.split()
            for t in triggers:
                if t in words:
                    idx = words.index(t)
                    if idx + 1 < len(words):
                        app_phrase = ' '.join(words[idx + 1:])
                        break

        # Last resort, use cleaned text
        if not app_phrase:
            app_phrase = cleaned.strip()

    if not app_phrase:
        return {
            'success': False,
            'app_name': 'unknown',
            'message': "I'm not sure which application you want to open, sir. Could you please be more specific?"
        }

    # Resolve against installed apps dynamically
    resolved = launcher._resolve_application(app_phrase)
    if resolved:
        display_name, _path, _score = resolved
        # If it's already running, focus instead of re-opening
        if platform.system() == 'Darwin' and launcher._is_app_running(display_name):
            launcher.activate_application(display_name)
            return {
                'success': True,
                'app_name': display_name,
                'message': f"Sir, {display_name} is already running, bringing it into focus now..."
            }
        success = launcher.open_application(display_name)
        return {
            'success': success,
            'app_name': display_name,
            'message': f"Opening {display_name} for you, sir." if success else f"Sorry sir, I couldn't open {display_name}. Please check if it's installed."
        }

    # If not resolved on macOS, avoid misleading attempts
    if platform.system() == 'Darwin':
        return {
            'success': False,
            'app_name': app_phrase,
            'message': f"I couldn't find {app_phrase} installed on your operating system, sir."
        }

    # Other OS: attempt generic open
    success = launcher.open_application(app_phrase)
    return {
        'success': success,
        'app_name': app_phrase,
        'message': f"Opening {app_phrase} for you, sir." if success else f"Sorry sir, I couldn't open {app_phrase}."
    }


def quit_app_by_voice(command, gpt_handler=None):
    """
    Parse voice command and quit appropriate application (SILENT - no voice feedback)

    Args:
        command (str): Voice command containing app name to quit
        gpt_handler: Optional GPT handler for intelligent parsing

    Returns:
        dict: {'success': bool, 'app_name': str, 'message': str} for voice_handler to process
    """
    launcher = AppLauncher()
    text = command.strip()
    lower = text.lower()

    # Prefer GPT interpretation if available
    app_phrase = None
    if gpt_handler:
        try:
            interp = gpt_handler.interpret_app_command(text)
            if interp.get('action') == 'quit' and interp.get('app') and interp.get('app') != 'none':
                app_phrase = interp['app']
        except Exception as e:
            print(f"GPT interpretation failed: {e}")

    # Basic extraction if GPT didn't provide
    if not app_phrase:
        # Remove common polite/filler phrases to better isolate the app name
        fillers_pattern = r"\b(could you|would you|can you|please|be a dear and|go ahead and|would you mind|do me a favour and|do me a favor and|for me|for my deskpilot|deskpilot|the|my|a|an|app|application)\b"
        cleaned = re.sub(fillers_pattern, " ", lower)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Support multi-word triggers via regex
        patterns = [
            r"\b(quit|close|stop|exit|kill)\s+(.+)$",
            r"\b(shut down|close out|end|terminate|dismiss)\s+(.+)$",
        ]
        for pat in patterns:
            m = re.search(pat, cleaned)
            if m:
                app_phrase = m.group(2).strip()
                break

        # Simple token fallback
        if not app_phrase:
            triggers = ['quit', 'close', 'stop', 'exit', 'kill']
            words = cleaned.split()
            for t in triggers:
                if t in words:
                    idx = words.index(t)
                    if idx + 1 < len(words):
                        app_phrase = ' '.join(words[idx + 1:])
                        break

        # Last resort, use cleaned text
        if not app_phrase:
            app_phrase = cleaned.strip()

    if not app_phrase:
        return {
            'success': False,
            'app_name': 'unknown',
            'message': "I'm not sure which application you want to quit, sir. Could you please specify?"
        }

    resolved = launcher._resolve_application(app_phrase)
    target_name = resolved[0] if resolved else app_phrase

    # If it's not running, report that cleanly (macOS dynamic behavior already mirrors current style)
    if platform.system() == 'Darwin' and not launcher._is_app_running(target_name):
        return {
            'success': False,
            'app_name': target_name,
            'message': f"Sir, {target_name} isn't currently running."
        }

    success = launcher.quit_application(target_name)
    return {
        'success': success,
        'app_name': target_name,
        'message': (f"I've quit {target_name} for you, sir." if success
                    else f"Sir, {target_name} doesn't appear to be running at the moment.")
    }