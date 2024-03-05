import argparse
from KSpace.kspacesetup import KSpaceSetup,update_k_vectors
from Job.job_manager import JobManager
from User.parser import parse_args
import os

def main():
    """
    Main function to execute the script logic. It parses user input, converts the symbolic k-space path
    to k-value pairs, and updates XML files accordingly.
    """
    ### SETUP XML FILES

    # Define relevant symettry points for KSpaceSetup
    symmetry_points = {
    'Γ': (0, 0, 0),  # Gamma point
    'X': (0, 2, 0),  # X point, considering 2π/a as 1 for simplicity
    'L': (1, 1, 1),  # L point
    'W': (1, 2, 0),  # W point
    'U': (0.5, 2, 0.5),  # U point
    'K': (1.5, 1.5, 0),  # K point
    }
    k_space_setup = KSpaceSetup(symmetry_points=symmetry_points)

    # Parse the command line arguments
    user_defined_args = parse_args()

    # Convert the user defined symbolic path to the format required by KSpaceSetup
    path_symbols = user_defined_args.path.replace('G','Γ').split(',')    
    k_values_path = k_space_setup.symbolic_path_to_k_pairs(path_symbols)

    # Update the XML files based on the user-defined k-space path
    xml_file_path = os.path.join(os.getcwd(),user_defined_args.xml_template)
    update_k_vectors(xml_file_path, k_values_path, user_defined_args.output, path_symbols)

    # Manage the jobs: submit, track, and combine
    job_manager = JobManager(
    xml_directory=user_defined_args.output,
    job_directory=user_defined_args.job_directory,
    executable=user_defined_args.executable,
    post_process_script=user_defined_args.post_process_script,
    combiner_script='csv_combiner.py',  # Path to your CSV combining script
    combiner_directory=user_defined_args.output  # Directory where the combined CSV should be saved
    )
    job_manager.manage_jobs()
    

if __name__ == '__main__':
    main()