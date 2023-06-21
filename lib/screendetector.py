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
from accessible_output2.outputs.auto import Auto
from termcolor import colored

from lib.panning import apply_panning
from lib.settings import save_settings, load_settings, update_settings
speaker = Auto()

class detector:
    def __init__(self, detection_duration_threshold, center_radius, confidence_threshold, show_detections_window, detection_area_width, detection_area_height):
        self.detection_duration_threshold = detection_duration_threshold
        self.center_radius = center_radius
        self.confidence_threshold = confidence_threshold
        self.show_detections_window = show_detections_window
        self.detection_area_width = detection_area_width
        self.detection_area_height = detection_area_height

        self.ignore_box_x1 = 0
        self.ignore_box_y1 = self.detection_area_height // 2
        self.ignore_box_x2 = self.detection_area_width // 4
        self.ignore_box_y2 = self.detection_area_height
        self.last_reset_time = time.time()

        pygame.mixer.init()
        self.detection_times = {}
        self.detection_counter = 0
        self.trackers = {}
        self.sound_enabled = True



        print("[INFO] Loading the neural network model")
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path='lib/best.pt', force_reload=False)
        if torch.cuda.is_available():
            print(colored("CUDA ACCELERATION [ENABLED]", "green"))
        else:
            print(colored("[!] CUDA ACCELERATION IS UNAVAILABLE", "red"))
            print(colored("[!] Performance might suffer. CUDA Acceleration only works on NVIDIA GPUs.", "red"))

    def reset_trackers(self):
        self.trackers = {}
        self.last_reset_time = time.time()

    def update_trackers(self, screen_np):
        updated_trackers = {}

        for tracker_id, tracker in self.trackers.items():
            # Check if the tracker confidence is above a threshold (e.g., 0.5)
            if tracker.update(screen_np) > 0.7:
                pos = tracker.get_position()
                tx1, ty1, tx2, ty2 = int(pos.left()), int(pos.top()), int(pos.right()), int(pos.bottom())

                updated_trackers[tracker_id] = tracker
                cv2.rectangle(screen_np, (tx1, ty1), (tx2, ty2), (0, 0, 255), 2)
                cv2.putText(screen_np, str(tracker_id), (tx1, ty1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        self.trackers = updated_trackers

    def detect_objects_on_screen(self):
        screen_width, screen_height = pyautogui.size()
        screen_center_x = screen_width // 2
        screen_center_y = screen_height // 2
        
        # Calculate the coordinates for capturing the screenshot
        x1 = screen_center_x - self.detection_area_width // 2
        y1 = screen_center_y - self.detection_area_height // 2
        x2 = x1 + self.detection_area_width
        y2 = y1 + self.detection_area_height
    
        # Take a screenshot of the specified region
        screen = pyautogui.screenshot(region=(x1, y1, self.detection_area_width, self.detection_area_height))
        screen_np = np.array(screen)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
    
        results = self.model(screen_np)
        detections = results.pandas().xyxy[0]
    
        max_trackers = 1
    
        # Draw the ignore box on the bottom left corner
        cv2.rectangle(screen_np, (self.ignore_box_x1, self.ignore_box_y1), 
                     (self.ignore_box_x2, self.ignore_box_y2), (0, 0, 255), 2)
    
        for _, row in detections.iterrows():
            x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
    
            # Check if the detection is inside the ignore box
            if (self.ignore_box_x1 < (x1 + x2) / 2 < self.ignore_box_x2) and (self.ignore_box_y1 < (y1 + y2) / 2 < self.ignore_box_y2):
                row['confidence'] -= 1  # Decrease the confidence by 1
                if row['confidence'] < 0:  # Ensure that confidence does not go below 0
                    row['confidence'] = 0
    
            if row['confidence'] < self.confidence_threshold:
                continue
    
            # Adjust the coordinates to be relative to the custom-sized screenshot
            x1, y1, x2, y2 = x1, y1, x2, y2
    
            cv2.rectangle(screen_np, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
            if len(self.trackers) < max_trackers:
                tracker = dlib.correlation_tracker()
                tracker.start_track(screen_np, dlib.rectangle(x1, y1, x2, y2))
                tracker_id = len(self.trackers)
                self.trackers[tracker_id] = tracker
    
        self.update_trackers(screen_np)
    
        return detections, screen_np
    
        
    def play_sound_based_on_position(self, x_center, y_center, screen_width, screen_height):
        if not self.sound_enabled:
            return
    
        volume_factor = 2
    
        # Calculate the pan value based on the position relative to the custom-sized screenshot
        pan = (x_center - self.detection_area_width / 2) / (self.detection_area_width / 2)
        pan = (pan + 1) / 2  # Normalize the pan value to be between 0 and 2
    
        # Function to play the audio using PyAudio
        def play_audio(filename, pan_value):
            # Load the audio file
            data, samplerate = sf.read(filename, dtype='float32')
        
            # Apply panning
            stereo_data = apply_panning(data, pan_value) * volume_factor
        
            pa = pyaudio.PyAudio()
            try:
                stream = pa.open(format=pyaudio.paFloat32,
                                 channels=2,
                                 rate=samplerate,
                                 output=True)
                stream.write(stereo_data.tobytes())
                stream.stop_stream()
                stream.close()
            except OSError as e:
                error_message = f"Error: An error occurred while trying to play audio: {e}. Restarting..."
                print(error_message)
                speaker.speak(error_message)  # Speak the error message
                os._exit(1)  # Indicate an error occurred with exit status 1
            finally:
                pa.terminate()
        
        # Check if the detection is inside the center_radius
        if (self.detection_area_width / 2 - self.center_radius) < x_center < (self.detection_area_width / 2 + self.center_radius) and \
                (self.detection_area_height / 2 - self.center_radius) < y_center < (self.detection_area_height / 2 + self.center_radius):
            audio_file = "lib/trackingsounds/trackinglocked.wav"
            audio_pan = 0.5  # Play the audio in the center
        else:
            audio_file = "lib/trackingsounds/tracking.wav"
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
    
            # Ignore if the detection is in the ignore box
            if self.ignore_box_x1 <= x_center <= self.ignore_box_x2 and self.ignore_box_y1 <= y_center <= self.ignore_box_y2:
                continue
    
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
                    cv2.resizeWindow("Visual Debug Window", self.detection_area_width, self.detection_area_height)
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
                        winsound.Beep(200, 200)  # Play a low-pitched beep when sound is disabled
                f5_key_pressed = True
            else:
                f5_key_pressed = False

            if keyboard.is_pressed('F6'):
                print("Shutting down script...")
                os._exit(0)  # Terminate the program immediately

            if time.time() - self.last_reset_time >= 1.0:  # check if 1 second has passed
                self.reset_trackers()

            detections, screen_np = self.detect_objects_on_screen()
            self.process_detections()


            # Draw the blue center zone square
            cv2.rectangle(screen_np, (self.detection_area_width // 2 - self.center_radius, self.detection_area_height // 2 - self.center_radius),
                          (self.detection_area_width // 2 + self.center_radius, self.detection_area_height // 2 + self.center_radius), (255, 0, 0), 2)

            if cv2.waitKey(1) == ord('q'):
                break

            if self.show_detections_window:
                cv2.imshow("Visual Debug Window", screen_np)

        if window_exists:
            cv2.destroyWindow("Visual Debug Window")

        cv2.destroyAllWindows()
