import unittest

from src.validate import validate


class ValidateTests(unittest.TestCase):
    def test_valid(self):
        normalized, missing = validate({"topic": "t", "budget": 10, "deadline_hours": 20})
        self.assertIsNone(missing)
        self.assertEqual(normalized["budget"], 10)

    def test_missing_budget(self):
        _, missing = validate({"topic": "t", "deadline_hours": 20})
        self.assertEqual(missing, ["budget"])

    def test_missing_deadline(self):
        _, missing = validate({"topic": "t", "budget": 10})
        self.assertEqual(missing, ["deadline_hours"])

    def test_bad_budget(self):
        for value in [0, -1, True, "10"]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate({"topic": "t", "budget": value, "deadline_hours": 20})

    def test_bad_deadline(self):
        for value in [0, -1, True]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate({"topic": "t", "budget": 10, "deadline_hours": value})

    def test_not_dict(self):
        with self.assertRaises(ValueError):
            validate([])


if __name__ == "__main__":
    unittest.main()