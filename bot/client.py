"""HTTP client wrapper for Binance USD-M Futures Testnet REST API."""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import requests


logger = logging.getLogger(__name__)


class BinanceClientError(Exception):
    """Base exception for Binance client failures."""


@dataclass
class BinanceAPIError(BinanceClientError):
    status_code: int
    code: int | None
    message: str
    payload: dict[str, Any] | None = None

    def __str__(self) -> str:
        code_text = f" code={self.code}" if self.code is not None else ""
        return f"Binance API error HTTP {self.status_code}{code_text}: {self.message}"


class BinanceNetworkError(BinanceClientError):
    """Raised when the request cannot reach Binance."""


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str,
        recv_window: int = 5000,
        timeout: int = 10,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.recv_window = recv_window
        self.timeout = timeout
        self.session = session or requests.Session()

    def create_order(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/fapi/v1/order", params=params, signed=True)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> dict[str, Any]:
        request_params = dict(params or {})
        if signed:
            request_params["recvWindow"] = self.recv_window
            request_params["timestamp"] = self._timestamp_ms()
            request_params["signature"] = self._signature(request_params)

        url = f"{self.base_url}{path}"
        headers = {"X-MBX-APIKEY": self.api_key}
        safe_params = self._sanitize_params(request_params)
        logger.info("API request %s %s params=%s", method.upper(), url, safe_params)

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                data=request_params if method.upper() in {"POST", "PUT", "DELETE"} else None,
                params=request_params if method.upper() == "GET" else None,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.Timeout as exc:
            logger.exception("Network timeout while calling Binance")
            raise BinanceNetworkError("Request timed out while calling Binance.") from exc
        except requests.RequestException as exc:
            logger.exception("Network failure while calling Binance")
            raise BinanceNetworkError(f"Network failure while calling Binance: {exc}") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}

        logger.info(
            "API response status=%s body=%s",
            response.status_code,
            payload,
        )

        if response.status_code >= 400:
            raise BinanceAPIError(
                status_code=response.status_code,
                code=payload.get("code") if isinstance(payload, dict) else None,
                message=payload.get("msg", response.text) if isinstance(payload, dict) else response.text,
                payload=payload if isinstance(payload, dict) else None,
            )

        if not isinstance(payload, dict):
            raise BinanceAPIError(
                status_code=response.status_code,
                code=None,
                message="Unexpected non-object response from Binance.",
                payload={"response": payload},
            )

        return payload

    def _signature(self, params: dict[str, Any]) -> str:
        query_string = urlencode(params, doseq=True)
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def _timestamp_ms() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def _sanitize_params(params: dict[str, Any]) -> dict[str, Any]:
        safe = dict(params)
        if "signature" in safe:
            safe["signature"] = "***"
        return safe

