import os
import subprocess
import zipfile
import urllib.request

def run_command(command):
    """Subprocess wrapper to run shell commands."""
    result = subprocess.run(command, shell=True, check=True, text=True)
    return result

def clone_repository(repo_url):
    """Clone a Git repository."""
    run_command(f"git clone {repo_url}")

def download_and_extract_zip(url, extract_to):
    """Download and extract a ZIP file."""
    zip_path = os.path.join(extract_to, "repo.zip")
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)

def main():
    repo_url = "https://github.com/yodaka0/ImageExtractWin.git"
    zip_url = "https://github.com/yodaka0/ImageExtractWin/archive/refs/heads/master.zip"
    project_dir = os.path.expanduser("~/ImageExtractWin")

    # Clone the repository
    try:
        clone_repository(repo_url)
    except subprocess.CalledProcessError:
        print("Git clone failed, attempting to download ZIP.")
        download_and_extract_zip(zip_url, os.path.expanduser("~"))

    # Move to project directory
    os.chdir(project_dir)
    print(os.getcwd())

    # Run the make_batch.py script
    try:
        run_command("python make_batch.py")
        run_command("python make_batch_gui.py")
    except subprocess.CalledProcessError:
        print("Warning: make batch file failed.")

    # Create conda environment
    run_command("conda env create -f environment.yml")

    print("Setup completed successfully.")

if __name__ == "__main__":
    main()
