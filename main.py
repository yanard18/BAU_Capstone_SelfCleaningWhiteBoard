#!/usr/bin/env python3

from calibration import get_board_corners


if __name__ == "__main__":
    arr = get_board_corners('mock3.png')
    print(f"{arr}")
