import speech_recognition as sr
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def listen_command(timeout=5, phrase_time_limit=10):
    """
    Listen for a voice command using Whisper for transcription

    Args:
        timeout (int): Seconds to wait for speech to begin
        phrase_time_limit (int): Max seconds for a phrase

    Returns:
        str: Transcribed command in lowercase, or empty string on error
    """
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for command...")

        try:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)

            # Listen for audio
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            print("Transcribing with Whisper...")

            # Placeholder: Whisper model is hardcoded as "base" — consider making this configurable
            query = recognizer.recognize_whisper(audio, model="base")
            print(f"You said: {query}")

            return query.lower().strip()

        except sr.WaitTimeoutError:
            print("Listening timeout - no speech detected")
            return ""

        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""

        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return ""

def get_microphone_list():
    """
    Get list of available microphones

    Returns:
        list: List of microphone names with indices
    """
    mic_list = []
    # Placeholder: No filtering or selection logic — may want to allow user to set default mic
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        mic_list.append(f"{index}: {name}")
    return mic_list
