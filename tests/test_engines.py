import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
import cv2
from src.enhancers.engines import FastUpscaler, FaceFixUpscaler


class TestUpscalers(unittest.TestCase):
    def setUp(self):
        self.color_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        self.gray_img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)

    def test_fast_upscaler_shape(self):
        upscaler = FastUpscaler(scale=2, sharpness=0.6)
        result = upscaler.process(self.color_img)
        self.assertEqual(result.shape, (200, 200, 3))

    def test_fast_upscaler_sharpness_effect(self):
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        cv2.circle(img, (25, 25), 20, (255, 255, 255), -1)
        upscaler = FastUpscaler(scale=2, sharpness=1.0)
        result = upscaler.process(img)
        self.assertNotEqual(np.sum(result), np.sum(cv2.resize(img, (100, 100), interpolation=cv2.INTER_LANCZOS4)))

    def test_face_fix_upscaler_shape(self):
        upscaler = FaceFixUpscaler(scale=2)
        result = upscaler.process(self.color_img)
        self.assertEqual(result.shape, (200, 200, 3))
        self.assertTrue(np.all(result >= 0) and np.all(result <= 255))

    def test_face_fix_clahe_applied(self):
        dark_img = np.full((100, 100, 3), 30, dtype=np.uint8)
        upscaler = FaceFixUpscaler(scale=2)
        result = upscaler.process(dark_img)
        resized_dark = cv2.resize(dark_img, (200, 200), interpolation=cv2.INTER_CUBIC)
        self.assertGreater(np.mean(result), np.mean(resized_dark))

    def test_scale_parameter(self):
        for scale in [1, 2, 3, 4]:
            upscaler = FastUpscaler(scale=scale)
            result = upscaler.process(self.color_img)
            self.assertEqual(result.shape[0], 100 * scale)
            self.assertEqual(result.shape[1], 100 * scale)

    def test_grayscale_input(self):
        color_img = cv2.cvtColor(self.gray_img, cv2.COLOR_GRAY2BGR)
        upscaler = FastUpscaler(scale=2)
        result = upscaler.process(color_img)
        self.assertEqual(len(result.shape), 3)
        self.assertEqual(result.shape[2], 3)

    def test_empty_frame(self):
        upscaler = FastUpscaler()
        self.assertIsNone(upscaler.process(None))


if __name__ == "__main__":
    unittest.main()