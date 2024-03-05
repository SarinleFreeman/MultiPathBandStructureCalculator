# job_manager.py
import os
import subprocess
import time

class JobManager:
    def __init__(self, xml_directory, job_directory, executable, post_process_script, combiner_script, combiner_directory):
        self.xml_directory = xml_directory
        self.job_directory = job_directory
        self.executable = executable
        self.post_process_script = post_process_script
        self.combiner_script = combiner_script
        self.combiner_directory = combiner_directory
        self.job_ids = []

    def create_job_script(self, xml_file):
        """Creates and writes a job script for the given XML file."""
        # Check if the job directory exists, create it if not
        os.makedirs(self.job_directory, exist_ok=True)  # This will create the directory if it does not exist

        job_name = os.path.splitext(os.path.basename(xml_file))[0]  # Extract name without extension
        job_script_path = os.path.join(self.job_directory, f"{job_name}.sh")
        nd_ek_ascii_file = xml_file.replace('.xml', '.nd_Ek')  # Expected output from fmtdat
        csv_file = nd_ek_ascii_file.replace('.nd_Ek', '.nd_Ek_ascii')

        with open(job_script_path, 'w') as job_script:
            job_script.write(f"""#!/bin/bash
#PBS -P ad73
#PBS -l walltime=00:30:00
#PBS -q express
#PBS -l mem=100GB
#PBS -l jobfs=100GB
#PBS -l ncpus=1
#PBS -o {self.job_directory}/{job_name}.out
#PBS -e {self.job_directory}/{job_name}.err
#PBS -l storage=gdata/ad73+scratch/ad73
#PBS -N {job_name}
#PBS -M z5329803@ad.unsw.edu.au
#PBS -m ae
#PBS -l software=y_program
#PBS -l wd


module purge
module load pbs
module load intel-compiler/2020.0.166
module load openmpi/4.0.2
module load intel-mkl/2020.0.166

source "/scratch/ad73/sy1090/NEMO/my_venv/bin/activate"

cd $PBS_O_WORKDIR
mpirun -np $PBS_NCPUS "{self.executable}" "{xml_file}"

# Post-processing
{self.post_process_script} -a2 "{nd_ek_ascii_file}"

# Convert ASCII to CSV
python3 csv_ascii_converter.py "{csv_file}"
""")
        return job_script_path

    def submit_jobs(self):
        """Submits a job for each XML file in the specified directory and collects job IDs."""
        for xml_file in os.listdir(self.xml_directory):
            if xml_file.endswith('.xml'):
                full_xml_path = os.path.join(self.xml_directory, xml_file)
                job_script_path = self.create_job_script(full_xml_path)
                print(f"Submitting job for {xml_file}")

                result = subprocess.run(['qsub', job_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                job_id = result.stdout.decode().strip()
                self.job_ids.append(job_id)

    def check_job_status(self, job_id):
        """Checks the status of a job given its job ID."""
        try:
            output = subprocess.check_output(['qstat', job_id]).decode('utf-8')
            if ' C ' in output:  # Assuming ' C ' indicates a completed job in qstat output
                return 'completed'
            else:
                return 'running'
        except subprocess.CalledProcessError:
            # If 'qstat' fails, assume the job is no longer listed and thus completed
            return 'completed'

    def track_jobs(self):
        """Tracks the submitted jobs until all have completed."""
        all_completed = False
        while not all_completed:
            all_completed = True  # Assume all jobs are completed, prove otherwise below
            for job_id in self.job_ids:
                status = self.check_job_status(job_id)
                if status != 'completed':
                    all_completed = False
                    break  # Exit the loop early as we found a job that's not completed
            if not all_completed:
                print("Waiting for jobs to complete...")
                time.sleep(60)  # Check again in 60 seconds

    def track_and_combine_jobs(self):
        """Tracks the submitted jobs and combines them after completion."""
        if self.job_ids:
            print("Tracking job status...")
            self.track_jobs()  # Track jobs until completion
            print("All jobs completed. Running the combiner script.")
            os.system(f'python {self.combiner_script} -dir {self.combiner_directory}')
        else:
            print("No jobs were submitted, so no tracking or combining is necessary.")

    def manage_jobs(self):
        """Manages the full lifecycle of job submission, tracking, and combining."""
        self.submit_jobs()
        self.track_and_combine_jobs()
