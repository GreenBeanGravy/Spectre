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

# Prompt user for settings
def prompt_settings(settings):
    duration_input = input("Enter the duration a player has to be on screen in order to play a sound. Lower values sacrifice accuracy for speed, while higher values sacifice speed for accuracy. (0 to 1): ")
    while duration_input != "" and (not duration_input.replace(".", "").isdigit() or not 0 <= float(duration_input) <= 1):
        print("Invalid input. Please enter a valid number between 0 and 1, or leave blank for the default value (0.5).")
        duration_input = input("Enter the duration a player has to be on screen in order to play a sound. Lower values sacrifice accuracy for speed, while higher values sacifice speed for accuracy. (0 to 1): ")

    if duration_input != "":
        settings["General"]["duration_threshold"] = duration_input

    center_radius_input = input("Enter the size (in pixels) of the detection zone for playing the Tracking sound whenever a player/detection is centered on screen. (Default: 100): ")
    while center_radius_input != "" and (not center_radius_input.isdigit() or int(center_radius_input) < 0):
        print("Invalid input. Please enter a positive integer or leave blank for the default value (100).")
        center_radius_input = input("Enter the size (in pixels) of the detection zone for playing the Tracking sound whenever a player/detection is centered on screen. (Default: 100): ")

    if center_radius_input != "":
        settings["General"]["center_radius"] = center_radius_input
    else:
        settings["General"]["center_radius"] = "100"

    display_window_input = input("Do you want to display the 'Visual Debug Window' window? (y/n): ")
    while display_window_input.lower() not in ["y", "n"]:
        print("Invalid input. Please enter 'y' or 'n'.")
        display_window_input = input("Do you want to display the 'Visual Debug Window' window? (y/n): ")

    settings["General"]["show_detections_window"] = str(display_window_input.lower() == "y")

    confidence_input = input("Enter the confidence threshold for player detections. Higher values decrease the likelyhood of false detections, but values too high can prevent players from being detected. Lower values subsequently increase the likelyhood of false detections, but gurentee that players actually get detected. It is reccomended to not change this value from the default of 0.65 unless issues occur. (0 to 1, default is 0.65): ")
    while confidence_input != "" and (not confidence_input.replace(".", "").isdigit() or not 0 <= float(confidence_input) <= 1):
        print("Invalid input. Please enter a valid number between 0 and 1, or leave blank for the default value (0.65).")
        confidence_input = input("Enter the confidence threshold for player detections. (0 to 1, default is 0.65): ")

    if confidence_input != "":
        settings["General"]["confidence_threshold"] = confidence_input
    else:
        settings["General"]["confidence_threshold"] = "0.65"

    save_settings(settings)