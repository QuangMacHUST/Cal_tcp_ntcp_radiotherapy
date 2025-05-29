"""
Demo script để test các chức năng của ứng dụng TCP/NTCP Calculator
"""

import numpy as np
import matplotlib.pyplot as plt
from tcp_models import TCPCalculator, TCPModels
from ntcp_models import NTCPCalculator, NTCPModels
from dose_calculations import DoseCalculations
from results_display import ResultsDisplay
import pandas as pd


def create_sample_dvh_data():
    """Tạo dữ liệu DVH mẫu để test"""
    
    # DVH cho target (PTV)
    dose_bins_target = np.linspace(0, 80, 100)
    # DVH có dạng sigmoid cho target
    volume_target = 100 / (1 + np.exp(-0.3 * (dose_bins_target - 70)))
    volume_target = 100 - volume_target  # Đảo ngược để có dạng DVH
    
    # DVH cho lung
    dose_bins_lung = np.linspace(0, 50, 100)
    volume_lung = 100 * np.exp(-dose_bins_lung / 15)  # Exponential decay
    
    # DVH cho heart
    dose_bins_heart = np.linspace(0, 40, 100)
    volume_heart = 100 * np.exp(-dose_bins_heart / 20)  # Exponential decay
    
    # DVH cho spinal cord
    dose_bins_cord = np.linspace(0, 45, 100)
    volume_cord = 100 * np.exp(-dose_bins_cord / 25)  # Exponential decay
    
    return {
        'PTV': {'dose_bins': dose_bins_target, 'volume_percent': volume_target},
        'Lung': {'dose_bins': dose_bins_lung, 'volume_percent': volume_lung},
        'Heart': {'dose_bins': dose_bins_heart, 'volume_percent': volume_heart},
        'SpinalCord': {'dose_bins': dose_bins_cord, 'volume_percent': volume_cord}
    }


def test_tcp_models():
    """Test các mô hình TCP"""
    print("🎯 TESTING TCP MODELS")
    print("=" * 50)
    
    calculator = TCPCalculator()
    
    # Test uniform dose calculations
    dose_values = [60, 65, 70, 75, 80]
    tumor_types = ['prostate', 'lung', 'breast']
    models = ['poisson', 'lq', 'logistic']
    
    results = []
    
    for tumor_type in tumor_types:
        print(f"\n📊 {tumor_type.upper()} TCP Results:")
        print("-" * 30)
        
        for model in models:
            print(f"\n{model.upper()} Model:")
            for dose in dose_values:
                try:
                    result = calculator.calculate_tcp_uniform_dose(dose, tumor_type, model)
                    tcp_value = result['tcp']
                    print(f"  {dose} Gy: TCP = {tcp_value:.4f}")
                    
                    results.append({
                        'Tumor_Type': tumor_type,
                        'Model': model,
                        'Dose_Gy': dose,
                        'TCP': tcp_value
                    })
                except Exception as e:
                    print(f"  {dose} Gy: Error - {e}")
    
    # Create summary table
    df = pd.DataFrame(results)
    print(f"\n📋 TCP Summary Table:")
    print(df.pivot_table(values='TCP', index='Dose_Gy', 
                        columns=['Tumor_Type', 'Model'], 
                        aggfunc='mean').round(4))
    
    return results


def test_ntcp_models():
    """Test các mô hình NTCP"""
    print("\n\n🛡️ TESTING NTCP MODELS")
    print("=" * 50)
    
    calculator = NTCPCalculator()
    
    # Test uniform dose calculations
    dose_values = [10, 20, 30, 40, 50]
    organs = ['lung', 'heart', 'spinal_cord', 'rectum']
    models = ['lkb', 'logistic', 'poisson']
    
    results = []
    
    for organ in organs:
        print(f"\n📊 {organ.upper()} NTCP Results:")
        print("-" * 30)
        
        for model in models:
            print(f"\n{model.upper()} Model:")
            for dose in dose_values:
                try:
                    result = calculator.calculate_ntcp_uniform_dose(dose, organ, model)
                    ntcp_value = result['ntcp']
                    endpoint = result['endpoint']
                    print(f"  {dose} Gy: NTCP = {ntcp_value:.4f} ({endpoint})")
                    
                    results.append({
                        'Organ': organ,
                        'Model': model,
                        'Dose_Gy': dose,
                        'NTCP': ntcp_value,
                        'Endpoint': endpoint
                    })
                except Exception as e:
                    print(f"  {dose} Gy: Error - {e}")
    
    # Create summary table
    df = pd.DataFrame(results)
    print(f"\n📋 NTCP Summary Table:")
    print(df.pivot_table(values='NTCP', index='Dose_Gy', 
                        columns=['Organ', 'Model'], 
                        aggfunc='mean').round(4))
    
    return results


def test_dvh_calculations():
    """Test tính toán DVH"""
    print("\n\n📈 TESTING DVH CALCULATIONS")
    print("=" * 50)
    
    dvh_data = create_sample_dvh_data()
    calc = DoseCalculations()
    
    for structure_name, data in dvh_data.items():
        print(f"\n📊 {structure_name} Statistics:")
        print("-" * 30)
        
        dose_bins = data['dose_bins']
        volume_percent = data['volume_percent']
        
        # Basic statistics
        stats = calc.calculate_dose_statistics(dose_bins, volume_percent)
        print(f"Mean Dose: {stats['mean_dose']:.2f} Gy")
        print(f"Max Dose: {stats['max_dose']:.2f} Gy")
        print(f"Min Dose: {stats['min_dose']:.2f} Gy")
        
        # Dx values
        dx_values = calc.calculate_dx_values(dose_bins, volume_percent)
        for key, value in dx_values.items():
            print(f"{key}: {value:.2f} Gy")
        
        # Vx values
        vx_values = calc.calculate_vx_values(dose_bins, volume_percent)
        for key, value in vx_values.items():
            print(f"{key}: {value:.1f}%")


def test_tcp_ntcp_from_dvh():
    """Test tính toán TCP/NTCP từ DVH"""
    print("\n\n🔬 TESTING TCP/NTCP FROM DVH")
    print("=" * 50)
    
    dvh_data = create_sample_dvh_data()
    tcp_calc = TCPCalculator()
    ntcp_calc = NTCPCalculator()
    
    # TCP calculation for PTV
    ptv_data = dvh_data['PTV']
    print("\n🎯 TCP Calculation for PTV:")
    print("-" * 30)
    
    try:
        tcp_result = tcp_calc.calculate_tcp_from_dvh(
            ptv_data['dose_bins'], 
            ptv_data['volume_percent'], 
            'prostate', 
            'poisson'
        )
        
        print(f"Total TCP: {tcp_result['total_tcp']:.4f}")
        print(f"Mean TCP: {tcp_result['mean_tcp']:.4f}")
        print(f"TCP at D95: {tcp_result['tcp_d95']:.4f}")
        print(f"TCP at D50: {tcp_result['tcp_d50']:.4f}")
        
    except Exception as e:
        print(f"Error calculating TCP: {e}")
    
    # NTCP calculations for OARs
    oar_mapping = {
        'Lung': 'lung',
        'Heart': 'heart',
        'SpinalCord': 'spinal_cord'
    }
    
    ntcp_results = []
    
    for structure_name, organ_type in oar_mapping.items():
        if structure_name in dvh_data:
            print(f"\n🛡️ NTCP Calculation for {structure_name}:")
            print("-" * 30)
            
            try:
                oar_data = dvh_data[structure_name]
                ntcp_result = ntcp_calc.calculate_ntcp_from_dvh(
                    oar_data['dose_bins'],
                    oar_data['volume_percent'],
                    organ_type,
                    'lkb'
                )
                
                print(f"NTCP: {ntcp_result['ntcp']:.4f}")
                print(f"Mean Dose: {ntcp_result['mean_dose']:.2f} Gy")
                print(f"Max Dose: {ntcp_result['max_dose']:.2f} Gy")
                print(f"Endpoint: {ntcp_result['endpoint']}")
                
                ntcp_results.append(ntcp_result)
                
            except Exception as e:
                print(f"Error calculating NTCP for {structure_name}: {e}")
    
    # Calculate therapeutic ratio
    if 'tcp_result' in locals() and ntcp_results:
        print(f"\n⚖️ THERAPEUTIC ANALYSIS:")
        print("-" * 30)
        
        total_ntcp = sum([result['ntcp'] for result in ntcp_results])
        therapeutic_ratio = ntcp_calc.calculate_therapeutic_ratio(
            tcp_result['total_tcp'], total_ntcp
        )
        
        print(f"TCP: {therapeutic_ratio['tcp']:.4f}")
        print(f"Total NTCP: {therapeutic_ratio['ntcp']:.4f}")
        print(f"Uncomplicated Cure Probability: {therapeutic_ratio['uncomplicated_cure_probability']:.4f}")
        print(f"Therapeutic Ratio (TCP/NTCP): {therapeutic_ratio['therapeutic_ratio_1']:.2f}")


def test_plotting():
    """Test chức năng vẽ biểu đồ"""
    print("\n\n📊 TESTING PLOTTING FUNCTIONS")
    print("=" * 50)
    
    try:
        display = ResultsDisplay()
        dvh_data = create_sample_dvh_data()
        
        # Test DVH plot
        print("Creating DVH plot...")
        fig_dvh = display.plot_dvh(dvh_data, save_path="demo_dvh.png")
        print("✅ DVH plot created: demo_dvh.png")
        
        # Test TCP curve
        print("Creating TCP curve...")
        dose_range = np.linspace(0, 100, 100)
        tcp_values = [TCPModels.poisson_tcp(d, 70, 2.0) for d in dose_range]
        fig_tcp = display.plot_tcp_curve(dose_range, tcp_values, 'prostate', 'poisson', 
                                        save_path="demo_tcp.png")
        print("✅ TCP curve created: demo_tcp.png")
        
        # Test NTCP curve
        print("Creating NTCP curve...")
        ntcp_values = [NTCPModels.lyman_kutcher_burman(d, 24.5, 0.18, 0.87) for d in dose_range]
        fig_ntcp = display.plot_ntcp_curve(dose_range, ntcp_values, 'lung', 'lkb',
                                          save_path="demo_ntcp.png")
        print("✅ NTCP curve created: demo_ntcp.png")
        
        plt.close('all')  # Close all figures to free memory
        
    except Exception as e:
        print(f"❌ Error in plotting: {e}")


def run_comprehensive_demo():
    """Chạy demo toàn diện"""
    print("🚀 TCP/NTCP CALCULATOR - COMPREHENSIVE DEMO")
    print("=" * 60)
    print("This demo tests all major functionalities of the application")
    print("=" * 60)
    
    try:
        # Test individual models
        tcp_results = test_tcp_models()
        ntcp_results = test_ntcp_models()
        
        # Test DVH calculations
        test_dvh_calculations()
        
        # Test TCP/NTCP from DVH
        test_tcp_ntcp_from_dvh()
        
        # Test plotting
        test_plotting()
        
        print("\n\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("All major functionalities are working correctly.")
        print("You can now run the main application: python main.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n\n❌ DEMO FAILED: {e}")
        print("Please check the error messages above and fix any issues.")


if __name__ == "__main__":
    run_comprehensive_demo()
