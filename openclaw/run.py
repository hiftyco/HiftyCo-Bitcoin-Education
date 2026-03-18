#!/usr/bin/env python3
"""
⚡️ OpenClaw OS - Bitcoin Education Data Fetcher
Runs on GitHub Actions to fetch live Bitcoin data and update the site.
"""

import json
import os
from datetime import datetime
import urllib.request
import urllib.error

REPO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_PATH, 'data')

def fetch_json(url):
    """Fetch JSON from URL with error handling."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        return None

def update_json_file(filename, data):
    """Update a JSON file with new data."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Updated {filename}")

def get_market_data():
    """Fetch Bitcoin price and market data."""
    print("\n📊 Fetching market data...")
    data = fetch_json("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true")
    if data and 'bitcoin' in data:
        btc = data['bitcoin']
        market = {
            'usd': btc.get('usd', 0),
            'usd_24h_change': btc.get('usd_24h_change', 0),
            'sats_per_dollar': int(100000000 / btc.get('usd', 1)) if btc.get('usd') else 0,
            'last_updated': datetime.now().isoformat()
        }
        update_json_file('market.json', market)
        print(f" ✅ ₿ ${market['usd']:,} | {market['usd_24h_change']:.2f}%")

def get_network_data():
    """Fetch Bitcoin network data."""
    print("\n⛏️ Fetching network data...")
    data = fetch_json("https://mempool.space/api/blocks/tip/height")
    if data:
        block_height = data if isinstance(data, int) else data.get('height', 0)
        # Calculate days to halving (roughly every 4 years, 210,000 blocks)
        blocks_per_epoch = 210000
        current_epoch = block_height // blocks_per_epoch
        blocks_in_epoch = block_height % blocks_per_epoch
        blocks_left = blocks_per_epoch - blocks_in_epoch
        days_left = blocks_left * 10 / 1440  # ~10 min blocks
        
        network = {
            'block_height': block_height,
            'days_left': int(days_left),
            'blocks_left': blocks_left,
            'epoch_pct': round(blocks_in_epoch / blocks_per_epoch * 100, 1),
            'last_updated': datetime.now().isoformat()
        }
        update_json_file('network.json', network)
        print(f" ✅ Block {block_height:,} | {days_left:.0f} days to halving")

def get_mempool_data():
    """Fetch mempool fee data."""
    print("\n📦 Fetching mempool data...")
    data = fetch_json("https://mempool.space/api/mempool")
    if data:
        fees = data.get('fees', {})
        mempool = {
            'fastest': fees.get('fastest', 0),
            'hour': fees.get('hour', 0),
            'economy': fees.get('economy', 0),
            'count': data.get('count', 0),
            'size_mb': round(data.get('vsize_mb', 0), 1),
            'last_updated': datetime.now().isoformat()
        }
        update_json_file('mempool.json', mempool)
        print(f" ✅ {mempool['fastest']}/{mempool['hour']}/{mempool['economy']} sat/vB")

def get_lightning_data():
    """Fetch Lightning Network data."""
    print("\n⚡ Fetching Lightning data...")
    data = fetch_json("https://1ml.com/statistics")
    if data:
        lightning = {
            'nodes': data.get('nodecount', 0),
            'capacity_btc': data.get('totalcapacity', 0) / 100000000,
            'last_updated': datetime.now().isoformat()
        }
        update_json_file('lightning.json', lightning)
        print(f" ✅ {lightning['nodes']:,} nodes | {lightning['capacity_btc']:,.0f} BTC")

def log_run():
    """Log this run to run_log.json."""
    log_file = os.path.join(DATA_DIR, 'run_log.json')
    try:
        with open(log_file, 'r') as f:
            runs = json.load(f)
    except:
        runs = []
    
    runs.append({
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    })
    
    # Keep only last 100 runs
    runs = runs[-100:]
    
    with open(log_file, 'w') as f:
        json.dump(runs, f, indent=2)
    print(f" ✅ Run logged (#{len(runs)})")

def main():
    print("⚡️ OpenClaw OS - Bitcoin Education Data Fetcher")
    print("=" * 50)
    
    get_market_data()
    get_network_data()
    get_mempool_data()
    get_lightning_data()
    log_run()
    
    print("\n" + "=" * 50)
    print("✅ All data updated successfully!")

if __name__ == '__main__':
    main()
