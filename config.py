#!/usr/bin/env python3

_config = {
    'adaptive_block_size': {
        'type': 'range', 'value': 45,  'min': 3,   'max': 101, 'step': 2,
        'label': 'Block Size',       'unit': 'px', 'group': 'ink_detection',
    },
    'adaptive_c': {
        'type': 'range', 'value': 5,   'min': 0,   'max': 20,  'step': 1,
        'label': 'Threshold C',      'unit': '',   'group': 'ink_detection',
    },
    'cell_size': {
        'type': 'range', 'value': 60,  'min': 10,  'max': 200, 'step': 5,
        'label': 'Grid Cell Size',   'unit': 'px', 'group': 'grid_path',
    },
    'ink_pixel_threshold': {
        'type': 'range', 'value': 15,  'min': 1,   'max': 200, 'step': 1,
        'label': 'Ink Threshold',    'unit': 'px', 'group': 'grid_path',
    },
    'robot_mask_radius': {
        'type': 'range', 'value': 100, 'min': 0,   'max': 300, 'step': 5,
        'label': 'Mask Radius',      'unit': 'px', 'group': 'robot',
    },
    'show_grid': {
        'type': 'bool', 'value': True,
        'label': 'Grid Cells',       'group': 'debug',
    },
    'show_aruco': {
        'type': 'bool', 'value': True,
        'label': 'ArUco Marker',     'group': 'debug',
    },
    'show_path_lines': {
        'type': 'bool', 'value': True,
        'label': 'Path Lines',       'group': 'debug',
    },
    'show_path_numbers': {
        'type': 'bool', 'value': True,
        'label': 'Path Numbers',     'group': 'debug',
    },
    'show_orientation': {
        'type': 'bool', 'value': True,
        'label': 'Robot Orientation','group': 'debug',
    },
    'show_direction': {
        'type': 'bool', 'value': True,
        'label': 'Direction Arrow',  'group': 'debug',
    },
}

# Fields that must stay odd (OpenCV requirement).
_ODD_FIELDS = {'adaptive_block_size'}


def _config_values() -> dict:
    return {k: v['value'] for k, v in _config.items()}
