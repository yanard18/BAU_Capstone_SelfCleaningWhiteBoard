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

        

    gray_img = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)

    ink_mask = cv2.adaptiveThreshold(
        gray_img, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        45,  # blockSize (Must be an odd number)
        5   # C (Constant subtracted from the local mean)
    )

    # Assuming only found 1 marker (ids == 0)
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(warped_image, corners, ids)

        c = corners[0][0]
        center_x = int((c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4)
        center_y = int((c[0][1] + c[1][1] + c[2][1] + c[3][1]) / 4)

        cv2.circle(warped_image, (center_x, center_y), 5, (0, 255, 0), -1)

        robot_radius_pixels = 100
        cv2.circle(ink_mask, (center_x, center_y), robot_radius_pixels, 0, -1)

    else:
        print("No ArCuo marker found!")

    # clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    clean_mask = cv2.morphologyEx(ink_mask, cv2.MORPH_OPEN, kernel)

    cell_size = 60

    pixel_threshold = 20

    grid_targets = []

    h, w = clean_mask.shape

    for y in range(0, h, cell_size):
        for x in range(0, w, cell_size):
            y_end = min(y + cell_size, h)
            x_end = min(x + cell_size, w)
            
            cell = clean_mask[y:y_end, x:x_end]
            
            ink_pixel_count = cv2.countNonZero(cell)
            
            if ink_pixel_count >= pixel_threshold:
                # Calculate center of the grid cell
                cell_center_x = x + (x_end - x) // 2
                cell_center_y = y + (y_end - y) // 2
                
                grid_targets.append((cell_center_x, cell_center_y))
                
                # VISUAL DEBUGGING: Draw a red rectangle over the dirty cell
                cv2.rectangle(warped_image, (x, y), (x_end, y_end), (0, 0, 255), 1)
                # Draw a small blue dot at the center waypoint
                cv2.circle(warped_image, (cell_center_x, cell_center_y), 3, (255, 0, 0), -1)
        
    #cv2.imshow("Whiteboard Tracker", warped_image)
    cv2.imshow("Display", warped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
