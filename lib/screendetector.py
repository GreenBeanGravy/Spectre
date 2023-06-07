import cv2
import torch
import numpy as np
import os
import pyautogui
import pygame
import keyboard
import time
import dlib
import winsound
import tkinter as tk
import threading
import soundfile as sf
import pyaudio
from termcolor import colored

from lib.panning import apply_panning
from lib.settings import save_settings, load_settings, update_settings, prompt_settings

class detector:
    def __init__(self, detection_window_option, detection_duration_threshold, center_radius, confidence_threshold, show_detections_window):

        self.detection_window_option = detection_window_option
        self.detection_duration_threshold = detection_duration_threshold
        self.center_radius = center_radius
        self.optimal_border_option = (200, 200, 1600, 800)
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
        x1, y1, x2, y2 = self.optimal_border_option
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
                ignored_x1, ignored_y1, ignored_x2, ignored_y2 = 675, 600, 800, 800
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
            x1, y1, x2, y2 = self.optimal_border_option
            cv2.rectangle(screen_np, (x1, y1), (x2, y2), (0, 255, 255), 2)

            # Draw the bounding box
            if self.detection_window_option == (100, 300, 1600, 900):
                cv2.rectangle(screen_np, (675, 600), (800, 800), (100, 0, 255), 2)

            if cv2.waitKey(1) == ord('q'):
                break

            if self.show_detections_window:
                cv2.imshow("Visual Debug Window", screen_np)

        if window_exists:
            cv2.destroyWindow("Visual Debug Window")

        cv2.destroyAllWindows()
