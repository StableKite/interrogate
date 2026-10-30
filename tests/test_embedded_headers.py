"""The real embedding script must preserve source bytes across read boundaries."""
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class EmbeddedHeaders(unittest.TestCase):
    def test_crlf_at_each_chunk_boundary(self):
        script = Path(__file__).resolve().parents[1] / "cmake/scripts/ConcatenateToCXX.cmake"
        cmake = shutil.which("cmake")
        self.assertIsNotNone(cmake, "CMake is required to test the embedding script")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Include literal zero bytes, lone CR, and CRLF on either side of
            # both 1024-byte read boundaries.  Test the real script output.
            for offset in (0, 1022, 1023, 1024, 2046, 2047, 2048):
                for suffix in (b"\r\nnext\x00\r", b"\r", b"\r\n"):
                    with self.subTest(offset=offset, suffix=suffix):
                        payload = b"x" * offset + suffix
                        source = root / "input.h"
                        source.write_bytes(payload)
                        output = root / "embedded.cxx"
                        subprocess.run([cmake, "-DOUTPUT_FILE=" + str(output),
                            "-DINPUT_FILES=" + str(source), "-DSYMBOL_NAME=embedded",
                            "-P", str(script)], check=True, capture_output=True)
                        generated = output.read_text(encoding="utf8")
                        actual = bytes(int(value, 16) for value in re.findall(r"0x([0-9a-fA-F]{2}),", generated))
                        expected = payload.replace(b"\r\n", b"\n")
                        self.assertEqual(actual, expected)
                        self.assertIn("extern const int embedded_size = " + str(len(expected)) + ";", generated)


if __name__ == "__main__":
    unittest.main()
