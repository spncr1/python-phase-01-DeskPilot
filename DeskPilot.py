# Entry point for project (i.e., the main menu / home screen)

# add the following imports to their specific files later, for now keep here so i remember where each goes

# Std Lib
import os
import sys
import subprocess
from pathlib import Path

# GUI
import tkinter as tk
from gui.main_menu import build_main_menu # placehodler for when i build main_menu.py in the GUI folder

# File handling & parsing
import shutil
import fitz # PyMuPDF for PDF parsing
import docx # python-docx for Word docs

# Data handling (placeholder for future .csv file handling expansion)
import csv
import pandas as pd

# OpenAI API
import openai

# ElevenLabs API
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# Voice I/O
import speech_recognition as sr
from gtts import gTTS
import playsound

# Environment variables
from dotenv import load_dotenv

if __name__ == "__main__":
    root = tk.Tk()
    root.title("DeskPilot")
    root.geometry("400x400")

    build_main_menu(root)

    root.mainloop()