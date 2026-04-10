import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from src.core.exceptions import (
    ReVoxError,
    DependencyError,
    ConfigError,
    ResourceError,
    MediaProcessError,
    ValidationError,
    SecurityError
)


class TestExceptions(unittest.TestCase):
    def test_base_exception(self):
        err = ReVoxError("test", 123)
        self.assertEqual(str(err), "test")
        self.assertEqual(err.error_code, 123)

    def test_dependency_error(self):
        err = DependencyError("missing ffmpeg")
        self.assertIn("依赖缺失", str(err))
        self.assertEqual(err.error_code, 501)

    def test_config_error(self):
        err = ConfigError("bad yaml")
        self.assertIn("配置错误", str(err))
        self.assertEqual(err.error_code, 400)

    def test_resource_error(self):
        err = ResourceError("out of memory")
        self.assertIn("资源受限", str(err))
        self.assertEqual(err.error_code, 507)

    def test_media_process_error(self):
        err = MediaProcessError("ffmpeg failed")
        self.assertIn("多媒体错误", str(err))
        self.assertEqual(err.error_code, 502)

    def test_validation_error(self):
        err = ValidationError("invalid image")
        self.assertIn("数据校验失败", str(err))
        self.assertEqual(err.error_code, 422)

    def test_security_error(self):
        err = SecurityError("path traversal")
        self.assertIn("安全审计失败", str(err))
        self.assertEqual(err.error_code, 403)


if __name__ == "__main__":
    unittest.main()