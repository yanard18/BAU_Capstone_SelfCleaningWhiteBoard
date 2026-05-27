#!/usr/bin/env python3

import cv2
import numpy as np
from itertools import groupby
from calibration import load_calibration
from source import frames


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


def apply_grid_detection(
        img: np.ndarray,
        warped_img: np.ndarray,
        cell_size: int,
        pixel_threshold: int,
        debug: bool = True
) -> list[tuple[int, int]]:

    grid_targets: list[tuple[int, int]] = []
    h, w = img.shape

    for y in range(0, h, cell_size):
        for x in range(0, w, cell_size):
            y_end = min(y + cell_size, h)
            x_end = min(x + cell_size, w)

            cell = img[y:y_end, x:x_end]

            if cv2.countNonZero(cell) >= pixel_threshold:
                grid_targets.append((x + (x_end - x) // 2, y + (y_end - y) // 2))

                if debug:
                    cv2.rectangle(warped_img, (x, y), (x_end, y_end), (0, 0, 255), 1)

    return grid_targets


def draw_robot_overlays(img, corners, center, path,
                        show_orientation=True, show_direction=True):
    c = corners[0][0]  # (4, 2) float32 — TL, TR, BR, BL

    if show_orientation:
        mid_top  = ((c[0][0] + c[1][0]) / 2, (c[0][1] + c[1][1]) / 2)
        marker_w = float(np.linalg.norm(c[1] - c[0]))
        dx, dy   = mid_top[0] - center[0], mid_top[1] - center[1]
        dist     = np.hypot(dx, dy)
        if dist > 0:
            scale = marker_w / dist
            tip = (int(center[0] + dx * scale), int(center[1] + dy * scale))
            cv2.arrowedLine(img, center, tip, (0, 255, 255), 2, tipLength=0.25)

    if show_direction and path:
        target  = path[0]
        dist_to = np.linalg.norm(np.array(target) - np.array(center))
        if dist_to > 10:
            cv2.arrowedLine(img, center, target, (255, 255, 0), 2, tipLength=0.05)


def debug_path(img, path, show_numbers=True, connect_dots=True):
    for i in range(len(path)):
        current_pt = path[i]

        if show_numbers:
            cv2.putText(img, str(i), (current_pt[0] + 5, current_pt[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        if connect_dots and i < len(path) - 1:
            cv2.line(img, current_pt, path[i + 1], (0, 255, 0), 2)


def get_robot(
        img: np.ndarray,
        debug: bool = True
) -> tuple[tuple[int, int], tuple[np.ndarray, ...]]:

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    detector = cv2.aruco.ArucoDetector(aruco_dict, cv2.aruco.DetectorParameters())
    corners, ids, _ = detector.detectMarkers(img)

    if ids is None:
        raise Exception("No ArUco marker found!")

    elif len(ids) > 1:
        raise Exception("Multiple ArUco markers found!")

    if debug:
        cv2.aruco.drawDetectedMarkers(img, corners, ids)
        
    c = corners[0][0]
    robot_pos = (
        int((c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4),
        int((c[0][1] + c[1][1] + c[2][1] + c[3][1]) / 4),
    )

    return robot_pos, corners


def run_pipeline(image: np.ndarray, matrix: np.ndarray, width: int, height: int,
                 cfg: dict) -> dict:

    out_img = cv2.warpPerspective(image, matrix, (width, height))

    robot_pos, robot_corners = get_robot(out_img, cfg.get('show_aruco'))
        
    gray_img = cv2.cvtColor(out_img, cv2.COLOR_BGR2GRAY)
    ink_mask = cv2.adaptiveThreshold(
        gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        cfg['adaptive_block_size'], cfg['adaptive_c']
    )

    if robot_pos is not None:
        cv2.circle(ink_mask, robot_pos, cfg['robot_mask_radius'], 0, -1)

    grid_targets = apply_grid_detection(
        ink_mask,
        out_img,
        cfg['cell_size'],
        cfg['ink_pixel_threshold'],
        debug=cfg.get('show_grid', True),
    )

    path = sort_lawnmower_path(grid_targets)
    debug_path(out_img, path,
               show_numbers=cfg.get('show_path_numbers', True),
               connect_dots=cfg.get('show_path_lines', True))

    if robot_pos is not None:
        draw_robot_overlays(out_img, robot_corners, robot_pos, path,
                            show_orientation=cfg.get('show_orientation', True),
                            show_direction=cfg.get('show_direction', True))

    return {
        'output':   out_img,
        'ink_mask': ink_mask,
        'gray':     gray_img,
    }
