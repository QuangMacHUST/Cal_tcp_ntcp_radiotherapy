"""
File cấu hình cho ứng dụng TCP/NTCP Calculator
"""

import os
from typing import Dict, Any

# Application settings
APP_NAME = "TCP/NTCP Calculator"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Radiotherapy Team"

# Default directories
DEFAULT_DICOM_DIR = os.path.expanduser("~/Documents/DICOM")
DEFAULT_EXPORT_DIR = os.path.expanduser("~/Documents/TCP_NTCP_Results")
DEFAULT_LOG_DIR = "logs"

# Create directories if they don't exist
for directory in [DEFAULT_DICOM_DIR, DEFAULT_EXPORT_DIR, DEFAULT_LOG_DIR]:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            pass

# GUI settings
GUI_SETTINGS = {
    'window_width': 1200,
    'window_height': 800,
    'min_width': 800,
    'min_height': 600,
    'font_family': 'Arial',
    'font_size': 10,
    'theme': 'default'
}

# Default TCP parameters for different tumor types
DEFAULT_TCP_PARAMETERS = {
    'prostate': {
        'td50': 70.0,
        'gamma50': 2.0,
        'alpha': 0.15,
        'beta': 0.05,
        'description': 'Prostate adenocarcinoma'
    },
    'lung': {
        'td50': 60.0,
        'gamma50': 1.8,
        'alpha': 0.18,
        'beta': 0.04,
        'description': 'Non-small cell lung cancer'
    },
    'breast': {
        'td50': 50.0,
        'gamma50': 2.2,
        'alpha': 0.20,
        'beta': 0.05,
        'description': 'Breast adenocarcinoma'
    },
    'head_neck': {
        'td50': 65.0,
        'gamma50': 2.5,
        'alpha': 0.25,
        'beta': 0.06,
        'description': 'Head and neck squamous cell carcinoma'
    },
    'rectum': {
        'td50': 55.0,
        'gamma50': 1.9,
        'alpha': 0.16,
        'beta': 0.04,
        'description': 'Rectal adenocarcinoma'
    },
    'cervix': {
        'td50': 65.0,
        'gamma50': 2.1,
        'alpha': 0.22,
        'beta': 0.05,
        'description': 'Cervical squamous cell carcinoma'
    }
}

# Default NTCP parameters for different organs
DEFAULT_NTCP_PARAMETERS = {
    'lung': {
        'td50': 24.5,
        'm': 0.18,
        'n': 0.87,
        'd50': 20.0,
        'gamma': 1.0,
        'endpoint': 'pneumonitis',
        'seriality': 0.0,
        'description': 'Radiation pneumonitis (Grade ≥2)'
    },
    'heart': {
        'td50': 48.0,
        'm': 0.16,
        'n': 0.35,
        'd50': 45.0,
        'gamma': 1.2,
        'endpoint': 'pericarditis',
        'seriality': 0.5,
        'description': 'Pericarditis (Grade ≥2)'
    },
    'spinal_cord': {
        'td50': 66.5,
        'm': 0.175,
        'n': 0.05,
        'd50': 60.0,
        'gamma': 1.5,
        'endpoint': 'myelitis',
        'seriality': 1.0,
        'description': 'Myelitis (Grade ≥2)'
    },
    'rectum': {
        'td50': 76.9,
        'm': 0.15,
        'n': 0.12,
        'd50': 70.0,
        'gamma': 1.0,
        'endpoint': 'bleeding',
        'seriality': 0.3,
        'description': 'Rectal bleeding (Grade ≥2)'
    },
    'bladder': {
        'td50': 80.0,
        'm': 0.11,
        'n': 0.5,
        'd50': 75.0,
        'gamma': 1.1,
        'endpoint': 'contracture',
        'seriality': 0.2,
        'description': 'Bladder contracture (Grade ≥2)'
    },
    'kidney': {
        'td50': 28.0,
        'm': 0.1,
        'n': 0.87,
        'd50': 25.0,
        'gamma': 0.8,
        'endpoint': 'nephritis',
        'seriality': 0.0,
        'description': 'Nephritis (Grade ≥2)'
    },
    'liver': {
        'td50': 40.0,
        'm': 0.12,
        'n': 0.97,
        'd50': 35.0,
        'gamma': 0.9,
        'endpoint': 'hepatitis',
        'seriality': 0.1,
        'description': 'Hepatitis (Grade ≥2)'
    },
    'parotid': {
        'td50': 46.0,
        'm': 0.4,
        'n': 0.7,
        'd50': 40.0,
        'gamma': 1.3,
        'endpoint': 'xerostomia',
        'seriality': 0.0,
        'description': 'Xerostomia (Grade ≥2)'
    },
    'brainstem': {
        'td50': 65.0,
        'm': 0.16,
        'n': 0.16,
        'd50': 60.0,
        'gamma': 1.4,
        'endpoint': 'necrosis',
        'seriality': 0.9,
        'description': 'Brainstem necrosis (Grade ≥2)'
    },
    'optic_nerve': {
        'td50': 65.0,
        'm': 0.25,
        'n': 0.25,
        'd50': 60.0,
        'gamma': 1.5,
        'endpoint': 'neuropathy',
        'seriality': 0.8,
        'description': 'Optic neuropathy (Grade ≥2)'
    }
}

# Calculation settings
CALCULATION_SETTINGS = {
    'dvh_bins': 100,
    'dose_resolution': 0.1,  # Gy
    'max_dose_range': 100,   # Gy
    'volume_tolerance': 0.01,  # 1%
    'convergence_tolerance': 1e-6
}

# Plot settings
PLOT_SETTINGS = {
    'figure_size': (10, 6),
    'dpi': 300,
    'line_width': 2,
    'grid_alpha': 0.3,
    'legend_location': 'best',
    'color_palette': 'tab10',
    'save_format': 'png'
}

# Export settings
EXPORT_SETTINGS = {
    'csv_separator': ',',
    'decimal_places': 4,
    'include_parameters': True,
    'include_plots': True,
    'report_format': 'pdf'
}

# Logging settings
LOGGING_SETTINGS = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'max_file_size': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5
}

# Validation settings
VALIDATION_SETTINGS = {
    'min_dose': 0.0,
    'max_dose': 200.0,
    'min_volume': 0.0,
    'max_volume': 100.0,
    'required_dicom_tags': [
        'Modality',
        'StudyInstanceUID',
        'SeriesInstanceUID',
        'SOPInstanceUID'
    ]
}

# Model-specific settings
MODEL_SETTINGS = {
    'tcp_models': {
        'poisson': {
            'name': 'Poisson TCP',
            'parameters': ['td50', 'gamma50'],
            'description': 'Classical Poisson TCP model'
        },
        'lq': {
            'name': 'Linear-Quadratic TCP',
            'parameters': ['alpha', 'beta'],
            'description': 'Linear-Quadratic based TCP model'
        },
        'webb_nahum': {
            'name': 'Webb-Nahum TCP',
            'parameters': ['d50', 'gamma', 'clonogen_density'],
            'description': 'Webb-Nahum TCP model with clonogen density'
        },
        'logistic': {
            'name': 'Logistic TCP',
            'parameters': ['d50', 'k'],
            'description': 'Logistic TCP model'
        }
    },
    'ntcp_models': {
        'lkb': {
            'name': 'Lyman-Kutcher-Burman',
            'parameters': ['td50', 'm', 'n'],
            'description': 'Classical LKB NTCP model'
        },
        'critical_volume': {
            'name': 'Critical Volume',
            'parameters': ['d50', 'v50', 'gamma'],
            'description': 'Critical volume NTCP model'
        },
        'relative_seriality': {
            'name': 'Relative Seriality',
            'parameters': ['d50', 'gamma', 's'],
            'description': 'Relative seriality NTCP model'
        },
        'logistic': {
            'name': 'Logistic NTCP',
            'parameters': ['d50', 'k'],
            'description': 'Logistic NTCP model'
        },
        'poisson': {
            'name': 'Poisson NTCP',
            'parameters': ['d50', 'gamma'],
            'description': 'Poisson NTCP model'
        }
    }
}

# File format settings
FILE_FORMATS = {
    'dicom': {
        'extensions': ['.dcm', '.dicom'],
        'description': 'DICOM files'
    },
    'images': {
        'extensions': ['.png', '.jpg', '.jpeg', '.tiff', '.bmp'],
        'description': 'Image files'
    },
    'data': {
        'extensions': ['.csv', '.xlsx', '.txt'],
        'description': 'Data files'
    },
    'reports': {
        'extensions': ['.pdf', '.html', '.docx'],
        'description': 'Report files'
    }
}


def get_config(section: str = None) -> Dict[str, Any]:
    """
    Lấy cấu hình theo section
    
    Args:
        section: Tên section cấu hình
        
    Returns:
        Dict: Cấu hình tương ứng
    """
    config_map = {
        'gui': GUI_SETTINGS,
        'tcp_params': DEFAULT_TCP_PARAMETERS,
        'ntcp_params': DEFAULT_NTCP_PARAMETERS,
        'calculation': CALCULATION_SETTINGS,
        'plot': PLOT_SETTINGS,
        'export': EXPORT_SETTINGS,
        'logging': LOGGING_SETTINGS,
        'validation': VALIDATION_SETTINGS,
        'models': MODEL_SETTINGS,
        'file_formats': FILE_FORMATS
    }
    
    if section is None:
        return {
            'app_name': APP_NAME,
            'app_version': APP_VERSION,
            'app_author': APP_AUTHOR,
            **config_map
        }
    
    return config_map.get(section, {})


def update_config(section: str, key: str, value: Any) -> bool:
    """
    Cập nhật cấu hình
    
    Args:
        section: Tên section
        key: Tên key
        value: Giá trị mới
        
    Returns:
        bool: True nếu cập nhật thành công
    """
    config_map = {
        'gui': GUI_SETTINGS,
        'tcp_params': DEFAULT_TCP_PARAMETERS,
        'ntcp_params': DEFAULT_NTCP_PARAMETERS,
        'calculation': CALCULATION_SETTINGS,
        'plot': PLOT_SETTINGS,
        'export': EXPORT_SETTINGS,
        'logging': LOGGING_SETTINGS,
        'validation': VALIDATION_SETTINGS,
        'models': MODEL_SETTINGS,
        'file_formats': FILE_FORMATS
    }
    
    if section in config_map and key in config_map[section]:
        config_map[section][key] = value
        return True
    
    return False


if __name__ == "__main__":
    # Test configuration
    print(f"Application: {APP_NAME} v{APP_VERSION}")
    print(f"Available configurations: {list(get_config().keys())}")
    
    # Test getting specific config
    gui_config = get_config('gui')
    print(f"GUI settings: {gui_config}")
