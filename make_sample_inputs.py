"""Create SAMPLE input files in Blufab's expected formats (so we can test the
ingestion before the event). Reads data/panels.json and writes data_in/.

Run:  python generate_data.py  (once)  ->  python make_sample_inputs.py
"""
import csv
import json
import os

from openpyxl import Workbook

from src.features import OP_KEYS, OP_LABEL

HERE = os.path.dirname(__file__)
data = json.load(open(os.path.join(HERE, "data", "panels.json"), encoding="utf-8"))
panels = data["panels"]
out = os.path.join(HERE, "data_in")
os.makedirs(out, exist_ok=True)

# 1) panel_features.csv — what we read from the drawings/BOM (ALL panels)
with open(os.path.join(out, "panel_features.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name", "n_frames", "n_studs", "n_noggins", "n_boards", "height_mm", "n_drillings", "cladding"])
    for p in panels:
        w.writerow([p["name"], p["n_frames"], p["n_studs"], p["n_noggins"], p["n_boards"],
                    p["height_mm"], p["n_drillings"], p["cladding"]])

# 2) micro_operations.xlsx — times matrix, ONLY for panels Blufab measured (train)
train = [p for p in panels if p["split"] == "train"]
wb = Workbook(); ws = wb.active; ws.title = "tempos"
ws.append(["micro_operation"] + [p["name"] for p in train])
for k in OP_KEYS:
    ws.append([OP_LABEL[k]] + [p.get("op_times_s", {}).get(k, "") for p in train])
wb.save(os.path.join(out, "micro_operations.xlsx"))

# 3) production_orders.csv
with open(os.path.join(out, "production_orders.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["order_id", "panels"])
    for o in data["production_orders"]:
        w.writerow([o["order_id"], ";".join(o["panels"])])

print("Wrote data_in/: panel_features.csv, micro_operations.xlsx, production_orders.csv")
print(f"  features for {len(panels)} panels, measured times for {len(train)} panels.")
