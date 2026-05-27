#!/usr/bin/env python3

import io
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file
from calibration import get_homography_matrix, save_calibration, load_calibration
from main import run_pipeline

app = Flask(__name__)
IMG_PATH = './mock_data/mock6.png'

try:
    _matrix, _width, _height = load_calibration()
    print("Loaded saved calibration.")
except FileNotFoundError:
    _matrix, _width, _height = None, None, None
    print("No calibration file found. Visit /calibrate to calibrate.")


@app.route('/calibrate')
def calibrate():
    return app.send_static_file('calibrate.html')


@app.route('/image')
def serve_image():
    return send_file(IMG_PATH, mimetype='image/png')


@app.route('/calibrate/points', methods=['POST'])
def receive_points():
    global _matrix, _width, _height

    data = request.get_json()
    points = data.get('points', [])

    if len(points) != 4:
        return jsonify({'error': 'Exactly 4 points required'}), 400

    src_pts = np.array([[p['x'], p['y']] for p in points], dtype=np.float32)
    _matrix, _width, _height = get_homography_matrix(src_pts)
    save_calibration(_matrix, _width, _height)

    image = cv2.imread(IMG_PATH)
    result = run_pipeline(image, _matrix, _width, _height)

    _, buffer = cv2.imencode('.png', result)
    return send_file(io.BytesIO(buffer), mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
