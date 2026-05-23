"""Plug-and-run: read Blufab-format files from data_in/ and produce estimates.

At the event you literally just replace the files in data_in/ with Blufab's and
run this. No code changes (only adjust NAME_MAP / column names if their labels differ).

Run:  python make_sample_inputs.py   (creates sample data_in/)
      python run_real_data.py
"""
import json
import os

from src.ingest import load_features_csv, load_microops_xlsx, load_orders_csv, build_panels
from src.model import fit, predict
from src.order_match import match_order
from src.features import OP_KEYS, OP_LABEL

HERE = os.path.dirname(__file__)
D = os.path.join(HERE, "data_in")


def main():
    features = load_features_csv(os.path.join(D, "panel_features.csv"))
    microops = load_microops_xlsx(os.path.join(D, "micro_operations.xlsx"))
    orders = load_orders_csv(os.path.join(D, "production_orders.csv"))

    panels = build_panels(features, microops)
    train = [p for p in panels if p["split"] == "train"]
    test = [p for p in panels if p["split"] == "test"]
    print(f"Ingested {len(panels)} panels from data_in/  "
          f"({len(train)} with measured times -> training, {len(test)} to estimate).")

    model = fit(train)
    print(f"Model fitted. Training fit error: {model['mape']*100:.1f}%\n")

    results = []
    for p in test:
        r = predict(p, model)
        order = match_order(p, orders)
        results.append({"panel": p["name"], "predicted_s": round(r["total"]),
                        "low_s": round(r["low"]), "high_s": round(r["high"]), "order": order})
        print(f"{p['name']:<8} -> {r['total']:>6.0f} s  (range {r['low']:.0f}-{r['high']:.0f}, "
              f"+/-{r['pct']*100:.0f}%)   order {order}")

    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("\nSaved results.json  ·  drop Blufab's files in data_in/ and re-run — no code changes.")


if __name__ == "__main__":
    main()
