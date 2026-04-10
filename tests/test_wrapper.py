import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import shutil
from src.sadtalker_wrapper import run_sadtalker
from src.core.config_manager import ConfigManager
from src.core.exceptions import DependencyError, MediaProcessError


class TestSadTalkerWrapper(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.source_image = os.path.join(self.test_dir, "face.png")
        with open(self.source_image, 'wb') as f:
            f.write(b'fake png content')
        self.driven_audio = os.path.join(self.test_dir, "audio.wav")
        with open(self.driven_audio, 'wb') as f:
            f.write(b'fake wav content')
        self.sadtalker_root = os.path.join(self.test_dir, "SadTalker")
        os.makedirs(self.sadtalker_root, exist_ok=True)
        with open(os.path.join(self.sadtalker_root, "inference.py"), 'w') as f:
            f.write("# dummy")
        self.config = ConfigManager()
        self.config.set("paths.sadtalker_path", self.sadtalker_root)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch("subprocess.run")
    @patch("glob.glob")
    def test_run_sadtalker_success(self, mock_glob, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")
        fake_video = os.path.join(self.test_dir, "temp_sadtalker", "result.mp4")
        os.makedirs(os.path.dirname(fake_video), exist_ok=True)
        with open(fake_video, 'wb') as f:
            f.write(b'fake video')
        mock_glob.return_value = [fake_video]

        result = run_sadtalker(self.source_image, self.driven_audio, self.config)
        self.assertEqual(result, fake_video)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_sadtalker_no_video(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        with patch("glob.glob", return_value=[]):
            with self.assertRaises(MediaProcessError):
                run_sadtalker(self.source_image, self.driven_audio, self.config)

    def test_run_sadtalker_missing_path(self):
        self.config.set("paths.sadtalker_path", "/nonexistent")
        with self.assertRaises(DependencyError):
            run_sadtalker(self.source_image, self.driven_audio, self.config)

    def test_run_sadtalker_invalid_image(self):
        with self.assertRaises(ValueError):
            run_sadtalker("nonexistent.png", self.driven_audio, self.config)


if __name__ == "__main__":
    unittest.main()