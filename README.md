# Binance Futures Testnet Trading Bot

A small Python CLI application for placing `MARKET` and `LIMIT` orders on Binance USD-M Futures Testnet.

The project uses direct REST calls with HMAC SHA256 signing, structured validation, exception handling, and file logging.

## Features

- Place `MARKET` and `LIMIT` orders
- Supports `BUY` and `SELL`
- Validates symbol, side, order type, quantity, and limit price
- Prints request summary and Binance response details
- Logs API requests, responses, and errors to `logs/trading_bot.log`
- Keeps API credentials in `.env`, not in source code
- Includes a small test suite for validation and request signing
- Bonus: interactive CLI prompt mode with `--interactive`


## 1. Get Binance Futures Testnet API Keys

Use testnet/demo credentials only. Do not use real Binance account API keys for this assignment.

1. Open the Binance Futures Testnet/Demo Trading page:
   - Assignment URL: https://testnet.binancefuture.com
   - If Binance redirects you to the newer demo flow, use: https://demo.binance.com
2. Create or log in to your demo/testnet account.
3. Open the account/profile menu and go to `API Management`.
4. Click `Create API`.
5. Give it a name, for example `python-intern-bot`.
6. Choose a system-generated/HMAC key if asked.
7. Copy the API Key and Secret Key immediately.


## 2. Setup

```bash
cd binance-futures-testnet-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Open `.env` and replace the placeholders:

```env
BINANCE_API_KEY=your_actual_testnet_api_key
BINANCE_API_SECRET=your_actual_testnet_secret_key
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

## 3. Run Examples

Validate input without sending an order:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

Place a market order:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Place a limit order:

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

Use interactive prompts:

```bash
python cli.py --interactive
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Output

The CLI prints:

- order request summary
- `orderId`
- `status`
- `executedQty`
- `avgPrice`, when returned by Binance
- full JSON response
- success/failure message

## Assumptions

- This bot is for Binance USD-M Futures Testnet only.
- It supports one-way mode by default.
- `LIMIT` orders use `GTC` unless another supported time-in-force value is passed.
- A limit order may return `NEW` if it is placed away from market price and does not fill immediately.
- Testnet balances and orders can be reset by Binance.

