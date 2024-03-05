import json
import pandas as pd
import os
import glob  # Import glob module to find all the pathnames matching a specified pattern
import argparse

# Define mapping from symbols to k values
symmetry_points = {
    'Γ': (0, 0, 0),
    'X': (0, 2, 0),
    'L': (1, 1, 1),
    'W': (1, 2, 0),
    'U': (0.5, 2, 0.5),
    'K': (1.5, 1.5, 0)
}

def read_json_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

def symbolic_path_to_k_pairs(symbolic_path):
    """
    Convert a list of symbolic path points to a list of k-value pairs.
    """
    k_path = [symmetry_points[symbol] for symbol in symbolic_path]
    return [(k_path[i], k_path[i + 1]) for i in range(len(k_path) - 1)]

def create_file_names_from_k_pairs(base_name, k_pairs):
    """
    Generates a list of file names based on the provided list of k-value pairs.
    """
    file_names = []
    for initial_k, final_k in k_pairs:
        file_name = f"{base_name}_{'_'.join(map(str, initial_k))}to{'_'.join(map(str, final_k))}.csv"
        file_names.append(file_name)
    return file_names

def combine_csv_files(file_paths, k_pairs):
    combined_df = pd.DataFrame()
    for i, file_path in enumerate(file_paths):
        df = pd.read_csv(file_path)
        # Assign the segment start and end points to the first and last row respectively
        df['Segment_Point'] = ''  # Initialize the column with empty strings
        if not df.empty:  # Check if the DataFrame is not empty
            df.at[0, 'Segment_Point'] = str(k_pairs[i][0])  # Set start of segment
            df.at[len(df) - 1, 'Segment_Point'] = str(k_pairs[i][1])  # Set end of segment
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

def find_first_csv_file(base_path):
    """
    Finds the first CSV file in the specified directory.
    """
    csv_files = glob.glob(f'{base_path}/*.csv')
    return os.path.basename(csv_files[0]) if csv_files else None

def extract_title_from_file_name(file_name):
    """
    Extracts the title from a file name by removing the k-point segment and any preceding path.
    """
    base_name = os.path.basename(file_name)  # Remove directory path if present
 
    title = base_name.split('_')[0] # Remove the last three elements (k-point segment)
    return title

def run_combination_process(base_path):
    # Read configuration
    config = read_json_config(f'{base_path}/args.json')

    
    # Find the first CSV file in the directory to extract the title
    first_csv_file = find_first_csv_file(base_path)
    if not first_csv_file:
        raise Exception("No CSV files found in the directory.")
    title = extract_title_from_file_name(first_csv_file)

    # Generate k-value pairs and corresponding file names
    symbolic_path = config['symbolic_path']
    k_pairs = symbolic_path_to_k_pairs(symbolic_path)
    csv_files = create_file_names_from_k_pairs(f'{base_path}/{title}', k_pairs)
    
    # Combine CSV files
    combined_df = combine_csv_files(csv_files,k_pairs)
    
    # Save the combined DataFrame
    combined_df.to_csv(f'{base_path}/{title}_combined.csv', index=False)
    print(f'Combined CSV file saved to {base_path}/{title}_combined.csv')



#Parse argument
parser = argparse.ArgumentParser(description='Combine CSV files based on k-value pairs.')
parser.add_argument('-dir','--directory',type=str, help='Path to the directory containing CSV files and args.json')
args = parser.parse_args()

run_combination_process(args.directory)
