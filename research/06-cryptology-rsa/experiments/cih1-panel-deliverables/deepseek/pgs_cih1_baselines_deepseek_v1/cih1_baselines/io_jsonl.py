"""JSONL and JSON I/O helpers."""
import json

def load_jsonl(path):
    rows = []
    with open(path, 'r') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows

def write_jsonl(path, rows):
    with open(path, 'w') as fh:
        for row in rows:
            fh.write(json.dumps(row) + '\n')

def load_json(path):
    with open(path, 'r') as fh:
        return json.load(fh)

def save_json(path, data):
    with open(path, 'w') as fh:
        json.dump(data, fh, indent=2)
