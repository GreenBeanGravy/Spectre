import configparser
import pyautogui
import time
import threading
import cv2
from PIL import ImageGrab
import numpy as np
import os
import keyboard
import winsound
import tkinter as tk
from tkinter import ttk
import soundfile as sf
import pyaudio
from termcolor import colored
import dlib
import pygame
from accessible_output2.outputs.auto import Auto
from scipy.optimize import linear_sum_assignment
from collections import defaultdict
import torch

from lib.gui import create_tkinter_gui
from lib.panning import apply_panning
from lib.settings import save_settings, load_settings, update_settings, prompt_settings
from lib.screendetector import detector


if __name__ == '__main__':
    settings = load_settings()
    settings = update_settings(settings)
    use_existing_settings = input("Do you want to use existing settings? (y/n): ")
    if use_existing_settings.lower() != "y":
        prompt_settings(settings)

    detection_duration_threshold = float(settings["General"]["duration_threshold"])
    center_radius = int(settings["General"]["center_radius"])
    show_detections_window = settings["General"]["show_detections_window"].lower() == "true"
    confidence_threshold = float(settings["General"]["confidence_threshold"])

    detection_area_width = int(settings["General"]["detection_area_width"])
    detection_area_height = int(settings["General"]["detection_area_height"])
    
    show_detections_window = settings["General"]["show_detections_window"] == "True"
    detector = detector(detection_duration_threshold, center_radius, confidence_threshold, show_detections_window, detection_area_width, detection_area_height)

    threading.Thread(target=create_tkinter_gui, args=(settings, detector)).start()

    detector.run()
