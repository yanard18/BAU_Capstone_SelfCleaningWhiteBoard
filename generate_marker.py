#!/usr/bin/env python3

import cv2
import numpy as np


def create_perfect_marker():
    # 1. Define Marker Parameters
    dictionary_id = cv2.aruco.DICT_4X4_50
    marker_id = 0
    marker_size = 500  # Size of the black square in pixels

    # Load the dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(dictionary_id)

    # 2. Generate the black-and-white marker grid
    # (Using a try/except to handle the API change between OpenCV 4.6 and 4.7+)
    try:
        # Modern OpenCV (4.7+)
        marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
    except AttributeError:
        # Older OpenCV (4.6 and below)
        marker_image = cv2.aruco.drawMarker(aruco_dict, marker_id, marker_size)

    # 3. Add the "Quiet Zone" (The White Border)
    # We add a 20% white margin to all four sides to ensure maximum contrast
    border_width = int(marker_size * 0.2)
    
    marker_with_border = cv2.copyMakeBorder(
        marker_image,
        top=border_width,
        bottom=border_width,
        left=border_width,
        right=border_width,
        borderType=cv2.BORDER_CONSTANT,
        value=[255, 255, 255]  # Pure White
    )

    # 4. Save the final image to disk
    filename = f"perfect_aruco_id{marker_id}.png"
    cv2.imwrite(filename, marker_with_border)
    
    print(f"Success! Perfect marker generated and saved as: {filename}")
    print(f"Total image size: {marker_with_border.shape[1]}x{marker_with_border.shape[0]} pixels")

if __name__ == "__main__":
    create_perfect_marker()
