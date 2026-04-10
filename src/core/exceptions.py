"""
错误管理模块
"""
import torch
class ReVoxError(Exception):
    def __init__(self, message="ReVox 运行过程中发生未知错误", error_code=500):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class DependencyError(ReVoxError):
    def __init__(self, message):
        super().__init__(f"依赖缺失————{message}", error_code=501)

class ConfigError(ReVoxError):
    def __init__(self, message):
        super().__init__(f"配置错误————{message}", error_code=400)

class ResourceError(ReVoxError):
    def __init__(self, message="硬件资源不足"):
        device_info = "CPU"
        if torch.cuda.is_available():
            try:
                curr_mem = torch.cuda.memory_allocated() / 1024**2
                max_mem = torch.cuda.get_device_properties(0).total_memory / 1024**2
                device_info = f"GPU (已用: {curr_mem:.0f}MB / 总量: {max_mem:.0f}MB)"
            except:
                device_info = "GPU (状态获取失败)"
        full_msg = f"资源受限————{message} | 运行环境: {device_info}"
        super().__init__(full_msg, error_code=507)

class MediaProcessError(ReVoxError):
    def __init__(self, message):
        super().__init__(f"多媒体错误————{message}", error_code=502)

class ValidationError(ReVoxError):
    def __init__(self, message):
        super().__init__(f"数据校验失败————{message}", error_code=422)

class SecurityError(ReVoxError):
    def __init__(self, message):
        super().__init__(f"安全审计失败————{message}", error_code=403)