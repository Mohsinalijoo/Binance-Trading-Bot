import unittest

from bot.validators import ValidationError, validate_order_input


class ValidatorTests(unittest.TestCase):
    def test_market_order_validation_normalizes_values(self):
        result = validate_order_input(
            symbol="btcusdt",
            side="buy",
            order_type="market",
            quantity="0.0010",
        )

        self.assertEqual(result["symbol"], "BTCUSDT")
        self.assertEqual(result["side"], "BUY")
        self.assertEqual(result["order_type"], "MARKET")
        self.assertEqual(result["quantity"], "0.001")
        self.assertIsNone(result["price"])

    def test_limit_order_requires_price(self):
        with self.assertRaisesRegex(ValidationError, "price is required"):
            validate_order_input(
                symbol="BTCUSDT",
                side="BUY",
                order_type="LIMIT",
                quantity="0.001",
            )

    def test_market_order_rejects_price(self):
        with self.assertRaisesRegex(ValidationError, "price should only"):
            validate_order_input(
                symbol="BTCUSDT",
                side="SELL",
                order_type="MARKET",
                quantity="0.001",
                price="70000",
            )

    def test_rejects_negative_quantity(self):
        with self.assertRaisesRegex(ValidationError, "greater than 0"):
            validate_order_input(
                symbol="BTCUSDT",
                side="BUY",
                order_type="MARKET",
                quantity="-1",
            )


if __name__ == "__main__":
    unittest.main()
