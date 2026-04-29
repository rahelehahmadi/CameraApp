# Object Detection and Tracking with YOLOv8

This project is an advanced object detection and tracking system using the YOLOv8 deep learning model.

## Features
- Object detection using YOLOv8
- Object tracking in video
- Simple command-line interface
- Image and video support

## Requirements
- Python 3.8 or higher
- All dependencies listed in `requirements.txt`
- The YOLOv8 model file (`yolov8n.pt`) is already included in the project directory, so you do not need to download anything extra.

## Installation
To get started, just install the required libraries:
```bash
pip install -r requirements.txt
```

## Usage
Run the program:
```bash
python main.py
```
After running, you will be asked to choose between image detection or video tracking, and then to enter the path to your image or video file. Press 'q' to exit video tracking at any time.

## Project Structure
- `main.py`: Main program (user interface)
- `object_detector.py`: Object detection and tracking module (YOLOv8)
- `requirements.txt`: List of dependencies
- `yolov8n.pt`: YOLOv8 model weights (required)
- `sample.jpg`, `test_video.mp4`, etc.: Example image and video files
- `report.pdf`: Project report 
- `README.md`: This file

## Notes
- The program does not use the webcam; you need to provide a file path for your image or video.
- If you see a `ModuleNotFoundError`, please make sure you have installed the requirements.

---
For more details, see the project report (`report.pdf`).
