import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import argparse
import os
import json

class BandStructureAnalyzer:
    def __init__(self, args):
        self.args = args
        self.df = pd.read_csv(os.path.join(os.getcwd(), args.csv_local_dir))
        self.subspace_df = self.df[(self.df['E'] >= args.sep_limits[0]) & (self.df['E'] <= args.sep_limits[1])]
        self.mean_energy = None
        self.bandgap_energy = None
        self.segment_of_max_valence = None

    def apply_kmeans_clustering(self):
        kmeans = KMeans(n_clusters=2)
        subspace_clusters = kmeans.fit_predict(self.subspace_df[['kx', 'E']].values)
        self.subspace_df['cluster'] = subspace_clusters
        centroids = kmeans.cluster_centers_
        self.mean_energy = centroids[:, 1].mean()

    def identify_band_edges(self):
        valence_band = self.df[self.df['E'] < self.mean_energy]
        conduction_band = self.df[self.df['E'] > self.mean_energy]
        highest_valence_point = valence_band.loc[valence_band['E'].idxmax()]
        lowest_conduction_point = conduction_band.loc[conduction_band['E'].idxmin()]
        self.bandgap_energy = lowest_conduction_point['E'] - highest_valence_point['E']
        self.segment_of_max_valence = self.find_nearest_segment(highest_valence_point.name)

    def find_nearest_segment(self, index):
        max_range = max(len(self.df), index)
        nearest_segment = None
        nearest_distance = max_range
        
        for distance in range(max_range):
            if index - distance >= 0:
                if pd.notna(self.df.at[index - distance, 'Segment_Point']):
                    nearest_segment = self.df.at[index - distance, 'Segment_Point']
                    break

            if index + distance < len(self.df):
                if pd.notna(self.df.at[index + distance, 'Segment_Point']):
                    if distance <= nearest_distance:
                        nearest_segment = self.df.at[index + distance, 'Segment_Point']
                    break
        
        return nearest_segment

    def plot_and_save(self):
        plt.figure(figsize=(10, 8))
        # Add plotting code here, similar to what you already have
        # Remember to use self.mean_energy, self.bandgap_energy, etc.
        plt.close()

    def update_args_file(self):
        args_file_path = os.path.join(os.path.dirname(self.args.csv_local_dir), 'args.json')
        with open(args_file_path, 'r') as file:
            args_data = json.load(file)
        
        args_data['max_segment_point'] = str(self.segment_of_max_valence)
        args_data['band_energy'] = self.bandgap_energy
        args_data['mean_energy'] = self.mean_energy
        
        with open(args_file_path, 'w') as file:
            json.dump(args_data, file, indent=4)
        print("Updated args data:", args_data)

    def run(self):
        self.apply_kmeans_clustering()
        self.identify_band_edges()
        self.plot_and_save()
        self.update_args_file()

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Bandstructure Viewer with Clustering and Plotting Options.')
    parser.add_argument('--csv_local_dir', type=str, required=True, help='Local relative directory of the CSV file.')
    parser.add_argument('--sep_limits', type=float, nargs=2, default=[-3, 3], help='Energy range limits for separation calculation (valence and conduction bands).')
    parser.add_argument('--plot_limits', type=float, nargs=2, help='Energy range limits for plotting. If not provided, sep_limits will be used.')
    parser.add_argument('--save_dir', type=str, required=True, help='Directory where the plot should be saved.')
    parser.add_argument('--plot_title', type=str, required=True, help='Title of Plot')
    args = parser.parse_args()

    analyzer = BandStructureAnalyzer(args)
    analyzer.run()
