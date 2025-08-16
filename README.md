# Crypto Cycles Feed

A Python script to send cryptocurrency price data to the **[Cycles App](https://app.cycles.org)** from [CoinGecko](https://www.coingecko.com/en/api), supporting both continuous monitoring and single-test modes.

---

## Setup

1. **Save the Script**  
    Save the code as:  
    ```bash
    crypto_cycles.py
    ```

2. **Configure Your API Key**  

    Open `crypto_cycles.py` and update the configuration at the top:  
    ```python
    CYCLES_API_KEY = "your-actual-api-key-here"
    ```

---

## Usage

### Command Line Options

```bash
python crypto_cycles.py                 # Start
python crypto_cycles.py --5m            # Run continuously every 5 minutes
python crypto_cycles.py --1h            # Run continuously every 1 hour
python crypto_cycles.py --test          # Run once for testing
python crypto_cycles.py --preview       # Preview stream mappings
```

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

---
