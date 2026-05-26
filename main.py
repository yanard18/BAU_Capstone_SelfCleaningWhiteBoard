#!/usr/bin/env python3

import cv2
from calibration import get_board_corners
from calibration import apply_homography


if __name__ == "__main__":
    img_path = './mock_data/mock3.png'
    src_pts = get_board_corners(img_path)
    image = cv2.imread(img_path)
    flat_board = apply_homography(image, src_pts)

    cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Original", 800, 600)
    cv2.imshow("Original", image)

    cv2.namedWindow("Flat", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Flat", 800, 600)
    cv2.imshow("Flat", flat_board)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
