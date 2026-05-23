"""Fit on labelled panels, predict the held-out test panels, report accuracy.

Run:  python generate_data.py   (once)
      python cli.py
"""
import json
import os

from src.features import OP_KEYS, OP_LABEL
from src.model import fit, predict
from src.order_match import match_order


def load():
    path = os.path.join(os.path.dirname(__file__), "data", "panels.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    data = load()
    panels = data["panels"]
    train = [p for p in panels if p["split"] == "train"]
    test = [p for p in panels if p["split"] == "test"]

    model = fit(train)
    gt = data["ground_truth_unit_times_s"]

    print("=" * 70)
    print(f"Fitted unit times from {len(train)} labelled panels (recovered vs truth)")
    print("=" * 70)
    print(f"{'micro-operation':<32}{'fitted s':>10}{'truth s':>10}")
    for k in OP_KEYS:
        print(f"{OP_LABEL[k]:<32}{model['unit_times'][k]:>10.1f}{gt[k]:>10.1f}")
    print(f"\nTrain fit error (MAPE): {model['mape']*100:.1f}%")

    print("\n" + "=" * 70)
    print(f"Predictions on {len(test)} UNSEEN test panels")
    print("=" * 70)
    errs = []
    for p in test:
        r = predict(p, model)
        actual = p["total_time_s"]
        err = abs(r["total"] - actual) / actual * 100
        errs.append(err)
        order = match_order(p, data["production_orders"])
        print(f"\n{p['name']}  ({p['n_studs']} studs, {p['n_boards']} board(s), "
              f"{p['counts']['screw_board']} screws)  -> order {order}")
        for k in OP_KEYS:
            if p["counts"][k]:
                print(f"   {OP_LABEL[k]:<30} {p['counts'][k]:>3} x  = {r['per_op'][k]:>6.1f} s")
        print(f"   {'TOTAL (predicted)':<30}        = {r['total']:>6.1f} s "
              f"(range {r['low']:.0f}-{r['high']:.0f} s, +/-{r['pct']*100:.0f}%)")
        print(f"   {'TOTAL (actual)':<30}        = {actual:>6.1f} s   |  error {err:.1f}%")

    print(f"\nMean absolute % error on unseen panels: {sum(errs)/len(errs):.1f}%")


if __name__ == "__main__":
    main()
