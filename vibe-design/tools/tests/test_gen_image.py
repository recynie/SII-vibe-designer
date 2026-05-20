from pathlib import Path
import importlib.util
import unittest


TOOLS_DIR = Path(__file__).resolve().parents[1]
GEN_IMAGE = TOOLS_DIR / "gen_image.py"

spec = importlib.util.spec_from_file_location("gen_image", GEN_IMAGE)
gen_image = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(gen_image)


class CandidatePathTest(unittest.TestCase):
    def test_appends_index_before_suffix(self):
        base = Path("outputs/run-x/artifacts/logo/v1.png")
        self.assertEqual(
            gen_image.candidate_path(base, 1),
            Path("outputs/run-x/artifacts/logo/v1-1.png"),
        )
        self.assertEqual(
            gen_image.candidate_path(base, 3),
            Path("outputs/run-x/artifacts/logo/v1-3.png"),
        )

    def test_preserves_multi_part_suffix(self):
        base = Path("outputs/run-x/artifacts/mockup/v1.final.png")
        self.assertEqual(
            gen_image.candidate_path(base, 2),
            Path("outputs/run-x/artifacts/mockup/v1.final-2.png"),
        )

    def test_rejects_invalid_index(self):
        with self.assertRaisesRegex(ValueError, "candidate index"):
            gen_image.candidate_path(Path("v1.png"), 0)


if __name__ == "__main__":
    unittest.main()
