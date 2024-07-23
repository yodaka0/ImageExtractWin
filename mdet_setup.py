import os
import subprocess
import zipfile
import urllib.request

def run_command(command):
    """Subprocess wrapper to run shell commands."""
    result = subprocess.run(command, shell=True, executable='/bin/bash', check=True, text=True)
    return result

def clone_repository(repo_url, dest_dir):
    """Clone a Git repository."""
    run_command(f"git clone {repo_url} {dest_dir}")

def download_and_extract_zip(url, extract_to):
    """Download and extract a ZIP file."""
    zip_path = os.path.join(extract_to, "repo.zip")
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)

def setup_conda_environment(env_file):
    """Create a conda environment from an environment.yml file."""
    run_command(f"conda env create -f {env_file}")

def main():
    repo_url = "https://github.com/yodaka0/ImageExtractWin.git"
    zip_url = "https://github.com/yodaka0/ImageExtractWin/archive/refs/heads/master.zip"
    project_dir = os.path.expanduser("~/ImageExtractWin")

    # Clone the repository
    try:
        clone_repository(repo_url, project_dir)
    except subprocess.CalledProcessError:
        print("Git clone failed, attempting to download ZIP.")
        download_and_extract_zip(zip_url, os.path.expanduser("~"))

    # Move to project directory
    os.chdir(project_dir)

    # Run the make_batch.py script
    run_command("python make_batch.py")
    run_command("python make_batch_s.py")

    # Create conda environment
    setup_conda_environment("environment.yml")

    print("Setup completed successfully.")

if __name__ == "__main__":
    main()
