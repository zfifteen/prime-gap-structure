import json

def load_jsonl(filepath):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data

def save_jsonl(filepath, records):
    with open(filepath, 'w') as f:
        for r in records:
            f.write(json.dumps(r) + '\n')
            
def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
