from urllib.parse import urlencode
import hashlib
import hmac
import unittest

from bot.client import BinanceFuturesClient


class ClientTests(unittest.TestCase):
    def test_signature_uses_hmac_sha256_over_urlencoded_params(self):
        params = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": "1",
            "price": "9000",
            "timeInForce": "GTC",
            "recvWindow": 5000,
            "timestamp": 1591702613943,
        }
        secret = "test-secret"
        expected = hmac.new(
            secret.encode("utf-8"),
            urlencode(params).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        client = BinanceFuturesClient(
            api_key="test-key",
            api_secret=secret,
            base_url="https://testnet.binancefuture.com",
        )

        self.assertEqual(client._signature(params), expected)


if __name__ == "__main__":
    unittest.main()
