#!/usr/bin/env python3

import cv2
from calibration import get_board_corners
from calibration import get_homography_matrix


if __name__ == "__main__":
    img_path = './mock_data/mock6.png'
    src_pts = get_board_corners(img_path)
    image = cv2.imread(img_path)

    (matrix, width, height) = get_homography_matrix(image, src_pts)

    warped_image = cv2.warpPerspective(image, matrix, (width, height))

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    corners, ids, rejected = detector.detectMarkers(warped_image)

    # Assuming only found 1 marker (ids == 0)
    if ids is not None:
        # cv2.aruco.drawDetectedMarkers(warped_image, corners, ids)

        c = corners[0][0]
        center_x = int((c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4)
        center_y = int((c[0][1] + c[1][1] + c[2][1] + c[3][1]) / 4)

        cv2.circle(warped_image, (center_x, center_y), 5, (0, 255, 0), -1)

        front_x = int((c[0][0] + c[1][0]) / 2)
        front_y = int((c[0][1] + c[1][1]) / 2)

        cv2.line(warped_image, (center_x, center_y), (front_x, front_y), (255, 0, 0), 3)

        text = f"X:{center_x} Y:{center_y}"
        cv2.putText(warped_image, text, (center_x - 80, center_y - 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.imshow("Whiteboard Tracker", warped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
