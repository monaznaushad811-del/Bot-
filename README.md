# Simplified Trading Bot — Binance Futures Testnet (USDT-M)

A small, structured Python CLI application that places **MARKET**, **LIMIT**,
and (bonus) **STOP-LIMIT** orders on the [Binance Futures Testnet](https://testnet.binancefuture.com),
with input validation, logging, and error handling.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py          # Binance client wrapper (testnet-configured)
    orders.py           # Order placement logic (market/limit/stop-limit)
    validators.py        # CLI input validation
    logging_config.py    # Logging setup (console + rotating file)
  cli.py                 # CLI entry point
  README.md
  requirements.txt
  logs/
    trading_bot.log      # created automatically on first run
```

## Setup

### 1. Register and activate a Binance Futures Testnet account

- Go to https://testnet.binancefuture.com
- Log in with a GitHub account (this is how the testnet handles auth)
- Your testnet account starts with demo USDT funds — no real money is involved

### 2. Generate API credentials

- On the testnet site, go to **API Key** management and generate an API key
  and secret. Keep these safe — treat them like real credentials even though
  they only work on testnet.

### 3. Install dependencies

```bash
cd trading_bot
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Provide your API credentials

Either export them as environment variables:

```bash
export BINANCE_TESTNET_API_KEY="your_api_key"
export BINANCE_TESTNET_API_SECRET="your_api_secret"
```

or pass them directly on the command line with `--api-key` / `--api-secret`
(see examples below).

## How to Run

### Market order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

### Stop-limit order (bonus order type)

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP-LIMIT --quantity 0.01 \
    --price 61000 --stop-price 60900
```

Each run prints:

1. An **order request summary** (symbol, side, type, quantity, price)
2. The **order response details** (order ID, status, executed quantity, average
   price when available)
3. A clear **success/failure message**

All requests, responses, and errors are also written to `logs/trading_bot.log`.

## CLI Arguments

| Argument        | Required            | Description                                  |
|-----------------|----------------------|-----------------------------------------------|
| `--symbol`      | Yes                  | Trading pair, e.g. `BTCUSDT`                  |
| `--side`        | Yes                  | `BUY` or `SELL`                               |
| `--type`        | Yes                  | `MARKET`, `LIMIT`, or `STOP-LIMIT`            |
| `--quantity`    | Yes                  | Order quantity (must be > 0)                  |
| `--price`       | For LIMIT/STOP-LIMIT | Limit price (must be > 0)                     |
| `--stop-price`  | For STOP-LIMIT       | Stop trigger price (must be > 0)              |
| `--api-key`     | No*                  | Testnet API key                               |
| `--api-secret`  | No*                  | Testnet API secret                            |

\* Required either via flags or the `BINANCE_TESTNET_API_KEY` /
`BINANCE_TESTNET_API_SECRET` environment variables.

## Error Handling

- **Invalid input** (bad symbol format, invalid side/type, non-numeric or
  non-positive quantity/price) is caught by `bot/validators.py` before any
  network call is made, and printed/logged clearly.
- **API errors** (e.g. invalid symbol on Binance's side, insufficient testnet
  balance, precision/quantity filter violations) and **network failures**
  are caught around every `futures_create_order` call in `bot/orders.py`,
  logged with full detail, and surfaced to the user as
  `Order FAILED: <reason>`.

## Assumptions

- This bot only supports **USDT-M Futures** (not Coin-M or Spot).
- The bot always targets the **Binance Futures Testnet**
  (`https://testnet.binancefuture.com`); it is not configured for
  Binance's live/production endpoints.
- Quantity and price precision/step-size rules are enforced by Binance's API
  itself (the bot does not pre-round values); if you hit a precision error,
  check the symbol's exchange info for `stepSize`/`tickSize`.
- STOP-LIMIT orders use Binance Futures' `STOP` order type (a stop order with
  both a trigger price and a limit price), submitted with `timeInForce=GTC`.
- The user is expected to have already funded their testnet futures wallet
  (the testnet UI provides free demo USDT).

## Bonus Features Implemented

- **Third order type:** STOP-LIMIT (`--type STOP-LIMIT`)
- **Structured code:** separate client (`client.py`), order logic
  (`orders.py`), validation (`validators.py`), and CLI (`cli.py`) layers
- **Logging:** rotating file handler + console output, capturing every
  request, response, and error
