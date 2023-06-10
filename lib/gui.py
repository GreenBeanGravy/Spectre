import numpy as np
import tkinter as tk
from tkinter import ttk
from lib.settings import save_settings, load_settings, update_settings, prompt_settings
from lib.panning import speaker

def get_current_values(duration_var, center_radius_var, show_detections_var, confidence_var):
    duration = duration_var.get()
    center_radius = center_radius_var.get()
    show_detections = show_detections_var.get()
    confidence = confidence_var.get()

    return duration, center_radius, show_detections, confidence

def create_tkinter_gui(settings, detector):

    def apply_settings():
        duration, center_radius, show_detections, confidence = get_current_values(duration_var, center_radius_var, show_detections_var, confidence_var)

        settings["General"]["duration_threshold"] = duration
        settings["General"]["center_radius"] = center_radius
        settings["General"]["show_detections_window"] = str(show_detections)
        settings["General"]["confidence_threshold"] = confidence

        # Apply Settings when the "Apply" button is pressed
        detector.detection_duration_threshold = float(duration)
        detector.center_radius = int(center_radius)
        detector.show_detections_window = show_detections
        detector.confidence_threshold = float(confidence)

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
    apply_button.grid(column=0, row=6, pady=(10, 0), sticky="W")
    save_button = ttk.Button(frame, text="Save", command=save_and_apply_settings)
    save_button.grid(column=1, row=6, pady=(10, 0), sticky="W")

    duration_label.bind('<Enter>', lambda e: speaker.speak("Duration Threshold (0 to 1)"))
    center_radius_label.bind('<Enter>', lambda e: speaker.speak("Center Radius (in pixels)"))
    show_detections_label.bind('<Enter>', lambda e: speaker.speak("Show Detections Window"))
    confidence_label.bind('<Enter>', lambda e: speaker.speak("Confidence Threshold (0 to 1)"))
    
    duration_entry.bind('<FocusIn>', lambda e: speaker.speak(f"Duration Threshold (0 to 1), Edit Box, {duration_var.get()}"))
    center_radius_entry.bind('<FocusIn>', lambda e: speaker.speak(f"Center Radius (in pixels), Edit Box, {center_radius_var.get()}"))
    show_detections_checkbutton.bind('<FocusIn>', lambda e: speaker.speak(f"Show Detections Window, Checkbox {'checked' if show_detections_var.get() else 'not checked'}"))
    confidence_entry.bind('<FocusIn>', lambda e: speaker.speak(f"Confidence Threshold (0 to 1), Edit Box, {confidence_var.get()}"))
    apply_button.bind('<FocusIn>', lambda e: speaker.speak("Apply, Button"))
    save_button.bind('<FocusIn>', lambda e: speaker.speak("Save, Button"))
    
    # Set the takefocus attribute for each widget
    duration_entry.configure(takefocus=1)
    center_radius_entry.configure(takefocus=1)
    show_detections_checkbutton.configure(takefocus=1)
    confidence_entry.configure(takefocus=1)
    apply_button.configure(takefocus=1)
    save_button.configure(takefocus=1)

    # Define variables for speaking the values of elements when they change
    def speak_duration(*args):
        speaker.speak(f"{duration_var.get()}")

    def speak_center_radius(*args):
        speaker.speak(f"{center_radius_var.get()}")

    def speak_confidence(*args):
        speaker.speak(f"{confidence_var.get()}")

    def speak_show_detections(*args):
        speaker.speak(f"{'checked' if show_detections_var.get() else 'not checked'}")
 
    # Use trace to activate whenever a var changes
    show_detections_var.trace('w', speak_show_detections)
    duration_var.trace('w', speak_duration)
    center_radius_var.trace('w', speak_center_radius)
    confidence_var.trace('w', speak_confidence)

    root.mainloop()
