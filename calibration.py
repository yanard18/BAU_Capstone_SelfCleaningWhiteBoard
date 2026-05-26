#!/usr/bin/env python3

import cv2  # type: ignore
import numpy as np  # type: ignore
import numpy.typing as npt  # type: ignore
from typing import List, Tuple, Any


def get_board_corners(image_path: str) -> npt.NDArray[np.float32]:
    corner_points: List[Tuple[int, int]] = []
    image = cv2.imread('mock3.png')
    clone = image.copy()

    def select_points(event: int, x: int, y: int,
                      flags: int, param: Any) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            corner_points.append((x, y))
            cv2.circle(image, (x, y), 12, (0, 0, 255), -1)
            cv2.imshow("Calibration", image)

    cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Calibration", 800, 600)
    cv2.setMouseCallback("Calibration", select_points)

    while True:
        cv2.imshow("Calibration", image)
        key = cv2.waitKey(1) & 0xFF

        # Break the loop when have 4 points
        if len(corner_points) == 4:
            print("4 points captured!")
            break

        # Press 'c' to clear points
        if key == ord("c"):
            image = clone.copy()
            corner_points.clear()
            print("Points cleared. Try again.")

    cv2.destroyAllWindows()

    return np.array(corner_points, dtype=np.float32)
