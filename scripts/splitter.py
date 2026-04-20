import json
import math

with open("final_april_2026_v2.json", "r") as f:
    data = json.load(f)

institution_id = data["institution_id"]
items = data["items"]

# Calculate chunk size
num_splits = 3
chunk_size = math.ceil(len(items) / num_splits)

# Split and save
for i in range(num_splits):
    start = i * chunk_size
    end = start + chunk_size
    chunk_items = items[start:end]

    new_data = {"institution_id": institution_id, "items": chunk_items}

    with open(f"final_exam_{i+1}.json", "w") as f:
        json.dump(new_data, f, indent=2)

print("✅ Done splitting into 3 files")
