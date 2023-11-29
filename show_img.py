import cv2
from matplotlib import pyplot as plt

img_path="C:\\Users\\tomoyakanno\\Documents\\nullremove\\ogawa.2020.12\\21pre\\10030021.JPG"
img = cv2.imread(img_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # OpenCVはBGR形式で画像を読み込むため、RGB形式に変換します。

plt.imshow(img)
plt.show()