#!/usr/bin/env python3

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
_ODD_FIELDS = {'adaptive_block_size'}


def _config_values() -> dict:
    return {k: v['value'] for k, v in _config.items()}
