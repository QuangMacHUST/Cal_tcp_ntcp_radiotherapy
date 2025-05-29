"""
Module tính toán liều lượng và các chỉ số dose-volume
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from scipy import interpolate
import warnings


class DoseCalculations:
    """Class tính toán các chỉ số liều lượng"""
    
    @staticmethod
    def calculate_dose_statistics(dose_bins: np.ndarray, volume_percent: np.ndarray) -> Dict:
        """
        Tính toán các thống kê dose cơ bản
        
        Args:
            dose_bins: Array liều lượng (Gy)
            volume_percent: Array phần trăm thể tích
            
        Returns:
            Dict: Các thống kê dose
        """
        if len(dose_bins) != len(volume_percent):
            raise ValueError("Dose bins và volume percent phải có cùng độ dài")
        
        # Normalize volume để tổng = 100%
        volume_normalized = volume_percent / np.sum(volume_percent) * 100
        
        # Mean dose (weighted average)
        mean_dose = np.average(dose_bins, weights=volume_normalized)
        
        # Median dose
        cumulative_volume = np.cumsum(volume_normalized)
        median_idx = np.argmin(np.abs(cumulative_volume - 50))
        median_dose = dose_bins[median_idx]
        
        # Min và Max dose
        min_dose = np.min(dose_bins)
        max_dose = np.max(dose_bins)
        
        # Standard deviation
        variance = np.average((dose_bins - mean_dose)**2, weights=volume_normalized)
        std_dose = np.sqrt(variance)
        
        return {
            'mean_dose': mean_dose,
            'median_dose': median_dose,
            'min_dose': min_dose,
            'max_dose': max_dose,
            'std_dose': std_dose,
            'dose_range': max_dose - min_dose
        }
    
    @staticmethod
    def calculate_dx_values(dose_bins: np.ndarray, volume_percent: np.ndarray, 
                           percentiles: List[float] = [95, 50, 5, 2]) -> Dict:
        """
        Tính toán Dx values (dose received by x% of volume)
        
        Args:
            dose_bins: Array liều lượng
            volume_percent: Array phần trăm thể tích
            percentiles: List các percentile cần tính (%)
            
        Returns:
            Dict: Dx values
        """
        # Sắp xếp theo dose giảm dần
        sorted_indices = np.argsort(dose_bins)[::-1]
        sorted_doses = dose_bins[sorted_indices]
        sorted_volumes = volume_percent[sorted_indices]
        
        # Tính cumulative volume
        cumulative_volume = np.cumsum(sorted_volumes)
        cumulative_volume = cumulative_volume / cumulative_volume[-1] * 100  # Normalize to 100%
        
        dx_values = {}
        
        for percentile in percentiles:
            # Tìm dose tương ứng với percentile
            if percentile <= cumulative_volume[-1]:
                # Interpolation để tìm dose chính xác
                f = interpolate.interp1d(cumulative_volume, sorted_doses, 
                                       kind='linear', fill_value='extrapolate')
                dx_value = float(f(percentile))
                dx_values[f'D{percentile}'] = dx_value
            else:
                dx_values[f'D{percentile}'] = 0.0
        
        return dx_values
    
    @staticmethod
    def calculate_vx_values(dose_bins: np.ndarray, volume_percent: np.ndarray,
                           dose_levels: List[float] = [20, 30, 40, 50, 60, 70]) -> Dict:
        """
        Tính toán Vx values (volume receiving ≥ x Gy)
        
        Args:
            dose_bins: Array liều lượng
            volume_percent: Array phần trăm thể tích
            dose_levels: List các mức dose cần tính (Gy)
            
        Returns:
            Dict: Vx values
        """
        vx_values = {}
        
        for dose_level in dose_levels:
            # Tìm volume nhận dose >= dose_level
            volume_above = np.sum(volume_percent[dose_bins >= dose_level])
            vx_values[f'V{dose_level}'] = volume_above
        
        return vx_values
    
    @staticmethod
    def calculate_conformity_index(target_dose_bins: np.ndarray, target_volume_percent: np.ndarray,
                                 prescription_dose: float, tolerance: float = 0.05) -> Dict:
        """
        Tính toán Conformity Index
        
        Args:
            target_dose_bins: Array liều lượng của target
            target_volume_percent: Array thể tích của target
            prescription_dose: Liều lượng kê đơn (Gy)
            tolerance: Tolerance cho prescription dose (±5%)
            
        Returns:
            Dict: Các chỉ số conformity
        """
        # Volume của target nhận prescription dose
        dose_range = [prescription_dose * (1 - tolerance), 
                     prescription_dose * (1 + tolerance)]
        
        target_volume_covered = np.sum(target_volume_percent[
            (target_dose_bins >= dose_range[0]) & 
            (target_dose_bins <= dose_range[1])
        ])
        
        total_target_volume = np.sum(target_volume_percent)
        
        # Coverage (fraction of target receiving prescription dose)
        coverage = target_volume_covered / total_target_volume if total_target_volume > 0 else 0
        
        # Conformity Index (simplified - cần thêm thông tin về total volume receiving prescription dose)
        # CI = V_target_prescription / V_total_prescription
        # Ở đây chỉ tính được coverage do thiếu thông tin về total volume
        
        return {
            'coverage': coverage,
            'target_volume_covered': target_volume_covered,
            'total_target_volume': total_target_volume,
            'prescription_dose': prescription_dose
        }
    
    @staticmethod
    def calculate_homogeneity_index(dose_bins: np.ndarray, volume_percent: np.ndarray) -> Dict:
        """
        Tính toán Homogeneity Index
        
        Args:
            dose_bins: Array liều lượng
            volume_percent: Array thể tích
            
        Returns:
            Dict: Các chỉ số homogeneity
        """
        # Tính D5 và D95
        dx_values = DoseCalculations.calculate_dx_values(dose_bins, volume_percent, [5, 95])
        
        d5 = dx_values.get('D5', 0)
        d95 = dx_values.get('D95', 0)
        
        # Homogeneity Index = (D5 - D95) / D_prescription
        # Ở đây sử dụng mean dose làm reference
        mean_dose = np.average(dose_bins, weights=volume_percent)
        
        hi = (d5 - d95) / mean_dose if mean_dose > 0 else 0
        
        return {
            'homogeneity_index': hi,
            'D5': d5,
            'D95': d95,
            'mean_dose': mean_dose
        }
    
    @staticmethod
    def calculate_equivalent_uniform_dose(dose_bins: np.ndarray, volume_percent: np.ndarray,
                                        a_value: float) -> float:
        """
        Tính toán Equivalent Uniform Dose (EUD)
        
        Args:
            dose_bins: Array liều lượng
            volume_percent: Array thể tích
            a_value: Tham số a (âm cho tumor, dương cho normal tissue)
            
        Returns:
            float: EUD value
        """
        if len(dose_bins) != len(volume_percent):
            raise ValueError("Dose bins và volume percent phải có cùng độ dài")
        
        # Normalize volume fractions
        volume_fractions = volume_percent / np.sum(volume_percent)
        
        if a_value == 0:
            # a = 0: EUD = geometric mean
            log_doses = np.log(dose_bins + 1e-10)  # Tránh log(0)
            eud = np.exp(np.average(log_doses, weights=volume_fractions))
        elif np.isinf(a_value):
            # a = ∞: EUD = max dose
            eud = np.max(dose_bins)
        elif a_value == -np.inf:
            # a = -∞: EUD = min dose
            eud = np.min(dose_bins)
        else:
            # General case
            try:
                powered_doses = np.power(dose_bins, a_value)
                weighted_sum = np.average(powered_doses, weights=volume_fractions)
                eud = np.power(weighted_sum, 1/a_value)
            except (OverflowError, ZeroDivisionError):
                if a_value > 0:
                    eud = np.max(dose_bins)
                else:
                    eud = np.min(dose_bins)
        
        return eud
    
    @staticmethod
    def calculate_biological_effective_dose(dose: float, alpha_beta_ratio: float,
                                          n_fractions: int = 1, 
                                          dose_rate: float = None,
                                          repair_half_time: float = None) -> Dict:
        """
        Tính toán Biologically Effective Dose (BED)
        
        Args:
            dose: Tổng liều lượng (Gy)
            alpha_beta_ratio: Tỷ lệ α/β
            n_fractions: Số phân liều
            dose_rate: Tốc độ liều (Gy/min) - optional
            repair_half_time: Thời gian bán hủy sửa chữa (min) - optional
            
        Returns:
            Dict: BED và các thông tin liên quan
        """
        if n_fractions <= 0:
            raise ValueError("Số phân liều phải > 0")
        
        dose_per_fraction = dose / n_fractions
        
        # BED cơ bản (không tính incomplete repair)
        bed_basic = dose * (1 + dose_per_fraction / alpha_beta_ratio)
        
        # Nếu có thông tin về dose rate và repair time
        if dose_rate is not None and repair_half_time is not None:
            # Tính G factor cho incomplete repair
            delivery_time = dose_per_fraction / dose_rate
            lambda_repair = np.log(2) / repair_half_time
            
            if delivery_time > 0:
                g_factor = (2 / (lambda_repair * delivery_time)) * \
                          (1 - (1 - np.exp(-lambda_repair * delivery_time)) / 
                           (lambda_repair * delivery_time))
            else:
                g_factor = 1.0
            
            bed_corrected = dose * (1 + g_factor * dose_per_fraction / alpha_beta_ratio)
        else:
            bed_corrected = bed_basic
            g_factor = 1.0
        
        return {
            'bed_basic': bed_basic,
            'bed_corrected': bed_corrected,
            'dose_per_fraction': dose_per_fraction,
            'n_fractions': n_fractions,
            'alpha_beta_ratio': alpha_beta_ratio,
            'g_factor': g_factor
        }
    
    @staticmethod
    def interpolate_dvh(dose_bins: np.ndarray, volume_percent: np.ndarray,
                       new_dose_bins: np.ndarray) -> np.ndarray:
        """
        Interpolate DVH data to new dose bins
        
        Args:
            dose_bins: Original dose bins
            volume_percent: Original volume percentages
            new_dose_bins: New dose bins for interpolation
            
        Returns:
            np.ndarray: Interpolated volume percentages
        """
        # Sắp xếp dữ liệu theo dose
        sorted_indices = np.argsort(dose_bins)
        sorted_doses = dose_bins[sorted_indices]
        sorted_volumes = volume_percent[sorted_indices]
        
        # Interpolation
        f = interpolate.interp1d(sorted_doses, sorted_volumes, 
                               kind='linear', bounds_error=False, 
                               fill_value=(sorted_volumes[0], sorted_volumes[-1]))
        
        interpolated_volumes = f(new_dose_bins)
        
        return interpolated_volumes
    
    @staticmethod
    def create_dose_report(dose_bins: np.ndarray, volume_percent: np.ndarray,
                          structure_name: str, prescription_dose: float = None) -> Dict:
        """
        Tạo báo cáo tổng hợp về dose cho một structure
        
        Args:
            dose_bins: Array liều lượng
            volume_percent: Array thể tích
            structure_name: Tên structure
            prescription_dose: Liều lượng kê đơn (optional)
            
        Returns:
            Dict: Báo cáo tổng hợp
        """
        report = {
            'structure_name': structure_name,
            'prescription_dose': prescription_dose
        }
        
        # Basic statistics
        report.update(DoseCalculations.calculate_dose_statistics(dose_bins, volume_percent))
        
        # Dx values
        report.update(DoseCalculations.calculate_dx_values(dose_bins, volume_percent))
        
        # Vx values
        report.update(DoseCalculations.calculate_vx_values(dose_bins, volume_percent))
        
        # Homogeneity index
        report.update(DoseCalculations.calculate_homogeneity_index(dose_bins, volume_percent))
        
        # Conformity index (nếu có prescription dose)
        if prescription_dose is not None:
            conformity = DoseCalculations.calculate_conformity_index(
                dose_bins, volume_percent, prescription_dose)
            report.update(conformity)
        
        # EUD for different a values
        report['eud_tumor'] = DoseCalculations.calculate_equivalent_uniform_dose(
            dose_bins, volume_percent, -10)  # a = -10 for tumor
        report['eud_normal'] = DoseCalculations.calculate_equivalent_uniform_dose(
            dose_bins, volume_percent, 2)    # a = 2 for normal tissue
        
        return report


if __name__ == "__main__":
    # Test code
    dose_bins = np.linspace(0, 80, 100)
    volume_percent = 100 * np.exp(-dose_bins/30)  # Exponential decay
    
    calc = DoseCalculations()
    
    # Test basic statistics
    stats = calc.calculate_dose_statistics(dose_bins, volume_percent)
    print(f"Mean dose: {stats['mean_dose']:.2f} Gy")
    
    # Test Dx values
    dx_values = calc.calculate_dx_values(dose_bins, volume_percent)
    print(f"D95: {dx_values['D95']:.2f} Gy")
    
    print("Dose Calculations module loaded successfully")
