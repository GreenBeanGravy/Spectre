# Spectre

## ⚠️ Hardware Requirements
Spectre is a highly resource-intensive application that demands powerful hardware for optimal performance. My testing has been conducted on a variety of systems, with GPUs ranging from the RTX 3060 to the RTX 3080, and CPUs from the i5 12600k to the Ryzen 7 7800x3D. While Spectre can operate on lower-end hardware, the performance will be noticeably slower. Swift audio feedback is crucial for Spectre's effectiveness as a tool, which means the more robust your hardware, the better Spectre will perform.

## About
Spectre is a Python script designed to enhance the accessibility of the popular game Fortnite for the blind and visually impaired. By leveraging the power of the YOLOv5 machine learning model, it provides real-time detection of players in the game, offering a new level of accessibility to these individuals. Spectre is compatible with many popular screen readers such as NVDA.

Please note that Spectre is currently in its early stages of development and operates primarily as a proof of concept. However, it is capable of providing some level of accessibility, despite its current limitations in speed and feature-set. I currently do not have any form of tutorial on how to use Spectre.

## Features
* Real-time player detection in Fortnite using YOLOv5 machine learning model.
* Audio feedback system for detected players.
* Adjustable settings for detection duration threshold, center radius, and confidence threshold.
* Option to display a window showing detections. This feature is primarily for debugging purposes but can be useful for users as well.
* GUI for adjusting settings, designed with accessibility in mind.

## Future Improvements
* Improve speed and efficiency of player detection.
* Expand the range of detectable objects and events in the game.
* Enhance the audio feedback system for better user experience.
* Add more customizable settings for users.
* Remove some redundant and/or useless options.

## Installation and Setup
1. Clone the repository.
2. Run the setup.bat file: `setup.bat`
3. Run the script: `python spectre.py`

## Usage
After running the script, the program will start providing audio feedback for detected players in Fortnite. You can adjust the settings using the GUI that pops up. The settings include detection duration threshold, center radius, and confidence threshold. You can also choose to display a window showing the detections.

## Contributing
I welcome contributions to Spectre. If you have a feature request, bug report, or proposal for improvement, please open an issue on GitHub. If you want to contribute code, please open a pull request.

## License
Please refer to the `LICENCE` file included with Spectre for more information.

I hope you find Spectre helpful. If you do, please consider giving it a star and watching the repository for updates. I have big plans for the future and I don't want you to miss out!
