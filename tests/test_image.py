import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import cv2
import numpy as np
import tempfile
from src.utils.image_utils import resize_and_pad, auto_crop_face


class TestImageUtils(unittest.TestCase):
    def setUp(self):
        self.test_img = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
        self.output_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        random_img = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
        cv2.imwrite(self.test_img, random_img)

    def tearDown(self):
        for f in [self.test_img, self.output_img]:
            if os.path.exists(f):
                os.remove(f)

    def test_resize_padding(self):
        print("\n测试图片缩放与填充...")
        out = resize_and_pad(self.test_img, self.output_img, target_size=(512, 512))
        self.assertTrue(os.path.exists(out))
        img = cv2.imread(out)
        self.assertEqual(img.shape[0], 512)
        self.assertEqual(img.shape[1], 512)
        print(f"图片标准化成功: 800x600 -> {img.shape[1]}x{img.shape[0]}")

    def test_auto_crop_face(self):
        out = auto_crop_face(self.test_img, self.output_img)
        self.assertTrue(os.path.exists(out))
        img = cv2.imread(out)
        self.assertEqual(img.shape[0], img.shape[1])

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            resize_and_pad("nonexistent.jpg", self.output_img)


if __name__ == '__main__':
    unittest.main()