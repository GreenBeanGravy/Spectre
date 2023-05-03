import configparser
import cv2
import torch
import numpy as np
import os
import pyautogui
import pygame
import keyboard
import time
from scipy.optimize import linear_sum_assignment
from collections import defaultdict
from termcolor import colored
from PIL import ImageGrab
import dlib
import winsound
import tkinter as tk
from tkinter import ttk
import threading
from accessible_output2.outputs.auto import Auto
import soundfile as sf
import pyaudio

def apply_panning(data, pan, panning_power=2):
    pan = min(max(0, pan), 2)  # Clamp pan value between 0 and 2
    if pan <= 1:
        left_gain = (1 - pan) ** panning_power
        right_gain = pan ** panning_power
    else:
        left_gain = (2 - pan) ** panning_power
        right_gain = (pan - 1) ** panning_power

    if len(data.shape) > 1:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
    else:
        left_channel = right_channel = data

    stereo_data = np.column_stack((left_channel * left_gain, right_channel * right_gain))
    return stereo_data

class Speaker:
    def __init__(self):
        self.output = Auto()

    def speak(self, text):
        self.output.speak(text)

speaker = Speaker()

def create_tkinter_gui(settings, detector):

    def apply_settings():
        settings["General"]["duration_threshold"] = duration_var.get()
        settings["General"]["center_radius"] = center_radius_var.get()
        settings["General"]["show_detections_window"] = str(show_detections_var.get())
        settings["General"]["confidence_threshold"] = confidence_var.get()
    
        # Apply Settings when the "Apply" button is pressed
        detector.detection_duration_threshold = float(settings["General"]["duration_threshold"])
        detector.center_radius = int(settings["General"]["center_radius"])
        detector.show_detections_window = settings["General"]["show_detections_window"].lower() == "true"
        detector.confidence_threshold = float(settings["General"]["confidence_threshold"])

    def save_and_apply_settings():
        apply_settings()
        save_settings(settings)

    root = tk.Tk()
    root.title("Settings")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky="NSEW")

    # Duration threshold
    duration_label = ttk.Label(frame, text="Duration Threshold (0 to 1):")
    duration_label.grid(column=0, row=0, sticky="W")
    duration_var = tk.StringVar(value=settings["General"]["duration_threshold"])
    duration_entry = ttk.Entry(frame, textvariable=duration_var)
    duration_entry.grid(column=1, row=0, sticky="W")

    # Center radius
    center_radius_label = ttk.Label(frame, text="Center Radius (in pixels):")
    center_radius_label.grid(column=0, row=1, sticky="W")
    center_radius_var = tk.StringVar(value=settings["General"]["center_radius"])
    center_radius_entry = ttk.Entry(frame, textvariable=center_radius_var)
    center_radius_entry.grid(column=1, row=1, sticky="W")

    # Show detections window
    show_detections_label = ttk.Label(frame, text="Show Detections Window:")
    show_detections_label.grid(column=0, row=2, sticky="W")
    show_detections_var = tk.BooleanVar(value=settings["General"]["show_detections_window"] == "True")
    show_detections_checkbutton = ttk.Checkbutton(frame, variable=show_detections_var)
    show_detections_checkbutton.grid(column=1, row=2, sticky="W")

    # Confidence threshold
    confidence_label = ttk.Label(frame, text="Confidence Threshold (0 to 1):")
    confidence_label.grid(column=0, row=3, sticky="W")
    confidence_var = tk.StringVar(value=settings["General"]["confidence_threshold"])
    confidence_entry = ttk.Entry(frame, textvariable=confidence_var)
    confidence_entry.grid(column=1, row=3, sticky="W")

    # Apply and Save buttons
    apply_button = ttk.Button(frame, text="Apply", command=apply_settings)
    apply_button.grid(column=0, row=4, pady=(10, 0), sticky="W")
    save_button = ttk.Button(frame, text="Save", command=save_and_apply_settings)
    save_button.grid(column=1, row=4, pady=(10, 0), sticky="W")

    duration_label.bind('<Enter>', lambda e: speaker.speak("Duration Threshold (0 to 1)"))
    center_radius_label.bind('<Enter>', lambda e: speaker.speak("Center Radius (in pixels)"))
    show_detections_label.bind('<Enter>', lambda e: speaker.speak("Show Detections Window"))
    confidence_label.bind('<Enter>', lambda e: speaker.speak("Confidence Threshold (0 to 1)"))
    
    duration_entry.bind('<FocusIn>', lambda e: speaker.speak("Edit Box, Duration Threshold (0 to 1)"))
    center_radius_entry.bind('<FocusIn>', lambda e: speaker.speak("Edit Box, Center Radius (in pixels)"))
    show_detections_checkbutton.bind('<FocusIn>', lambda e: speaker.speak(f"Checkbox, Show Detections Window, {'checked' if show_detections_var.get() else 'not checked'}"))
    confidence_entry.bind('<FocusIn>', lambda e: speaker.speak("Edit Box, Confidence Threshold (0 to 1)"))
    apply_button.bind('<FocusIn>', lambda e: speaker.speak("Apply, Button"))
    save_button.bind('<FocusIn>', lambda e: speaker.speak("Save, Button"))
    
    # Set the takefocus attribute for each widget
    duration_entry.configure(takefocus=1)
    center_radius_entry.configure(takefocus=1)
    show_detections_checkbutton.configure(takefocus=1)
    confidence_entry.configure(takefocus=1)
    apply_button.configure(takefocus=1)
    save_button.configure(takefocus=1)

    root.mainloop()

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

class YOLOv5ScreenDetector:
    def __init__(self, detection_window_option, detection_duration_threshold, center_radius, confidence_threshold, show_detections_window):

        self.detection_window_option = detection_window_option
        self.detection_duration_threshold = detection_duration_threshold
        self.center_radius = center_radius
        self.optimal_border_option = (100, 300, 1600, 900)
        self.confidence_threshold = confidence_threshold
        self.show_detections_window = show_detections_window

        pygame.mixer.init()
        self.detection_times = {}
        self.prev_detections = []
        self.detection_counter = 0
        self.detection_ids = {}
        self.trackers = {}

        print("[INFO] Loading the neural network model")
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path='lib/best.pt', force_reload=False)
        if torch.cuda.is_available():
            print(colored("CUDA ACCELERATION [ENABLED]", "green"))
        else:
            print(colored("[!] CUDA ACCELERATION IS UNAVAILABLE", "red"))
            print(colored("[!] Performance might suffer. CUDA Acceleration only works on NVIDIA GPUs.", "red"))

        self.left_sound = pygame.mixer.Sound("lib/trackingbeeps/trackingleft.wav")
        self.right_sound = pygame.mixer.Sound("lib/trackingbeeps/trackingright.wav")
        self.center_sound = pygame.mixer.Sound("lib/trackingbeeps/trackinglocked.wav")
        self.sound_enabled = True

    def reset_trackers(self):
        self.trackers = {}

    def is_detection_inside_area(self, x1, y1, x2, y2, area):
        x1_area, y1_area, x2_area, y2_area = area

        return x1 >= x1_area and y1 >= y1_area and x2 <= x2_area and y2 <= y2_area

    def is_new_detection(self, x1, y1, x2, y2, threshold=50):
        for tracker_id, tracker in self.trackers.items():
            pos = tracker.get_position()
            tx1, ty1, tx2, ty2 = int(pos.left()), int(pos.top()), int(pos.right()), int(pos.bottom())
            dist = np.sqrt((x1 - tx1) ** 2 + (y1 - ty1) ** 2 + (x2 - tx2) ** 2 + (y2 - ty2) ** 2)
            if dist < threshold:
                return False
        return True

    def update_trackers(self, screen_np):
        updated_trackers = {}

        for tracker_id, tracker in self.trackers.items():
            # Check if the tracker confidence is above a threshold (e.g., 0.5)
            if tracker.update(screen_np) > 0.7:
                pos = tracker.get_position()
                x1, y1, x2, y2 = int(pos.left()), int(pos.top()), int(pos.right()), int(pos.bottom())

                updated_trackers[tracker_id] = tracker
                cv2.rectangle(screen_np, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(screen_np, str(tracker_id), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        self.trackers = updated_trackers

    def detect_objects_on_screen(self):
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

        # Crop the screen to the detection area
        x1, y1, x2, y2 = self.detection_window_option
        detection_area_np = screen_np[y1:y2, x1:x2]

        results = self.model(detection_area_np)
        detections = results.pandas().xyxy[0]

        max_trackers = 3

        for _, row in detections.iterrows():
            if row['confidence'] < self.confidence_threshold:
                continue

            x1_d, y1_d, x2_d, y2_d = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])

            # Adjust the coordinates to be relative to the full screen
            x1, y1, x2, y2 = x1_d + x1, y1_d + y1, x2_d + x1, y2_d + y1

            # Define the ignored region based on the chosen detection window option
            if self.detection_window_option == (100, 300, 1600, 900):
                ignored_x1, ignored_y1, ignored_x2, ignored_y2 = 600, 600, 800, 800
            else:
                ignored_x1, ignored_y1, ignored_x2, ignored_y2 = -1, -1, -1, -1

            ignore_detection = False
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    if ignored_x1 <= x <= ignored_x2 and ignored_y1 <= y <= ignored_y2:
                        ignore_detection = True
                        break
                if ignore_detection:
                    break

            if ignore_detection:
                continue

            cv2.rectangle(screen_np, (x1, y1), (x2, y2), (0, 255, 0), 2)

            if self.detection_window_option == (100, 300, 1600, 900):
                if self.is_detection_inside_area(x1, y1, x2, y2, self.optimal_border_option):
                    cv2.rectangle(screen_np, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    if len(self.trackers) < max_trackers:
                        tracker = dlib.correlation_tracker()
                        tracker.start_track(screen_np, dlib.rectangle(x1, y1, x2, y2))
                        tracker_id = len(self.trackers)
                        self.trackers[tracker_id] = tracker

        self.update_trackers(screen_np)

        return detections, screen_np

    def get_detection_id(self, x1, y1, x2, y2):
        detection_key = (x1, y1, x2, y2)
        if detection_key not in self.detection_ids:
            self.detection_ids[detection_key] = self.detection_counter
            self.detection_counter += 1

        return self.detection_ids[detection_key]

    def play_sound_based_on_position(self, x_center, y_center, screen_width, screen_height):
        if not self.sound_enabled:
            return

        volume_factor = 2
    
        # Calculate the pan value based on the position relative to the center
        pan = (x_center - screen_width / 2) / (screen_width / 2)
        pan = (pan + 1) / 2  # Normalize the pan value to be between 0 and 2
    
        # Function to play the audio using PyAudio
        def play_audio(filename, pan_value):
            # Load the audio file
            data, samplerate = sf.read(filename, dtype='float32')
    
            # Apply panning
            stereo_data = apply_panning(data, audio_pan) * volume_factor
    
            pa = pyaudio.PyAudio()
            stream = pa.open(format=pyaudio.paFloat32,
                             channels=2,
                             rate=samplerate,
                             output=True)
    
            stream.write(stereo_data.tobytes())
            stream.stop_stream()
            stream.close()
            pa.terminate()
    
        # Check if the detection is inside the center_radius
        if (screen_width / 2 - self.center_radius) < x_center < (screen_width / 2 + self.center_radius) and \
                (screen_height / 2 - self.center_radius) < y_center < (screen_height / 2 + self.center_radius):
            audio_file = "lib/trackingbeeps/trackinglocked.wav"
            audio_pan = 0.5  # Play the audio in the center
        else:
            audio_file = "lib/trackingbeeps/tracking.wav"
            audio_pan = pan
    
        # Start a separate thread to play the audio
        audio_thread = threading.Thread(target=play_audio, args=(audio_file, audio_pan))
        audio_thread.start()
    
        self.reset_trackers()

    def process_detections(self):
        screen_width, screen_height = pyautogui.size()
    
        current_time = time.time()
    
        closest_detection = None
        min_distance_to_center = float('inf')
    
        for tracker_id, tracker in self.trackers.items():
            pos = tracker.get_position()
            x1, y1, x2, y2 = int(pos.left()), int(pos.top()), int(pos.right()), int(pos.bottom())
    
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
    
            if tracker_id not in self.detection_times:
                self.detection_times[tracker_id] = current_time
    
            time_detected = current_time - self.detection_times[tracker_id]
    
            if time_detected >= self.detection_duration_threshold:
                distance_to_center = ((x_center - screen_width / 2) ** 2 + (y_center - screen_height / 2) ** 2) ** 0.5
                if distance_to_center < min_distance_to_center:
                    min_distance_to_center = distance_to_center
                    closest_detection = (x_center, y_center)

        if closest_detection is not None:
            self.play_sound_based_on_position(closest_detection[0], closest_detection[1], screen_width, screen_height)
    
        # Remove inactive detections from self.detection_times
        active_detection_ids = set(self.trackers.keys())
        inactive_detection_ids = set(self.detection_times.keys()) - active_detection_ids
        for detection_id in inactive_detection_ids:
            del self.detection_times[detection_id]

    def run(self):
        f5_key_pressed = False

        while True:
            try:
                window_exists = cv2.getWindowProperty("Visual Debug Window", 0) >= 0
            except cv2.error:
                window_exists = False
    
            if self.show_detections_window:
                if not window_exists:
                    cv2.namedWindow("Visual Debug Window", cv2.WINDOW_NORMAL)
                    cv2.resizeWindow("Visual Debug Window", pyautogui.size())
            else:
                if window_exists:
                    cv2.destroyWindow("Visual Debug Window")

            if keyboard.is_pressed('F5'):
                if not f5_key_pressed:
                    self.sound_enabled = not self.sound_enabled
                    if self.sound_enabled:
                        print("Sound enabled")
                        winsound.Beep(1000, 200)  # Play a high-pitched beep when sound is enabled
                    else:
                        print("Sound disabled")
                        winsound.Beep(500, 200)  # Play a low-pitched beep when sound is disabled
                f5_key_pressed = True
            else:
                f5_key_pressed = False

            if keyboard.is_pressed('F6'):
                print("Shutting down script...")
                os._exit(0)  # Terminate the program immediately

            detections, screen_np = self.detect_objects_on_screen()
            self.process_detections()

            # Draw the blue center zone square
            screen_width, screen_height = pyautogui.size()
            cv2.rectangle(screen_np, (screen_width // 2 - self.center_radius, screen_height // 2 - self.center_radius),
                          (screen_width // 2 + self.center_radius, screen_height // 2 + self.center_radius), (255, 0, 0), 2)
    
            # Draw the detection area outline
            x1, y1, x2, y2 = self.detection_window_option
            cv2.rectangle(screen_np, (x1, y1), (x2, y2), (0, 255, 255), 2)

            # Draw the bounding box
            if self.detection_window_option == (100, 300, 1600, 900):
                cv2.rectangle(screen_np, (600, 600), (800, 800), (100, 0, 255), 2)

            if cv2.waitKey(1) == ord('q'):
                break

            if self.show_detections_window:
                cv2.imshow("Visual Debug Window", screen_np)

        if window_exists:
            cv2.destroyWindow("Visual Debug Window")

        cv2.destroyAllWindows()

if __name__ == '__main__':
    chosen_option = (100, 300, 1600, 900)
    settings = load_settings()
    settings = update_settings(settings)
    use_existing_settings = input("Do you want to use existing settings? (y/n): ")
    if use_existing_settings.lower() != "y":
        prompt_settings(settings)

    detection_duration_threshold = float(settings["General"]["duration_threshold"])
    center_radius = int(settings["General"]["center_radius"])
    show_detections_window = settings["General"]["show_detections_window"].lower() == "true"
    confidence_threshold = float(settings["General"]["confidence_threshold"])
    
    show_detections_window = settings["General"]["show_detections_window"] == "True"
    detector = YOLOv5ScreenDetector(chosen_option, detection_duration_threshold, center_radius, confidence_threshold, show_detections_window)

    threading.Thread(target=create_tkinter_gui, args=(settings, detector)).start()

    detector.run()