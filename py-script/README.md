# Crypto Cycles Feed

A Python script to send cryptocurrency price data to the **[Cycles App](https://app.cycles.org)** from [CoinGecko](https://www.coingecko.com/en/api), supporting both continuous monitoring and single-test modes.

---

## Setup

1. **Setup Script**  

    Save code and enviorment file as:  
    ```bash
    crypto_cycles.py
    .env
    ```

2. **Configure Your API Key**  

    Open `.env` and provide key such as:  
    ```python
    CYCLES_API_KEY=your-actual-api-key-here
    ```

---

## Usage

### Command Line Options

```bash
# Basic modes
python crypto_cycles.py                         # START
python crypto_cycles.py --5m                    # Run every 5 minutes (all symbols)
python crypto_cycles.py --1h                    # Run every 1 hour (all symbols)
python crypto_cycles.py --test                  # Run once for testing (all symbols)
python crypto_cycles.py --preview               # Preview stream mappings (all symbols)

# Single symbol modes
python crypto_cycles.py --symbol BTC            # Run continuously (BTC only)
python crypto_cycles.py --test --symbol BTC     # Test run (BTC only)
python crypto_cycles.py --preview --symbol BTC  # Preview BTC mapping
python crypto_cycles.py --5m -s ETH             # Run every 5 minutes (ETH only)

# Multiple symbol modes
python crypto_cycles.py --symbols BTC,ETH,ADA   # Run continuously (specific symbols)
python crypto_cycles.py --symbols=BTC,ETH,SOL   # Run continuously (inline format)
python crypto_cycles.py --test --symbols BTC,ETH # Test run (specific symbols)
```

### Symbol Options

- `--symbol BTC` - Single symbol
- `--symbol=BTC` - Single symbol (inline format)
- `--symbols BTC,ETH,ADA` - Multiple symbols (comma-separated)
- `--symbols=BTC,ETH,ADA` - Multiple symbols (inline format)
- `-s BTC` - Single symbol (short form)

### Valid Timeframes

- `--2m` - Every 2 minutes
- `--5m` - Every 5 minutes
- `--15m` - Every 15 minutes
- `--30m` - Every 30 minutes
- `--1h` - Every 1 hour
- `--2h` - Every 2 hours
- `--4h` - Every 4 hours
- `--6h` - Every 6 hours
- `--12h` - Every 12 hours
- `--1d` - Every 1 day

### Interactive Mode

When run without arguments, the script will prompt you to choose a mode:
- **(c)ontinuous** - Run continuously with specified interval
- **(t)est** - Run once for testing
- **(p)review** - Preview stream mappings without sending data

### Examples

```bash
# Monitor all cryptocurrencies continuously
python crypto_cycles.py

# Check Bitcoin price every 15 minutes
python crypto_cycles.py --15m --symbol BTC

# Test run for Ethereum and Solana only
python crypto_cycles.py --test --symbols ETH,SOL

# Preview what symbols would be monitored
python crypto_cycles.py --preview --symbols BTC,ETH,ADA,DOT

# Monitor top 3 cryptocurrencies every hour
python crypto_cycles.py --1h --symbols BTC,ETH,BNB
```
