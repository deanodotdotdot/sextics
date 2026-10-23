import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "records", Path(__file__).with_name("validate-records.py")
)
records = importlib.util.module_from_spec(spec)
spec.loader.exec_module(records)


class PolynomialEncodingTests(unittest.TestCase):
    def test_exact_encodings_agree_after_algebraic_expansion(self):
        records.polynomial(
            {
                "expression": "(X0 + X1)**2 / 2",
                "terms": [
                    ["1/2", [2, 0, 0, 0, 0, 0]],
                    ["1", [1, 1, 0, 0, 0, 0]],
                    ["1/2", [0, 2, 0, 0, 0, 0]],
                ],
            },
            2,
        )

    def test_individually_valid_but_different_encodings_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "disagree"):
            records.polynomial({"expression": "X0**6", "terms": [["1", [0, 6, 0, 0, 0, 0]]]}, 6)


if __name__ == "__main__":
    unittest.main()
