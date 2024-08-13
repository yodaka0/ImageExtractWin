import os
import subprocess
import zipfile
import urllib.request
import platform
try:
    import requests
except ImportError:
    subprocess.run("pip install requests", shell=True, check=True)
    import requests


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

def install_miniconda(installer_path):
    base_installer_path = os.path.basename(installer_path)
    if platform.system() == 'Windows':
        subprocess.run([base_installer_path, '/S'], check=True)
        print("Miniconda installed successfully")
    else:
        subprocess.run(['bash', base_installer_path, '-b', '-p', os.path.expanduser('~/miniconda')], check=True)
    

def add_conda_to_path():
    if platform.system() == 'Windows':
        # Add Miniconda to PATH from 'C:\username\Miniconda\Scripts'
        conda_path = os.path.expanduser('~/miniconda3/Scripts')
        current_path = os.environ['PATH']
        if conda_path not in current_path:
            os.environ['PATH'] = f"{conda_path};{current_path}"
            subprocess.run(['setx', 'PATH', os.environ['PATH']], check=True)
            print(f"Added {conda_path} to PATH")
    else:
        conda_path = os.path.expanduser('~/miniconda/bin')
        shell = os.environ.get('SHELL')
        if shell and 'bash' in shell:
            profile_path = os.path.expanduser('~/.bashrc')
        elif shell and 'zsh' in shell:
            profile_path = os.path.expanduser('~/.zshrc')
        else:
            profile_path = os.path.expanduser('~/.profile')
        
        with open(profile_path, 'a') as file:
            file.write(f'\n# Added by Python script\nexport PATH="{conda_path}:$PATH"\n')
        subprocess.run([shell, '-c', f'source {profile_path}'], check=True)
        print(f"Added {conda_path} to PATH in {profile_path}")


def run_command(command):
    """Subprocess wrapper to run shell commands."""
    result = subprocess.run(command, shell=True, check=True, text=True)
    return result

def clone_repository(repo_url,program_dir):
    """Clone a Git repository."""
    os.makedirs(os.path.expanduser(program_dir), exist_ok=True)
    try:
        # clone branch
        run_command(f"git clone -b gui {repo_url} {program_dir}")
    except subprocess.CalledProcessError:
        run_command(f"git clone {repo_url} {program_dir}")

def download_and_extract_zip(url, extract_to):
    """Download and extract a ZIP file."""
    zip_path = os.path.join(extract_to, "repo.zip")
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)

def main():
    # if conda hasn't been installed, install it
    try:
        run_command("conda --version")
        print("Conda is already installed")
    except subprocess.CalledProcessError:
        print("Conda is not installed, installing...")
        if platform.system() == 'Windows':
            installer_url = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe'
        elif platform.system() == 'Darwin':  # macOS
            installer_url = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh'
        else:  # Linux
            installer_url = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh'

        installer_path = download_miniconda(installer_url)
        install_miniconda(installer_path)
        add_conda_to_path()

        if platform.system() != 'Windows':
            conda_init_cmd = os.path.expanduser('~/miniconda/bin/conda init')
            subprocess.run(['bash', '-c', conda_init_cmd], check=True)
            print("Conda initialized successfully")
        
        run_command("conda --version")

    repo_url = "https://github.com/yodaka0/ImageExtractWin.git"
    zip_url = "https://github.com/yodaka0/ImageExtractWin/archive/refs/heads/gui.zip"
    # project_dir = "C:\\Users\\username\\ImageExtractWin-gui"
    project_dir = "~/ImageExtractWin-gui"

    # Clone the repository and change to the project directory
    try:
        clone_repository(repo_url, project_dir)
    except subprocess.CalledProcessError:
        print("Git clone failed, attempting to download ZIP.")
        download_and_extract_zip(zip_url, os.path.expanduser("~"))
        
    os.chdir(os.path.expanduser(project_dir))
    print(os.getcwd())

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
