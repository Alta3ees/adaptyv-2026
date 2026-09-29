import csv
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_candidates.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CandidateValidationTests(unittest.TestCase):
    def check(self, rows=(), *, raw=None, allow_empty=False):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "candidates.csv"
            if raw is None:
                stream = io.StringIO(newline="")
                writer = csv.writer(stream)
                writer.writerow(["name", "sequence", "molecule_class"])
                writer.writerows(rows)
                raw = stream.getvalue()
            path.write_text(raw, encoding="utf-8")
            return validator.validate_csv(path, allow_empty=allow_empty)[1]

    def test_protein_length_boundaries(self):
        for size in (10, 250):
            self.assertFalse(self.check([("a", "A" * size, "protein")]))
        for size in (0, 9, 251):
            self.assertTrue(self.check([("a", "A" * size, "protein")]))

    def test_invalid_characters(self):
        for residue in ("a", "X", "B", "Z", "J", "U", "O", "*", "-", " ", "\n", ":"):
            with self.subTest(residue=residue):
                self.assertTrue(self.check([("a", "A" * 10 + residue, "protein")]))

    def test_classes_and_fab_chains(self):
        for kind in ("protein", "nanobody", "scfv", "fab_kappa", "fab_lambda"):
            seq = "A" * 10 + (":" + "C" * 10 if kind.startswith("fab_") else "")
            self.assertFalse(self.check([("a", seq, kind)]))
        for seq in ("AAAAAAAAAA", ":AAAA", "AAAA:", "AA:CC:DD", "AA:XX"):
            self.assertTrue(self.check([("a", seq, "fab_kappa")]))
        self.assertTrue(self.check([("a", "A" * 10, "antibody")]))
        self.assertFalse(self.check([("a", "A" * 251, "scfv")]))

    def test_names_and_duplicates(self):
        for name in ("", " ", " a", "a "):
            self.assertTrue(self.check([(name, "A" * 10, "protein")]))
        self.assertTrue(self.check([("a", "A" * 10, "protein"), ("a", "C" * 10, "protein")]))
        self.assertTrue(self.check([("a", "A" * 10, "protein"), ("b", "A" * 10, "nanobody")]))

    def test_header_and_row_shape(self):
        for raw in ("", "name,sequence\n", "name,sequence,molecule_class,name\n",
                    "name,sequence,molecule_class\na,AAAAAAAAAA\n",
                    "name,sequence,molecule_class\na,AAAAAAAAAA,protein,extra\n",
                    'name,sequence,molecule_class\n"unclosed'):
            self.assertTrue(self.check(raw=raw, allow_empty=True))
        self.assertFalse(self.check(raw='\ufeffname,sequence,molecule_class,notes\na,AAAAAAAAAA,protein,"one, two"\n'))

    def test_empty_and_count(self):
        self.assertTrue(self.check())
        self.assertFalse(self.check(allow_empty=True))
        rows = [(str(i), "A" * i + "C" * (30-i), "protein") for i in range(21)]
        self.assertFalse(self.check(rows[:20]))
        self.assertTrue(self.check(rows))

    def test_missing_file_and_cli(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertTrue(validator.validate_csv(Path(folder) / "missing.csv")[1])
        command = [sys.executable, str(ROOT / "scripts/validate_candidates.py"), str(ROOT / "data/candidates.csv")]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        self.assertEqual(subprocess.run(command + ["--allow-empty"], capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
