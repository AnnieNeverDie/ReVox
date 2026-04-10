import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import tempfile
import logging
import shutil
from src.core.logger import ReVoxLogger, logger


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.log_dir = tempfile.mkdtemp()
        self.logger_instance = ReVoxLogger(name="TestLogger", log_dir=self.log_dir)
        self.test_logger = self.logger_instance.get_logger()

    def tearDown(self):
        handlers = self.test_logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.test_logger.removeHandler(handler)
        shutil.rmtree(self.log_dir, ignore_errors=True)

    def test_logger_creation(self):
        self.assertIsInstance(self.test_logger, logging.Logger)
        self.assertEqual(self.test_logger.name, "TestLogger")
        self.assertEqual(self.test_logger.level, logging.DEBUG)

    def test_logger_handlers(self):
        handlers = self.test_logger.handlers
        self.assertEqual(len(handlers), 2)  # console + file
        file_handler = [h for h in handlers if isinstance(h, logging.FileHandler)][0]
        self.assertTrue(os.path.dirname(file_handler.baseFilename) == self.log_dir)

    def test_global_logger(self):
        global_logger = logger
        self.assertIsInstance(global_logger, logging.Logger)
        self.assertEqual(global_logger.name, "ReVox")

    def test_log_levels(self):
        try:
            self.test_logger.debug("debug msg")
            self.test_logger.info("info msg")
            self.test_logger.warning("warning msg")
            self.test_logger.error("error msg")
            self.test_logger.critical("critical msg")
        except Exception as e:
            self.fail(f"Logging failed: {e}")


if __name__ == "__main__":
    unittest.main()