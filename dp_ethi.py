import torch
import numpy as np
import matplotlib.pyplot as plt
#from tkinter import filedialog
from PIL import Image
from transformers import pipeline


def load_image():
    """ファイルダイアログを開き、画像を読み込む"""
    image_path = filedialog.askopenfilename()
    return Image.open(image_path).convert("RGB")

def estimate_depth(image,bbox):
    """画像の深度マップを推定"""
    try:
        normalize = False
        depth_pipeline = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")
        result = depth_pipeline(image)
        depth_map = np.array(result["depth"])
        if normalize:
            depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())  # 0-1正規化
        #print("Depth map successfully estimated")
        # バウンディングボックス内の平均深度を計算
        mean_depths = []
        for b in bbox:
            x1, y1, x2, y2 = b
            depth_map_bbox = depth_map[int(y1):int(y2), int(x1):int(x2)]
            # 外れ値を除外するために、5パーセンタイルと95パーセンタイルの間の値のみを使用
            lower_threshold = np.percentile(depth_map_bbox, 5)
            upper_threshold = np.percentile(depth_map_bbox, 95)
            mask = (depth_map_bbox >= lower_threshold) & (depth_map_bbox <= upper_threshold)
            mean_depth = depth_map_bbox[mask].mean()
            mean_depths.append(mean_depth)

        return depth_map, mean_depths
    
    except Exception as e:
        print(f"Error in depth estimation: {e}")
        raise

def visualize_depth(image, depth_map, bbox):
    """元画像と深度マップを保存"""
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(image)
    plt.title("Original Image")
    plt.axis("off")
    for b in bbox:
        x1, y1, x2, y2 = b
        plt.gca().add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=1, edgecolor="r", facecolor="none"))
    plt.subplot(1, 2, 2)
    plt.imshow(depth_map, cmap="inferno")  # 深度マップをカラーマップで表示
    plt.title("Depth Map")
    plt.axis("off")
    plt.show()

def main():
    """メイン関数"""
    image = load_image()
    depth_map, mean_depths = estimate_depth(image)
    visualize_depth(image, depth_map)

if __name__ == "__main__":
    main()
