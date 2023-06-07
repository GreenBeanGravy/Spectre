import numpy as np
import tkinter as tk
from accessible_output2.outputs.auto import Auto
from tkinter import ttk
from lib.settings import save_settings, load_settings, update_settings, prompt_settings

class Speaker:
    def __init__(self):
        self.output = Auto()

    def speak(self, text):
        self.output.speak(text)

speaker = Speaker()

def apply_panning(data, pan, panning_power=2):
    """
    Apply panning effect to audio data.

    Args:
        data (numpy.ndarray): The audio data.
        pan (float): The panning value. Should be between 0 (left) and 2 (right).
        panning_power (int, optional): The power to raise the pan value to. Defaults to 2.

    Returns:
        numpy.ndarray: The audio data with panning applied.
    """
    try:
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
    except Exception as e:
        print(f"Error applying panning: {e}")
        return data