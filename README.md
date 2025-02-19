# ImageExtractWin

## What's this：このプログラムについて

This program aims to detect wildlife from camera trap images using [MegaDetector (Beery et al. 2019)](https://github.com/microsoft/CameraTraps) and to extract images in which animals were detected. This document is a minimal description and will be updated as needed.  
このプログラムは、[MegaDetector (Beery et al. 2019)](https://github.com/microsoft/CameraTraps)を利用してカメラトラップ映像から野生動物を検出し、動物が検出された画像を抽出することを目的として作成されました。このドキュメントは現時点では最低限の記述しかされていないため、今後随時更新していく予定です。

![10100043](https://github.com/yodaka0/ImageExtractWin/assets/38493521/c7bac078-706d-4b13-9dbb-20ae96b971f2)


---

## Get Started：はじめに

<br />

### Prerequisites：環境整備

* OS  
    The following code was tested on Windows 10 Pro.  
    During the test run, .jpg as the image file format.  
    以下のコードはWindows 10 Proで動作確認しています。  
    動作確認時、静止画ファイル形式は.jpgを用いました。

* NVIDIA Driver(if you use gpu)
    NVIDAドライバーをインストールする

    Please refer to [NVIDIA Driver Version Check](https://www.nvidia.com/Download/index.aspx?lang=en-us).
    *** is a placeholder. Please enter the recommended nvidia driver version.  
    [NVIDIAドライババージョンチェック](https://www.nvidia.com/Download/index.aspx?lang=en-us)を参照し、***に推奨されるnvidiaドライババージョンを入力した上で実行してください。  

    Check installation.  
    インストール状況の確認。

    ```commandprompt
    nvidia-smi 
    # NVIDIA Driver installation check
    ```

    If nvidia-smi does not work, Try Rebooting.  
    nvidia-smiコマンドが動作しない場合は再起動してみてください。


<br />

### Instllation：インストール

0. Auto Installation
    download mdet_setup.py
   
    ```commandprompt
    python mdet_setup.py
    ```
    If auto installation fail, run berow step.

OR

1. Clone the Repository：リポジトリの複製

    Run ```git clone```,  
    ```git clone```を実行する


    or Download ZIP and Unzip in any directory of yours. The following codes are assumed that it was extracted to the user's home directory (`/home/${USER}/`).  
    もしくはZIPをダウンロードし、任意のディレクトリで解凍してください。なお、このページではユーザのホームディレクトリ（`/home/${USER}/`）に解凍した前提でスクリプトを記載しています。

2. Move Project Directory：プロジェクトディレクトリへ移動

    ```commandprompt
    cd {ImageExtractWinのパス}
   例
    cd project\ImageExtractWin-master
    python make_batch_gui.py
    ```
3. install miniconda(anaconda) : miniconda(anaconda)をインストール

    https://docs.conda.io/projects/miniconda/en/latest/

    condaのパスを通す
    Pass through the path of conda
    システム環境変数の編集->環境変数->PATH->新規->condaのpathをコピペ(例　C:\Users\{ユーザー名}\miniconda3\condabin)
    Edit System Environment Variables->Environment Variables->PATH->New->copy and paste the path for conda (e.g. C:\Users\{user name}\miniconda3\condabin)
   
5. create conda environment：conda環境の構築

    ```commandprompt
    conda env create -f environment.yml
    ```
    
6. If you use gpu, visit the following site and install the matching version
   gpuを使う場合、以下のサイトを見てバージョンを合わせたものをインストールする
   
    CUDA Toolkit 12.3 Downloads
    https://developer.nvidia.com/cuda-downloads 

    Installation of cudnn (login required)
    cudnnのインストール(ログインが必要)
    https://developer.nvidia.com/rdp/cudnn-download

   ```commandprompt
    pip uninstall torch torchvision torchaudio
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ```
  
<br />



---

## Usage：使い方

<br />
Click on the Detect_gui shortcut on the Desktop
デスクトップにあるDetect_guiのショートカットをクリックする

Select a folder with images in browse, and click
browseで画像があるフォルダを選択,

Select detection model,.
検出モデルの選択,

Start 
開始

threshold:検出の閾値 ;
skip:既にファイルがある場合スキップする ;
differential reasoning:前の画像と同じ位置のanimalの検出をblankに変換する


 



