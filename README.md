# Spectre

## ⚠️ Suggested Hardware
Spectre is a highly resource-intensive application that demands powerful hardware for optimal performance. My personal testing has been conducted on a system that uses an RTX 3080. While Spectre can operate on lower-end hardware, the performance will be noticeably slower. Swift audio feedback is crucial for Spectre's effectiveness as a tool, which means the more robust your hardware, the better Spectre will perform.

## About
Spectre is a Python script designed to enhance the accessibility of the popular game Fortnite for the blind and visually impaired. By leveraging the power of the YOLOv5 machine learning model, it provides real-time detection of players in the game, offering a new level of accessibility to these individuals. Spectre is compatible with many popular screen readers such as NVDA.

Please note that Spectre is currently in its early stages of development and operates primarily as a proof of concept. However, it is capable of providing some level of accessibility, despite its current limitations in speed and feature-set. I currently do not have any form of tutorial on how to use Spectre.

## Features
* Real-time player detection in Fortnite using YOLOv5 machine learning model.
* Audio feedback system for detected players.
* Adjustable settings for detection duration threshold, center radius, and confidence threshold.
* Option to display a window showing detections. This feature is primarily for debugging purposes but can be useful for users as well.
* GUI for adjusting settings, designed with accessibility in mind.

## Settings Explanation
* **Duration Threshold**: This defines how long a detection/player needs to be on screen in order to play a sound. This can be very helpful if the sound is giving you a headache. By default, this is set to 0.05.
* **Center Radius**: This defines how close a detection/player needs to be to the center of the screen (in pixels) in order to play the "tracking" sound. Lower values are helpful at closer ranges, but severely affect long range accuracy. By default, this is set to 50.
* **Show Detections Window**: This is a toggle on whether or not the "Detections Window" should be displayed. This was added as a debug tool, but it can be helpful for users as well so I decided to keep it as a feature. By default, this is toggled OFF.
* **Confidence Threshold**: This defines what the confidence of the neural network should be in order to determine someone/something as a detection/player. Lower values seem to help with longer ranges, but they cause more false detections. By default, this is set to 0.35.

## Future Improvements
* Improve speed and efficiency of player detection.
* Expand the range of detectable objects and events in the game.
* Enhance the audio feedback system for better user experience.
* Add more customizable settings for users.
* Add some elements to the GUI to allow users to change the keybinds that Spectre uses.

## Installation and Setup
1. Download the latest release.
2. Navigate to and extract the downloaded zip file.
3. Open the extracted folder and open Command Prompt within the folder.
4. Run the command "pip install -r requirements.txt"

## Usage
After running the script, the program will start providing audio feedback for detected players in Fortnite. You can adjust the settings using the GUI that pops up. The settings include detection duration threshold, center radius, and confidence threshold. You can also choose to display a window showing the detections.

## Contributing
I welcome contributions to Spectre. If you have a feature request, bug report, or proposal for improvement, please open an issue on GitHub. If you want to contribute code, please open a pull request.

## License
Please refer to the `LICENCE` file included with Spectre for more information.

I hope you find Spectre helpful. If you do, please consider giving it a star and watching the repository for updates. I have big plans for the future and I don't want you to miss out!
