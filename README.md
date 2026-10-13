# Agri-Bot: Hand-Gesture Controlled Smart Farming Simulation

## Overview

This project is an interactive simulation of an agricultural robot controlled using real-time hand gestures. It combines computer vision and game development to simulate farming activities such as plowing, seeding, and watering crops.

The system uses a webcam to detect hand gestures and controls a virtual bot inside a field environment.

---

## Technologies Used

* Python
* OpenCV (cv2)
* MediaPipe
* Pygame

---

## Features

* Real-time hand gesture recognition
* Bot movement control using gestures
* Simulated farming tasks:

  * Plowing
  * Seeding
  * Watering
* Dynamic crop growth visualization
* Interactive graphical environment using Pygame

---

## System Workflow

1. The webcam captures live video input.
2. MediaPipe processes the hand landmarks.
3. Gestures are detected based on finger positions.
4. The bot performs actions in the simulation:

   * Moves across the field
   * Plows land
   * Plants seeds
   * Waters crops
5. Crops visually change state based on actions.

---

## Gesture Controls

### Movement

* Open Palm → Move Forward
* Index Finger Down → Move Backward
* Fist + Thumb Right → Move Right
* Fist + Thumb Left → Move Left

### Actions

* Right Hand Index Up → Start Plowing

* Left Hand Index Up → Stop Plowing

* Right Hand Pinky Up → Start Seeding

* Left Hand Pinky Up → Stop Seeding

* Right Hand Peace Sign → Start Watering

* Left Hand Peace Sign → Stop Watering

---

## Crop States

Each crop progresses through different stages:

* Unplowed
* Plowed
* Seeded
* Watered
* Fully Grown

---

## How to Run

1. Install required libraries:

```bash
pip install opencv-python mediapipe pygame
```

2. Place an optional image file named `bot.jpeg` in the project folder (used for bot visualization).

3. Run the script:

```bash
python your_script_name.py
```

4. Press `q` to exit the application.

---

## Project Structure

```
Agri-Bot-Simulation/
│── main.py
│── bot.jpeg (optional)
│── README.md
```

---

## Requirements

* Python 3.x
* Webcam (for gesture detection)
* Supported OS: Windows / macOS / Linux

---

## Limitations

* Gesture detection accuracy depends on lighting conditions
* Requires a functioning webcam
* Limited gesture set

---

## Future Enhancements

* Add more advanced gestures
* Improve gesture accuracy using machine learning models
* Introduce additional farming activities
* Convert into a full-scale web or mobile application
* Add scoring or task completion system

---

## Author

Ananya Reddy
