#!/usr/bin/env python3

import os
import time
import cv2
import numpy as np
from typing import Iterator

MODE      = os.environ.get('MODE', 'mock')
MOCK_PATH = './mock_data/mock6.png'


def frames() -> Iterator[np.ndarray]:
    if MODE == 'mock':
        frame = cv2.imread(MOCK_PATH)
        while True:
            yield frame
            time.sleep(1 / 30)    # cap at ~30fps; real camera sets its own pace
    else:
        cap = cv2.VideoCapture(0)
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                yield frame
        finally:
            cap.release()
