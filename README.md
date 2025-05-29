# TCP/NTCP Calculator for Radiotherapy

Ứng dụng Python tính toán TCP (Tumor Control Probability) và NTCP (Normal Tissue Complication Probability) từ dữ liệu DICOM RT Dose và RT Structure Set trong xạ trị.

## Tính năng chính

### 📊 Xử lý dữ liệu DICOM
- Đọc và phân tích file DICOM RT Dose
- Đọc và phân tích file DICOM RT Structure Set
- Trích xuất thông tin DVH (Dose Volume Histogram)
- Tính toán các chỉ số dose-volume (Dx, Vx, EUD, BED)

### 🎯 Tính toán TCP (Tumor Control Probability)
- **Mô hình Poisson**: Mô hình TCP cổ điển
- **Mô hình Linear-Quadratic**: Dựa trên lý thuyết LQ
- **Mô hình Webb-Nahum**: Tính đến mật độ tế bào ung thư
- **Mô hình Logistic**: Mô hình logistic đơn giản

### 🛡️ Tính toán NTCP (Normal Tissue Complication Probability)
- **Lyman-Kutcher-Burman (LKB)**: Mô hình NTCP cổ điển
- **Critical Volume**: Mô hình thể tích tới hạn
- **Relative Seriality**: Mô hình seriality tương đối
- **Logistic NTCP**: Mô hình logistic cho NTCP
- **Poisson NTCP**: Mô hình Poisson cho NTCP

### 📈 Hiển thị và báo cáo
- Vẽ biểu đồ DVH tương tác
- Vẽ đường cong TCP/NTCP
- Dashboard tổng hợp kết quả
- Xuất báo cáo PDF/Excel/CSV
- Bảng thống kê chi tiết

## Cài đặt

### Yêu cầu hệ thống
- Python 3.7 trở lên
- Windows/Linux/macOS
- RAM: tối thiểu 4GB
- Dung lượng: 500MB trống

### Cài đặt dependencies

```bash
# Clone repository
git clone https://github.com/your-repo/Cal_tcp_ntcp_radiotherapy.git
cd Cal_tcp_ntcp_radiotherapy

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### Chạy ứng dụng

```bash
python main.py
```

## Hướng dẫn sử dụng

### 1. Load dữ liệu DICOM
1. Mở tab "Load DICOM Data"
2. Chọn file RT Dose DICOM
3. Chọn file RT Structure Set DICOM
4. Click "Load DICOM Files"
5. Kiểm tra danh sách structures đã load

### 2. Tính toán TCP
1. Chuyển sang tab "TCP Calculation"
2. Chọn target structure từ dropdown
3. Chọn loại tumor (prostate, lung, breast, etc.)
4. Chọn mô hình TCP (poisson, lq, webb_nahum, logistic)
5. Click "Calculate TCP"
6. Xem kết quả trong panel bên dưới

### 3. Tính toán NTCP
1. Chuyển sang tab "NTCP Calculation"
2. Chọn OAR structure từ dropdown
3. Chọn loại organ (lung, heart, spinal_cord, etc.)
4. Chọn mô hình NTCP (lkb, critical_volume, etc.)
5. Click "Calculate NTCP"
6. Xem kết quả trong panel bên dưới

### 4. Xem kết quả và biểu đồ
1. Chuyển sang tab "Results & Plots"
2. Click "Generate DVH Plot" để vẽ DVH
3. Click "Generate TCP/NTCP Plot" để vẽ đường cong
4. Click "Export Results" để xuất báo cáo

## Cấu trúc dự án

```
Cal_tcp_ntcp_radiotherapy/
├── main.py                 # File chính khởi chạy ứng dụng
├── main_gui.py            # Giao diện người dùng chính
├── dicom_reader.py        # Module đọc và xử lý DICOM
├── tcp_models.py          # Các mô hình tính toán TCP
├── ntcp_models.py         # Các mô hình tính toán NTCP
├── dose_calculations.py   # Tính toán liều lượng và DVH
├── results_display.py     # Hiển thị kết quả và biểu đồ
├── config.py             # Cấu hình ứng dụng
├── utils.py              # Các hàm tiện ích
├── requirements.txt      # Dependencies
├── README.md            # Tài liệu hướng dẫn
└── logs/                # Thư mục log files
```

## Mô hình và tham số

### TCP Models

#### Poisson TCP
```
TCP = 1 / (1 + exp(-4γ₅₀(D - TD₅₀)/TD₅₀))
```
- TD₅₀: Liều lượng cho TCP 50%
- γ₅₀: Độ dốc tại TD₅₀

#### Linear-Quadratic TCP
```
TCP = 1 - exp(-αD - βD²)
```
- α: Tham số alpha (Gy⁻¹)
- β: Tham số beta (Gy⁻²)

### NTCP Models

#### Lyman-Kutcher-Burman
```
NTCP = (1/√2π) ∫ exp(-t²/2) dt
t = (EUD - TD₅₀)/(m × TD₅₀)
```
- EUD: Equivalent Uniform Dose
- TD₅₀: Liều lượng cho NTCP 50%
- m: Tham số độ dốc
- n: Tham số thể tích

## Tham số mặc định

### Tumor Types
- **Prostate**: TD₅₀=70Gy, γ₅₀=2.0, α=0.15, β=0.05
- **Lung**: TD₅₀=60Gy, γ₅₀=1.8, α=0.18, β=0.04
- **Breast**: TD₅₀=50Gy, γ₅₀=2.2, α=0.20, β=0.05
- **Head & Neck**: TD₅₀=65Gy, γ₅₀=2.5, α=0.25, β=0.06

### Organ at Risk
- **Lung**: TD₅₀=24.5Gy, m=0.18, n=0.87 (pneumonitis)
- **Heart**: TD₅₀=48Gy, m=0.16, n=0.35 (pericarditis)
- **Spinal Cord**: TD₅₀=66.5Gy, m=0.175, n=0.05 (myelitis)
- **Rectum**: TD₅₀=76.9Gy, m=0.15, n=0.12 (bleeding)

## Xuất kết quả

Ứng dụng hỗ trợ xuất kết quả ra nhiều định dạng:
- **CSV**: Dữ liệu số dạng bảng
- **JSON**: Dữ liệu có cấu trúc với metadata
- **PNG/PDF**: Biểu đồ và hình ảnh
- **Excel**: Báo cáo tổng hợp

## Troubleshooting

### Lỗi thường gặp

1. **"Missing required modules"**
   ```bash
   pip install -r requirements.txt
   ```

2. **"Invalid DICOM files"**
   - Kiểm tra file có đúng định dạng DICOM không
   - Đảm bảo file RT Dose có Modality = "RTDOSE"
   - Đảm bảo file RT Struct có Modality = "RTSTRUCT"

3. **"No structures found"**
   - Kiểm tra file RT Structure Set có chứa ROI không
   - Thử load lại file DICOM

4. **"Calculation error"**
   - Kiểm tra dữ liệu DVH có hợp lệ không
   - Thử với structure khác
   - Kiểm tra log file để biết chi tiết lỗi

### Log files
Log files được lưu trong thư mục `logs/`:
- `tcp_ntcp_app.log`: Log chính của ứng dụng
- Chứa thông tin debug và error messages

## Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng:
1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## Giấy phép

Dự án này được phát hành dưới giấy phép MIT. Xem file LICENSE để biết chi tiết.

## Liên hệ

- Email: support@radiotherapy-team.com
- Issues: [GitHub Issues](https://github.com/your-repo/Cal_tcp_ntcp_radiotherapy/issues)

## Tài liệu tham khảo

1. Lyman JT. Complication probability as assessed from dose-volume histograms. Radiat Res. 1985;104(2s):S13-S19.
2. Kutcher GJ, Burman C. Calculation of complication probability factors for non-uniform normal tissue irradiation. Int J Radiat Oncol Biol Phys. 1989;16(6):1623-1630.
3. Webb S, Nahum AE. A model for calculating tumour control probability in radiotherapy including the effects of inhomogeneous distributions of dose and clonogenic cell density. Phys Med Biol. 1993;38(6):653-666.
4. Fowler JF. The linear-quadratic formula and progress in fractionated radiotherapy. Br J Radiol. 1989;62(740):679-694.
