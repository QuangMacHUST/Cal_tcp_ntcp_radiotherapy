"""
Giao diện chính cho ứng dụng tính toán TCP/NTCP
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from dicom_reader import DicomRTReader, validate_dicom_files
from tcp_models import TCPCalculator
from ntcp_models import NTCPCalculator
from dose_calculations import DoseCalculations
from results_display import ResultsDisplay


class TCPNTCPApp:
    """Ứng dụng chính tính toán TCP/NTCP"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TCP/NTCP Calculator - Radiotherapy")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.dicom_reader = DicomRTReader()
        self.tcp_calculator = TCPCalculator()
        self.ntcp_calculator = NTCPCalculator()
        self.dose_calc = DoseCalculations()
        self.results_display = None
        
        # Data storage
        self.current_results = {}
        self.loaded_structures = []
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Load Data
        self.create_data_tab()
        
        # Tab 2: TCP Calculation
        self.create_tcp_tab()
        
        # Tab 3: NTCP Calculation
        self.create_ntcp_tab()
        
        # Tab 4: Results
        self.create_results_tab()
        
    def create_data_tab(self):
        """Tạo tab load dữ liệu DICOM"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Load DICOM Data")
        
        # File selection frame
        file_frame = ttk.LabelFrame(data_frame, text="Select DICOM Files")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # RT Dose file
        ttk.Label(file_frame, text="RT Dose File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.dose_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.dose_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_dose_file).grid(row=0, column=2, padx=5, pady=5)
        
        # RT Struct file
        ttk.Label(file_frame, text="RT Struct File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.struct_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.struct_file_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_struct_file).grid(row=1, column=2, padx=5, pady=5)
        
        # Load button
        ttk.Button(file_frame, text="Load DICOM Files", 
                  command=self.load_dicom_files).grid(row=2, column=1, pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(data_frame, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.status_text = tk.Text(status_frame, height=10, width=80)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Structures frame
        struct_frame = ttk.LabelFrame(data_frame, text="Available Structures")
        struct_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.structures_listbox = tk.Listbox(struct_frame, height=6)
        self.structures_listbox.pack(fill=tk.X, padx=5, pady=5)
        
    def create_tcp_tab(self):
        """Tạo tab tính toán TCP"""
        tcp_frame = ttk.Frame(self.notebook)
        self.notebook.add(tcp_frame, text="TCP Calculation")
        
        # Parameters frame
        params_frame = ttk.LabelFrame(tcp_frame, text="TCP Parameters")
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Structure selection
        ttk.Label(params_frame, text="Target Structure:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.tcp_structure_var = tk.StringVar()
        self.tcp_structure_combo = ttk.Combobox(params_frame, textvariable=self.tcp_structure_var, width=30)
        self.tcp_structure_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Tumor type
        ttk.Label(params_frame, text="Tumor Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.tumor_type_var = tk.StringVar(value="prostate")
        tumor_combo = ttk.Combobox(params_frame, textvariable=self.tumor_type_var, 
                                  values=self.tcp_calculator.get_available_tumor_types())
        tumor_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Model selection
        ttk.Label(params_frame, text="TCP Model:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.tcp_model_var = tk.StringVar(value="poisson")
        model_combo = ttk.Combobox(params_frame, textvariable=self.tcp_model_var,
                                  values=["poisson", "lq", "webb_nahum", "logistic"])
        model_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Calculate button
        ttk.Button(params_frame, text="Calculate TCP", 
                  command=self.calculate_tcp).grid(row=3, column=1, pady=10)
        
        # Results frame
        tcp_results_frame = ttk.LabelFrame(tcp_frame, text="TCP Results")
        tcp_results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tcp_results_text = tk.Text(tcp_results_frame, height=15)
        tcp_scrollbar = ttk.Scrollbar(tcp_results_frame, orient=tk.VERTICAL, 
                                     command=self.tcp_results_text.yview)
        self.tcp_results_text.configure(yscrollcommand=tcp_scrollbar.set)
        
        self.tcp_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tcp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_ntcp_tab(self):
        """Tạo tab tính toán NTCP"""
        ntcp_frame = ttk.Frame(self.notebook)
        self.notebook.add(ntcp_frame, text="NTCP Calculation")
        
        # Parameters frame
        params_frame = ttk.LabelFrame(ntcp_frame, text="NTCP Parameters")
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Structure selection
        ttk.Label(params_frame, text="OAR Structure:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ntcp_structure_var = tk.StringVar()
        self.ntcp_structure_combo = ttk.Combobox(params_frame, textvariable=self.ntcp_structure_var, width=30)
        self.ntcp_structure_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Organ type
        ttk.Label(params_frame, text="Organ Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.organ_type_var = tk.StringVar(value="lung")
        organ_combo = ttk.Combobox(params_frame, textvariable=self.organ_type_var,
                                  values=self.ntcp_calculator.get_available_organs())
        organ_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Model selection
        ttk.Label(params_frame, text="NTCP Model:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.ntcp_model_var = tk.StringVar(value="lkb")
        ntcp_model_combo = ttk.Combobox(params_frame, textvariable=self.ntcp_model_var,
                                       values=["lkb", "critical_volume", "relative_seriality", 
                                              "logistic", "poisson"])
        ntcp_model_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Calculate button
        ttk.Button(params_frame, text="Calculate NTCP", 
                  command=self.calculate_ntcp).grid(row=3, column=1, pady=10)
        
        # Results frame
        ntcp_results_frame = ttk.LabelFrame(ntcp_frame, text="NTCP Results")
        ntcp_results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.ntcp_results_text = tk.Text(ntcp_results_frame, height=15)
        ntcp_scrollbar = ttk.Scrollbar(ntcp_results_frame, orient=tk.VERTICAL,
                                      command=self.ntcp_results_text.yview)
        self.ntcp_results_text.configure(yscrollcommand=ntcp_scrollbar.set)
        
        self.ntcp_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ntcp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_results_tab(self):
        """Tạo tab hiển thị kết quả tổng hợp"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results & Plots")
        
        # Control frame
        control_frame = ttk.Frame(results_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Generate DVH Plot", 
                  command=self.plot_dvh).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Generate TCP/NTCP Plot", 
                  command=self.plot_tcp_ntcp).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Plot frame
        self.plot_frame = ttk.Frame(results_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def browse_dose_file(self):
        """Browse for RT Dose file"""
        filename = filedialog.askopenfilename(
            title="Select RT Dose DICOM file",
            filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
        )
        if filename:
            self.dose_file_var.set(filename)
            
    def browse_struct_file(self):
        """Browse for RT Struct file"""
        filename = filedialog.askopenfilename(
            title="Select RT Structure Set DICOM file",
            filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
        )
        if filename:
            self.struct_file_var.set(filename)
            
    def load_dicom_files(self):
        """Load DICOM files"""
        dose_file = self.dose_file_var.get()
        struct_file = self.struct_file_var.get()
        
        if not dose_file or not struct_file:
            messagebox.showerror("Error", "Please select both RT Dose and RT Struct files")
            return
            
        self.log_message("Loading DICOM files...")
        
        try:
            # Validate files
            if not validate_dicom_files(dose_file, struct_file):
                messagebox.showerror("Error", "Invalid DICOM files")
                return
            
            # Load files
            dose_success = self.dicom_reader.load_rt_dose(dose_file)
            struct_success = self.dicom_reader.load_rt_struct(struct_file)
            
            if dose_success and struct_success:
                self.log_message("DICOM files loaded successfully!")
                
                # Update structures list
                self.update_structures_list()
                
                self.log_message(f"Found {len(self.dicom_reader.structures)} structures")
                
            else:
                messagebox.showerror("Error", "Failed to load DICOM files")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading DICOM files: {str(e)}")
            self.log_message(f"Error: {str(e)}")
            
    def update_structures_list(self):
        """Update the structures list in GUI"""
        self.structures_listbox.delete(0, tk.END)
        self.loaded_structures = self.dicom_reader.get_structure_names()
        
        for structure in self.loaded_structures:
            self.structures_listbox.insert(tk.END, structure)
            
        # Update comboboxes
        self.tcp_structure_combo['values'] = self.loaded_structures
        self.ntcp_structure_combo['values'] = self.loaded_structures
        
    def log_message(self, message: str):
        """Add message to status log"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update()
        
    def calculate_tcp(self):
        """Calculate TCP for selected structure"""
        structure_name = self.tcp_structure_var.get()
        tumor_type = self.tumor_type_var.get()
        model = self.tcp_model_var.get()
        
        if not structure_name:
            messagebox.showerror("Error", "Please select a target structure")
            return
            
        try:
            self.log_message(f"Calculating TCP for {structure_name}...")
            
            # Calculate DVH
            dose_bins, volume_percent = self.dicom_reader.calculate_dvh(structure_name)
            
            # Calculate TCP
            tcp_result = self.tcp_calculator.calculate_tcp_from_dvh(
                dose_bins, volume_percent, tumor_type, model)
            
            # Store results
            self.current_results['tcp'] = tcp_result
            self.current_results['tcp_structure'] = structure_name
            
            # Display results
            self.display_tcp_results(tcp_result)
            
            self.log_message("TCP calculation completed!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating TCP: {str(e)}")
            self.log_message(f"TCP Error: {str(e)}")
            
    def calculate_ntcp(self):
        """Calculate NTCP for selected structure"""
        structure_name = self.ntcp_structure_var.get()
        organ_type = self.organ_type_var.get()
        model = self.ntcp_model_var.get()
        
        if not structure_name:
            messagebox.showerror("Error", "Please select an OAR structure")
            return
            
        try:
            self.log_message(f"Calculating NTCP for {structure_name}...")
            
            # Calculate DVH
            dose_bins, volume_percent = self.dicom_reader.calculate_dvh(structure_name)
            
            # Calculate NTCP
            ntcp_result = self.ntcp_calculator.calculate_ntcp_from_dvh(
                dose_bins, volume_percent, organ_type, model)
            
            # Store results
            if 'ntcp' not in self.current_results:
                self.current_results['ntcp'] = []
            self.current_results['ntcp'].append(ntcp_result)
            
            # Display results
            self.display_ntcp_results(ntcp_result)
            
            self.log_message("NTCP calculation completed!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating NTCP: {str(e)}")
            self.log_message(f"NTCP Error: {str(e)}")
            
    def display_tcp_results(self, result: Dict):
        """Display TCP results"""
        self.tcp_results_text.delete(1.0, tk.END)
        
        text = f"TCP Results for {self.current_results['tcp_structure']}\n"
        text += "=" * 50 + "\n\n"
        text += f"Model: {result['model_used']}\n"
        text += f"Tumor Type: {result['tumor_type']}\n\n"
        text += f"Total TCP: {result['total_tcp']:.4f}\n"
        text += f"Mean TCP: {result['mean_tcp']:.4f}\n"
        text += f"TCP at D95: {result['tcp_d95']:.4f}\n"
        text += f"TCP at D50: {result['tcp_d50']:.4f}\n\n"
        text += "Parameters used:\n"
        for key, value in result['parameters'].items():
            text += f"  {key}: {value}\n"
            
        self.tcp_results_text.insert(1.0, text)
        
    def display_ntcp_results(self, result: Dict):
        """Display NTCP results"""
        self.ntcp_results_text.delete(1.0, tk.END)
        
        text = f"NTCP Results for {result['organ']}\n"
        text += "=" * 50 + "\n\n"
        text += f"Model: {result['model_used']}\n"
        text += f"Endpoint: {result['endpoint']}\n\n"
        text += f"NTCP: {result['ntcp']:.4f}\n"
        text += f"Mean Dose: {result['mean_dose']:.2f} Gy\n"
        text += f"Max Dose: {result['max_dose']:.2f} Gy\n"
        text += f"V20: {result['v20']:.1f}%\n"
        text += f"V30: {result['v30']:.1f}%\n"
        text += f"V40: {result['v40']:.1f}%\n\n"
        text += "Parameters used:\n"
        for key, value in result['parameters'].items():
            text += f"  {key}: {value}\n"
            
        self.ntcp_results_text.insert(1.0, text)
        
    def plot_dvh(self):
        """Plot DVH for selected structures"""
        # Implementation for DVH plotting
        messagebox.showinfo("Info", "DVH plotting feature will be implemented")
        
    def plot_tcp_ntcp(self):
        """Plot TCP/NTCP curves"""
        # Implementation for TCP/NTCP plotting
        messagebox.showinfo("Info", "TCP/NTCP plotting feature will be implemented")
        
    def export_results(self):
        """Export results to file"""
        # Implementation for results export
        messagebox.showinfo("Info", "Results export feature will be implemented")


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = TCPNTCPApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
