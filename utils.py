"""
Các hàm tiện ích cho ứng dụng TCP/NTCP Calculator
"""

import os
import json
import csv
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import datetime
import logging
from pathlib import Path


def create_directory(path: str) -> bool:
    """
    Tạo thư mục nếu chưa tồn tại
    
    Args:
        path: Đường dẫn thư mục
        
    Returns:
        bool: True nếu tạo thành công hoặc đã tồn tại
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {path}: {e}")
        return False


def validate_dose_range(dose_values: np.ndarray, min_dose: float = 0.0, 
                       max_dose: float = 200.0) -> bool:
    """
    Kiểm tra tính hợp lệ của dải liều lượng
    
    Args:
        dose_values: Array liều lượng
        min_dose: Liều lượng tối thiểu
        max_dose: Liều lượng tối đa
        
    Returns:
        bool: True nếu hợp lệ
    """
    if len(dose_values) == 0:
        return False
    
    if np.any(dose_values < min_dose) or np.any(dose_values > max_dose):
        return False
    
    if np.any(np.isnan(dose_values)) or np.any(np.isinf(dose_values)):
        return False
    
    return True


def validate_volume_range(volume_values: np.ndarray, min_volume: float = 0.0,
                         max_volume: float = 100.0) -> bool:
    """
    Kiểm tra tính hợp lệ của dải thể tích
    
    Args:
        volume_values: Array thể tích
        min_volume: Thể tích tối thiểu
        max_volume: Thể tích tối đa
        
    Returns:
        bool: True nếu hợp lệ
    """
    if len(volume_values) == 0:
        return False
    
    if np.any(volume_values < min_volume) or np.any(volume_values > max_volume):
        return False
    
    if np.any(np.isnan(volume_values)) or np.any(np.isinf(volume_values)):
        return False
    
    return True


def format_number(value: float, decimal_places: int = 3) -> str:
    """
    Format số với số chữ số thập phân xác định
    
    Args:
        value: Giá trị số
        decimal_places: Số chữ số thập phân
        
    Returns:
        str: Chuỗi đã format
    """
    if np.isnan(value) or np.isinf(value):
        return "N/A"
    
    format_str = f"{{:.{decimal_places}f}}"
    return format_str.format(value)


def save_results_to_csv(results: Dict, filename: str) -> bool:
    """
    Lưu kết quả ra file CSV
    
    Args:
        results: Dict chứa kết quả
        filename: Tên file
        
    Returns:
        bool: True nếu lưu thành công
    """
    try:
        # Chuẩn bị dữ liệu cho CSV
        csv_data = []
        
        # TCP results
        if 'tcp' in results:
            tcp_data = results['tcp']
            csv_data.append({
                'Type': 'TCP',
                'Structure': results.get('tcp_structure', 'Unknown'),
                'Model': tcp_data.get('model_used', ''),
                'Tumor_Type': tcp_data.get('tumor_type', ''),
                'Probability': tcp_data.get('total_tcp', 0),
                'Mean_TCP': tcp_data.get('mean_tcp', 0),
                'TCP_D95': tcp_data.get('tcp_d95', 0),
                'TCP_D50': tcp_data.get('tcp_d50', 0)
            })
        
        # NTCP results
        if 'ntcp' in results:
            for ntcp_data in results['ntcp']:
                csv_data.append({
                    'Type': 'NTCP',
                    'Structure': ntcp_data.get('organ', 'Unknown'),
                    'Model': ntcp_data.get('model_used', ''),
                    'Endpoint': ntcp_data.get('endpoint', ''),
                    'Probability': ntcp_data.get('ntcp', 0),
                    'Mean_Dose': ntcp_data.get('mean_dose', 0),
                    'Max_Dose': ntcp_data.get('max_dose', 0),
                    'V20': ntcp_data.get('v20', 0),
                    'V30': ntcp_data.get('v30', 0),
                    'V40': ntcp_data.get('v40', 0)
                })
        
        # Lưu ra CSV
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False)
            return True
        
        return False
        
    except Exception as e:
        logging.error(f"Error saving results to CSV: {e}")
        return False


def save_results_to_json(results: Dict, filename: str) -> bool:
    """
    Lưu kết quả ra file JSON
    
    Args:
        results: Dict chứa kết quả
        filename: Tên file
        
    Returns:
        bool: True nếu lưu thành công
    """
    try:
        # Convert numpy arrays to lists for JSON serialization
        json_results = convert_numpy_to_list(results)
        
        # Add metadata
        json_results['metadata'] = {
            'export_time': datetime.datetime.now().isoformat(),
            'application': 'TCP/NTCP Calculator',
            'version': '1.0.0'
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logging.error(f"Error saving results to JSON: {e}")
        return False


def convert_numpy_to_list(obj: Any) -> Any:
    """
    Chuyển đổi numpy arrays thành lists để serialize JSON
    
    Args:
        obj: Object cần chuyển đổi
        
    Returns:
        Any: Object đã chuyển đổi
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_to_list(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_list(item) for item in obj]
    else:
        return obj


def load_results_from_json(filename: str) -> Optional[Dict]:
    """
    Đọc kết quả từ file JSON
    
    Args:
        filename: Tên file
        
    Returns:
        Optional[Dict]: Kết quả đã đọc hoặc None nếu lỗi
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return results
    except Exception as e:
        logging.error(f"Error loading results from JSON: {e}")
        return None


def calculate_confidence_interval(values: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Tính khoảng tin cậy cho dữ liệu
    
    Args:
        values: Array giá trị
        confidence: Mức tin cậy (0-1)
        
    Returns:
        Tuple[float, float]: (lower_bound, upper_bound)
    """
    from scipy import stats
    
    if len(values) == 0:
        return (0.0, 0.0)
    
    mean = np.mean(values)
    sem = stats.sem(values)  # Standard error of mean
    
    # Calculate confidence interval
    alpha = 1 - confidence
    t_value = stats.t.ppf(1 - alpha/2, len(values) - 1)
    
    margin_error = t_value * sem
    
    return (mean - margin_error, mean + margin_error)


def interpolate_dvh_data(dose_bins: np.ndarray, volume_percent: np.ndarray,
                        target_doses: np.ndarray) -> np.ndarray:
    """
    Interpolate DVH data tại các liều lượng mục tiêu
    
    Args:
        dose_bins: Array liều lượng gốc
        volume_percent: Array thể tích gốc
        target_doses: Array liều lượng mục tiêu
        
    Returns:
        np.ndarray: Array thể tích interpolated
    """
    from scipy.interpolate import interp1d
    
    # Sắp xếp dữ liệu theo dose
    sorted_indices = np.argsort(dose_bins)
    sorted_doses = dose_bins[sorted_indices]
    sorted_volumes = volume_percent[sorted_indices]
    
    # Tạo interpolation function
    f = interp1d(sorted_doses, sorted_volumes, kind='linear', 
                bounds_error=False, fill_value=(sorted_volumes[0], sorted_volumes[-1]))
    
    # Interpolate tại target doses
    interpolated_volumes = f(target_doses)
    
    return interpolated_volumes


def calculate_statistical_metrics(values: np.ndarray) -> Dict[str, float]:
    """
    Tính các chỉ số thống kê cơ bản
    
    Args:
        values: Array giá trị
        
    Returns:
        Dict[str, float]: Các chỉ số thống kê
    """
    if len(values) == 0:
        return {}
    
    metrics = {
        'mean': np.mean(values),
        'median': np.median(values),
        'std': np.std(values),
        'min': np.min(values),
        'max': np.max(values),
        'q25': np.percentile(values, 25),
        'q75': np.percentile(values, 75),
        'range': np.max(values) - np.min(values),
        'cv': np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
    }
    
    return metrics


def generate_dose_range(min_dose: float = 0, max_dose: float = 100, 
                       step: float = 0.5) -> np.ndarray:
    """
    Tạo dải liều lượng đều
    
    Args:
        min_dose: Liều lượng tối thiểu
        max_dose: Liều lượng tối đa
        step: Bước nhảy
        
    Returns:
        np.ndarray: Array liều lượng
    """
    return np.arange(min_dose, max_dose + step, step)


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Kiểm tra extension của file
    
    Args:
        filename: Tên file
        allowed_extensions: List các extension cho phép
        
    Returns:
        bool: True nếu hợp lệ
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]


def get_file_size(filename: str) -> int:
    """
    Lấy kích thước file
    
    Args:
        filename: Tên file
        
    Returns:
        int: Kích thước file (bytes)
    """
    try:
        return os.path.getsize(filename)
    except OSError:
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Format kích thước file thành chuỗi dễ đọc
    
    Args:
        size_bytes: Kích thước (bytes)
        
    Returns:
        str: Chuỗi kích thước đã format
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(np.floor(np.log(size_bytes) / np.log(1024)))
    p = np.power(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def create_backup_filename(original_filename: str) -> str:
    """
    Tạo tên file backup
    
    Args:
        original_filename: Tên file gốc
        
    Returns:
        str: Tên file backup
    """
    path = Path(original_filename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    return str(path.parent / backup_name)


def setup_logger(name: str, log_file: str = None, level: str = 'INFO') -> logging.Logger:
    """
    Thiết lập logger
    
    Args:
        name: Tên logger
        log_file: File log (optional)
        level: Mức log
        
    Returns:
        logging.Logger: Logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        create_directory(os.path.dirname(log_file))
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")
    
    # Test dose validation
    dose_values = np.array([0, 10, 20, 30, 40, 50])
    print(f"Dose validation: {validate_dose_range(dose_values)}")
    
    # Test statistical metrics
    metrics = calculate_statistical_metrics(dose_values)
    print(f"Statistical metrics: {metrics}")
    
    print("Utilities module loaded successfully")
