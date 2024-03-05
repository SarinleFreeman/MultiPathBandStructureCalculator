
import argparse

def parse_args():
    """
    Parse command line arguments to determine the k-space path and other configurations specified by the user.
    The user will pass in a sequence of points in k-space, such as 'G X L',
    where 'G' stands for Gamma, 'X', 'L', etc., represent standard points in the Brillouin zone.
    Additionally, the user can specify the path to the XML template file and the output directory.
    """
    parser = argparse.ArgumentParser(description='Parse user options for the k-space setup')
    # Define the expected command-line arguments
    parser.add_argument('-p', '--path', type=str, default='G,X,L',
                    help='A sequence of points in k-space separated by commas, e.g., "G,X,L"')
    parser.add_argument('-o', '--output', type=str, default='BSNewOutput',
                        help='Relative output directory where the updated XML files will be saved')
    parser.add_argument('-x', '--xml_template', type=str, required=True,
                        help='The path to the XML template file to be used for generating new XML files')
    parser.add_argument('-j', '--job_directory', type=str, default='./jobs',
                        help='Directory to store job scripts and outputs')
    parser.add_argument('-e', '--executable', type=str, default='/g/data/ad73/codes/NEMO3D_original/NEMO_3D/nemo3d/bin/nemo3d-x86_64_intel20_64_openmpi_gadi.ex',
                        help='Path to the NEMO3D executable')
    parser.add_argument('-f', '--post_process_script', type=str, default='./fmtdat.ex',
                        help='Path to the post-processing script')
    

    # Parse the command line arguments
    args = parser.parse_args()
    return args