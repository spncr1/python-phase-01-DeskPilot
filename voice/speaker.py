import pygame
import time
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from elevenlabs import play
from config import elevenlabs_client, ELEVENLABS_VOICE_ID, ASSISTANT_NAME

# Global transcription log reference (to be set by UI)
TRANSCRIPTION_LOG = None  # PLACEHOLDER: This will be set from the UI


def _log_to_transcription_box(text):
    """
    Append text to the transcription log in the UI.
    """
    if TRANSCRIPTION_LOG is not None:
        TRANSCRIPTION_LOG.insert("end", text + "\n")
        TRANSCRIPTION_LOG.see("end")
    else:
        print(text)  # Fallback for debugging


def speak(text, voice_id=ELEVENLABS_VOICE_ID):
    """
    Convert text to speech using ElevenLabs TTS
    """
    print(f"{ASSISTANT_NAME} says: {text}")
    _log_to_transcription_box(f"{ASSISTANT_NAME} says: {text}")

    try:
        # Generate audio using ElevenLabs
        audio = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        play(audio)

    except Exception as e:
        print(f"Error in ElevenLabs TTS: {e}")
        try:
            _fallback_pygame_tts(text, voice_id)
        except Exception as fallback_error:
            print(f"Fallback TTS also failed: {fallback_error}")


def speak_dynamic(fixed_text=None):
    """
    Speak a fixed phrase or a GPT-generated dynamic response.

    Args:
        fixed_text (str): Optional fixed string to speak.
    """
    if fixed_text:
        text_to_speak = fixed_text
    else:
        # PLACEHOLDER: GPT-generated speech content will go here
        text_to_speak = "Hello, this is your assistant speaking."

    speak(text_to_speak)


def _fallback_pygame_tts(text, voice_id):
    """
    Fallback TTS method using pygame (requires pre-generated audio)
    """
    try:
        audio = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(audio)
            temp_audio_path = temp_file.name

        pygame.mixer.init()
        pygame.mixer.music.load(temp_audio_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        os.remove(temp_audio_path)

    except Exception as e:
        print(f"Pygame fallback failed: {e}")


def play_sound_file(file_path):
    """
    Play a sound file using pygame
    """
    try:
        if os.path.exists(file_path):
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        else:
            print(f"Sound file not found: {file_path}")
    except Exception as e:
        print(f"Error playing sound file: {e}")
