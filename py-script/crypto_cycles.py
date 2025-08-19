#!/usr/bin/env python3
"""
Cryptocurrency Price to Cycles App
Fetches crypto prices from CoinGecko and posts them to Cycles app
Enhanced with symbol filtering capability
"""

import json
import time
import urllib.request
import urllib.parse
from datetime import datetime
import sys
import re


# Simple API key loader from .env file (no extra libraries)
# or delete from None - add it to .env") and replace with hardcoded api key in ""
CYCLES_API_KEY = None

try:
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("CYCLES_API_KEY="):
                CYCLES_API_KEY = line.split("=", 1)[1].strip()
                break
except FileNotFoundError:
    print(".env file not found!")

if not CYCLES_API_KEY:
    print("CYCLES_API_KEY not set! Please add it to .env")


CYCLES_WEBHOOK_URL = "https://api.cycle.tools/api/Stream/SubmitStreamData"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false"

def parse_timeframe(timeframe_str):
    """
    Parse timeframe string like '2m', '5m', '1h', '1d' into seconds
    Returns tuple (seconds, display_name)
    """
    if not timeframe_str:
        return None, None
    
    timeframe_str = timeframe_str.lstrip('-')
    
    # Match pattern like '2m', '15m', '1h', '4h', '1d'
    match = re.match(r'^(\d+)([smhd])$', timeframe_str.lower())
    if not match:
        return None, None
    
    value = int(match.group(1))
    unit = match.group(2)
    
    multipliers = {
        's': 1,      # seconds
        'm': 60,     # minutes
        'h': 3600,   # hours
        'd': 86400   # days
    }
    
    if unit not in multipliers:
        return None, None
    
    seconds = value * multipliers[unit]
    
    # Minimum timeframe is 2 minutes (120 seconds) due to API rate limits
    if seconds < 120:
        return None, None
    
    unit_names = {
        's': 'second' if value == 1 else 'seconds',
        'm': 'minute' if value == 1 else 'minutes',
        'h': 'hour' if value == 1 else 'hours',
        'd': 'day' if value == 1 else 'days'
    }
    
    display_name = f"{value} {unit_names[unit]}"
    
    return seconds, display_name

def parse_symbols(symbol_args):
    """
    Parse symbol arguments and return a set of uppercase symbols
    Handles both --symbols=BTC,ETH and multiple --symbol BTC --symbol ETH formats
    """
    symbols = set()
    
    for arg in symbol_args:
        if '=' in arg:
            # Handle --symbols=BTC,ETH,ADA format
            symbol_list = arg.split('=')[1]
            symbols.update(s.strip().upper() for s in symbol_list.split(',') if s.strip())
        else:
            # Handle individual symbol
            symbols.add(arg.strip().upper())
    
    return symbols

def generate_stream_id(symbol, name):
    """Generate a stream ID from symbol and name"""
    # Convert symbol to uppercase and append _PRICE for cycle app symbol
    return f"{symbol.upper()}_PRICE"

def fetch_crypto_prices():
    """Fetch cryptocurrency prices from CoinGecko API"""
    try:
        with urllib.request.urlopen(COINGECKO_API_URL) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data
            else:
                print(f"Error fetching data: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching crypto prices: {e}")
        return None

def send_to_cycles(stream_id, price, timestamp):
    """Send price data to Cycles app"""
    try:
        payload = {
            "streamid": stream_id,
            "messagetype": "UPSERT",
            "dates": [timestamp],
            "values": [price]
        }
        
        url_with_key = f"{CYCLES_WEBHOOK_URL}?api_key={CYCLES_API_KEY}"
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            url_with_key,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Send
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"✓ Sent {stream_id}: ${price}")
                return True
            else:
                print(f"✗ Failed to send {stream_id}: HTTP {response.status}")
                return False
                
    except Exception as e:
        print(f"✗ Error sending {stream_id} to Cycles: {e}")
        return False

def filter_cryptos_by_symbols(crypto_data, target_symbols):
    """Filter cryptocurrency data by specified symbols"""
    if not target_symbols:
        return crypto_data  # Return all if no symbols specified
    
    filtered = []
    found_symbols = set()
    
    for crypto in crypto_data:
        symbol = crypto.get('symbol', '').upper()
        if symbol in target_symbols:
            filtered.append(crypto)
            found_symbols.add(symbol)
    
    # Report missing symbols
    missing_symbols = target_symbols - found_symbols
    if missing_symbols:
        print(f"Symbols not found in API data: {', '.join(sorted(missing_symbols))}")
    
    if found_symbols:
        print(f"✓ Found symbols: {', '.join(sorted(found_symbols))}")
    
    return filtered

def process_crypto_data(target_symbols=None):
    """Main processing function with optional symbol filtering"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching crypto prices...")
    
    crypto_data = fetch_crypto_prices()
    if not crypto_data:
        return False
    
    if target_symbols:
        print(f"Filtering for symbols: {', '.join(sorted(target_symbols))}")
        crypto_data = filter_cryptos_by_symbols(crypto_data, target_symbols)
        
        if not crypto_data:
            print("No matching cryptocurrencies found!")
            return False
    
    # Get current timestamp in ISO format
    timestamp = datetime.now().isoformat()
    
    # Process each cryptocurrency
    success_count = 0
    total_count = 0
    
    print(f"Processing {len(crypto_data)} cryptocurrencies")
    
    for crypto in crypto_data:
        crypto_id = crypto.get('id')
        symbol = crypto.get('symbol')
        name = crypto.get('name')
        current_price = crypto.get('current_price')
        
        if symbol and current_price and name:
            # Generate stream ID automatically via Coinbase data
            stream_id = generate_stream_id(symbol, name)
            total_count += 1
            
            print(f"Processing {name} ({symbol.upper()}) -> {stream_id}")
            
            if send_to_cycles(stream_id, current_price, timestamp):
                success_count += 1
        else:
            print(f"Skipping {crypto_id}: missing required fields")
    
    print(f"Processed {success_count}/{total_count} cryptocurrencies successfully")
    return success_count > 0

def validate_config():
    """Validate configuration before running"""
    if CYCLES_API_KEY == "REDACTED":
        print("Please update CYCLES_API_KEY with your actual API key")
        return False
    
    print(f"✓ Configuration validated")
    print(f"✓ Using Cycles API key: {CYCLES_API_KEY[:8]}...")
    return True

def preview_stream_mappings(target_symbols=None):
    """Preview what stream IDs will be generated without sending data"""
    print("Previewing stream mappings...")
    
    crypto_data = fetch_crypto_prices()
    if not crypto_data:
        return
    
    # Filter by symbols if specified
    if target_symbols:
        print(f"Filtering for symbols: {', '.join(sorted(target_symbols))}")
        crypto_data = filter_cryptos_by_symbols(crypto_data, target_symbols)
    
    if not crypto_data:
        print("No matching cryptocurrencies found!")
        return
    
    print(f"\nWill create the following stream mappings:")
    print("-" * 60)
    
    for crypto in crypto_data:
        symbol = crypto.get('symbol')
        name = crypto.get('name')
        current_price = crypto.get('current_price')
        
        if symbol and name and current_price:
            stream_id = generate_stream_id(symbol, name)
            print(f"{name:<20} ({symbol.upper():<6}) -> {stream_id:<15} (${current_price:,.2f})")
    
    print("-" * 60)

def run_continuous(interval_seconds=120, target_symbols=None):
    """Run the Crypto Price Monitor continuously with rate-limit handling."""
    
    interval_display = f"{interval_seconds // 60} minutes" if interval_seconds >= 60 else f"{interval_seconds} seconds"
    
    print("🚀 Starting Crypto Price Monitor...")
    
    if target_symbols:
        print(f"Monitoring specific symbols: {', '.join(sorted(target_symbols))}")
    else:
        print("Monitoring all top cryptocurrencies")
        
    print(f"Updating prices every {interval_display}")
    print("Press Ctrl+C to stop")
    
    if not validate_config():
        return
    
    request_count = 0
    start_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            elapsed_minutes = (current_time - start_time) / 60
            
            # Reset request counter every minute
            if elapsed_minutes >= 1:
                request_count = 0
                start_time = current_time
            
            # Check rate limit
            if request_count >= 25:
                print("⏸️  Approaching rate limit, pausing for 60 seconds...")
                time.sleep(60)
                request_count = 0
                start_time = time.time()
                continue  # Skip to next iteration
            
            # Process crypto data
            if process_crypto_data(target_symbols):
                request_count += 1
            
            print(f"⏱ Waiting {interval_display}... (Requests this minute: {request_count}/25)")
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping Crypto Price Monitor...")
        print("✓ Shutdown complete")
        
def run_once(target_symbols=None):
    """Run once for testing"""
    print("Running single test...")
    
    if target_symbols:
        print(f"Testing symbols: {', '.join(sorted(target_symbols))}")
    
    if not validate_config():
        return
        
    success = process_crypto_data(target_symbols)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed")

def main():
    """Main entry point"""
    print("=" * 50)
    print("  CRYPTOCURRENCY PRICE TO CYCLES APP")
    print("=" * 50)
    
    # Parse command line arguments
    interval_seconds = 120  # Default 2 minutes
    interval_display = "2 minutes"
    target_symbols = set()
    mode_args = []
    
    i = 0
    while i < len(sys.argv[1:]):
        arg = sys.argv[i + 1]
        
        if arg.startswith('--') and re.match(r'^--\d+[smhd]$', arg):
            # Timeframe argument
            parsed_seconds, parsed_display = parse_timeframe(arg)
            if parsed_seconds is not None:
                interval_seconds = parsed_seconds
                interval_display = parsed_display
                print(f"✓ Using custom timeframe: {interval_display}")
            else:
                print(f"✗ Invalid timeframe: {arg}")
                print("Valid examples: --2m, --5m, --15m, --1h, --4h, --1d")
                print("Minimum interval is 2 minutes (--2m)")
                return
                
        elif arg == '--symbol' or arg == '-s':
            # Single symbol argument: --symbol BTC
            if i + 1 < len(sys.argv) - 1:
                i += 1
                symbol_arg = sys.argv[i + 1]
                target_symbols.update(parse_symbols([symbol_arg]))
            else:
                print("Error: --symbol requires a symbol argument")
                return
                
        elif arg == '--symbols':
            # Multiple symbols argument: --symbols BTC,ETH,ADA
            if i + 1 < len(sys.argv) - 1:
                i += 1
                symbol_arg = sys.argv[i + 1]
                target_symbols.update(parse_symbols([f'symbols={symbol_arg}']))
            else:
                print("Error: --symbols requires a comma-separated list")
                return
                
        elif arg.startswith('--symbols='):
            # Inline multiple symbols: --symbols=BTC,ETH,ADA
            target_symbols.update(parse_symbols([arg]))
            
        elif arg.startswith('--symbol='):
            # Inline single symbol: --symbol=BTC
            symbol = arg.split('=')[1].strip().upper()
            if symbol:
                target_symbols.add(symbol)
                
        else:
            # Other arguments (test, preview)
            mode_args.append(arg)
        
        i += 1
    
    # Display selected symbols
    if target_symbols:
        print(f"✓ Target symbols: {', '.join(sorted(target_symbols))}")
    
    # Handle mode arguments
    if mode_args:
        if mode_args[0] == "--test":
            run_once(target_symbols)
        elif mode_args[0] == "--preview":
            preview_stream_mappings(target_symbols)
        else:
            print(f"Unknown argument: {mode_args[0]}. Use --test or --preview")
    else:
        if len([arg for arg in sys.argv[1:] if not arg.startswith('-')]) == 0 and not target_symbols:
            # No arguments provided
            print("\nModes:")
            print("  python crypto_cycles.py                         - Run continuously (all symbols)")
            print("  python crypto_cycles.py --5m                    - Run every 5 minutes (all symbols)")
            print("  python crypto_cycles.py --symbol BTC            - Run continuously (BTC only)")
            print("  python crypto_cycles.py --symbols BTC,ETH,ADA   - Run continuously (specific symbols)")
            print("  python crypto_cycles.py --test                  - Test run (all symbols)")
            print("  python crypto_cycles.py --test --symbol BTC     - Test run (BTC only)")
            print("  python crypto_cycles.py --preview               - Preview mappings")
            print("  python crypto_cycles.py --preview --symbol BTC  - Preview BTC mapping")
            print("\nSymbol Options:")
            print("  --symbol BTC              - Single symbol")
            print("  --symbol=BTC              - Single symbol (inline)")
            print("  --symbols BTC,ETH,ADA     - Multiple symbols")
            print("  --symbols=BTC,ETH,ADA     - Multiple symbols (inline)")
            print("  -s BTC                    - Single symbol (short form)")
            print("\nTimeframes: --2m, --5m, --15m, --30m, --1h, --2h, --4h, --6h, --12h, --1d")
            
            choice = input("\nChoose mode (c)ontinuous/(t)est/(p)review: ").strip().lower()
            
            # Ask for symbols if no symbols specified yet
            interactive_symbols = set()
            if not target_symbols:
                symbol_input = input("Enter symbols (comma-separated, or press Enter for all): ").strip()
                if symbol_input:
                    interactive_symbols = set(s.strip().upper() for s in symbol_input.split(',') if s.strip())
                    print(f"✓ Will monitor symbols: {', '.join(sorted(interactive_symbols))}")
            
            final_symbols = target_symbols if target_symbols else (interactive_symbols if interactive_symbols else None)
            
            if choice in ['c', 'continuous']:
                run_continuous(interval_seconds, final_symbols)
            elif choice in ['p', 'preview']:
                preview_stream_mappings(final_symbols)
            else:
                run_once(final_symbols)

                # Run continuous with specified options
                run_continuous(interval_seconds, target_symbols if target_symbols else None)


if __name__ == "__main__":
    main()