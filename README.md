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

### Key Outputs:

- **Critical Point CSV Files**: These files encapsulate the bandstructure between two critical points, the files are formatted as "base-name_point1_to_point2" e.g `IndiumAntimony_0_2_0to0.5_2_0.5.csv`. The files contain tabulated energy values against wave vectors (`kx, ky, kz`). An example snippet:
  
  ```
  kx,ky,kz,E
  0.0,0.0,0.0,-11.435075688020001
  ```

- **Combined CSV**: Aggregated data across critical point paths, Includes segment points to denote path starts and ends. Example format:

  ```
  kx,ky,kz,E,Segment_Point
  0.0,0.0,0.0,-11.435075688020001,"(0, 0, 0)"
  ```

### Additional Files:

- **Energy Dispersion (`*Ek`)**: Contains E vs k values, formatted as `<kx ky kz Energy>`.

- **Eigen-vectors (`*evec_i`)**: Correspond to each energy level detailed in the `*Ek` files, formatted as `<real complex>`, representing the real and complex parts of Eigen-vectors.

- **Wave Functions (`*wf_i`)**: One per energy level, detailing the wave function’s squared magnitude, `< |ψ|2 >`.

- **Local Band Structure (`*Ek_proc_*`)**: Local band edge data for subdomains, one file per processor.

- **Trace of Eigen-values (`*eval`)**: Iteration versus Eigen-value data from the Lanczos Eigen-solver.

- **Optical Matrix Elements (`*TransX/Y/Z`)**: Contains optical transition rates for different light polarizations, formatted as `<energy_state_i energy_state_f energy_gap transition_rate>`.

- **Atom Position Files (`*rAtom_0/1`)**: Pre- and post-strain atom positions in Cartesian coordinates.

- **Atom Type Files (`*aType`)**: Types of atoms present, represented by ASCII numbers.

- **Neighbor Index Files (`*nbrIndx`)**: Information about the four nearest neighbors for each atom, aligning with the atom positions in the `rAtom` file.

### Example Command

To generate the outputs as described, use the following command with default values:

```bash
python main.py --path G,X,L --xml_template TemplateFiles/silicon.xml --output OutputDirectory --job_directory JobScripts --executable /path/to/nemo3d --post_process_script /path/to/post_process_script
```

This command instructs MPBCalc to perform simulations along the Γ-X-L path in k-space, using the provided silicon XML template and saving results to `OutputDirectory`.

---

Adapt and expand upon these sections as necessary to match your project's output structure and analysis capabilities.



Example of running a job:

bash
Copy code
python main.py --path G,X,L --xml_template TemplateFiles/silicon.xml --output OutputDirectory
This command sets up the environment for simulating the electronic band structure along the Γ-X-L path for silicon, using the silicon.xml template, and saving the outputs to OutputDirectory.
