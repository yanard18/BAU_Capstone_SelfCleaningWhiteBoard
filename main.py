#!/usr/bin/env python3

import cv2
import numpy as np
from itertools import groupby
from calibration import load_calibration
from source import frames

DEFAULT_CONFIG = {
    'adaptive_block_size': 45,
    'adaptive_c':          5,
    'robot_mask_radius':   100,
    'morph_kernel_size':   3,
    'cell_size':           60,
    'ink_pixel_threshold': 15,
}


def sort_lawnmower_path(targets):
    if not targets:
        return []

    targets.sort(key=lambda coord: (coord[1], coord[0]))

    final_path = []
    sweep_left_to_right = True

    for _, row_group in groupby(targets, key=lambda coord: coord[1]):
        current_row = list(row_group)

        if not sweep_left_to_right:
            current_row.reverse()

        final_path.extend(current_row)
        sweep_left_to_right = not sweep_left_to_right

    return final_path


def apply_grid_detection(img, warped_img, cell_size, pixel_threshold, debug_grids=True):
    grid_targets = []
    h, w = img.shape

    for y in range(0, h, cell_size):
        for x in range(0, w, cell_size):
            y_end = min(y + cell_size, h)
            x_end = min(x + cell_size, w)

            cell = img[y:y_end, x:x_end]

            if cv2.countNonZero(cell) >= pixel_threshold:
                grid_targets.append((x + (x_end - x) // 2, y + (y_end - y) // 2))

                if debug_grids:
                    cv2.rectangle(warped_img, (x, y), (x_end, y_end), (0, 0, 255), 1)

    return grid_targets


def debug_path(img, path, connect_dots=True):
    for i in range(len(path)):
        current_pt = path[i]

        cv2.putText(img, str(i), (current_pt[0] + 5, current_pt[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        if connect_dots and i < len(path) - 1:
            cv2.line(img, current_pt, path[i + 1], (0, 255, 0), 2)


def run_pipeline(image: np.ndarray, matrix: np.ndarray, width: int, height: int,
                 config: dict = None) -> dict:
    cfg = config or DEFAULT_CONFIG

    warped_img = cv2.warpPerspective(image, matrix, (width, height))

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    detector = cv2.aruco.ArucoDetector(aruco_dict, cv2.aruco.DetectorParameters())
    corners, ids, _ = detector.detectMarkers(warped_img)

    center = None
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(warped_img, corners, ids)
        c = corners[0][0]
        center = (
            int((c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4),
            int((c[0][1] + c[1][1] + c[2][1] + c[3][1]) / 4),
        )
    else:
        print("No ArUco marker found!")

    gray_img = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    ink_mask = cv2.adaptiveThreshold(
        gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        cfg['adaptive_block_size'], cfg['adaptive_c']
    )

    if center is not None:
        cv2.circle(ink_mask, center, cfg['robot_mask_radius'], 0, -1)

    k = cfg['morph_kernel_size']
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    ink_mask_clean = cv2.morphologyEx(ink_mask, cv2.MORPH_OPEN, kernel)

    grid_targets = apply_grid_detection(
        ink_mask_clean, warped_img,
        cfg['cell_size'], cfg['ink_pixel_threshold']
    )
    path = sort_lawnmower_path(grid_targets)
    debug_path(warped_img, path)

    return {
        'output':   warped_img,
        'ink_mask': ink_mask_clean,
    }


if __name__ == "__main__":
    try:
        matrix, width, height = load_calibration()
        print("Loaded saved calibration.")

        for frame in frames():
            result = run_pipeline(frame, matrix, width, height)
            cv2.imshow("Display", result['output'])
            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destroyAllWindows()
    except FileNotFoundError:
        print("No calibration matrix found. Starting interactive calibration...")
