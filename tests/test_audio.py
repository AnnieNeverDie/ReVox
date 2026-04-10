import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import soundfile as sf
import numpy as np
import tempfile
from src.utils.audio_utils import preprocess_audio, get_audio_duration
from src.enhancers.denoise import process_audio
from src.core.exceptions import ValidationError, MediaProcessError


class TestAudioPipeline(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        self.sample_rate = 44100
        t = np.linspace(0, 1, self.sample_rate)
        signal = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.1 * np.random.randn(self.sample_rate)
        sf.write(self.test_file, signal, self.sample_rate)
        self.output_std = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        self.output_denoised = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

    def tearDown(self):
        for f in [self.test_file, self.output_std, self.output_denoised]:
            if os.path.exists(f):
                os.remove(f)

    def test_01_preprocessing(self):
        print("\n测试音频标准化 (audio_utils)...")
        out = preprocess_audio(self.test_file, self.output_std, target_sr=16000)
        self.assertTrue(os.path.exists(out))
        data, sr = sf.read(out)
        self.assertEqual(sr, 16000)
        print(f"采样率已成功转换: {sr}Hz")

    def test_02_denoising(self):
        print("\n测试音频降噪 (denoise)...")
        std_audio = preprocess_audio(self.test_file, self.output_std, target_sr=16000)
        out = process_audio(std_audio, self.output_denoised)
        self.assertTrue(os.path.exists(out))
        original_data, _ = sf.read(std_audio)
        denoised_data, _ = sf.read(out)
        self.assertLess(np.var(denoised_data), np.var(original_data))
        print("降噪测试通过，能量分布已改变。")

    def test_03_get_audio_duration(self):
        print("\n测试获取音频时长...")
        duration = get_audio_duration(self.test_file)
        self.assertAlmostEqual(duration, 1.0, places=1)
        # 测试无效文件
        self.assertEqual(get_audio_duration("nonexistent.wav"), 0.0)

    def test_04_preprocess_invalid_file(self):
        print("\n测试预处理异常处理...")
        with self.assertRaises(FileNotFoundError):
            preprocess_audio("missing.wav", self.output_std)

    def test_05_denoise_invalid_file(self):
        with self.assertRaises(ValidationError):
            process_audio("missing.wav", self.output_denoised)


if __name__ == '__main__':
    unittest.main()