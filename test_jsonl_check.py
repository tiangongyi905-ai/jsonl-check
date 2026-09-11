import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("jsonl_check.py")


class CommandLineTests(unittest.TestCase):
    def run_check(self, data, *args):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "dataset with spaces.jsonl"
            source.write_bytes(data)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), *args],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(source.read_bytes(), data, "Input must remain unchanged")
            return result, json.loads(result.stdout)

    def test_valid_unicode_crlf_and_last_line_without_newline(self):
        result, report = self.run_check('{"text":"你好"}\r\nnull\r\n[1,2]'.encode())
        self.assertEqual(result.returncode, 0)
        self.assertEqual((report["lines"], report["valid"], report["invalid"]), (3, 3, 0))

    def test_large_standard_json_numbers_are_valid(self):
        result, report = self.run_check(("9" * 5000 + "\n1e10000\n").encode())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["valid"], 2)

    def test_mixed_errors_report_positions_without_content(self):
        data = b'\xef\xbb\xbf{}\n\n{"secret":"private-demo",}\n\xff\nNaN\n{}\n'
        result, report = self.run_check(data)
        self.assertEqual(result.returncode, 1)
        self.assertEqual([error["line"] for error in report["errors"]], [1, 2, 3, 4, 5])
        self.assertEqual([error["code"] for error in report["errors"]], ["bom", "blank", "json", "encoding", "constant"])
        self.assertEqual(report["valid"], 1)
        self.assertNotIn("private-demo", result.stdout + result.stderr)

    def test_cap_does_not_stop_counting(self):
        result, report = self.run_check(b'bad\nbad\nbad\n{}\n', "--max-errors", "1")
        self.assertEqual(result.returncode, 1)
        self.assertEqual((report["lines"], report["invalid"], report["errors_omitted"]), (4, 3, 2))
        self.assertEqual(len(report["errors"]), 1)

    def test_optional_object_requirement(self):
        result, report = self.run_check(b'null\n[]\n{"text":"ok"}\n', "--objects-only")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["invalid"], 2)
        self.assertEqual(report["valid"], 1)

    def test_non_json_whitespace_is_rejected(self):
        result, report = self.run_check('\u00a0\n'.encode())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["errors"][0]["code"], "json")

    def test_depth_limit_is_reported_without_crashing(self):
        result, report = self.run_check(b'[' * 3000 + b'0' + b']' * 3000 + b'\n{}\n')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["errors"][0]["code"], "depth_limit")
        self.assertEqual(report["valid"], 1)

    def test_empty_file_is_zero_records(self):
        result, report = self.run_check(b'')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["lines"], 0)

    def test_missing_file_returns_io_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(SCRIPT), str(Path(directory) / "missing.jsonl")], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["error"], "Cannot read the input file.")


if __name__ == "__main__":
    unittest.main()
