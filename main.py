#!/usr/bin/env python3

import cv2
from calibration import get_board_corners
from calibration import get_homography_matrix


if __name__ == "__main__":
    img_path = './mock_data/mock3.png'
    src_pts = get_board_corners(img_path)
    image = cv2.imread(img_path)
    (matrix, width, height) = get_homography_matrix(image, src_pts)
    print(f"{matrix}, {width}, {height}")
