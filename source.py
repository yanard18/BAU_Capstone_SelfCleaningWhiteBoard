#!/usr/bin/env python3

import cv2


def frames():
    image = cv2.imread('./mock_data/mock6.png')
    while True:
        yield image
