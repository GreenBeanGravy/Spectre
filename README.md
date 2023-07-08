# Spectre

## About
Spectre is a Python script designed to enhance the accessibility of the popular game Fortnite for the blind and visually impaired. By leveraging the power of the YOLOv5 machine learning model, it provides real-time detection of players in the game, offering a new level of accessibility to these individuals. Spectre is compatible with many popular screen readers such as NVDA.
Please note that Spectre is currently in its early stages of development. It takes some getting used to and is to be used primarily as an aim assist, do not expect Spectre to do all the leg work for you. I have plans for the future to implement an optional interactive aim assist which would be able to move the mouse for you, but created in a way that doesn't give anyone an unfair advantage. This technically goes against the Fortnite TOS which is why it would be made optional.

## Keybinds
* **F5**: Toggles player detection on and off. Useful in some cases, such as the Fortnite lobby.
* **F6**: Closes Spectre.
* **F7**: Is used to activate the *currently* experimental GUI detection feature. Does not currently work out of the box, but will in a future release.
* **Space**: Only used in the interactive GUI. Used to press buttons!
  
## ⚠️ Suggested Hardware
Spectre is a highly resource-intensive application that demands powerful hardware for optimal performance. My personal testing has been conducted on a system that uses an RTX 3080. While Spectre can operate on lower-end hardware, the performance will suffer. Swift audio feedback is crucial for Spectre's effectiveness as a tool, which means the more robust your hardware, the better Spectre will perform.

## Features
* Real-time player detection in Fortnite using YOLOv5 machine learning model.
* Audio feedback system for detected players.
* Customizable settings
* Option to display a window showing detections. This feature is primarily for debugging purposes but can be useful for users as well.
* GUI for adjusting settings in real time, designed with accessibility in mind.

## Settings Explanation
* **Duration Threshold**: This defines how long a detection/player needs to be on screen in order to play a sound. This can be very helpful if the sound is giving you a headache. By default, this is set to 0.05.
* **Center Radius**: This defines how close a detection/player needs to be to the center of the screen (in pixels) in order to play the "tracking" sound. Lower values are helpful at closer ranges, but severely affect long range accuracy. By default, this is set to 50.
* **Show Detections Window**: This is a toggle on whether or not the "Detections Window" should be displayed. This was added as a debug tool, but it can be helpful for users as well so I decided to keep it as a feature. By default, this is toggled ON.
* **Confidence Threshold**: This defines what the confidence of the neural network should be in order to determine someone/something as a detection/player. Lower values seem to help with longer ranges, but they cause more false detections. By default, this is set to 0.35.

## Future Improvements
* ~~Improve speed and efficiency of player detection.~~
* Expand the range of detectable objects and events in the game.
* Add more customizable settings for users.
* Add some elements to the GUI to allow users to change the keybinds that Spectre uses.

## Currently Working On:
* Vertical detection. This would allow Spectre to give audio feedback for height by changing the pitch of the tracking sound in realtime.
* Higher accuracy. I am currently working on a new YOLO model (hopefully transitioning to YOLOv8) with significantly more data than the last. This should greatly improve accuracy and potentially speed if the switch to YOLOv8 is made.
* Keybinds.

## Installation and Setup
1. Download the latest release.
2. Navigate to and extract the downloaded zip file.
3. Open the extracted folder.
4. Please run the "install_packages.bat" file as admin to install the required libraries to use Spectre. A .whl file is included to install dlib without cmake. THIS IS ONLY FOR PYTHON 3.9!

## Usage
Please run the script using the "start_spectre.bat" file.

## Contributing
I welcome contributions to Spectre. If you have a feature request, bug report, or proposal for improvement, please open an issue on GitHub. If you want to contribute code, please open a pull request.

## License
Please refer to the `LICENCE` file included with Spectre for more information.

I hope you find Spectre helpful. If you do, please consider giving it a star and watching the repository for updates. I have big plans for the future and I don't want you to miss out!
