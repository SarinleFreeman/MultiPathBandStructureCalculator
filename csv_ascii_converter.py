import os
import pandas as pd
import sys  # Importing sys to read command-line arguments

def read_ascii_file(file_path):
    """
    Reads the ASCII file, skipping the first 5 rows and using whitespace as delimiter.
    Returns a DataFrame with column names for dispersion data.
    """
    df = pd.read_csv(file_path, skiprows=5, delim_whitespace=True, header=None, names=['kx', 'ky', 'kz', 'E'])
    return df

def process_file_and_save_csv(file_path):
    """
    Processes a single .nd_Ek_ascii file with read_ascii_file, and saves it as a CSV file with the same name.
    
    :param file_path: Full path to the ASCII file.
    """
    # Check if the file ends with the .nd_Ek_ascii extension
    if file_path.endswith(".nd_Ek_ascii"):
        # Read the file into a DataFrame
        df = read_ascii_file(file_path)
        
        # Construct the CSV file name by replacing the extension
        folder_path, file_name = os.path.split(file_path)
        csv_file_name = file_name.replace('.nd_Ek_ascii', '.csv')
        csv_file_path = os.path.join(folder_path, csv_file_name)
        
        # Save the DataFrame to a CSV file
        df.to_csv(csv_file_path, index=False)
        print(f"Saved CSV file: {csv_file_name}")
    else:
        print(f"The file {file_name} does not end with .nd_Ek_ascii")

if __name__ == "__main__":
    # Check if a file path was provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]  # Get the file path from command-line arguments
        process_file_and_save_csv(file_path)
    else:
        print("Please provide the path to the .nd_Ek_ascii file.")
