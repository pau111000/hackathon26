"""Generate a SYNTHETIC panel dataset for the demo (aligned with the brief:
includes drillings and cladding/ceramic). Run:  python generate_data.py
"""
import json
import os
import random

from src.features import counts, OP_KEYS

random.seed(42)

# Ground-truth seconds per micro-operation (UNKNOWN to the model; for scoring).
GT = {
    "setup_jig": 45, "place_track": 18, "place_stud": 22, "place_noggin": 13,
    "clinch_frame": 7, "place_board": 40, "screw_board": 4.5, "drill_hole": 25,
    "place_ceramic": 60, "turn_and_finish": 50, "unscrew_exception": 11,
}

panels = []
for i in range(1, 16):
    n_studs = random.randint(2, 6)
    n_frames = 1 if n_studs <= 4 else 2
    spec = {
        "id": f"P{i:02d}", "name": f"PQT{i}", "project": "Bathroom block A",
        "width_mm": random.choice([600, 800, 1000, 1200, 1500, 1800, 2200, 2600, 3000]),
        "height_mm": random.choice([2400, 2600, 2800, 3000]),
        "n_frames": n_frames, "n_studs": n_studs,
        "n_noggins": random.randint(0, max(0, n_studs - 1)),
        "n_boards": random.choice([1, 1, 2]),
        "n_drillings": random.randint(0, 6),
        "cladding": random.choice(["standard", "standard", "ceramic"]),
    }
    c = counts(spec)
    op_factor = random.choice([0.92, 0.96, 1.0, 1.04, 1.08])  # operator experience
    op_times = {}
    for k in OP_KEYS:
        if c[k] > 0:
            opn = random.uniform(-0.05, 0.05)
            op_times[k] = round(c[k] * GT[k] * op_factor * (1 + opn), 1)
    spec["counts"] = c
    spec["op_times_s"] = op_times
    spec["operator"] = "senior" if op_factor < 1 else ("junior" if op_factor > 1 else "mid")
    spec["total_time_s"] = round(sum(op_times.values()), 1)
    spec["split"] = "train" if i <= 12 else "test"
    panels.append(spec)

orders = [
    {"order_id": "PO-1001", "panels": [p["name"] for p in panels[0:5]]},
    {"order_id": "PO-1002", "panels": [p["name"] for p in panels[5:10]]},
    {"order_id": "PO-1003", "panels": [p["name"] for p in panels[10:]]},
]

out = {"note": "SYNTHETIC demo data. Not real Blufab data.", "micro_ops": OP_KEYS,
       "ground_truth_unit_times_s": GT, "panels": panels, "production_orders": orders}

os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
path = os.path.join(os.path.dirname(__file__), "data", "panels.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print(f"Wrote {path} with {len(panels)} panels "
      f"({sum(1 for p in panels if p['split']=='train')} train / "
      f"{sum(1 for p in panels if p['split']=='test')} test).")
