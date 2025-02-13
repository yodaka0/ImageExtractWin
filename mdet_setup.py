import os
import subprocess
import zipfile
import platform
import urllib.request
#import stat
import shutil
try:
    import requests
except ImportError:
    subprocess.run("pip install requests", shell=True, check=True)
    import requests


"""def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)"""

def download_miniconda(installer_url):
    response = requests.get(installer_url, stream=True)
    installer_path = os.path.basename(installer_url)
    with open(installer_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    downloaded_installer_path = os.path.abspath(installer_path)
    print(f"Downloaded Miniconda installer to {downloaded_installer_path}")

    return downloaded_installer_path

def install_miniconda(downloaded_installer_path, abs_conda_path):
    subprocess.run([downloaded_installer_path, '/S'], check=True)
    os.remove(downloaded_installer_path)
    run_command(f"{os.path.join(abs_conda_path, 'conda')} --version")
    print("Miniconda installed successfully")
    

def add_conda_to_path(abs_conda_path):

    current_path = os.environ['PATH']
    if abs_conda_path not in current_path:
        new_path = f"{abs_conda_path};{current_path}"
        subprocess.run(['setx', 'PATH', new_path], check=True)
        os.environ['PATH'] = new_path
        print(f"Added {abs_conda_path} to PATH")

def run_command(command):
    """Subprocess wrapper to run shell commands."""
    result = subprocess.run(command, shell=True, check=True, text=True)
    return result

def create_program_dir(project_dir, github_url):
    repo_url = github_url + "ImageExtractWin.git"
    zip_url = github_url + "ImageExtractWin/archive/refs/heads/gui.zip"

    """Create a directory for the program."""
    # If project directory already exists, check whether to overwrite
    project_dir_path = os.path.expanduser(project_dir)
    print("project directory is {}".format(project_dir_path))
    if os.path.exists(project_dir_path):
        print(f"{project_dir_path} already exists, do you want to overwrite it?")
        overwrite = input("Overwrite? (y/n): ")
        if overwrite.lower() == 'y':
            try:
                shutil.rmtree(project_dir_path)
            except:
                print(f"\033[32mFailed to remove existing directory. You should remove {project_dir_path} manually.\033[0m")
                raise
        else:
            print("Exiting...")
            return
    
    os.makedirs(project_dir_path, exist_ok=True)

    try:
        run_command(f"git clone {repo_url} {project_dir_path}")
    except subprocess.CalledProcessError:
        print("Git clone failed, attempting to download ZIP.")
        download_and_extract_zip(zip_url, project_dir_path)

    print("Repository cloned successfully into {}.".format(project_dir))

def download_and_extract_zip(zip_url, project_dir):
    """Download and extract a ZIP file."""
    zip_path = "ImageExtractWin-gui.zip"
    urllib.request.urlretrieve(zip_url, zip_path)
    # Extract the ZIP file to the program directory
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(project_dir)
    os.remove(zip_path)

def main():
    github_url = "https://github.com/yodaka0/"

    if platform.system() == 'Windows':
        # Change to the user's home directory
        os.chdir(os.path.expanduser("~"))
        print(os.getcwd())

    else:
        print("This script is only supported on Windows. If you are on macOS or Linux, please contact to {}.".format(github_url))
        return

    # if conda hasn't been installed, install it
    try:
        run_command("conda --version")
        print("Conda is already installed")
    except subprocess.CalledProcessError:
        print("Conda is not installed, installing...")
        installer_url = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe'
        
        try:
            downloaded_installer_path = download_miniconda(installer_url)
            abs_conda_path = os.path.abspath("miniconda3/Scripts")
            #print(abs_conda_path)
            install_miniconda(downloaded_installer_path, abs_conda_path)
            add_conda_to_path(abs_conda_path)
        
            run_command("conda --version")
        except:
            print(f"\033[32mFailed to install Miniconda. Please install Miniconda manually from {installer_url}\033[0m")
            raise


    project_dir = "~/ImageExtractWin-v1.2"

    create_program_dir(project_dir, github_url)

    os.chdir(os.path.expanduser(project_dir))

    # Run the make_batch.py script
    try:
        run_command("python make_batch_gui.py")
    except subprocess.CalledProcessError:
        print("Warning: make batch file failed.")

    # Update conda environment. If it doesn't exist, create conda environment
    try:
        # If the environment already exists, update it
        run_command("conda env update -f environment.yml")
    except subprocess.CalledProcessError:
        # If the environment doesn't exist, create it
        print("Environment doesn't exist, creating...")
        run_command("conda env create -f environment.yml")    

    print("Setup completed successfully.")
    run_command("pause")

if __name__ == "__main__":
    main()
