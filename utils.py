import json
from datetime import datetime

DATA_FILE = 'data.json'

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_lead_days(start, end):
    try:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        return (e - s).days
    except:
        return None

def is_late(actual, max_days, reference):
    try:
        a = datetime.fromisoformat(actual)
        r = datetime.fromisoformat(reference)
        return (a - r).days > max_days
    except:
        return False

def summarize_status(data):
    counts = {"NOT YET": 0, "ON PROGRESS": 0, "DONE": 0}
    for d in data:
        st = d.get("STATUS PENERIMAAN STNK", "NOT YET")
        if st in counts:
            counts[st] += 1
    return counts
