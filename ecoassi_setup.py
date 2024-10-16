import os
import platform
import subprocess
import urllib.request

def run_command(command):
    """Run a shell command."""
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode()

def main():

    if platform.system() == 'Windows':
        # Change to the user's home directory
        os.chdir(os.path.expanduser("~"))
        print(os.getcwd())

    else:
        print("This script is only supported on Windows.")
        return

    # if miniforge hasn't been installed, install it
    if os.path.exists(os.path.join(os.path.expanduser("~"), "Miniforge3")):
        print("Miniforge is already installed")
    else:
        try:
            miniforge_installer_url = "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe"
            installer_path = os.path.basename(miniforge_installer_url)
            urllib.request.urlretrieve(miniforge_installer_url, installer_path)
            run_command(installer_path + " /S")
            os.remove(installer_path)
            print("Miniforge installed successfully")
        except subprocess.CalledProcessError:
            print("\033[32mMiniforge installation failed. Please install Miniforge manually from {}\033[0m".format(miniforge_installer_url))
            raise
        
    # if git hasn't been installed, install it
    try:
        run_command("git --version")
        print("Git is already installed")
    except subprocess.CalledProcessError:
        print("Git is not installed, installing...")
        git_installer_url = 'https://github.com/git-for-windows/git/releases/download/v2.46.0.windows.1/Git-2.46.0-64-bit.exe'
        git_installer_path = os.path.basename(git_installer_url)
        try:
            urllib.request.urlretrieve(git_installer_url, git_installer_path)
            run_command(git_installer_path + " /S")
            os.remove(git_installer_path)
            run_command("git --version")
        except:
            print(f"\033[32mFailed to install Git. Please install Git manually from {git_installer_url}\033[0m")
            raise


    #Install Ecoassist
    ecoassist_installer_url = "https://petervanlunteren.github.io/EcoAssist/install.bat"
    ecoassist_installer_path = os.path.basename(ecoassist_installer_url)
    try:
        urllib.request.urlretrieve(ecoassist_installer_url, ecoassist_installer_path)
        run_command(ecoassist_installer_path + " /S")
        os.remove(ecoassist_installer_path)
        print("ecoassist installed successfully")
    except subprocess.CalledProcessError:
        print("\033[32mecoassist installation failed. Please install ecoassist manually from {}\033[0m".format(ecoassist_installer_url))
        raise



if __name__ == "__main__":
    main()