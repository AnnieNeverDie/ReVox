__version__ = "1.0.0"
__author__ = "ReVox Team"

from .core.exceptions import (
    ReVoxError,
    DependencyError,
    ConfigError,
    ResourceError,
    MediaProcessError,
    ValidationError,
    SecurityError,
)
from .core.logger import logger
from .core.config_manager import ConfigManager

from .utils.security_utils import safe_path_check, validate_file_type, sanitize_filename, SecureFileOperations
from .utils.video_utils import merge_audio_video, check_ffmpeg_env
from .utils.image_utils import resize_and_pad
from .utils.info_utils import print_video_info

__all__ = [
    "__version__",

    "ReVoxError",
    "DependencyError",
    "ConfigError",
    "ResourceError",
    "MediaProcessError",
    "ValidationError",
    "SecurityError",

    "logger",
    "ConfigManager",

    "safe_path_check",
    "validate_file_type",
    "sanitize_filename",
    "SecureFileOperations",
    "merge_audio_video",
    "check_ffmpeg_env",
    "resize_and_pad",
    "print_video_info",
]