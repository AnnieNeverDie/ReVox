import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import cv2
import numpy as np
from src.utils.info_utils import get_video_info, print_video_info


class TestInfoUtils(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.examples_dir = os.path.join(self.project_root, "examples")
        os.makedirs(self.examples_dir, exist_ok=True)
        self.test_video = os.path.join(self.examples_dir, "test_video.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.test_video, fourcc, 25.0, (192, 108))
        for _ in range(50):
            out.write(np.zeros((108, 192, 3), dtype=np.uint8))
        out.release()

    def tearDown(self):
        if os.path.exists(self.test_video):
            os.remove(self.test_video)

    def test_get_video_info(self):
        info = get_video_info(self.test_video)
        self.assertIsNotNone(info)
        self.assertEqual(info['width'], 192)
        self.assertEqual(info['height'], 108)
        self.assertAlmostEqual(info['fps'], 25.0, places=1)
        self.assertEqual(info['frame_count'], 50)
        self.assertAlmostEqual(info['duration'], 2.0, places=1)
        self.assertGreater(info['file_size_bytes'], 0)
        self.assertIn('duration_formatted', info)

    def test_get_video_info_nonexistent(self):
        info = get_video_info("nonexistent.mp4")
        self.assertIsNone(info)

    def test_print_video_info(self):
        try:
            print_video_info(self.test_video)
        except Exception as e:
            self.fail(f"print_video_info raised {e}")


if __name__ == "__main__":
    unittest.main()