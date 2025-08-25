#!/usr/bin/env python3
"""
Speaker module for DeskPilot using ElevenLabs TTS
"""

import os
import threading
import time
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Try to import voice ID from config, fallback to env only if not available
try:
    from config import ELEVENLABS_VOICE_ID as CONFIG_ELEVENLABS_VOICE_ID
except Exception:
    CONFIG_ELEVENLABS_VOICE_ID = None

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play

    ELEVENLABS_AVAILABLE = True
    print("✓ ElevenLabs imported successfully")
except ImportError as e:
    ELEVENLABS_AVAILABLE = False
    print(f"❌ ElevenLabs not available: {e}")

# Global transcription log reference (set by GUI)
TRANSCRIPTION_LOG = None


class VoiceSpeaker:
    """Handles text-to-speech using ElevenLabs API - FIXED to prevent feedback"""

    def __init__(self):
        self.is_speaking = False
        self.speaking_lock = threading.Lock()
        self._speech_finished_callback = None  # NEW: Callback for when speech finishes

        # Get API credentials from environment
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        # Determine voice ID: ENV takes precedence, then config, then fallback default
        env_voice = os.getenv("ELEVENLABS_VOICE_ID")
        self.voice_id = (env_voice or CONFIG_ELEVENLABS_VOICE_ID or "PYVunL4QLJz0auimQhZB").strip()

        # Initialize ElevenLabs client
        self.elevenlabs_client = None

        if ELEVENLABS_AVAILABLE and self.api_key:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=self.api_key)
                print(f"✓ ElevenLabs TTS initialized with voice ID: {self.voice_id}")

                # Test the connection
                try:
                    voices = list(self.elevenlabs_client.voices.get_all())
                    print(f"✓ ElevenLabs API verified. Found {len(voices)} voices.")
                except Exception as test_e:
                    print(f"⚠️ ElevenLabs API test failed: {test_e}")

            except Exception as e:
                print(f"❌ ElevenLabs initialization failed: {e}")
                self.elevenlabs_client = None
        else:
            if not self.api_key:
                print("❌ ELEVENLABS_API_KEY not found in environment variables")
            print("❌ ElevenLabs TTS not available - using fallback")

    def speak(self, text, log_to_transcription=True, on_finished_callback=None):
        """
        Convert text to speech using ElevenLabs TTS
        FIXED: Now supports callback when speech finishes

        Args:
            text (str): Text to speak
            log_to_transcription (bool): Whether to log to GUI transcription box
            on_finished_callback (callable): Called when speech finishes (NEW)
        """
        if not text or not text.strip():
            return

        print(f"🎤 DeskPilot says: {text}")

        # Store callback
        self._speech_finished_callback = on_finished_callback

        # Log to transcription if available
        if log_to_transcription and TRANSCRIPTION_LOG:
            try:
                def add_to_log():
                    TRANSCRIPTION_LOG.config(state="normal")
                    TRANSCRIPTION_LOG.insert("end", f"(DeskPilot) says: {text}\n")
                    TRANSCRIPTION_LOG.see("end")
                    TRANSCRIPTION_LOG.config(state="disabled")

                # Try to call on main thread if possible
                if hasattr(TRANSCRIPTION_LOG, 'after'):
                    TRANSCRIPTION_LOG.after(0, add_to_log)
                else:
                    add_to_log()
            except Exception as e:
                print(f"Failed to log to transcription: {e}")

        # Start speaking in a separate thread to avoid blocking
        threading.Thread(target=self._speak_threaded, args=(text,), daemon=True).start()

    def _speak_threaded(self, text):
        """Internal method to handle TTS in a separate thread - FIXED with proper callback"""
        with self.speaking_lock:
            if self.is_speaking:
                return  # Already speaking

            self.is_speaking = True

            try:
                if self.elevenlabs_client:
                    print("🔊 Using ElevenLabs TTS")
                    self._speak_elevenlabs(text)
                else:
                    print("🔊 Using fallback TTS")
                    self._speak_fallback(text)
            except Exception as e:
                print(f"❌ TTS Error: {e}")
                print("🔊 Falling back to system TTS")
                self._speak_fallback(text)
            finally:
                self.is_speaking = False

                # FIXED: Call the callback when speech is completely finished
                if self._speech_finished_callback:
                    try:
                        self._speech_finished_callback()
                    except Exception as e:
                        print(f"❌ Callback error: {e}")
                    finally:
                        self._speech_finished_callback = None

    def _speak_elevenlabs(self, text):
        """Use ElevenLabs TTS - exactly like your working code"""
        try:
            print(f"🎵 Generating ElevenLabs audio...")

            # Use your working ElevenLabs implementation
            audio = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",  # Using your model
                output_format="mp3_44100_128"
            )

            # Play audio using ElevenLabs helper play() - like your working code
            play(audio)

            print("✓ ElevenLabs TTS playback complete")

            # FIXED: Add small buffer to ensure audio system clears
            time.sleep(0.5)  # 500ms buffer

        except Exception as e:
            print(f"❌ ElevenLabs TTS failed: {e}")
            raise

    def _speak_fallback(self, text):
        """Fallback TTS method (system TTS)"""
        print(f"🔄 FALLBACK TTS: {text}")

        try:
            import platform
            system = platform.system()

            if system == "Darwin":  # macOS
                # Escape quotes properly for shell
                escaped_text = text.replace('"', '\\"').replace("'", "\\'")
                os.system(f'say "{escaped_text}"')
                print("✓ macOS TTS completed")
            elif system == "Windows":
                escaped_text = text.replace("'", "''")
                os.system(
                    f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{escaped_text}\')"')
                print("✓ Windows TTS completed")
            elif system == "Linux":
                escaped_text = text.replace('"', '\\"')
                os.system(f'espeak "{escaped_text}"')
                print("✓ Linux TTS completed")
            else:
                print(f"DeskPilot says: {text}")

            # FIXED: Add buffer for system TTS too
            time.sleep(1.0)  # 1 second buffer for system TTS

        except Exception as e:
            print(f"❌ System TTS failed: {e}")
            print(f"DeskPilot says: {text}")

    def speak_and_wait(self, text, log_to_transcription=True):
        """
        NEW METHOD: Speak and wait until completely finished (synchronous)
        Use this when you need to ensure speech finishes before continuing
        """
        if not text or not text.strip():
            return

        finished_event = threading.Event()

        def on_finished():
            finished_event.set()

        self.speak(text, log_to_transcription, on_finished)

        # Wait for user to finish the speech for their request...
        finished_event.wait(timeout=30)  # 30 second timeout

    def stop_speaking(self):
        """Stop current speech"""
        self.is_speaking = False
        print("🛑 Speech stopped")


# Global speaker instance
_speaker = VoiceSpeaker()


def speak(text, log_to_transcription=True, on_finished_callback=None):
    """
    Global speak function - UPDATED with callback support

    Args:
        text (str): Text to speak
        log_to_transcription (bool): Whether to log to GUI transcription box
        on_finished_callback (callable): Called when speech finishes
    """
    _speaker.speak(text, log_to_transcription, on_finished_callback)


def speak_and_wait(text, log_to_transcription=True):
    """
    NEW: Speak and wait until completely finished (synchronous)
    Use this when you need to ensure speech finishes before listening
    """
    _speaker.speak_and_wait(text, log_to_transcription)


def stop_speaking():
    """Stop current speech"""
    _speaker.stop_speaking()


def is_speaking():
    """Check if currently speaking"""
    return _speaker.is_speaking


# For testing
if __name__ == "__main__":
    print("🧪 Testing DeskPilot voice...")
    speak_and_wait("Hello sir, this is DeskPilot. Voice system is working correctly.")
    print("✅ Voice test complete - no feedback should occur.")