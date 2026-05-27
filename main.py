#!/usr/bin/env python3

import cv2
from itertools import groupby
from calibration import get_board_corners
from calibration import get_homography_matrix

def sort_lawnmower_path(targets):
    if not targets:
        return []

    targets.sort(key=lambda coord: (coord[1], coord[0]))
    
    final_path = []
    sweep_left_to_right = True
    
    for y_value, row_group in groupby(targets, key=lambda coord: coord[1]):
        
        current_row = list(row_group)
        
        if not sweep_left_to_right:
            current_row.reverse()
            
        final_path.extend(current_row)
        
        sweep_left_to_right = not sweep_left_to_right
        
    return final_path


def apply_grid_detection(img, debug_grids: bool = True):
    cell_size = 60
    pixel_threshold = 15
    grid_targets = []
    h, w = img.shape

    for y in range(0, h, cell_size):
        for x in range(0, w, cell_size):
            y_end = min(y + cell_size, h)
            x_end = min(x + cell_size, w)
            
            cell = img[y:y_end, x:x_end]
            
            ink_pixel_count = cv2.countNonZero(cell)
            
            if ink_pixel_count >= pixel_threshold:
                cell_center_x = x + (x_end - x) // 2
                cell_center_y = y + (y_end - y) // 2
                
                grid_targets.append((cell_center_x, cell_center_y))
                
                if debug_grids:
                    cv2.rectangle(warped_img, (x, y), (x_end, y_end), (0, 0, 255), 1)

    return grid_targets
    

def debug_path(img, path, connect_dots: bool = True):
    for i in range(len(path)):
        current_pt = path[i]
        
        text_pos = (current_pt[0] + 5, current_pt[1] - 5)
        cv2.putText(
            img, 
            str(i),           # The index number (0, 1, 2...)
            text_pos, 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.4,              # Font scale
            (255, 0, 0),      # Blue text
            1                 # Thickness
        )
        
        if connect_dots and i < len(path) - 1:
            next_pt = path[i + 1]
            cv2.line(
                img, 
                current_pt, 
                next_pt, 
                (0, 255, 0),  # Green line
                2             # Thickness
            )


if __name__ == "__main__":
    img_path = './mock_data/mock6.png'
    src_pts = get_board_corners(img_path)
    image = cv2.imread(img_path)

    (matrix, width, height) = get_homography_matrix(src_pts)
    warped_img = cv2.warpPerspective(image, matrix, (width, height))

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, rejected = detector.detectMarkers(warped_img)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(warped_img, corners, ids)

        c = corners[0][0]
        center_x = int((c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4)
        center_y = int((c[0][1] + c[1][1] + c[2][1] + c[3][1]) / 4)

    else:
        print("No ArCuo marker found!")

    gray_img = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)

    ink_mask = cv2.adaptiveThreshold(
        gray_img, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        45,  # blockSize (Must be an odd number)
        5   # C (Constant subtracted from the local mean)
    )

    # filter out robot
    cv2.circle(ink_mask, (center_x, center_y), 100, 0, -1)

    # clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    ink_mask_clean = cv2.morphologyEx(ink_mask, cv2.MORPH_OPEN, kernel)

    grid_targets = apply_grid_detection(ink_mask_clean)
    
    path = sort_lawnmower_path(grid_targets)

    debug_path(warped_img, path)

    cv2.imshow("Display", warped_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

