import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import yaml
from unittest.mock import patch
from src.core.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = os.path.join(self.project_root, "config")
        os.makedirs(self.config_dir, exist_ok=True)
        self.test_yaml = os.path.join(self.config_dir, "test_custom.yaml")
        self.sample_data = {
            "render": {"preprocess": "crop", "still": False},
            "enhancements": {"superres": True, "method": "face_fix"}
        }
        with open(self.test_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(self.sample_data, f)

    def tearDown(self):
        if os.path.exists(self.test_yaml):
            os.remove(self.test_yaml)
        save_path = os.path.join(self.config_dir, "test_save.yaml")
        if os.path.exists(save_path):
            os.remove(save_path)

    def test_default_values(self):
        """测试内置默认配置（不依赖外部 default.yaml）"""
        with patch('os.path.exists', return_value=False):
            cfg = ConfigManager()
        self.assertEqual(cfg.get("render.preprocess"), "full")
        self.assertTrue(cfg.get("render.still"))
        self.assertFalse(cfg.get("enhancements.superres"))
        self.assertEqual(cfg.get("enhancements.method", "fast"), "fast")
        self.assertIsNone(cfg.get("nonexistent"))

    def test_yaml_loading(self):
        cfg = ConfigManager(self.test_yaml)
        self.assertEqual(cfg.get("render.preprocess"), "crop")
        self.assertFalse(cfg.get("render.still"))
        self.assertTrue(cfg.get("enhancements.superres"))
        self.assertEqual(cfg.get("enhancements.method"), "face_fix")
        self.assertEqual(cfg.get("paths.source_image"), "examples/image_test.png")

    def test_merge_dict(self):
        cfg = ConfigManager()
        override = {"render": {"preprocess": "resize"}}
        cfg._config = cfg._merge_dict(cfg._config, override)
        self.assertEqual(cfg.get("render.preprocess"), "resize")
        self.assertTrue(cfg.get("render.still"))

    def test_get_nested_value(self):
        cfg = ConfigManager()
        self.assertEqual(cfg.get("render.still"), True)
        self.assertIsNone(cfg.get("a.b.c"))
        self.assertEqual(cfg.get("a.b.c", "default"), "default")

    def test_set_nested_value(self):
        cfg = ConfigManager()
        cfg.set("test.new.key", 123)
        self.assertEqual(cfg.get("test.new.key"), 123)

    def test_save_config(self):
        cfg = ConfigManager()
        cfg.set("custom.field", "value")
        save_path = os.path.join(self.config_dir, "test_save.yaml")
        if os.path.exists(save_path):
            os.remove(save_path)
        cfg.save_config(save_path)
        self.assertTrue(os.path.exists(save_path))
        with open(save_path, 'r') as f:
            data = yaml.safe_load(f)
        self.assertEqual(data["custom"]["field"], "value")

    def test_cli_override(self):
        class Args:
            source_image = "cli_img.jpg"
            driven_audio = "cli_audio.wav"
            output_dir = "cli_out"
            upscale = True
            method = "fast"
        args = Args()
        cfg = ConfigManager(cli_args=args)
        self.assertEqual(cfg.get("paths.source_image"), "cli_img.jpg")
        self.assertEqual(cfg.get("paths.driven_audio"), "cli_audio.wav")
        self.assertEqual(cfg.get("paths.output_path"), "cli_out")
        self.assertTrue(cfg.get("enhancements.superres"))
        self.assertEqual(cfg.get("enhancements.method"), "fast")

    def test_missing_config_file(self):
        cfg = ConfigManager("nonexistent.yaml")
        self.assertEqual(cfg.get("render.preprocess"), "full")


if __name__ == "__main__":
    unittest.main()