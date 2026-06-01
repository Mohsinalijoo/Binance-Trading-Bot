"""Command-line interface for placing Binance Futures Testnet orders."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from bot.client import BinanceAPIError, BinanceFuturesClient, BinanceNetworkError
from bot.config import DEFAULT_BASE_URL, load_env_file, load_settings
from bot.logging_config import setup_logging
from bot.orders import OrderRequest, build_order_request, place_order
from bot.validators import ValidationError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place MARKET and LIMIT orders on Binance USD-M Futures Testnet."
    )
    parser.add_argument("--symbol", help="Trading pair, for example BTCUSDT")
    parser.add_argument("--side", choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    parser.add_argument(
        "--type",
        "--order-type",
        dest="order_type",
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", help="Order quantity, for example 0.001")
    parser.add_argument("--price", help="Limit price. Required only for LIMIT orders")
    parser.add_argument(
        "--time-in-force",
        default="GTC",
        choices=["GTC", "IOC", "FOK", "gtc", "ioc", "fok"],
        help="Time in force for LIMIT orders. Default: GTC",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help=f"Override Binance Futures base URL. Default: {DEFAULT_BASE_URL}",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Ask for missing values using prompts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print the request without sending it to Binance.",
    )
    return parser.parse_args()


def main() -> int:
    load_env_file()
    setup_logging()
    args = parse_args()

    try:
        args = fill_interactive_values(args) if args.interactive else args
        order_request = build_order_request(
            symbol=require_value(args.symbol, "symbol"),
            side=require_value(args.side, "side"),
            order_type=require_value(args.order_type, "type"),
            quantity=require_value(args.quantity, "quantity"),
            price=args.price,
            time_in_force=args.time_in_force,
        )
    except (ValidationError, ValueError) as exc:
        print_failure(str(exc))
        return 2

    print_order_summary(order_request, dry_run=args.dry_run)

    if args.dry_run:
        print_success("Dry run complete. No order was sent to Binance.")
        return 0

    try:
        settings = load_settings(base_url_override=args.base_url)
        client = BinanceFuturesClient(
            api_key=settings.api_key,
            api_secret=settings.api_secret,
            base_url=settings.base_url,
            recv_window=settings.recv_window,
            timeout=settings.timeout,
        )
        response = place_order(client, order_request)
    except ValueError as exc:
        print_failure(str(exc))
        return 2
    except BinanceAPIError as exc:
        print_failure(str(exc))
        if exc.payload:
            print_json("API Error Payload", exc.payload)
        return 1
    except BinanceNetworkError as exc:
        print_failure(str(exc))
        return 1

    print_response_details(response)
    print_success("Order request completed successfully.")
    return 0


def fill_interactive_values(args: argparse.Namespace) -> argparse.Namespace:
    if not args.symbol:
        args.symbol = prompt_until_valid("Symbol", lambda value: build_order_request(value, "BUY", "MARKET", "0.001"))
    if not args.side:
        args.side = prompt_choice("Side", ["BUY", "SELL"])
    if not args.order_type:
        args.order_type = prompt_choice("Order type", ["MARKET", "LIMIT"])
    if not args.quantity:
        args.quantity = prompt_text("Quantity")
    if str(args.order_type).upper() == "LIMIT" and not args.price:
        args.price = prompt_text("Limit price")
    return args


def prompt_text(label: str) -> str:
    return input(f"{label}: ").strip()


def prompt_choice(label: str, options: list[str]) -> str:
    option_text = "/".join(options)
    while True:
        value = input(f"{label} ({option_text}): ").strip().upper()
        if value in options:
            return value
        print(f"Please enter one of: {', '.join(options)}.")


def prompt_until_valid(label: str, validator: Any) -> str:
    while True:
        value = prompt_text(label)
        try:
            validator(value)
        except Exception as exc:
            print(str(exc))
        else:
            return value


def require_value(value: str | None, field_name: str) -> str:
    if value is None or str(value).strip() == "":
        raise ValueError(f"Missing required argument: --{field_name}. Use --interactive for prompts.")
    return value


def print_order_summary(order_request: OrderRequest, dry_run: bool = False) -> None:
    print("\nOrder Request Summary")
    print("---------------------")
    print(f"Mode       : {'DRY RUN' if dry_run else 'LIVE TESTNET ORDER'}")
    print(f"Symbol     : {order_request.symbol}")
    print(f"Side       : {order_request.side}")
    print(f"Type       : {order_request.order_type}")
    print(f"Quantity   : {order_request.quantity}")
    if order_request.order_type == "LIMIT":
        print(f"Price      : {order_request.price}")
        print(f"TimeInForce: {order_request.time_in_force}")


def print_response_details(response: dict[str, Any]) -> None:
    print("\nOrder Response Details")
    print("----------------------")
    fields = {
        "orderId": response.get("orderId"),
        "status": response.get("status"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice"),
        "clientOrderId": response.get("clientOrderId"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "type": response.get("type"),
    }
    for key, value in fields.items():
        if value is not None:
            print(f"{key:13}: {value}")
    print_json("Full Response", response)


def print_json(title: str, payload: dict[str, Any]) -> None:
    print(f"\n{title}")
    print(json.dumps(payload, indent=2, sort_keys=True))


def print_success(message: str) -> None:
    print(f"\nSUCCESS: {message}")


def print_failure(message: str) -> None:
    print(f"\nFAILED: {message}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
