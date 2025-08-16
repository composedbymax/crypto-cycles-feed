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

# Configuration - Update these values
CYCLES_API_KEY = "REDACTED"  # Replace with your actual API key
CYCLES_WEBHOOK_URL = "https://api.cycle.tools/api/Stream/SubmitStreamData"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false"

# Cryptocurrency stream IDs - customize as needed
CRYPTO_STREAMS = {
    "bitcoin": "BTC_PRICE",
    "ethereum": "ETH_PRICE", 
    "binancecoin": "BNB_PRICE",
    "solana": "SOL_PRICE",
    "cardano": "ADA_PRICE",
    "avalanche-2": "AVAX_PRICE",
    "chainlink": "LINK_PRICE",
    "polygon": "MATIC_PRICE",
    "litecoin": "LTC_PRICE",
    "polkadot": "DOT_PRICE"
}

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
    
    for crypto in crypto_data:
        crypto_id = crypto.get('id')
        current_price = crypto.get('current_price')
        
        if crypto_id in CRYPTO_STREAMS and current_price:
            stream_id = CRYPTO_STREAMS[crypto_id]
            total_count += 1
            
            if send_to_cycles(stream_id, current_price, timestamp):
                success_count += 1
    
    print(f"Processed {success_count}/{total_count} cryptocurrencies successfully")
    return success_count > 0

def validate_config():
    """Validate configuration before running"""
    if CYCLES_API_KEY == "YOUR-API-KEY":
        print("Please update CYCLES_API_KEY with your actual API key")
        return False
    
    print(f"✓ Configuration validated")
    print(f"✓ Will track {len(CRYPTO_STREAMS)} cryptocurrencies")
    print(f"✓ Using Cycles API key: {CYCLES_API_KEY[:8]}...")
    return True

def run_continuous():
    """Run the app continuously with rate limiting"""
    print("Starting Crypto Price Monitor...")
    print("Will update prices every 2 minutes (respecting API rate limits)")
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
            
            # Wait 2 minutes before next update
            print(f"Waiting 2 minutes... (Request {request_count}/25 this minute)")
            time.sleep(120)  # 2 minutes
            
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
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_once()
    else:
        print("\nModes:")
        print("  python crypto_cycles.py         - Run continuously")
        print("  python crypto_cycles.py --test  - Run once for testing")
        
        choice = input("\nRun continuously? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            run_continuous()
        else:
            run_once()

if __name__ == "__main__":
    main()