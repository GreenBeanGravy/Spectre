import numpy as np
import tkinter as tk
from tkinter import ttk
from lib.panning import speaker

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