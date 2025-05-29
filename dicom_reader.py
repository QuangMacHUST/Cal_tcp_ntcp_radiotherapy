"""
Module xử lý đọc và phân tích file DICOM RT Dose và RT Struct
"""

import pydicom
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import os


class DicomRTReader:
    """Class để đọc và xử lý file DICOM RT"""
    
    def __init__(self):
        self.rt_dose = None
        self.rt_struct = None
        self.dose_data = None
        self.structures = {}
        
    def load_rt_dose(self, file_path: str) -> bool:
        """
        Đọc file RT Dose DICOM
        
        Args:
            file_path: Đường dẫn đến file RT Dose
            
        Returns:
            bool: True nếu đọc thành công
        """
        try:
            self.rt_dose = pydicom.dcmread(file_path)
            
            # Kiểm tra xem có phải RT Dose không
            if self.rt_dose.Modality != 'RTDOSE':
                raise ValueError("File không phải là RT Dose DICOM")
                
            # Trích xuất dữ liệu dose
            self.dose_data = self._extract_dose_data()
            print(f"Đã đọc thành công RT Dose: {file_path}")
            return True
            
        except Exception as e:
            print(f"Lỗi khi đọc RT Dose: {e}")
            return False
    
    def load_rt_struct(self, file_path: str) -> bool:
        """
        Đọc file RT Structure Set DICOM
        
        Args:
            file_path: Đường dẫn đến file RT Struct
            
        Returns:
            bool: True nếu đọc thành công
        """
        try:
            self.rt_struct = pydicom.dcmread(file_path)
            
            # Kiểm tra xem có phải RT Structure Set không
            if self.rt_struct.Modality != 'RTSTRUCT':
                raise ValueError("File không phải là RT Structure Set DICOM")
                
            # Trích xuất thông tin structures
            self.structures = self._extract_structures()
            print(f"Đã đọc thành công RT Struct: {file_path}")
            return True
            
        except Exception as e:
            print(f"Lỗi khi đọc RT Struct: {e}")
            return False
    
    def _extract_dose_data(self) -> Dict:
        """Trích xuất dữ liệu dose từ RT Dose"""
        if self.rt_dose is None:
            return None
            
        dose_array = self.rt_dose.pixel_array
        dose_scaling = float(self.rt_dose.DoseGridScaling)
        
        # Chuyển đổi sang đơn vị Gy
        dose_array = dose_array * dose_scaling
        
        # Thông tin geometry
        image_position = self.rt_dose.ImagePositionPatient
        pixel_spacing = self.rt_dose.PixelSpacing
        slice_thickness = float(self.rt_dose.SliceThickness) if hasattr(self.rt_dose, 'SliceThickness') else 1.0
        
        return {
            'dose_array': dose_array,
            'dose_scaling': dose_scaling,
            'image_position': image_position,
            'pixel_spacing': pixel_spacing,
            'slice_thickness': slice_thickness,
            'dose_units': getattr(self.rt_dose, 'DoseUnits', 'GY'),
            'dose_type': getattr(self.rt_dose, 'DoseType', 'PHYSICAL')
        }
    
    def _extract_structures(self) -> Dict:
        """Trích xuất thông tin structures từ RT Struct"""
        if self.rt_struct is None:
            return {}
            
        structures = {}
        
        # Đọc thông tin ROI
        for roi_sequence in self.rt_struct.StructureSetROISequence:
            roi_number = roi_sequence.ROINumber
            roi_name = roi_sequence.ROIName
            
            structures[roi_number] = {
                'name': roi_name,
                'number': roi_number,
                'contours': []
            }
        
        # Đọc thông tin contour
        if hasattr(self.rt_struct, 'ROIContourSequence'):
            for contour_sequence in self.rt_struct.ROIContourSequence:
                roi_number = contour_sequence.ReferencedROINumber
                
                if roi_number in structures:
                    contours = []
                    if hasattr(contour_sequence, 'ContourSequence'):
                        for contour in contour_sequence.ContourSequence:
                            if hasattr(contour, 'ContourData'):
                                # Chuyển đổi contour data thành array 3D
                                contour_data = np.array(contour.ContourData).reshape(-1, 3)
                                contours.append(contour_data)
                    
                    structures[roi_number]['contours'] = contours
        
        return structures
    
    def get_structure_names(self) -> List[str]:
        """Lấy danh sách tên các structure"""
        return [struct['name'] for struct in self.structures.values()]
    
    def get_structure_by_name(self, name: str) -> Optional[Dict]:
        """Lấy thông tin structure theo tên"""
        for struct in self.structures.values():
            if struct['name'].lower() == name.lower():
                return struct
        return None
    
    def calculate_dvh(self, structure_name: str, bins: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Tính toán Dose Volume Histogram (DVH) cho một structure
        
        Args:
            structure_name: Tên structure
            bins: Số bins cho histogram
            
        Returns:
            Tuple[dose_bins, volume_percent]: DVH data
        """
        if self.dose_data is None or not self.structures:
            raise ValueError("Chưa load đủ dữ liệu RT Dose và RT Struct")
        
        structure = self.get_structure_by_name(structure_name)
        if structure is None:
            raise ValueError(f"Không tìm thấy structure: {structure_name}")
        
        # Tạo mask cho structure (simplified implementation)
        # Trong thực tế cần implement thuật toán phức tạp hơn để tạo mask từ contours
        dose_array = self.dose_data['dose_array']
        
        # Placeholder cho DVH calculation - cần implement chi tiết
        max_dose = np.max(dose_array)
        dose_bins = np.linspace(0, max_dose, bins)
        
        # Simplified DVH calculation
        # Trong thực tế cần tính toán chính xác từ mask và dose array
        volume_percent = np.linspace(100, 0, bins)
        
        return dose_bins, volume_percent
    
    def get_dose_statistics(self, structure_name: str) -> Dict:
        """
        Tính toán các thống kê dose cho structure
        
        Args:
            structure_name: Tên structure
            
        Returns:
            Dict: Các thống kê dose (mean, max, min, D95, V20, etc.)
        """
        dose_bins, volume_percent = self.calculate_dvh(structure_name)
        
        # Tính toán các thống kê cơ bản
        stats = {
            'mean_dose': np.mean(dose_bins),
            'max_dose': np.max(dose_bins),
            'min_dose': np.min(dose_bins),
            'median_dose': np.median(dose_bins)
        }
        
        # Tính D95, D50, etc. (dose received by 95%, 50% of volume)
        # Simplified calculation
        stats['D95'] = np.percentile(dose_bins, 95)
        stats['D50'] = np.percentile(dose_bins, 50)
        stats['D5'] = np.percentile(dose_bins, 5)
        
        return stats


def validate_dicom_files(rt_dose_path: str, rt_struct_path: str) -> bool:
    """
    Kiểm tra tính hợp lệ của các file DICOM
    
    Args:
        rt_dose_path: Đường dẫn RT Dose
        rt_struct_path: Đường dẫn RT Struct
        
    Returns:
        bool: True nếu cả hai file hợp lệ
    """
    try:
        # Kiểm tra file tồn tại
        if not os.path.exists(rt_dose_path):
            print(f"File RT Dose không tồn tại: {rt_dose_path}")
            return False
            
        if not os.path.exists(rt_struct_path):
            print(f"File RT Struct không tồn tại: {rt_struct_path}")
            return False
        
        # Kiểm tra có thể đọc được không
        reader = DicomRTReader()
        dose_ok = reader.load_rt_dose(rt_dose_path)
        struct_ok = reader.load_rt_struct(rt_struct_path)
        
        return dose_ok and struct_ok
        
    except Exception as e:
        print(f"Lỗi khi validate DICOM files: {e}")
        return False


if __name__ == "__main__":
    # Test code
    reader = DicomRTReader()
    print("DICOM Reader module loaded successfully")
