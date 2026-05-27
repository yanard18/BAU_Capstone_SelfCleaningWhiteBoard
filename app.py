#!/usr/bin/env python3

import io
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file, Response
from calibration import get_homography_matrix, save_calibration, load_calibration
from main import run_pipeline
from source import frames

app = Flask(__name__)
IMG_PATH = './mock_data/mock6.png'

try:
    _matrix, _width, _height = load_calibration()
    print("Loaded saved calibration.")
except FileNotFoundError:
    _matrix, _width, _height = None, None, None
    print("No calibration file found. Visit /calibrate to calibrate.")

_debug_flags = {
    'robot_detection': True,
    'grid_markers':    True,
    'path_overlay':    True,
}


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/status')
def status():
    return jsonify({'calibrated': _matrix is not None})


@app.route('/debug/<name>', methods=['POST'])
def set_debug(name):
    if name not in _debug_flags:
        return jsonify({'error': f'Unknown debug flag: {name}'}), 400
    _debug_flags[name] = bool(request.get_json().get('enabled', False))
    return jsonify({'ok': True, 'flags': _debug_flags})


@app.route('/stream')
def stream():
    if _matrix is None:
        return jsonify({'error': 'Not calibrated'}), 400
    return Response(_generate_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


def _generate_stream():
    for frame in frames():
        result = run_pipeline(frame, _matrix, _width, _height)
        _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 85])
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + buffer.tobytes()
            + b'\r\n'
        )


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
    app.run(debug=True, threaded=True)
