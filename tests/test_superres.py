import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import tempfile
import cv2
import numpy as np
from src.enhancers.superres import run_video_upscale
from src.core.config_manager import ConfigManager
from src.core.exceptions import MediaProcessError


class TestSuperRes(unittest.TestCase):
    def setUp(self):
        self.test_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        self.output_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        self.config = ConfigManager()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.test_video, fourcc, 10.0, (64, 64))
        for _ in range(10):
            frame = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

    def tearDown(self):
        for f in [self.test_video, self.output_video]:
            if os.path.exists(f):
                os.remove(f)

    def test_fast_upscale(self):
        result = run_video_upscale(self.test_video, self.output_video, self.config, method="fast")
        self.assertTrue(os.path.exists(result))
        cap = cv2.VideoCapture(result)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        self.assertEqual(width, 128)   # 64 * 2
        self.assertEqual(height, 128)

    def test_face_fix_upscale(self):
        result = run_video_upscale(self.test_video, self.output_video, self.config, method="face_fix")
        self.assertTrue(os.path.exists(result))
        cap = cv2.VideoCapture(result)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap.release()
        self.assertEqual(width, 128)

    def test_invalid_input(self):
        with self.assertRaises(MediaProcessError):
            run_video_upscale("nonexistent.mp4", self.output_video, self.config)

    def test_scale_from_config(self):
        self.config.set("enhancements.scale", 3)
        result = run_video_upscale(self.test_video, self.output_video, self.config, method="fast")
        cap = cv2.VideoCapture(result)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap.release()
        self.assertEqual(width, 192)   # 64 * 3


if __name__ == "__main__":
    unittest.main()