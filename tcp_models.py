"""
Module tính toán các mô hình TCP (Tumor Control Probability)
"""

import numpy as np
import scipy.optimize as opt
from typing import Dict, List, Tuple, Optional
import math


class TCPModels:
    """Class chứa các mô hình tính toán TCP"""
    
    @staticmethod
    def poisson_tcp(dose: float, td50: float, gamma50: float) -> float:
        """
        Mô hình Poisson TCP
        
        Args:
            dose: Liều lượng (Gy)
            td50: Liều lượng cho TCP 50% (Gy)
            gamma50: Độ dốc tại TD50
            
        Returns:
            float: TCP value (0-1)
        """
        try:
            exponent = -4 * gamma50 * (dose - td50) / td50
            tcp = 1 / (1 + np.exp(exponent))
            return np.clip(tcp, 0, 1)
        except (OverflowError, ZeroDivisionError):
            return 0.0 if dose < td50 else 1.0
    
    @staticmethod
    def linear_quadratic_tcp(dose: float, alpha: float, beta: float, 
                           n_fractions: int = 1, repair_time: float = 0) -> float:
        """
        Mô hình Linear-Quadratic TCP
        
        Args:
            dose: Tổng liều lượng (Gy)
            alpha: Tham số alpha (Gy^-1)
            beta: Tham số beta (Gy^-2)
            n_fractions: Số phân liều
            repair_time: Thời gian sửa chữa (giờ)
            
        Returns:
            float: TCP value (0-1)
        """
        if n_fractions <= 0:
            return 0.0
            
        dose_per_fraction = dose / n_fractions
        
        # Tính BED (Biologically Effective Dose)
        bed = dose * (1 + dose_per_fraction / (alpha / beta))
        
        # Survival fraction
        sf = np.exp(-alpha * dose - beta * dose**2)
        
        # TCP từ survival fraction
        tcp = 1 - sf
        
        return np.clip(tcp, 0, 1)
    
    @staticmethod
    def webb_nahum_tcp(dose: float, d50: float, gamma: float, 
                      clonogen_density: float = 1e7) -> float:
        """
        Mô hình Webb-Nahum TCP
        
        Args:
            dose: Liều lượng (Gy)
            d50: Liều lượng cho survival fraction 50%
            gamma: Tham số độ dốc
            clonogen_density: Mật độ tế bào ung thư (cells/cm³)
            
        Returns:
            float: TCP value (0-1)
        """
        try:
            # Survival fraction
            sf = np.exp(-np.log(2) * (dose / d50)**gamma)
            
            # TCP với mật độ tế bào
            tcp = np.exp(-clonogen_density * sf)
            
            return np.clip(tcp, 0, 1)
        except (OverflowError, ZeroDivisionError):
            return 0.0 if dose < d50 else 1.0
    
    @staticmethod
    def logistic_tcp(dose: float, d50: float, k: float) -> float:
        """
        Mô hình Logistic TCP
        
        Args:
            dose: Liều lượng (Gy)
            d50: Liều lượng cho TCP 50%
            k: Tham số độ dốc
            
        Returns:
            float: TCP value (0-1)
        """
        try:
            tcp = 1 / (1 + np.exp(-k * (dose - d50)))
            return np.clip(tcp, 0, 1)
        except OverflowError:
            return 0.0 if dose < d50 else 1.0


class TCPCalculator:
    """Class tính toán TCP cho các structure"""
    
    def __init__(self):
        self.tumor_parameters = {
            'prostate': {'td50': 70, 'gamma50': 2.0, 'alpha': 0.15, 'beta': 0.05},
            'lung': {'td50': 60, 'gamma50': 1.8, 'alpha': 0.18, 'beta': 0.04},
            'breast': {'td50': 50, 'gamma50': 2.2, 'alpha': 0.20, 'beta': 0.05},
            'head_neck': {'td50': 65, 'gamma50': 2.5, 'alpha': 0.25, 'beta': 0.06},
            'rectum': {'td50': 55, 'gamma50': 1.9, 'alpha': 0.16, 'beta': 0.04}
        }
    
    def calculate_tcp_from_dvh(self, dose_bins: np.ndarray, volume_percent: np.ndarray,
                              tumor_type: str, model: str = 'poisson') -> Dict:
        """
        Tính toán TCP từ DVH data
        
        Args:
            dose_bins: Array liều lượng
            volume_percent: Array phần trăm thể tích
            tumor_type: Loại khối u
            model: Mô hình TCP ('poisson', 'lq', 'webb_nahum', 'logistic')
            
        Returns:
            Dict: Kết quả TCP và thông tin chi tiết
        """
        if tumor_type not in self.tumor_parameters:
            raise ValueError(f"Không hỗ trợ loại tumor: {tumor_type}")
        
        params = self.tumor_parameters[tumor_type]
        
        # Tính TCP cho từng bin
        tcp_values = []
        
        for i, dose in enumerate(dose_bins):
            volume_fraction = volume_percent[i] / 100.0
            
            if model == 'poisson':
                tcp = TCPModels.poisson_tcp(dose, params['td50'], params['gamma50'])
            elif model == 'lq':
                tcp = TCPModels.linear_quadratic_tcp(dose, params['alpha'], params['beta'])
            elif model == 'webb_nahum':
                tcp = TCPModels.webb_nahum_tcp(dose, params['td50'], params['gamma50'])
            elif model == 'logistic':
                tcp = TCPModels.logistic_tcp(dose, params['td50'], params['gamma50'])
            else:
                raise ValueError(f"Mô hình không hỗ trợ: {model}")
            
            tcp_values.append(tcp * volume_fraction)
        
        # TCP tổng thể
        total_tcp = np.sum(tcp_values)
        mean_tcp = np.mean(tcp_values)
        
        # Tính TCP cho các mức dose đặc biệt
        d95_index = np.argmin(np.abs(volume_percent - 95))
        d50_index = np.argmin(np.abs(volume_percent - 50))
        
        tcp_d95 = tcp_values[d95_index] if d95_index < len(tcp_values) else 0
        tcp_d50 = tcp_values[d50_index] if d50_index < len(tcp_values) else 0
        
        return {
            'total_tcp': total_tcp,
            'mean_tcp': mean_tcp,
            'tcp_d95': tcp_d95,
            'tcp_d50': tcp_d50,
            'tcp_values': tcp_values,
            'model_used': model,
            'tumor_type': tumor_type,
            'parameters': params
        }
    
    def calculate_tcp_uniform_dose(self, dose: float, tumor_type: str, 
                                 model: str = 'poisson') -> Dict:
        """
        Tính toán TCP cho liều lượng đồng nhất
        
        Args:
            dose: Liều lượng (Gy)
            tumor_type: Loại khối u
            model: Mô hình TCP
            
        Returns:
            Dict: Kết quả TCP
        """
        if tumor_type not in self.tumor_parameters:
            raise ValueError(f"Không hỗ trợ loại tumor: {tumor_type}")
        
        params = self.tumor_parameters[tumor_type]
        
        if model == 'poisson':
            tcp = TCPModels.poisson_tcp(dose, params['td50'], params['gamma50'])
        elif model == 'lq':
            tcp = TCPModels.linear_quadratic_tcp(dose, params['alpha'], params['beta'])
        elif model == 'webb_nahum':
            tcp = TCPModels.webb_nahum_tcp(dose, params['td50'], params['gamma50'])
        elif model == 'logistic':
            tcp = TCPModels.logistic_tcp(dose, params['td50'], params['gamma50'])
        else:
            raise ValueError(f"Mô hình không hỗ trợ: {model}")
        
        return {
            'tcp': tcp,
            'dose': dose,
            'model_used': model,
            'tumor_type': tumor_type,
            'parameters': params
        }
    
    def add_tumor_parameters(self, tumor_type: str, parameters: Dict):
        """
        Thêm tham số cho loại tumor mới
        
        Args:
            tumor_type: Tên loại tumor
            parameters: Dict chứa các tham số (td50, gamma50, alpha, beta)
        """
        required_params = ['td50', 'gamma50', 'alpha', 'beta']
        
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Thiếu tham số: {param}")
        
        self.tumor_parameters[tumor_type] = parameters
        print(f"Đã thêm tham số cho tumor type: {tumor_type}")
    
    def get_available_tumor_types(self) -> List[str]:
        """Lấy danh sách các loại tumor có sẵn"""
        return list(self.tumor_parameters.keys())
    
    def optimize_parameters(self, dose_data: np.ndarray, tcp_data: np.ndarray,
                          tumor_type: str, model: str = 'poisson') -> Dict:
        """
        Tối ưu hóa tham số mô hình từ dữ liệu thực nghiệm
        
        Args:
            dose_data: Array liều lượng thực nghiệm
            tcp_data: Array TCP thực nghiệm
            tumor_type: Loại tumor
            model: Mô hình TCP
            
        Returns:
            Dict: Tham số tối ưu
        """
        def objective_function(params):
            if model == 'poisson':
                predicted_tcp = [TCPModels.poisson_tcp(d, params[0], params[1]) 
                               for d in dose_data]
            elif model == 'lq':
                predicted_tcp = [TCPModels.linear_quadratic_tcp(d, params[0], params[1]) 
                               for d in dose_data]
            else:
                raise ValueError(f"Optimization not implemented for model: {model}")
            
            # Mean squared error
            mse = np.mean((np.array(predicted_tcp) - tcp_data)**2)
            return mse
        
        # Initial guess
        if model == 'poisson':
            initial_guess = [70, 2.0]  # td50, gamma50
            bounds = [(30, 100), (0.5, 5.0)]
        elif model == 'lq':
            initial_guess = [0.15, 0.05]  # alpha, beta
            bounds = [(0.01, 1.0), (0.001, 0.2)]
        else:
            raise ValueError(f"Optimization not implemented for model: {model}")
        
        # Optimization
        result = opt.minimize(objective_function, initial_guess, 
                            bounds=bounds, method='L-BFGS-B')
        
        if result.success:
            optimized_params = result.x
            if model == 'poisson':
                params_dict = {'td50': optimized_params[0], 'gamma50': optimized_params[1]}
            elif model == 'lq':
                params_dict = {'alpha': optimized_params[0], 'beta': optimized_params[1]}
            
            return {
                'optimized_parameters': params_dict,
                'optimization_success': True,
                'final_error': result.fun,
                'model': model
            }
        else:
            return {
                'optimized_parameters': None,
                'optimization_success': False,
                'error_message': result.message,
                'model': model
            }


if __name__ == "__main__":
    # Test code
    calculator = TCPCalculator()
    
    # Test uniform dose calculation
    result = calculator.calculate_tcp_uniform_dose(70, 'prostate', 'poisson')
    print(f"TCP for 70 Gy to prostate: {result['tcp']:.3f}")
    
    print("TCP Models module loaded successfully")
