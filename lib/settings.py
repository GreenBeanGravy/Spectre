import configparser
import os
import soundfile as sf
import pyaudio
from termcolor import colored

# Save settings to settings.ini file
def save_settings(settings):
    with open("settings.ini", "w") as settings_file:
        settings.write(settings_file)

# Load settings from settings.ini file
def load_settings():
    settings = configparser.ConfigParser()
    settings.read("settings.ini")
    return settings

# Update and return settings
def update_settings(settings):
    # Set default values if not present
    if "General" not in settings:
        settings["General"] = {}
    if "duration_threshold" not in settings["General"]:
        settings["General"]["duration_threshold"] = "0.5"
    if "center_radius" not in settings["General"]:
        settings["General"]["center_radius"] = "100"
    if "show_detections_window" not in settings["General"]:
        settings["General"]["show_detections_window"] = "True"
    if "confidence_threshold" not in settings["General"]:
        settings["General"]["confidence_threshold"] = "0.5"

    save_settings(settings)
    return settings
