"""
Script tự động cài đặt dependencies cho ứng dụng TCP/NTCP Calculator
"""

import subprocess
import sys
import os
import importlib
from typing import List, Tuple


def check_python_version() -> bool:
    """Kiểm tra phiên bản Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python version {version.major}.{version.minor} không được hỗ trợ")
        print("✅ Cần Python 3.7 trở lên")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True


def check_pip() -> bool:
    """Kiểm tra pip có sẵn không"""
    try:
        import pip
        print("✅ pip - OK")
        return True
    except ImportError:
        print("❌ pip không có sẵn")
        print("Vui lòng cài đặt pip trước khi tiếp tục")
        return False


def install_package(package: str) -> bool:
    """
    Cài đặt một package
    
    Args:
        package: Tên package
        
    Returns:
        bool: True nếu cài đặt thành công
    """
    try:
        print(f"📦 Đang cài đặt {package}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True, check=True)
        
        print(f"✅ {package} - Cài đặt thành công")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} - Lỗi cài đặt:")
        print(f"   {e.stderr}")
        return False


def check_package_installed(package: str) -> bool:
    """
    Kiểm tra package đã được cài đặt chưa
    
    Args:
        package: Tên package
        
    Returns:
        bool: True nếu đã cài đặt
    """
    try:
        # Xử lý tên package đặc biệt
        import_name = package
        if package == "scikit-image":
            import_name = "skimage"
        elif package == "tkinter-tooltip":
            import_name = "tktooltip"
        elif package.startswith("matplotlib"):
            import_name = "matplotlib"
        elif package.startswith("numpy"):
            import_name = "numpy"
        elif package.startswith("scipy"):
            import_name = "scipy"
        elif package.startswith("pandas"):
            import_name = "pandas"
        elif package.startswith("pydicom"):
            import_name = "pydicom"
        elif package.startswith("Pillow"):
            import_name = "PIL"
        
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False


def read_requirements() -> List[str]:
    """Đọc file requirements.txt"""
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ Không tìm thấy file {requirements_file}")
        return []
    
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            packages = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Loại bỏ version constraints để lấy tên package
                    package_name = line.split('>=')[0].split('==')[0].split('<=')[0]
                    packages.append(line)  # Giữ nguyên constraint
            return packages
    except Exception as e:
        print(f"❌ Lỗi đọc file requirements.txt: {e}")
        return []


def install_all_packages() -> Tuple[List[str], List[str]]:
    """
    Cài đặt tất cả packages từ requirements.txt
    
    Returns:
        Tuple[List[str], List[str]]: (successful_packages, failed_packages)
    """
    packages = read_requirements()
    
    if not packages:
        print("❌ Không có packages nào để cài đặt")
        return [], []
    
    print(f"📋 Tìm thấy {len(packages)} packages cần cài đặt")
    print("-" * 50)
    
    successful = []
    failed = []
    
    for package in packages:
        package_name = package.split('>=')[0].split('==')[0].split('<=')[0]
        
        # Kiểm tra đã cài đặt chưa
        if check_package_installed(package_name):
            print(f"✅ {package_name} - Đã cài đặt")
            successful.append(package)
            continue
        
        # Cài đặt package
        if install_package(package):
            successful.append(package)
        else:
            failed.append(package)
    
    return successful, failed


def install_tkinter():
    """Cài đặt tkinter nếu cần thiết"""
    try:
        import tkinter
        print("✅ tkinter - OK")
        return True
    except ImportError:
        print("❌ tkinter không có sẵn")
        print("Trên Ubuntu/Debian, chạy: sudo apt-get install python3-tk")
        print("Trên CentOS/RHEL, chạy: sudo yum install tkinter")
        print("Trên macOS với Homebrew: brew install python-tk")
        return False


def create_test_script():
    """Tạo script test để kiểm tra cài đặt"""
    test_script = """
# Test script để kiểm tra cài đặt
import sys

def test_imports():
    modules_to_test = [
        ('pydicom', 'pydicom'),
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
        ('matplotlib', 'matplotlib.pyplot'),
        ('pandas', 'pandas'),
        ('tkinter', 'tkinter'),
        ('PIL', 'PIL'),
        ('skimage', 'skimage')
    ]
    
    print("Kiểm tra imports...")
    success_count = 0
    
    for display_name, module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
    
    print(f"\\nKết quả: {success_count}/{len(modules_to_test)} modules OK")
    return success_count == len(modules_to_test)

if __name__ == "__main__":
    if test_imports():
        print("\\n🎉 Tất cả dependencies đã được cài đặt thành công!")
        print("Bạn có thể chạy ứng dụng bằng: python main.py")
    else:
        print("\\n❌ Một số dependencies chưa được cài đặt đúng")
        print("Vui lòng kiểm tra lại và cài đặt thủ công nếu cần")
"""
    
    with open("test_installation.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✅ Đã tạo file test_installation.py")


def main():
    """Hàm chính"""
    print("🚀 TCP/NTCP Calculator - Cài đặt Dependencies")
    print("=" * 50)
    
    # Kiểm tra Python version
    if not check_python_version():
        sys.exit(1)
    
    # Kiểm tra pip
    if not check_pip():
        sys.exit(1)
    
    # Kiểm tra tkinter
    install_tkinter()
    
    print("\n📦 Bắt đầu cài đặt packages...")
    print("-" * 50)
    
    # Cài đặt packages
    successful, failed = install_all_packages()
    
    print("\n" + "=" * 50)
    print("📊 KẾT QUẢ CÀI ĐẶT")
    print("=" * 50)
    
    print(f"✅ Thành công: {len(successful)} packages")
    for package in successful:
        print(f"   - {package}")
    
    if failed:
        print(f"\n❌ Thất bại: {len(failed)} packages")
        for package in failed:
            print(f"   - {package}")
        print("\nVui lòng cài đặt thủ công các packages bị lỗi:")
        for package in failed:
            print(f"   pip install {package}")
    
    # Tạo test script
    print("\n🧪 Tạo script kiểm tra...")
    create_test_script()
    
    print("\n" + "=" * 50)
    if not failed:
        print("🎉 CÀI ĐẶT HOÀN TẤT!")
        print("Chạy lệnh sau để kiểm tra:")
        print("   python test_installation.py")
        print("\nSau đó chạy ứng dụng:")
        print("   python main.py")
    else:
        print("⚠️  CÀI ĐẶT HOÀN TẤT NHƯNG CÓ LỖI")
        print("Vui lòng xử lý các packages bị lỗi trước khi chạy ứng dụng")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
