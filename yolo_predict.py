import cv2
from ultralytics import YOLO
import numpy as np

class yolo_class():
    def __init__(self,yolo_path):
        self.yolo_path = yolo_path
        # model = YOLO("yolov8n-cls.pt")  # load an official model
        self.model = YOLO(yolo_path)  # load a custom model

    def YoloDetect(self,imgs):
        # Load a model
        # Predict with the model
        results = self.model(imgs)  # predict on an image
        # print(results)
        return results

    def FindMaxContours_For_torxtamperproof(self, contours, size=100):
        try:
            # 計算輪廓面積
            area = [cv2.contourArea(contour) for contour in contours]
            # 找到前三大的面積的索引
            max_indices = np.argsort(np.array(area))[::-1][:3]
            # 取得前三大的輪廓
            max_contours = [contours[i] for i in max_indices if cv2.contourArea(contours[i]) > 100]
            # 計算每個輪廓的重心
            centroids = []
            for contour in max_contours:
                moments = cv2.moments(contour)
                # 檢查面積是否為非零值，避免除以零的情況
                if moments["m00"] != 0:
                    cx = moments["m10"] / moments["m00"]
                    cy = moments["m01"] / moments["m00"]
                    centroids.append(np.array([cx, cy]))
            # 計算每個輪廓的重心距離影像中心的距離
            center = np.array([size / 2, size / 2])  # 替換成你的影像寬高
            distances = [np.linalg.norm(centroid - center) for centroid in centroids]
            # 找到最近的輪廓索引
            closest_idx = np.argmin(np.array(distances))
            # 找到最近的輪廓在前三大輪廓中的索引
            final_idx = max_indices[closest_idx]
        except Exception as e:
            # self.dev_logger.error(f'FindMaxContours_For_torxtamperproof {e}')
            final_idx = -1
            print(f'FindMaxContours_For_torxtamperproof --> {e}')
        return final_idx

if __name__ == '__main__':
    yolo = yolo_class(r"F:\weights\best.pt")
    image = cv2.imread(r"D:\Screwdriver_image\predict\01.png", cv2.IMREAD_GRAYSCALE)

    print(f"yolo.YoloDetect(image)[0].probs = {yolo.YoloDetect(image)[0].probs.top1}") #抓到的第一個類別
