import json
from pathlib import Path
import csv

def read_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def write_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def read_prompt(prompt_name):
    path = Path(__file__).parent.parent / 'prompts' / f'{prompt_name}.txt'
    return path.read_text()

def append_trade(trade_data, trades_path):
    """Append trade to trades.json."""
    trades = read_json(trades_path)
    trades["trades"].append(trade_data)
    write_json(trades_path, trades)

def read_csv(filepath):
    """Read CSV file and return list of dicts."""
    with open(filepath, 'r') as f:
        return list(csv.DictReader(f))

def write_csv(filepath, data, fieldnames):
    """Write list of dicts to CSV."""
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
