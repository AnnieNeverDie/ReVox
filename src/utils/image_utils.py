"""
图像通用模块
"""
import cv2
import numpy as np
from src.core.logger import logger
def resize_and_pad(image_path, output_path, target_size=(512, 512)):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法读取图片: {image_path}")
    h, w = img.shape[:2]
    scale = min(target_size[0] / w, target_size[1] / h)
    nw, nh = int(w * scale), int(h * scale)
    img_resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_CUBIC)
    canvas = np.full((target_size[1], target_size[0], 3), 128, dtype=np.uint8)
    dx, dy = (target_size[0] - nw) // 2, (target_size[1] - nh) // 2
    canvas[dy:dy + nh, dx:dx + nw] = img_resized
    cv2.imwrite(output_path, canvas)
    return output_path

def auto_crop_face(image_path, output_path):
    img = cv2.imread(image_path)
    if img is None:
        return resize_and_pad(image_path, output_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0:
        logger.warning("未检测到显著人脸，正在使用全景缩放。")
        return resize_and_pad(image_path, output_path)
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    p_w, p_h = int(w * 0.5), int(h * 0.5)
    x1, y1 = max(0, x - p_w), max(0, y - p_h)
    x2, y2 = min(img.shape[1], x + w + p_w), min(img.shape[0], y + h + p_h)
    cv2.imwrite(output_path, img[y1:y2, x1:x2])
    return resize_and_pad(output_path, output_path)
