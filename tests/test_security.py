import os
import tempfile
import unittest
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.security_utils import (
    safe_path_check,
    validate_file_type,
    sanitize_filename,
    SecureFileOperations,
    SecurityError,
    get_global_secure_ops
)


class TestSecurityUtils(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.allowed_base_dir = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_safe_path_check_valid(self):
        valid = ["file.txt", "subdir/file.png", os.path.join(self.test_dir, "safe")]
        for p in valid:
            self.assertTrue(safe_path_check(p))

    def test_safe_path_check_invalid(self):
        invalid = ["file\x00inject"]
        for p in invalid:
            self.assertFalse(safe_path_check(p))
        self.assertTrue(safe_path_check("../../../etc/passwd"))

    def test_validate_file_type(self):
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("hello")
        self.assertTrue(validate_file_type(test_file, ['.txt']))
        self.assertFalse(validate_file_type(test_file, ['.jpg']))
        self.assertFalse(validate_file_type("nonexist.txt"))

    def test_sanitize_filename(self):
        cases = [
            ("good.txt", "good.txt"),
            ("bad<>.txt", "bad__.txt"),
            ("CON", "_CON"),
            ("a|b&c", "a_b_c")
        ]
        for inp, out in cases:
            self.assertEqual(sanitize_filename(inp), out)

    def test_secure_join(self):
        ops = SecureFileOperations(self.test_dir)
        path = ops.secure_join(self.test_dir, "sub", "file.txt")
        self.assertEqual(path, os.path.join(self.test_dir, "sub", "file.txt"))
        with self.assertRaises(SecurityError):
            ops.secure_join("../../outside")

    def test_secure_temp_file(self):
        ops = SecureFileOperations()
        tmp = ops.secure_temp_file(suffix=".tmp")
        self.assertTrue(os.path.exists(tmp))
        ops.cleanup_temp_files()
        self.assertFalse(os.path.exists(tmp))

    def test_secure_copy(self):
        ops = SecureFileOperations(self.test_dir)
        src = os.path.join(self.test_dir, "src.txt")
        with open(src, 'w') as f:
            f.write("data")
        dst = os.path.join(self.test_dir, "dst.txt")
        ops.secure_copy(src, dst)
        self.assertTrue(os.path.exists(dst))
        with self.assertRaises(SecurityError):
            ops.secure_copy(src, "../../bad.txt")

    def test_secure_mkdir(self):
        ops = SecureFileOperations(self.test_dir)
        newdir = os.path.join(self.test_dir, "a", "b")
        ops.secure_mkdir(newdir)
        self.assertTrue(os.path.isdir(newdir))
        with self.assertRaises(SecurityError):
            ops.secure_mkdir("/forbidden")

    def test_validate_and_get_file_info(self):
        ops = SecureFileOperations(self.test_dir)
        fpath = os.path.join(self.test_dir, "info.txt")
        with open(fpath, 'w') as f:
            f.write("x" * 100)
        info = ops.validate_and_get_file_info(fpath)
        self.assertEqual(info['extension'], '.txt')
        self.assertGreater(info['size'], 0)
        with self.assertRaises(FileNotFoundError):
            ops.validate_and_get_file_info("missing")
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        outside_dir = os.path.join(project_root, "..", "test_outside_revox")
        os.makedirs(outside_dir, exist_ok=True)
        outside_file = os.path.join(outside_dir, "bad.txt")
        with open(outside_file, 'w') as f:
            f.write("bad")
        with self.assertRaises(SecurityError):
            ops.validate_and_get_file_info(outside_file)
        os.remove(outside_file)
        os.rmdir(outside_dir)

    def test_global_ops(self):
        ops = get_global_secure_ops()
        self.assertIsInstance(ops, SecureFileOperations)
        tmp = ops.secure_temp_file()
        self.assertTrue(os.path.exists(tmp))
        ops.cleanup_temp_files()
        self.assertFalse(os.path.exists(tmp))


if __name__ == '__main__':
    unittest.main()