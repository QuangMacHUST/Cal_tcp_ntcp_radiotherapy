"""
File chính để khởi chạy ứng dụng TCP/NTCP Calculator
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_gui import TCPNTCPApp
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure all required modules are installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


def check_dependencies():
    """Kiểm tra các dependencies cần thiết"""
    required_modules = [
        'pydicom',
        'numpy',
        'scipy',
        'matplotlib',
        'pandas',
        'tkinter'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"Missing required modules: {', '.join(missing_modules)}\n"
        error_msg += "Please install them using: pip install -r requirements.txt"
        messagebox.showerror("Missing Dependencies", error_msg)
        return False
    
    return True


def main():
    """Hàm chính để khởi chạy ứng dụng"""
    
    # Kiểm tra dependencies
    if not check_dependencies():
        return
    
    try:
        # Tạo root window
        root = tk.Tk()
        
        # Set window icon (nếu có)
        try:
            # root.iconbitmap('icon.ico')  # Uncomment if you have an icon file
            pass
        except:
            pass
        
        # Tạo ứng dụng
        app = TCPNTCPApp(root)
        
        # Thêm menu bar
        create_menu_bar(root, app)
        
        # Xử lý sự kiện đóng cửa sổ
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
        
        # Khởi chạy ứng dụng
        print("Starting TCP/NTCP Calculator...")
        print("Application ready!")
        
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Error starting application: {str(e)}\n\n"
        error_msg += "Traceback:\n" + traceback.format_exc()
        
        print(error_msg)
        
        # Hiển thị error dialog nếu tkinter có thể hoạt động
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            messagebox.showerror("Application Error", error_msg)
        except:
            pass


def create_menu_bar(root, app):
    """Tạo menu bar cho ứng dụng"""
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Load DICOM Files...", command=app.load_dicom_files)
    file_menu.add_separator()
    file_menu.add_command(label="Export Results...", command=app.export_results)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=lambda: on_closing(root))
    
    # Calculate menu
    calc_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Calculate", menu=calc_menu)
    calc_menu.add_command(label="Calculate TCP", command=app.calculate_tcp)
    calc_menu.add_command(label="Calculate NTCP", command=app.calculate_ntcp)
    
    # View menu
    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="View", menu=view_menu)
    view_menu.add_command(label="Plot DVH", command=app.plot_dvh)
    view_menu.add_command(label="Plot TCP/NTCP", command=app.plot_tcp_ntcp)
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=lambda: show_about_dialog(root))
    help_menu.add_command(label="User Guide", command=lambda: show_user_guide(root))


def show_about_dialog(root):
    """Hiển thị dialog About"""
    about_text = """TCP/NTCP Calculator for Radiotherapy

Version: 1.0.0
Author: Radiotherapy Team

This application calculates Tumor Control Probability (TCP) 
and Normal Tissue Complication Probability (NTCP) from 
DICOM RT Dose and RT Structure data.

Features:
- Load DICOM RT Dose and RT Structure files
- Calculate TCP using various models (Poisson, LQ, etc.)
- Calculate NTCP using various models (LKB, Critical Volume, etc.)
- Generate DVH plots and TCP/NTCP curves
- Export results to various formats

For support, please contact the development team.
"""
    
    messagebox.showinfo("About TCP/NTCP Calculator", about_text)


def show_user_guide(root):
    """Hiển thị hướng dẫn sử dụng"""
    guide_text = """User Guide - TCP/NTCP Calculator

1. LOADING DATA:
   - Go to "Load DICOM Data" tab
   - Select RT Dose DICOM file
   - Select RT Structure Set DICOM file
   - Click "Load DICOM Files"

2. TCP CALCULATION:
   - Go to "TCP Calculation" tab
   - Select target structure from dropdown
   - Choose tumor type and TCP model
   - Click "Calculate TCP"

3. NTCP CALCULATION:
   - Go to "NTCP Calculation" tab
   - Select OAR structure from dropdown
   - Choose organ type and NTCP model
   - Click "Calculate NTCP"

4. VIEWING RESULTS:
   - Go to "Results & Plots" tab
   - Generate DVH plots
   - Generate TCP/NTCP curves
   - Export results

SUPPORTED MODELS:
TCP: Poisson, Linear-Quadratic, Webb-Nahum, Logistic
NTCP: Lyman-Kutcher-Burman, Critical Volume, Relative Seriality

For detailed information about models and parameters,
please refer to the documentation.
"""
    
    # Create a new window for the user guide
    guide_window = tk.Toplevel(root)
    guide_window.title("User Guide")
    guide_window.geometry("600x500")
    
    # Create text widget with scrollbar
    text_frame = tk.Frame(guide_window)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 10))
    scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget.insert(tk.END, guide_text)
    text_widget.config(state=tk.DISABLED)  # Make it read-only


def on_closing(root):
    """Xử lý sự kiện đóng ứng dụng"""
    if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
        print("Closing TCP/NTCP Calculator...")
        root.quit()
        root.destroy()


def setup_logging():
    """Thiết lập logging cho ứng dụng"""
    import logging
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/tcp_ntcp_app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


if __name__ == "__main__":
    # Setup logging
    logger = setup_logging()
    logger.info("Starting TCP/NTCP Calculator application")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    finally:
        logger.info("Application terminated")
