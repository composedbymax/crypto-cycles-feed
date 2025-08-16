# Crypto Cycles Feed

A Python script to send cryptocurrency price data to the **[Cycles App](https://app.cycles.org)** API from [CoinGecko](https://www.coingecko.com/en/api), supporting both continuous monitoring and single-test modes.

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

##  Usage

### Preview what stream IDs will be generated (recommended first)
```bash
python crypto_cycles.py --preview
```

### Continuous Monitoring
```bash
python crypto_cycles.py
```

## Single Test Run
```bash
python crypto_cycles.py --test
```