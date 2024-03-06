# MultiPath Band Structure Calculator (MPBCalc)

The MPBCalC tool streamlines semiconductor band structure analysis, generating necessary simulation files for exploring critical Brillouin points using the NEMO3D atomistic tight-binding software. The tool provides post-processing capabilities, including effective mass calculations, bandstructure characteristics identifications and bandstructure visualization.

## File Structure
```
├── Job
│ └── job_manager.py
├── KSpace
│ └── kspacesetup.py
├── PostProcessing
│ ├── combination_csv_plotter.py
│ └── eff_mass_calculator.py
├── TemplateFiles
│ ├── IndiumAntimony.xml
│ ├── IndiumArsenide.xml
│ ├── galliumArsenide.xml
│ ├── germanium.xml
│ └── silicon.xml
├── User
│ └── parser.py
├── csv_ascii_converter.py
├── csv_combiner.py
├── main.py
└── requirements.txt
```

## Getting Started

To begin using MPBCalc, please follow these steps:

1. **Install Python**: Ensure you have Python 3.10 or newer installed on your system. You can download it from [Python's official website](https://www.python.org/downloads/).

2. **Acquire NEMO3D Software**: MPBCalc is designed to work with the NEMO3D tight-binding simulation software. Information regarding access and usage of NEMO3D can be found [here](https://engineering.purdue.edu/gekcogrp/software-projects/nemo3D/).

3. **Setup for PBS System**: MPBCalc utilises the PBS job scheduler, usage with other systems will require modification of job_manager.py file.

4. **Install Dependencies**: Navigate to the root directory of MPBCalc and install the required Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Running Jobs with MPBCalc

MPBCalc requires the following input arguments:

- **`--path PATH`**: Specifies a comma-separated sequence of k-space points, such as `"G,X,L"`. These represent critical points within the [Brillouin zone](https://en.wikipedia.org/wiki/Brillouin_zone), with current supported points including:
    - `Γ`: (0, 0, 0)
    - `X`: (0, 2, 0)
    - `L`: (1, 1, 1)
    - `W`: (1, 2, 0)
    - `U`: (0.5, 2, 0.5)
    - `K`: (1.5, 1.5, 0)
    
    *Note: The values assume 2π/a = 1 for simplicity, where 'a' is the lattice constant.*

- **`--output OUTPUT`**: Sets the relative directory for saving XML files and job scripts, tailored for each critical point.

- **`--xml_template XML_TEMPLATE`**: Directory to base XML template file. This template is used to generate specific XML files for each k-space path.

- **`--job_directory JOB_DIRECTORY`**: Identifies the directory for storing job scripts and output files.

- **`--executable EXECUTABLE`**: Defines the path to the NEMO3D executable used for running simulations.

- **`--post_process_script POST_PROCESS_SCRIPT`**: Provides the path to the script responsible for converting NEMO3D binary results into ASCII format.

### Example Usage

Here is an example command that demonstrates the typical usage of MPBCalc, utilizing default values where applicable:

```bash
python main.py --path G,X,L --xml_template TemplateFiles/silicon.xml --output OutputDirectory --job_directory JobScripts --executable nemo3d.exe --post_process_script converter.exe
```

In this example:
- The `--path` is set to `G,X,L`, indicating a path through the Gamma, X, and L points in k-space.
- `--xml_template` is pointing to a template XML file within the `TemplateFiles` directory.
- Output files and job scripts will be saved in `OutputDirectory`.
- PBS Job scripts and related output will be stored in `JobScripts`.
- NEMO3D simulations will run using the executable provided via `--executable`.
- The post-processing script is set with `--post_process_script`.

## Simulation Outputs
The MPBCalc simulation outputs are stored in the user-defined output directory. The key outputs are:

### Primary Outputs:

- **Individual CSV Files**: These files encapsulate the bandstructure between two critical points, the files are formatted as "base-name_point1_to_point2" e.g `IndiumAntimony_0_2_0to0.5_2_0.5.csv`. The files contain tabulated energy values against wave vectors (`kx, ky, kz`).
  
  ```
  kx,ky,kz,E
  0.0,0.0,0.0,-11.435075688020001
  ```

- **Combined CSV File**: Aggregated data across critical point paths, Includes segment points to denote path starts and ends.

  ```
  kx,ky,kz,E,Segment_Point
  0.0,0.0,0.0,-11.435075688020001,"(0, 0, 0)"
  ```

### Supporting Files:
- **Energy Dispersion Files (`args.json`)**: Stores user-defined path information, e.g ```{
    "title": "Si",
    "symbolic_path": [
        "\u0393",
        "L"
    ],
    "coordinate_representation": [
        [
            0,
            0,
            0
        ],
        [
            1,
            1,
            1
        ]
    ]
}```
- **Energy Dispersion Files (`*nd_Ek`)**: Stores energy (`E`) versus wave vector (`k`) values for segments of the path in binary.

- **ASCII Energy Dispersion Files (`*nd_Ek_ascii`)**: Energy Dispersion Files in ascii format.

- **Neighbor Index Files (`*nd_nbrIndx`)**: Detail the indices of neighboring atoms, relevant for understanding atomic interactions and lattice structure.

- **Phase Information Files (`*nd_phaseInfo`)**: Contain phase-related data for phase analysis in band structure studies.

- **Lattice Iteration Files (`*nd_lattice_iter`)**: Document details from iterations over the lattice calculations, useful for troubleshooting and understanding calculation progression.

- **Time Detail Files (`*nd_time_detail`)**: Offer insights into the time taken for various calculation stages, assisting in performance analysis.

- **XML Parse Files (`*nd_xmlparse`)**: Result from parsing the input XML configuration, providing a log that can be useful for debugging.

- **Template XML Files (`*xml`)**: The source XML files used for each simulation, capturing the simulation setup and parameters.


## Job Outputs

Post-job execution, MPBCalc generates several files in the job directory for monitoring and debugging:

- **Job Scripts (`*.sh`)**: Batch scripts executed by the scheduler, e.g., `silicon_0_0_0to1_1_1.sh`.

- **Standard Output (`*.out`)**: Execution logs and NEMO3D outputs, such as `silicon_0_0_0to1_1_1.out`.

- **Standard Error (`*.err`)**: Error messages from the simulation, for example, `silicon_0_0_0to1_1_1.err`.

Review these files to assess job execution and address potential issues.


## Bandstructure Viewer Post Processing

