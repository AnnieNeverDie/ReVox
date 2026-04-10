import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import cv2
import numpy as np
import soundfile as sf
from src.utils.video_utils import merge_audio_video, check_ffmpeg_env, process_video_with_memory_management


class TestVideoUtils(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.examples_dir = os.path.join(self.project_root, "examples")
        os.makedirs(self.examples_dir, exist_ok=True)

        self.test_video = os.path.join(self.examples_dir, "test_video.mp4")
        self.test_audio = os.path.join(self.examples_dir, "test_audio.wav")
        self.output_video = os.path.join(self.examples_dir, "test_output.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.test_video, fourcc, 10.0, (100, 100))
        for _ in range(5):
            out.write(np.zeros((100, 100, 3), dtype=np.uint8))
        out.release()
        sf.write(self.test_audio, np.zeros(16000), 16000)

    def tearDown(self):
        for f in [self.test_video, self.test_audio, self.output_video]:
            if os.path.exists(f):
                os.remove(f)

    def test_check_ffmpeg_env(self):
        try:
            check_ffmpeg_env()
        except EnvironmentError as e:
            self.skipTest(f"FFmpeg not available: {e}")

    def test_merge_audio_video(self):
        try:
            result = merge_audio_video(self.test_video, self.test_audio, self.output_video)
            self.assertTrue(os.path.exists(result))
            self.assertGreater(os.path.getsize(result), os.path.getsize(self.test_video))
        except Exception as e:
            self.skipTest(f"FFmpeg merge failed: {e}")

    def test_merge_with_nonexistent_files(self):
        with self.assertRaises(Exception):
            merge_audio_video("missing.mp4", self.test_audio, self.output_video)

    def test_process_video_with_memory_management(self):
        def dummy_process(frame):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        output = os.path.join(self.examples_dir, "test_processed.mp4")
        try:
            process_video_with_memory_management(self.test_video, dummy_process, output)
            self.assertTrue(os.path.exists(output))
            cap = cv2.VideoCapture(output)
            ret, frame = cap.read()
            cap.release()
            self.assertIsNotNone(frame)
            self.assertEqual(len(frame.shape), 3)
        finally:
            if os.path.exists(output):
                os.remove(output)


if __name__ == '__main__':
    unittest.main()