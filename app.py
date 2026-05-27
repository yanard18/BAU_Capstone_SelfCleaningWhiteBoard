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

# Each field: value + slider metadata + sidebar group.
# The frontend builds its UI entirely from this — no ranges hardcoded in HTML.
_config = {
    'adaptive_block_size': {
        'value': 45,  'min': 3,  'max': 101, 'step': 2,
        'label': 'Block Size',    'unit': 'px', 'group': 'ink_detection',
    },
    'adaptive_c': {
        'value': 5,   'min': 0,  'max': 20,  'step': 1,
        'label': 'Threshold C',   'unit': '',   'group': 'ink_detection',
    },
    'morph_kernel_size': {
        'value': 3,   'min': 3,  'max': 7,   'step': 2,
        'label': 'Kernel Size',   'unit': 'px', 'group': 'ink_detection',
    },
    'cell_size': {
        'value': 60,  'min': 10, 'max': 200, 'step': 5,
        'label': 'Grid Cell Size','unit': 'px', 'group': 'grid_path',
    },
    'ink_pixel_threshold': {
        'value': 15,  'min': 1,  'max': 200, 'step': 1,
        'label': 'Ink Threshold', 'unit': 'px', 'group': 'grid_path',
    },
    'robot_mask_radius': {
        'value': 100, 'min': 0,  'max': 300, 'step': 5,
        'label': 'Mask Radius',   'unit': 'px', 'group': 'robot',
    },
}

# Fields that must stay odd (OpenCV requirement).
_ODD_FIELDS = {'adaptive_block_size', 'morph_kernel_size'}


def _config_values() -> dict:
    return {k: v['value'] for k, v in _config.items()}


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/status')
def status():
    return jsonify({'calibrated': _matrix is not None})


@app.route('/config')
def get_config():
    return jsonify(_config)


@app.route('/config', methods=['POST'])
def set_config():
    data = request.get_json()
    for key, raw in data.items():
        if key not in _config:
            return jsonify({'error': f'Unknown field: {key}'}), 400
        field = _config[key]
        value = int(round(float(raw)))
        if key in _ODD_FIELDS and value % 2 == 0:
            value += 1
        _config[key]['value'] = max(field['min'], min(field['max'], value))
    return jsonify(_config)


@app.route('/debug/<name>', methods=['POST'])
def set_debug(name):
    if name not in _debug_flags:
        return jsonify({'error': f'Unknown debug flag: {name}'}), 400
    _debug_flags[name] = bool(request.get_json().get('enabled', False))
    return jsonify({'ok': True, 'flags': _debug_flags})


VIEWS = {'output', 'ink_mask'}


@app.route('/stream/<view>')
def stream(view):
    if _matrix is None:
        return jsonify({'error': 'Not calibrated'}), 400
    if view not in VIEWS:
        return jsonify({'error': f'Unknown view: {view}'}), 400
    return Response(_generate_stream(view), mimetype='multipart/x-mixed-replace; boundary=frame')


def _generate_stream(view):
    for frame in frames():
        # Re-read config on every frame so slider changes take effect immediately.
        result = run_pipeline(frame, _matrix, _width, _height, _config_values())
        _, buffer = cv2.imencode('.jpg', result[view], [cv2.IMWRITE_JPEG_QUALITY, 85])
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
    result = run_pipeline(image, _matrix, _width, _height, _config_values())

    _, buffer = cv2.imencode('.png', result['output'])
    return send_file(io.BytesIO(buffer), mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
