# MultiPath Band Structure Calculator (MPBCalc)

The MPBCalC tool streamlines semiconductor band structure analysis, generating necessary simulation files for exploring critical Brillouin points using the NEMO3D atomistic tight-binding software. The tool provides post-processing capabilities, including effective mass calculations, bandstructure characteristics identifications and bandstructure visualization.

### File Structure
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

1. **Install Python**: Ensure you have Python 3.7 or newer installed on your system. You can download it from [Python's official website](https://www.python.org/downloads/).

2. **Acquire NEMO3D Software**: MPBCalc is designed to work with the NEMO3D tight-binding simulation software. Information regarding access and usage of NEMO3D can be found (here)[https://engineering.purdue.edu/gekcogrp/software-projects/nemo3D/].

3. **Setup for PBS System**: MPBCalc utilises the PBS job scheduler, usage with other systems required modification of job_manager.py file.

4. **Install Dependencies**: Navigate to the root directory of MPBCalc and install the required Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

