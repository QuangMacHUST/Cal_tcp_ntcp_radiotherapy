"""
Module hiển thị kết quả và tạo biểu đồ
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import seaborn as sns


class ResultsDisplay:
    """Class hiển thị kết quả và tạo biểu đồ"""
    
    def __init__(self):
        # Set style for plots
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def plot_dvh(self, dvh_data: Dict, save_path: str = None) -> plt.Figure:
        """
        Vẽ biểu đồ Dose Volume Histogram
        
        Args:
            dvh_data: Dict chứa dữ liệu DVH cho các structure
            save_path: Đường dẫn lưu file (optional)
            
        Returns:
            plt.Figure: Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(dvh_data)))
        
        for i, (structure_name, data) in enumerate(dvh_data.items()):
            dose_bins = data['dose_bins']
            volume_percent = data['volume_percent']
            
            ax.plot(dose_bins, volume_percent, 
                   label=structure_name, 
                   linewidth=2, 
                   color=colors[i])
        
        ax.set_xlabel('Dose (Gy)', fontsize=12)
        ax.set_ylabel('Volume (%)', fontsize=12)
        ax.set_title('Dose Volume Histogram', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Set axis limits
        ax.set_xlim(0, None)
        ax.set_ylim(0, 100)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_tcp_curve(self, dose_range: np.ndarray, tcp_values: np.ndarray,
                      tumor_type: str, model: str, save_path: str = None) -> plt.Figure:
        """
        Vẽ đường cong TCP
        
        Args:
            dose_range: Array liều lượng
            tcp_values: Array giá trị TCP
            tumor_type: Loại tumor
            model: Mô hình TCP
            save_path: Đường dẫn lưu file
            
        Returns:
            plt.Figure: Figure object
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(dose_range, tcp_values, 'b-', linewidth=3, label=f'{model.upper()} model')
        
        # Add reference lines
        ax.axhline(y=0.5, color='r', linestyle='--', alpha=0.7, label='TCP = 50%')
        ax.axhline(y=0.95, color='g', linestyle='--', alpha=0.7, label='TCP = 95%')
        
        ax.set_xlabel('Dose (Gy)', fontsize=12)
        ax.set_ylabel('TCP', fontsize=12)
        ax.set_title(f'TCP Curve - {tumor_type.title()} ({model.upper()} model)', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Set axis limits
        ax.set_xlim(0, np.max(dose_range))
        ax.set_ylim(0, 1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_ntcp_curve(self, dose_range: np.ndarray, ntcp_values: np.ndarray,
                       organ: str, model: str, save_path: str = None) -> plt.Figure:
        """
        Vẽ đường cong NTCP
        
        Args:
            dose_range: Array liều lượng
            ntcp_values: Array giá trị NTCP
            organ: Tên organ
            model: Mô hình NTCP
            save_path: Đường dẫn lưu file
            
        Returns:
            plt.Figure: Figure object
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(dose_range, ntcp_values, 'r-', linewidth=3, label=f'{model.upper()} model')
        
        # Add reference lines
        ax.axhline(y=0.05, color='g', linestyle='--', alpha=0.7, label='NTCP = 5%')
        ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, label='NTCP = 50%')
        
        ax.set_xlabel('Dose (Gy)', fontsize=12)
        ax.set_ylabel('NTCP', fontsize=12)
        ax.set_title(f'NTCP Curve - {organ.title()} ({model.upper()} model)', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Set axis limits
        ax.set_xlim(0, np.max(dose_range))
        ax.set_ylim(0, 1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_tcp_ntcp_comparison(self, dose_range: np.ndarray, tcp_values: np.ndarray,
                               ntcp_values: np.ndarray, tumor_type: str, organ: str,
                               save_path: str = None) -> plt.Figure:
        """
        Vẽ biểu đồ so sánh TCP và NTCP
        
        Args:
            dose_range: Array liều lượng
            tcp_values: Array giá trị TCP
            ntcp_values: Array giá trị NTCP
            tumor_type: Loại tumor
            organ: Tên organ
            save_path: Đường dẫn lưu file
            
        Returns:
            plt.Figure: Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot TCP and NTCP curves
        ax.plot(dose_range, tcp_values, 'b-', linewidth=3, label=f'TCP ({tumor_type})')
        ax.plot(dose_range, ntcp_values, 'r-', linewidth=3, label=f'NTCP ({organ})')
        
        # Calculate and plot therapeutic window
        therapeutic_ratio = tcp_values / (ntcp_values + 1e-10)  # Avoid division by zero
        optimal_dose_idx = np.argmax(therapeutic_ratio)
        optimal_dose = dose_range[optimal_dose_idx]
        
        ax.axvline(x=optimal_dose, color='g', linestyle='--', alpha=0.7, 
                  label=f'Optimal dose: {optimal_dose:.1f} Gy')
        
        # Add reference lines
        ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
        ax.axhline(y=0.95, color='gray', linestyle=':', alpha=0.5)
        
        ax.set_xlabel('Dose (Gy)', fontsize=12)
        ax.set_ylabel('Probability', fontsize=12)
        ax.set_title('TCP vs NTCP Comparison', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Set axis limits
        ax.set_xlim(0, np.max(dose_range))
        ax.set_ylim(0, 1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_dose_statistics_bar(self, dose_stats: Dict, structure_name: str,
                               save_path: str = None) -> plt.Figure:
        """
        Vẽ biểu đồ cột thống kê dose
        
        Args:
            dose_stats: Dict chứa thống kê dose
            structure_name: Tên structure
            save_path: Đường dẫn lưu file
            
        Returns:
            plt.Figure: Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data
        stats_to_plot = ['mean_dose', 'median_dose', 'D95', 'D50', 'D5']
        values = [dose_stats.get(stat, 0) for stat in stats_to_plot]
        labels = ['Mean', 'Median', 'D95', 'D50', 'D5']
        
        colors = ['skyblue', 'lightgreen', 'orange', 'pink', 'lightcoral']
        
        bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='black')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Dose (Gy)', fontsize=12)
        ax.set_title(f'Dose Statistics - {structure_name}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def create_summary_table(self, tcp_results: Dict, ntcp_results: List[Dict]) -> pd.DataFrame:
        """
        Tạo bảng tổng kết kết quả
        
        Args:
            tcp_results: Kết quả TCP
            ntcp_results: List kết quả NTCP
            
        Returns:
            pd.DataFrame: Bảng tổng kết
        """
        summary_data = []
        
        # TCP data
        if tcp_results:
            tcp_row = {
                'Structure': tcp_results.get('tumor_type', 'Unknown'),
                'Type': 'Target (TCP)',
                'Model': tcp_results.get('model_used', ''),
                'Probability': tcp_results.get('total_tcp', 0),
                'Mean_Dose': tcp_results.get('parameters', {}).get('td50', 0),
                'Endpoint': 'Tumor Control'
            }
            summary_data.append(tcp_row)
        
        # NTCP data
        for ntcp_result in ntcp_results:
            ntcp_row = {
                'Structure': ntcp_result.get('organ', 'Unknown'),
                'Type': 'OAR (NTCP)',
                'Model': ntcp_result.get('model_used', ''),
                'Probability': ntcp_result.get('ntcp', 0),
                'Mean_Dose': ntcp_result.get('mean_dose', 0),
                'Endpoint': ntcp_result.get('endpoint', '')
            }
            summary_data.append(ntcp_row)
        
        df = pd.DataFrame(summary_data)
        return df
    
    def plot_summary_table(self, summary_df: pd.DataFrame, save_path: str = None) -> plt.Figure:
        """
        Vẽ bảng tổng kết dưới dạng hình ảnh
        
        Args:
            summary_df: DataFrame tổng kết
            save_path: Đường dẫn lưu file
            
        Returns:
            plt.Figure: Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.axis('tight')
        ax.axis('off')
        
        # Create table
        table = ax.table(cellText=summary_df.values,
                        colLabels=summary_df.columns,
                        cellLoc='center',
                        loc='center')
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Color header
        for i in range(len(summary_df.columns)):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color rows alternately
        for i in range(1, len(summary_df) + 1):
            for j in range(len(summary_df.columns)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#f0f0f0')
        
        plt.title('TCP/NTCP Summary Results', fontsize=16, fontweight='bold', pad=20)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def create_dashboard(self, tcp_results: Dict, ntcp_results: List[Dict],
                        dvh_data: Dict, save_path: str = None) -> plt.Figure:
        """
        Tạo dashboard tổng hợp
        
        Args:
            tcp_results: Kết quả TCP
            ntcp_results: List kết quả NTCP
            dvh_data: Dữ liệu DVH
            save_path: Đường dẫn lưu file
            
        Returns:
            plt.Figure: Figure object
        """
        fig = plt.figure(figsize=(16, 12))
        
        # Create subplots
        gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], hspace=0.3, wspace=0.3)
        
        # DVH plot (top, spanning both columns)
        ax1 = fig.add_subplot(gs[0, :])
        colors = plt.cm.tab10(np.linspace(0, 1, len(dvh_data)))
        for i, (structure_name, data) in enumerate(dvh_data.items()):
            ax1.plot(data['dose_bins'], data['volume_percent'], 
                    label=structure_name, linewidth=2, color=colors[i])
        ax1.set_xlabel('Dose (Gy)')
        ax1.set_ylabel('Volume (%)')
        ax1.set_title('Dose Volume Histogram')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # TCP results (bottom left)
        ax2 = fig.add_subplot(gs[1, 0])
        if tcp_results:
            tcp_value = tcp_results.get('total_tcp', 0)
            ax2.bar(['TCP'], [tcp_value], color='blue', alpha=0.7)
            ax2.set_ylabel('Probability')
            ax2.set_title('TCP Result')
            ax2.set_ylim(0, 1)
            ax2.text(0, tcp_value + 0.05, f'{tcp_value:.3f}', 
                    ha='center', va='bottom', fontweight='bold')
        
        # NTCP results (bottom right)
        ax3 = fig.add_subplot(gs[1, 1])
        if ntcp_results:
            organs = [result['organ'] for result in ntcp_results]
            ntcp_values = [result['ntcp'] for result in ntcp_results]
            ax3.bar(organs, ntcp_values, color='red', alpha=0.7)
            ax3.set_ylabel('Probability')
            ax3.set_title('NTCP Results')
            ax3.set_ylim(0, 1)
            plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
            
            for i, value in enumerate(ntcp_values):
                ax3.text(i, value + 0.02, f'{value:.3f}', 
                        ha='center', va='bottom', fontweight='bold')
        
        # Summary statistics (bottom, spanning both columns)
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('off')
        
        # Create summary text
        summary_text = "Summary Statistics:\n"
        if tcp_results:
            summary_text += f"TCP: {tcp_results.get('total_tcp', 0):.3f} "
            summary_text += f"({tcp_results.get('tumor_type', 'Unknown')} - {tcp_results.get('model_used', '')})\n"
        
        for result in ntcp_results:
            summary_text += f"NTCP ({result['organ']}): {result['ntcp']:.3f} "
            summary_text += f"({result['model_used']} model)\n"
        
        ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes, 
                fontsize=12, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5))
        
        plt.suptitle('TCP/NTCP Analysis Dashboard', fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig


if __name__ == "__main__":
    # Test code
    display = ResultsDisplay()
    print("Results Display module loaded successfully")
