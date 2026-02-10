import unittest

from app.core.errors import build_error_body


class ErrorFormatTest(unittest.TestCase):
    def test_error_body_shape_is_consistent(self):
        body = build_error_body(
            status_code=404,
            message="Product not found",
            path="/products/999",
            details={"product_id": 999},
        )

        self.assertEqual(body["success"], False)
        self.assertIn("error", body)
        self.assertEqual(body["error"]["code"], "NOT_FOUND")
        self.assertEqual(body["error"]["message"], "Product not found")
        self.assertEqual(body["error"]["path"], "/products/999")
        self.assertEqual(body["error"]["details"], {"product_id": 999})
        self.assertIn("timestamp", body["error"])

    def test_error_code_mapping(self):
        conflict = build_error_body(status_code=409, message="conflict", path="/test")
        validation = build_error_body(status_code=422, message="invalid", path="/test")
        internal = build_error_body(status_code=500, message="boom", path="/test")

        self.assertEqual(conflict["error"]["code"], "CONFLICT")
        self.assertEqual(validation["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(internal["error"]["code"], "INTERNAL_SERVER_ERROR")


if __name__ == "__main__":
    unittest.main()
