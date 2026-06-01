"""Order placement use cases."""

from __future__ import annotations

from dataclasses import dataclass

from bot.client import BinanceFuturesClient
from bot.validators import validate_order_input


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: str
    price: str | None = None
    time_in_force: str = "GTC"

    def to_api_params(self) -> dict[str, str]:
        params = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": self.quantity,
            "newOrderRespType": "RESULT",
        }
        if self.order_type == "LIMIT":
            params["timeInForce"] = self.time_in_force
            params["price"] = self.price or ""
        return params


def build_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    time_in_force: str = "GTC",
) -> OrderRequest:
    validated = validate_order_input(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        time_in_force=time_in_force,
    )
    return OrderRequest(**validated)


def place_order(client: BinanceFuturesClient, order_request: OrderRequest) -> dict[str, object]:
    return client.create_order(order_request.to_api_params())

