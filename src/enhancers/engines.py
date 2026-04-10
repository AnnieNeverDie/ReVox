"""
图像缩放模块
"""
import cv2
import numpy as np
from src.core.logger import logger
class BaseUpscaler:
    def __init__(self, scale=2):
        self.scale = scale
        self.is_ready = True
    def process(self, frame: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class FastUpscaler(BaseUpscaler):
    def __init__(self, scale=2, sharpness=0.5):
        super().__init__(scale)
        self.sharpness = sharpness
        logger.info(f"激活 FastUpscaler: 倍率x{scale}, 锐化系数{sharpness}")
    def process(self, frame):
        if frame is None: return None
        h, w = frame.shape[:2]
        upscaled = cv2.resize(frame, (w * self.scale, h * self.scale), interpolation=cv2.INTER_LANCZOS4)
        if self.sharpness > 0:
            gaussian = cv2.GaussianBlur(upscaled, (0, 0), 3.0)
            upscaled = cv2.addWeighted(upscaled, 1.0 + self.sharpness, gaussian, -self.sharpness, 0)
        return upscaled


class FaceFixUpscaler(BaseUpscaler):
    def __init__(self, scale=2):
        super().__init__(scale)
        self.clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
        logger.info(f"激活 FaceFixUpscaler: 视觉对比度增强开启 (平滑模式)")

    def process(self, frame):
        if frame is None: return None
        upscaled = cv2.resize(frame, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_CUBIC)
        lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l2 = self.clahe.apply(l)
        lab_enhanced = cv2.merge((l2, a, b))
        enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        kernel = np.array([[0, -0.1, 0], [-0.1, 1.4, -0.1], [0, -0.1, 0]])
        return cv2.filter2D(enhanced, -1, kernel)