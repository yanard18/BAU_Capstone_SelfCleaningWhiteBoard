#!/usr/bin/env python3

import cv2  # type: ignore
import numpy as np  # type: ignore
import numpy.typing as npt  # type: ignore
from typing import List, Tuple, Any

# .npz (not .npy) because we save multiple arrays: matrix + dimensions.
# np.savez packs them into one file; np.load gives them back by name.
CALIBRATION_FILE = 'calibration.npz'


def save_calibration(matrix: npt.NDArray[np.float64], width: int, height: int) -> None:
    np.savez(CALIBRATION_FILE, matrix=matrix, size=np.array([width, height]))
    print(f"Calibration saved to {CALIBRATION_FILE}")


def load_calibration() -> Tuple[npt.NDArray[np.float64], int, int]:
    data = np.load(CALIBRATION_FILE)
    width, height = int(data['size'][0]), int(data['size'][1])
    return data['matrix'], width, height


def get_board_corners(img_pth: str) -> npt.NDArray[np.float32]:
    corner_points: List[Tuple[int, int]] = []
    image = cv2.imread(img_pth)

    if image is None:
        raise FileNotFoundError(f"ERROR: OpenCV could not find the image at '{img_pth}'")

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


def get_homography_matrix(points: npt.NDArray[np.float32]) -> Tuple[npt.NDArray[np.float64], int, int]:

    rect = order_points(points)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    max_width = max(int(widthA), int(widthB))
    
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(heightA), int(heightB))

    dst_pts = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(rect, dst_pts)

    return matrix, max_width, max_height


def order_points(pts: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
    """
    Sorts the 4 points in this order: Top-Left, Top-Right, Bottom-Right, Bottom-Left.
    """
    rect = np.zeros((4, 2), dtype=np.float32)
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect
