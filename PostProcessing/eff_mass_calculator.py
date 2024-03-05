import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.optimize import curve_fit
import os
import json  # For saving effective mass arguments
import argparse

class EffectiveMassCalculator:
    def __init__(self, filepath, percentage_windows, mean_energy, sep_limits,max_valence_k):
        self.filepath = filepath
        self.percentage_windows = percentage_windows
        self.filename = os.path.basename(filepath).split('.')[0]
        self.directory = f'effective_mass_{self.filename}'
        self.args_directory = f'{self.directory}/args'
        self.mean_energy = mean_energy
        self.sep_limits = sep_limits
        self.max_valence_k = max_valence_k
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(self.args_directory):
            os.makedirs(self.args_directory)
        # Enable LaTeX in plots
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

    @staticmethod
    def parabolic_energy(k, E0, m_star_inverse):
        """Energy of a parabola: E = E0 + (\hbar^2 k^2) / (2m*)"""
        return E0 + (m_star_inverse) * k**2

    def fit_parabola(self, k_values, E_values, E0_initial):
        """Fits a parabolic energy band to given k and E values."""
        try:
            params, params_covariance = curve_fit(self.parabolic_energy, k_values, E_values, p0=[E0_initial, 1e-3])
            return params, True, np.sqrt(np.diag(params_covariance))  # Return fitting parameters and the standard deviation of the fit
        except RuntimeError:
            return [E0_initial, 0], False, [0, 0]  # Return initial values and False indicating failure to fit along with zero errors

    def plot_convergence(self, errors, percentage_windows, band_type):
        """Plots the fitting error as a function of the window percentage."""
        plt.figure(figsize=(10, 8))
        plt.plot(percentage_windows, errors, 'bo-', label=f'{band_type.capitalize()} Band Convergence')
        plt.xlabel('Window Size (Percent)')
        plt.ylabel('Fitting Error', fontsize=14)  # Correct LaTeX formatting
        plt.title(f'Convergence Plot for {band_type.capitalize()} Band')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'{self.directory}/convergence_{band_type}.png')
        plt.close()
        print(f"Convergence plot saved to {self.directory}/convergence_{band_type}.png")

    def best_fit_convergence_plot(self, df, band_type='heavy hole', energy_offset=0):
        """Finds the best fit for different percentage windows and plots the fitting for the best window."""

        
        # Separate the bands based on the adjusted mean energy
        valence_band = df[df['E'] < self.mean_energy]
        conduction_band = df[df['E'] > self.mean_energy]

        # Recalculate 'k_distance' for just the valence_band
        valence_band['k_distance'] = np.sqrt((valence_band['kx'] - self.max_valence_k[0]) ** 2 + 
                                            (valence_band['ky'] - self.max_valence_k[1]) ** 2 +
                                            (valence_band['kz'] - self.max_valence_k[2]) ** 2)
        # Find index of the point closest to max_valence_k in the valence_band
        valence_max_point_idx = valence_band['k_distance'].idxmin()

        # Now you can safely retrieve the max point from valence_band
        max_point = valence_band.loc[valence_max_point_idx]


        errors = []
        best_error = np.inf
        best_params = None
        best_window = None
        best_grouped = None

        for percentage_window in self.percentage_windows:
            window_size = int(len(valence_band) * percentage_window / 100.0)
            start_idx = valence_max_point_idx
            if start_idx + window_size > len(valence_band):
                end_idx = start_idx - window_size
            else:
                end_idx = start_idx + window_size

            windowed_valence_band = valence_band.iloc[start_idx:end_idx]
            
            # NOTE THERE IS SPIN DEGENERACY AND THEREFORE WE LOOK FOR THE 3RD MAX
            if band_type == 'heavy hole':
                grouped = windowed_valence_band.sort_values(by='E', ascending=False).groupby('k').nth(0)
            else:  # 'light hole'
                grouped = windowed_valence_band.sort_values(by='E', ascending=False).groupby('k').nth(3)
            
            params, success, param_errors = self.fit_parabola(grouped['k'], grouped['E'], max_point['E'])
            errors.append(param_errors[1] if success else np.inf)
            if success and param_errors[1] < best_error:
                best_error = param_errors[1]
                best_params = params
                best_window = percentage_window
                best_grouped = grouped
                if band_type == 'heavy hole':
                    self.best_heavy_hole_grouped = best_grouped
                else:  # 'light hole'
                    self.best_light_hole_grouped = best_grouped

        # Plotting the best fit
        if best_params is not None:
            g = best_params[1]  # best_params[1] should correspond to the fit value of (hbar^2/2m*)
            effective_mass_output = {'g': g, 'equivalency': '(h^2/a^2)(1/8m_{eff}e)'}
            with open(f'{self.args_directory}/m_star_{band_type.capitalize().replace(" ", "_")}.json', 'w') as f:
                json.dump(effective_mass_output, f)
            print(f"Effective mass m* = {m_star:.2e} hbar^2/eV*m^2 (for best fit in {band_type.capitalize()} band)")
            
            plt.figure(figsize=(10, 8))
            k_vals = np.linspace(best_grouped['k'].min(), best_grouped['k'].max(), 100)
            plt.scatter(best_grouped['k'], best_grouped['E'], c='blue', label=f'Band Points (Best Window: {best_window}%)')
            plt.plot(k_vals, self.parabolic_energy(k_vals, *best_params), 'r-', label=f'Fitted Parabola (Error: {best_error:.2e})')
            plt.xlabel('$k$ (sqrt($k_x^2 + k_y^2 + k_z^2$))', fontsize=14)
            plt.ylabel('Energy (E) [eV]', fontsize=14)
            plt.title(f'Optimal Parabola Fitting for {band_type.capitalize()} Band', fontsize=16)
            plt.legend()
            plt.grid(True)
            plot_filename = f'{self.directory}/{band_type.capitalize().replace(" ", "_")}_band_{best_window}%_fit.png'
            plt.savefig(plot_filename)
            #plt.show()
            plt.close()
            print(f"Plot saved to {plot_filename}")
        else:
            print("No successful fit found.")

        # Plot the convergence
        #self.plot_convergence(errors, self.percentage_windows, band_type)

   
    def plot_bands(self, df,offset=0):
        """Plots the total energy bands: valence and conduction."""
        plt.figure(figsize=(10, 8))

        
        valence_band = df[df['E'] < self.mean_energy]
        conduction_band = df[df['E'] > self.mean_energy]

        plt.scatter(valence_band['k'], valence_band['E'], c='blue', label='Valence Band', s=10)
        plt.scatter(conduction_band['k'], conduction_band['E'], c='red', label='Conduction Band', s=10)
        if hasattr(self, 'best_heavy_hole_grouped'):
            plt.scatter(self.best_heavy_hole_grouped['k'], self.best_heavy_hole_grouped['E'], c='green', label='Heavy Hole Group', s=10, marker='^')
        if hasattr(self, 'best_light_hole_grouped'):
            plt.scatter(self.best_light_hole_grouped['k'], self.best_light_hole_grouped['E'], c='purple', label='Light Hole Group', s=10, marker='s')

        plt.axhline(y=self.mean_energy, color='grey', linestyle='--', label='Mean Energy')
        plt.xlabel('k (pi/a)', fontsize=14)
        plt.ylabel('Energy (E) [eV]', fontsize=14)
        plt.title('Band Structure', fontsize=16)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
    def run(self):
        # Pull in data
        df = pd.read_csv(self.filepath)

        df['k'] = np.sqrt(df['kx']**2 + df['ky']**2 + df['kz']**2).round(4)
        df = df[(df['E'] >= self.sep_limits[0]) & (df['E'] <= self.sep_limits[1])]
        df.sort_values(by='k', inplace=True)
        df.reset_index(drop=True, inplace=True)

        self.best_fit_convergence_plot(df, band_type='heavy hole')
        self.best_fit_convergence_plot(df, band_type='light hole')
        self.plot_bands(df)

if __name__ == "__main__":


    # Argument parsing setup
    parser = argparse.ArgumentParser(description='Effective Mass Calculator for specific band path.')
    parser.add_argument('--csv_dir', type=str, required=True, help='Directory containing the band structure CSV files.')
    parser.add_argument('--max_valence_symbol', type=str, default='Γ', help='Symbol of the maximum valence point (default: Γ).')
    parser.add_argument('--mu', type=float, required=True, help='Pre-calculated mean energy value to use instead of calculating from centroids.')
    parser.add_argument('--sep_limits', type=float, nargs=2, default=[-3, 3], help='Energy range limits for separation calculation (valence and conduction bands).')

    args = parser.parse_args()
    csv_dir = os.path.join(os.getcwd(),args.csv_dir)
    
    #Mapping between k_vector and symbol
    segment_to_symbol = {
    '0_0_0': 'Γ',
    '0_2_0': 'X',
    '1_1_1': 'L',
    '1_2_0': 'W',
    '0.5_2_0.5': 'U',
    '1.5_1.5_0': 'K'
}
    # Find files that involve the maximum valence point
    max_valence_segment = [key for key, value in segment_to_symbol.items() if value == args.max_valence_symbol][0]
    relevant_files = [file for file in os.listdir(args.csv_dir) if max_valence_segment in file and file.endswith('.csv')]

    # Reverse the segment_to_symbol mapping to go from symbol to k-point strings
    symbol_to_segment = {v: k for k, v in segment_to_symbol.items()}

    # Find the k-point string that corresponds to the provided max valence symbol
    max_valence_k_string = symbol_to_segment.get(args.max_valence_symbol)
    if max_valence_k_string:
        # Convert the string to numerical values, assuming the format 'kx_ky_kz'
        max_valence_k = [float(num) for num in max_valence_k_string.split('_')]
    else:
        print(f"Warning: Max valence symbol '{args.max_valence_symbol}' is not recognized. Please check the symbol and try again.")
        max_valence_k = [0, 0, 0]  # Default to Gamma point if symbol not recognized
    


    # Run effective mass calculations
    percentage_windows = [1,2,3,4,5]
    for filename in relevant_files:
        filepath = os.path.join(args.csv_dir, filename)
        print(f"Processing {filepath}...")

        # Initialize and run EffectiveMassCalculator
        calculator = EffectiveMassCalculator(filepath, percentage_windows,args.mu, args.sep_limits,max_valence_k)
        calculator.run()

