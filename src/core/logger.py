"""
日志管理模块
"""
import logging
import os
import sys
from datetime import datetime
class ReVoxLogger:
    def __init__(self, name="ReVox", log_dir="logs"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            os.makedirs(log_dir, exist_ok=True)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            log_file = os.path.join(log_dir, f"revox_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            console_format = logging.Formatter('%(levelname)s: %(message)s')
            file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_format)
            file_handler.setFormatter(file_format)
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

logger = ReVoxLogger().get_logger()
