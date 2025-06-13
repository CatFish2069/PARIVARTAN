# Parivartan - 2D to 3D Converter

Parivartan is a Python-based application that converts 2D floor plan images into 3D OBJ models. The app uses OpenCV for image processing and Flet for the user interface. It supports both dark and light modes and generates a 3D model (OBJ file) from your floor plan.

> **Note:** This application does not include a 3D walkthrough feature.

## Features

- Convert 2D floor plan images to 3D models in OBJ format.
- Preprocess images using adaptive thresholding, noise reduction, and edge detection.
- Generate a simple 3D mesh by extruding detected contours.
- User interface built with Flet, featuring dark/light mode support.
- Automatic opening of the generated OBJ file (if supported by your OS).

## Installation

### Prerequisites

- Python 3.7 or later
- pip (Python package installer)

### Required Packages

Install the required Python packages using pip:

```bash
pip install flet opencv-python numpy pillow hupper pyfiglet trimesh pythreejs
