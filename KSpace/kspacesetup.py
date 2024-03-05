import xml.etree.ElementTree as ET
import os
import argparse
import json

class KSpaceSetup:
    """
    This class represents the setup for k-space path calculations.
    It allows for the conversion of symbolic representations of k-space paths into actual k-values.
    """
    def __init__(self,symmetry_points:dict):
        """
        :param symmetry_points: A dictionary mapping symbolic values to their coordinate representation.
        """
        self.symmetry_points = symmetry_points

    def convert_path_to_k_values(self,path):
        """
        Convert a symbolic path to its corresponding k values using the predefined symmetry points.

        :param path: A list of symbols representing the path in k-space.
        :return: A list of tuples with the k values for each point in the path.
        """
        k_path = []
        for symbol in path:
            if symbol in self.symmetry_points:
                k_path.append(self.symmetry_points[symbol])
            else:
                print(f"Symbol {symbol} not recognized. Skipping.")
        return k_path

    def symbolic_path_to_k_pairs(self,symbolic_path):
        """
        Convert a list of symbolic path points to a list of k-value pairs representing consecutive points in the path.

        :param symbolic_path: A list of symbols representing the path in k-space.
        :return: A list of tuples, where each tuple contains two tuples representing
                 the initial and final k-vectors (kx, ky, kz) for each segment of the path.
        """
        # Convert the symbolic path to a list of k-values
        k_values_path = self.convert_path_to_k_values(symbolic_path)

        # Generate pairs of initial and final k-vectors
        return [(k_values_path[i], k_values_path[i + 1]) for i in range(len(k_values_path) - 1)]

def pull_name(xml_file_path):
    """
    Extracts the type of base material from the 'ShapeName_1' group in an XML file.
    Raises an error if the 'ShapeName_1' group or material name is not found.

    :param xml_file_path: Path to the XML file to parse.
    :return: The extracted material type as a string.
    :raises: ValueError if the 'ShapeName_1' group or material type is not found.
    """
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Specifically find the 'ShapeName_1' group
    shape_name = root.find(".//group[@type='obj'][name='ShapeName_1']")
    if shape_name is not None:
        for param in shape_name.findall(".//param"):
            cTag = param.find('cTag')
            if cTag is not None and cTag.text == 'mat':
                value = param.find('value')
                if value is not None:
                    # Extract and return the material type, stripping curly braces and spaces
                    material_type = value.text.strip('{} ').split()[0]
                    return material_type
        else:
            raise ValueError("Failed to find 'mat' object")


def update_k_vectors(xml_file_path, paths, output_folder, symbolic_path):
    """
    Update the initial and final k-vectors in an XML file based on provided paths and save the updated XML
    in a specified folder with a filename that reflects the path. Additionally, save a JSON file with
    information about the path taken in both symbolic and coordinate representations.
    
    :param xml_file_path: The path to the original XML file.
    :param paths: A list of tuples, each containing the initial and final k-vectors.
    :param output_folder: The directory where the updated XML files and args.json will be saved.
    :param symbolic_path: The symbolic representation of the path taken.
    """
    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)
    base_file_name = os.path.splitext(os.path.basename(xml_file_path))[0]

    # Store information about path
    path_info = {
        "title": pull_name(xml_file_path),
        "symbolic_path": symbolic_path,
        "coordinate_representation": [list(pair) for segment in paths for pair in segment]  # Flatten and convert tuples to lists
    }

    # Write the JSON file
    json_file_path = os.path.join(output_folder, "args.json")
    with open(json_file_path, 'w') as json_file:
        json.dump(path_info, json_file, indent=4)
    print(f"Path information saved to {json_file_path}")

    for i, (initial_k, final_k) in enumerate(paths):
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Iterate over all param elements to find the ones related to k-vectors
        for param in root.findall(".//param"):
            cTag = param.find("./cTag")
            if cTag is not None and cTag.text == 'k0':
                # Update the initial k-vector
                param.find("./value").text = f"{{ {' '.join(map(str, initial_k))} }}"
            elif cTag is not None and cTag.text == 'kf':
                # Update the final k-vector
                param.find("./value").text = f"{{ {' '.join(map(str, final_k))} }}"

        # Construct the output filename
        path_str = "to".join(["_".join(map(str, initial_k)), "_".join(map(str, final_k))])
        output_file_name = f"{base_file_name}_{path_str}.xml"
        output_file_path = os.path.join(output_folder, output_file_name)

        # Save the modified XML to the new file
        tree.write(output_file_path)
        print(f"File saved: {output_file_path}")


