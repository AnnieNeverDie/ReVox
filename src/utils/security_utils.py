"""
安全通用模块
"""
import os
import tempfile
import mimetypes
import struct
from typing import Optional
class SecurityError(Exception):
    pass

def safe_path_check(path_str):
    try:
        if not isinstance(path_str, str) or not path_str.strip():
            return False
        invalid_chars = ['\x00']
        if any(char in path_str for char in invalid_chars):
            return False
        normalized = os.path.normpath(path_str)
        if normalized.startswith('/..') or normalized.startswith('../'):
            abs_path = os.path.abspath(path_str)
            current_dir = os.getcwd()
            return True
        else:
            return True
        return True
    except Exception:
        return False

def _detect_file_magic_type(file_path: str) -> Optional[str]:
    magic_signatures = {
        b'\xff\xd8\xff': 'image/jpeg',
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'GIF87a': 'image/gif',
        b'GIF89a': 'image/gif',
        b'BM': 'image/bmp',
        b'II*\x00': 'image/tiff',
        b'MM\x00*': 'image/tiff',
        b'RIFF....WEBP': 'image/webp',
        b'ID3': 'audio/mp3',
        b'\xff\xfb': 'audio/mp3',
        b'\xff\xf3': 'audio/mp3',
        b'\xff\xf2': 'audio/mp3',
        b'RIFF....WAVE': 'audio/wav',
        b'OggS': 'audio/ogg',
        b'fLaC': 'audio/flac',
        b'....ftypM4A': 'audio/m4a',
        b'....ftypmp4': 'audio/mp4',
        b'....ftypisom': 'video/mp4',
        b'....ftypmp42': 'video/mp4',
        b'....ftypM4V': 'video/mp4',
        b'....ftypmovi': 'video/quicktime',
        b'\x1aE\xdf\xa3': 'video/webm',
        b'%PDF-': 'application/pdf',
        b'PK\x03\x04': 'application/zip',
        b'PK\x05\x06': 'application/zip',
        b'PK\x07\x08': 'application/zip',
        b'doc': 'application/msword',
        b'....ftypqt': 'video/quicktime',
    }
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
            for signature, mime_type in magic_signatures.items():
                if isinstance(signature, str):
                    sig_bytes = signature.encode('ascii', errors='ignore')
                else:
                    sig_bytes = signature
                if sig_bytes.startswith(b'RIFF') and len(header) >= 12:
                    if header[:4] == b'RIFF':
                        riff_format = header[8:12]
                        if riff_format == b'WAVE':
                            return 'audio/wav'
                        elif riff_format == b'AVI ':
                            return 'video/avi'
                if header.startswith(sig_bytes):
                    return mime_type
            if len(header) >= 12:
                box_size = struct.unpack('>I', header[:4])[0]
                if box_size > 8 and header[4:8] == b'ftyp':
                    major_brand = header[8:12]
                    if major_brand in [b'M4A ', b'M4B ', b'M4P ', b'M4V ']:
                        return 'audio/m4a'
                    elif major_brand in [b'mp41', b'mp42', b'isom']:
                        return 'video/mp4'
                    elif major_brand == b'qt  ':
                        return 'video/quicktime'
            if len(header) >= 10:
                if header[:2] == b'\xff\xd8' and header[6:10] in [b'JFIF', b'Exif']:
                    return 'image/jpeg'
        return None
    except Exception:
        return None

def validate_file_type(file_path: str, allowed_extensions: list = None) -> bool:
    if not os.path.exists(file_path):
        return False
    if allowed_extensions is None:
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp',
                              '.mp3', '.wav', '.flac', '.m4a', '.mp4', '.avi',
                              '.mov', '.webm', '.gif', '.pdf', '.zip', '.txt']
    _, ext = os.path.splitext(file_path.lower())
    if ext not in allowed_extensions:
        return False
    if os.path.getsize(file_path) == 0:
        return False
    detected_mime = _detect_file_magic_type(file_path)
    if detected_mime:
        expected_mime = mimetypes.guess_type(file_path)[0]
        if expected_mime and detected_mime:
            expected_type = expected_mime.split('/')[0]
            detected_type = detected_mime.split('/')[0]
            return expected_type == detected_type
    return True

def sanitize_filename(filename: str) -> str:
    if not filename:
        return ""
    dangerous_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '&']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + \
                     [f'CON{i}' for i in range(1, 10)] + \
                     [f'LPT{i}' for i in range(1, 10)]
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        filename = f"_{filename}"
    return filename


class SecureFileOperations:
    def __init__(self, allowed_base_dirs=None):
        if allowed_base_dirs is None:
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_script_dir)
            parent_dir = os.path.dirname(project_root)
            self.allowed_base_dirs = [project_root, parent_dir]
        elif isinstance(allowed_base_dirs, str):
            self.allowed_base_dirs = [allowed_base_dirs]
        else:
            self.allowed_base_dirs = allowed_base_dirs
        self.temp_files = []

    def _is_safe_path(self, path):
        """内部路径安全检查：优先允许系统临时目录，然后检查基础目录限制"""
        # 1. 系统临时目录总是允许（用于临时文件）
        temp_dir = tempfile.gettempdir()
        if os.path.abspath(path).startswith(os.path.abspath(temp_dir)):
            return safe_path_check(path)

        # 2. 有基础目录限制：必须位于任一基础目录下
        if self.allowed_base_dirs:
            abs_path = os.path.abspath(path)
            for base in self.allowed_base_dirs:
                abs_base = os.path.abspath(base)
                if abs_path.startswith(abs_base):
                    return safe_path_check(path)
            return False
        else:
            # 3. 没有基础目录限制，直接调用原有检查
            return safe_path_check(path)

    def secure_join(self, *paths):
        result = os.path.join(*paths)
        if not self._is_safe_path(result):
            raise SecurityError(f"Unsafe path detected: {result}")
        return result

    def secure_temp_file(self, suffix="", prefix="revox_", cleanup_on_exit=True):
        temp_dir = tempfile.gettempdir()
        if not self._is_safe_path(temp_dir):
            raise SecurityError(f"Unsafe temporary directory: {temp_dir}")
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix,
            prefix=prefix,
            dir=temp_dir,
            delete=False
        )
        temp_path = temp_file.name
        temp_file.close()
        if cleanup_on_exit:
            self.temp_files.append(temp_path)
        return temp_path

    def secure_copy(self, src, dst, validate_src=True, validate_dst=True):
        if validate_src and not self._is_safe_path(src):
            raise SecurityError(f"Unsafe source path: {src}")
        if validate_dst and not self._is_safe_path(dst):
            raise SecurityError(f"Unsafe destination path: {dst}")
        if validate_src and not os.path.exists(src):
            raise FileNotFoundError(f"Source file does not exist: {src}")
        dst_dir = os.path.dirname(dst)
        os.makedirs(dst_dir, exist_ok=True)
        if validate_src:
            if not validate_file_type(src):
                raise SecurityError(f"Invalid file type for source: {src}")
        import shutil
        shutil.copy2(src, dst)
        return True

    def secure_mkdir(self, path, parents=True, exist_ok=True):
        if not self._is_safe_path(path):
            raise SecurityError(f"Unsafe directory path: {path}")
        if parents:
            os.makedirs(path, exist_ok=exist_ok)
        else:
            if not os.path.exists(path):
                os.mkdir(path)
        return True

    def validate_and_get_file_info(self, file_path):
        # 先检查文件是否存在，再检查路径安全性
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        if not self._is_safe_path(file_path):
            raise SecurityError(f"Unsafe file path: {file_path}")
        if not validate_file_type(file_path):
            raise SecurityError(f"Invalid file type: {file_path}")
        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024
        if file_size > max_size:
            raise SecurityError(f"File too large: {file_size} bytes")
        _, ext = os.path.splitext(file_path)
        return {
            'path': file_path,
            'size': file_size,
            'extension': ext.lower(),
            'exists': True
        }

    def cleanup_temp_files(self):
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass
        self.temp_files.clear()

current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_script_dir)
parent_dir = os.path.dirname(project_root)
global_secure_ops = SecureFileOperations([project_root, parent_dir])


def get_global_secure_ops():
    return global_secure_ops
