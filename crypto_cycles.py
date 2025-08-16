#!/usr/bin/env python3
"""
Cryptocurrency Price to Cycles App
Fetches crypto prices from CoinGecko and posts them to Cycles app
"""

import json
import time
import urllib.request
import urllib.parse
from datetime import datetime
import sys
import re

# Configuration - Update these values
CYCLES_API_KEY = "REDACTED"  # Replace with your actual API key
CYCLES_WEBHOOK_URL = "https://api.cycle.tools/api/Stream/SubmitStreamData"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false"

def parse_timeframe(timeframe_str):
    """
    Parse timeframe string like '2m', '5m', '1h', '1d' into seconds
    Returns tuple (seconds, display_name)
    """
    if not timeframe_str:
        return None, None
    
    # Remove leading dashes if present
    timeframe_str = timeframe_str.lstrip('-')
    
    # Match pattern like '2m', '15m', '1h', '4h', '1d'
    match = re.match(r'^(\d+)([smhd])$', timeframe_str.lower())
    if not match:
        return None, None
    
    value = int(match.group(1))
    unit = match.group(2)
    
    # Convert to seconds
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
    
    # Create display name
    unit_names = {
        's': 'second' if value == 1 else 'seconds',
        'm': 'minute' if value == 1 else 'minutes',
        'h': 'hour' if value == 1 else 'hours',
        'd': 'day' if value == 1 else 'days'
    }
    
    display_name = f"{value} {unit_names[unit]}"
    
    return seconds, display_name

def generate_stream_id(symbol, name):
    """Generate a stream ID from symbol and name"""
    # Convert symbol to uppercase and append _PRICE
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
        # Prepare the payload
        payload = {
            "streamid": stream_id,
            "messagetype": "UPSERT",
            "dates": [timestamp],
            "values": [price]
        }
        
        # Prepare the request
        url_with_key = f"{CYCLES_WEBHOOK_URL}?api_key={CYCLES_API_KEY}"
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            url_with_key,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Send the request
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

def process_crypto_data():
    """Main processing function"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching crypto prices...")
    
    # Fetch data from CoinGecko
    crypto_data = fetch_crypto_prices()
    if not crypto_data:
        return False
    
    # Get current timestamp in ISO format
    timestamp = datetime.now().isoformat()
    
    # Process each cryptocurrency
    success_count = 0
    total_count = 0
    
    print(f"Found {len(crypto_data)} cryptocurrencies from API")
    
    for crypto in crypto_data:
        crypto_id = crypto.get('id')
        symbol = crypto.get('symbol')
        name = crypto.get('name')
        current_price = crypto.get('current_price')
        
        if symbol and current_price and name:
            # Generate stream ID automatically
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

def preview_stream_mappings():
    """Preview what stream IDs will be generated without sending data"""
    print("Previewing stream mappings...")
    
    crypto_data = fetch_crypto_prices()
    if not crypto_data:
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

def run_continuous(interval_seconds=120, interval_display="2 minutes"):
    """Run the app continuously with configurable interval"""
    print("Starting Crypto Price Monitor...")
    print(f"Will update prices every {interval_display}")
    print("Press Ctrl+C to stop")
    
    if not validate_config():
        return
    
    request_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Check rate limits (30 requests per minute, 10k per month)
            current_time = time.time()
            elapsed_minutes = (current_time - start_time) / 60
            
            if elapsed_minutes >= 1:  # Reset counter every minute
                request_count = 0
                start_time = current_time
            
            if request_count >= 25:  # Stay under 30/minute limit
                print("⏸️  Rate limit approaching, waiting...")
                time.sleep(60)
                request_count = 0
                start_time = time.time()
            
            # Process crypto data
            if process_crypto_data():
                request_count += 1
            
            # Wait for specified interval before next update
            print(f"Waiting {interval_display}... (Request {request_count}/25 this minute)")
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\nStopping Crypto Price Monitor...")
        print("✓ Shutdown complete")

def run_once():
    """Run once for testing"""
    print("Running single test...")
    
    if not validate_config():
        return
        
    success = process_crypto_data()
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed")

def main():
    """Main entry point"""
    print("=" * 50)
    print("  CRYPTOCURRENCY PRICE TO CYCLES APP")
    print("=" * 50)
    
    # Parse command line arguments for timeframe
    interval_seconds = 120  # Default 2 minutes
    interval_display = "2 minutes"
    
    # Look for timeframe flags in arguments
    timeframe_arg = None
    other_args = []
    
    for arg in sys.argv[1:]:
        if arg.startswith('--') and re.match(r'^--\d+[smhd]$', arg):
            timeframe_arg = arg
        else:
            other_args.append(arg)
    
    # Parse timeframe if provided
    if timeframe_arg:
        parsed_seconds, parsed_display = parse_timeframe(timeframe_arg)
        if parsed_seconds is not None:
            interval_seconds = parsed_seconds
            interval_display = parsed_display
            print(f"✓ Using custom timeframe: {interval_display}")
        else:
            print(f"✗ Invalid timeframe: {timeframe_arg}")
            print("Valid examples: --2m, --5m, --15m, --1h, --4h, --1d")
            print("Minimum interval is 2 minutes (--2m)")
            return
    
    # Handle other command line arguments
    if other_args:
        if other_args[0] == "--test":
            run_once()
        elif other_args[0] == "--preview":
            preview_stream_mappings()
        else:
            print("Unknown argument. Use --test or --preview")
    else:
        if len(sys.argv) == 1:  # No arguments provided
            print("\nModes:")
            print("  python crypto_cycles.py                    - Run continuously (2 minute default)")
            print("  python crypto_cycles.py --5m               - Run continuously every 5 minutes")
            print("  python crypto_cycles.py --1h               - Run continuously every 1 hour")
            print("  python crypto_cycles.py --test             - Run once for testing")
            print("  python crypto_cycles.py --preview          - Preview stream mappings")
            print("\nValid timeframes: --2m, --5m, --15m, --30m, --1h, --2h, --4h, --6h, --12h, --1d")
            
            choice = input("\nChoose mode (c)ontinuous/(t)est/(p)review: ").strip().lower()
            if choice in ['c', 'continuous']:
                run_continuous(interval_seconds, interval_display)
            elif choice in ['p', 'preview']:
                preview_stream_mappings()
            else:
                run_once()
        else:
            # Run continuous with custom timeframe
            run_continuous(interval_seconds, interval_display)

if __name__ == "__main__":
    main()