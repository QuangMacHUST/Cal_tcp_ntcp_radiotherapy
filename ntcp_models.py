"""
Module tính toán các mô hình NTCP (Normal Tissue Complication Probability)
"""

import numpy as np
import scipy.special as special
import scipy.optimize as opt
from typing import Dict, List, Tuple, Optional
import math


class NTCPModels:
    """Class chứa các mô hình tính toán NTCP"""
    
    @staticmethod
    def lyman_kutcher_burman(dose: float, td50: float, m: float, n: float) -> float:
        """
        Mô hình Lyman-Kutcher-Burman NTCP
        
        Args:
            dose: Liều lượng (Gy)
            td50: Liều lượng cho NTCP 50% (Gy)
            m: Tham số độ dốc
            n: Tham số thể tích
            
        Returns:
            float: NTCP value (0-1)
        """
        try:
            t = (dose - td50) / (m * td50)
            # Sử dụng cumulative distribution function của phân phối chuẩn
            ntcp = 0.5 * (1 + special.erf(t / np.sqrt(2)))
            return np.clip(ntcp, 0, 1)
        except (OverflowError, ZeroDivisionError):
            return 0.0 if dose < td50 else 1.0
    
    @staticmethod
    def critical_volume_model(dose: float, volume_fraction: float, 
                            d50: float, v50: float, gamma: float) -> float:
        """
        Mô hình Critical Volume
        
        Args:
            dose: Liều lượng (Gy)
            volume_fraction: Phần trăm thể tích nhận liều (0-1)
            d50: Liều lượng cho NTCP 50%
            v50: Thể tích cho NTCP 50%
            gamma: Tham số độ dốc
            
        Returns:
            float: NTCP value (0-1)
        """
        try:
            if volume_fraction < v50:
                return 0.0
            
            effective_dose = dose * (volume_fraction / v50)**gamma
            t = (effective_dose - d50) / d50
            ntcp = 0.5 * (1 + special.erf(t))
            
            return np.clip(ntcp, 0, 1)
        except (OverflowError, ZeroDivisionError):
            return 0.0
    
    @staticmethod
    def relative_seriality_model(dose: float, d50: float, gamma: float, s: float) -> float:
        """
        Mô hình Relative Seriality
        
        Args:
            dose: Liều lượng (Gy)
            d50: Liều lượng cho NTCP 50%
            gamma: Tham số độ dốc
            s: Tham số seriality (0=parallel, 1=serial)
            
        Returns:
            float: NTCP value (0-1)
        """
        try:
            # Probability of complication for uniform dose
            p_uniform = 0.5 * (1 + special.erf((dose - d50) / (gamma * d50)))
            
            # Adjust for seriality
            if s == 0:  # Parallel organ
                ntcp = p_uniform
            elif s == 1:  # Serial organ
                ntcp = 1 - (1 - p_uniform)**dose
            else:  # Mixed seriality
                p_parallel = p_uniform
                p_serial = 1 - (1 - p_uniform)**dose
                ntcp = s * p_serial + (1 - s) * p_parallel
            
            return np.clip(ntcp, 0, 1)
        except (OverflowError, ZeroDivisionError):
            return 0.0
    
    @staticmethod
    def logistic_ntcp(dose: float, d50: float, k: float) -> float:
        """
        Mô hình Logistic NTCP
        
        Args:
            dose: Liều lượng (Gy)
            d50: Liều lượng cho NTCP 50%
            k: Tham số độ dốc
            
        Returns:
            float: NTCP value (0-1)
        """
        try:
            ntcp = 1 / (1 + np.exp(-k * (dose - d50)))
            return np.clip(ntcp, 0, 1)
        except OverflowError:
            return 0.0 if dose < d50 else 1.0
    
    @staticmethod
    def poisson_ntcp(dose: float, d50: float, gamma: float) -> float:
        """
        Mô hình Poisson NTCP
        
        Args:
            dose: Liều lượng (Gy)
            d50: Liều lượng cho NTCP 50%
            gamma: Tham số độ dốc
            
        Returns:
            float: NTCP value (0-1)
        """
        try:
            t = 2 * gamma * (dose / d50 - 1)
            ntcp = 0.5 * (1 + special.erf(t / np.sqrt(2)))
            return np.clip(ntcp, 0, 1)
        except (OverflowError, ZeroDivisionError):
            return 0.0 if dose < d50 else 1.0


class NTCPCalculator:
    """Class tính toán NTCP cho các organ at risk"""
    
    def __init__(self):
        self.organ_parameters = {
            'lung': {
                'td50': 24.5, 'm': 0.18, 'n': 0.87, 'd50': 20, 'gamma': 1.0,
                'endpoint': 'pneumonitis', 'seriality': 0.0
            },
            'heart': {
                'td50': 48, 'm': 0.16, 'n': 0.35, 'd50': 45, 'gamma': 1.2,
                'endpoint': 'pericarditis', 'seriality': 0.5
            },
            'spinal_cord': {
                'td50': 66.5, 'm': 0.175, 'n': 0.05, 'd50': 60, 'gamma': 1.5,
                'endpoint': 'myelitis', 'seriality': 1.0
            },
            'rectum': {
                'td50': 76.9, 'm': 0.15, 'n': 0.12, 'd50': 70, 'gamma': 1.0,
                'endpoint': 'bleeding', 'seriality': 0.3
            },
            'bladder': {
                'td50': 80, 'm': 0.11, 'n': 0.5, 'd50': 75, 'gamma': 1.1,
                'endpoint': 'contracture', 'seriality': 0.2
            },
            'kidney': {
                'td50': 28, 'm': 0.1, 'n': 0.87, 'd50': 25, 'gamma': 0.8,
                'endpoint': 'nephritis', 'seriality': 0.0
            },
            'liver': {
                'td50': 40, 'm': 0.12, 'n': 0.97, 'd50': 35, 'gamma': 0.9,
                'endpoint': 'hepatitis', 'seriality': 0.1
            },
            'parotid': {
                'td50': 46, 'm': 0.4, 'n': 0.7, 'd50': 40, 'gamma': 1.3,
                'endpoint': 'xerostomia', 'seriality': 0.0
            }
        }
    
    def calculate_ntcp_from_dvh(self, dose_bins: np.ndarray, volume_percent: np.ndarray,
                               organ: str, model: str = 'lkb') -> Dict:
        """
        Tính toán NTCP từ DVH data
        
        Args:
            dose_bins: Array liều lượng
            volume_percent: Array phần trăm thể tích
            organ: Tên organ at risk
            model: Mô hình NTCP ('lkb', 'critical_volume', 'relative_seriality', 'logistic', 'poisson')
            
        Returns:
            Dict: Kết quả NTCP và thông tin chi tiết
        """
        if organ not in self.organ_parameters:
            raise ValueError(f"Không hỗ trợ organ: {organ}")
        
        params = self.organ_parameters[organ]
        
        # Tính equivalent uniform dose (EUD) cho LKB model
        if model == 'lkb':
            eud = self._calculate_eud(dose_bins, volume_percent, params['n'])
            ntcp = NTCPModels.lyman_kutcher_burman(eud, params['td50'], params['m'], params['n'])
        
        elif model == 'critical_volume':
            # Tính NTCP cho critical volume model
            max_dose = np.max(dose_bins)
            volume_above_threshold = np.sum(volume_percent[dose_bins > params['d50']]) / 100.0
            ntcp = NTCPModels.critical_volume_model(max_dose, volume_above_threshold, 
                                                  params['d50'], 0.5, params['gamma'])
        
        elif model == 'relative_seriality':
            mean_dose = np.average(dose_bins, weights=volume_percent)
            ntcp = NTCPModels.relative_seriality_model(mean_dose, params['d50'], 
                                                     params['gamma'], params['seriality'])
        
        elif model == 'logistic':
            mean_dose = np.average(dose_bins, weights=volume_percent)
            ntcp = NTCPModels.logistic_ntcp(mean_dose, params['d50'], params['gamma'])
        
        elif model == 'poisson':
            mean_dose = np.average(dose_bins, weights=volume_percent)
            ntcp = NTCPModels.poisson_ntcp(mean_dose, params['d50'], params['gamma'])
        
        else:
            raise ValueError(f"Mô hình không hỗ trợ: {model}")
        
        # Tính toán các thống kê bổ sung
        mean_dose = np.average(dose_bins, weights=volume_percent)
        max_dose = np.max(dose_bins)
        
        # Tính V20, V30, V40 (volume receiving ≥20, 30, 40 Gy)
        v20 = np.sum(volume_percent[dose_bins >= 20]) if np.any(dose_bins >= 20) else 0
        v30 = np.sum(volume_percent[dose_bins >= 30]) if np.any(dose_bins >= 30) else 0
        v40 = np.sum(volume_percent[dose_bins >= 40]) if np.any(dose_bins >= 40) else 0
        
        return {
            'ntcp': ntcp,
            'mean_dose': mean_dose,
            'max_dose': max_dose,
            'v20': v20,
            'v30': v30,
            'v40': v40,
            'model_used': model,
            'organ': organ,
            'endpoint': params['endpoint'],
            'parameters': params
        }
    
    def _calculate_eud(self, dose_bins: np.ndarray, volume_percent: np.ndarray, n: float) -> float:
        """
        Tính toán Equivalent Uniform Dose (EUD)
        
        Args:
            dose_bins: Array liều lượng
            volume_percent: Array phần trăm thể tích
            n: Tham số thể tích
            
        Returns:
            float: EUD value
        """
        if len(dose_bins) != len(volume_percent):
            raise ValueError("Dose bins và volume percent phải có cùng độ dài")
        
        # Normalize volume percentages
        volume_fractions = volume_percent / np.sum(volume_percent)
        
        if n == 0:
            # Parallel organ (n=0): EUD = mean dose
            eud = np.average(dose_bins, weights=volume_fractions)
        elif np.isinf(n):
            # Serial organ (n=∞): EUD = max dose
            eud = np.max(dose_bins)
        else:
            # General case
            try:
                powered_doses = np.power(dose_bins, 1/n)
                weighted_sum = np.average(powered_doses, weights=volume_fractions)
                eud = np.power(weighted_sum, n)
            except (OverflowError, ZeroDivisionError):
                eud = np.max(dose_bins)
        
        return eud
    
    def calculate_ntcp_uniform_dose(self, dose: float, organ: str, 
                                  model: str = 'lkb') -> Dict:
        """
        Tính toán NTCP cho liều lượng đồng nhất
        
        Args:
            dose: Liều lượng (Gy)
            organ: Tên organ at risk
            model: Mô hình NTCP
            
        Returns:
            Dict: Kết quả NTCP
        """
        if organ not in self.organ_parameters:
            raise ValueError(f"Không hỗ trợ organ: {organ}")
        
        params = self.organ_parameters[organ]
        
        if model == 'lkb':
            ntcp = NTCPModels.lyman_kutcher_burman(dose, params['td50'], params['m'], params['n'])
        elif model == 'critical_volume':
            ntcp = NTCPModels.critical_volume_model(dose, 1.0, params['d50'], 0.5, params['gamma'])
        elif model == 'relative_seriality':
            ntcp = NTCPModels.relative_seriality_model(dose, params['d50'], 
                                                     params['gamma'], params['seriality'])
        elif model == 'logistic':
            ntcp = NTCPModels.logistic_ntcp(dose, params['d50'], params['gamma'])
        elif model == 'poisson':
            ntcp = NTCPModels.poisson_ntcp(dose, params['d50'], params['gamma'])
        else:
            raise ValueError(f"Mô hình không hỗ trợ: {model}")
        
        return {
            'ntcp': ntcp,
            'dose': dose,
            'model_used': model,
            'organ': organ,
            'endpoint': params['endpoint'],
            'parameters': params
        }
    
    def add_organ_parameters(self, organ: str, parameters: Dict):
        """
        Thêm tham số cho organ mới
        
        Args:
            organ: Tên organ
            parameters: Dict chứa các tham số
        """
        required_params = ['td50', 'm', 'n', 'd50', 'gamma', 'endpoint']
        
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Thiếu tham số: {param}")
        
        self.organ_parameters[organ] = parameters
        print(f"Đã thêm tham số cho organ: {organ}")
    
    def get_available_organs(self) -> List[str]:
        """Lấy danh sách các organ có sẵn"""
        return list(self.organ_parameters.keys())
    
    def calculate_complication_free_probability(self, ntcp_results: List[Dict]) -> float:
        """
        Tính toán xác suất không có biến chứng cho nhiều organ
        
        Args:
            ntcp_results: List các kết quả NTCP cho từng organ
            
        Returns:
            float: Complication-free probability
        """
        cfp = 1.0
        for result in ntcp_results:
            cfp *= (1 - result['ntcp'])
        
        return cfp
    
    def calculate_therapeutic_ratio(self, tcp: float, ntcp_total: float) -> Dict:
        """
        Tính toán Therapeutic Ratio
        
        Args:
            tcp: Tumor Control Probability
            ntcp_total: Total NTCP (có thể từ nhiều organ)
            
        Returns:
            Dict: Therapeutic ratio và các chỉ số liên quan
        """
        # Uncomplicated cure probability
        ucp = tcp * (1 - ntcp_total)
        
        # Therapeutic ratio (different definitions)
        tr1 = tcp / ntcp_total if ntcp_total > 0 else float('inf')
        tr2 = ucp / ntcp_total if ntcp_total > 0 else float('inf')
        
        return {
            'uncomplicated_cure_probability': ucp,
            'therapeutic_ratio_1': tr1,  # TCP/NTCP
            'therapeutic_ratio_2': tr2,  # UCP/NTCP
            'tcp': tcp,
            'ntcp': ntcp_total
        }


if __name__ == "__main__":
    # Test code
    calculator = NTCPCalculator()
    
    # Test uniform dose calculation
    result = calculator.calculate_ntcp_uniform_dose(20, 'lung', 'lkb')
    print(f"NTCP for 20 Gy to lung: {result['ntcp']:.3f}")
    
    print("NTCP Models module loaded successfully")
