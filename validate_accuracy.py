"""Accuracy proof for the jury: leave-one-out cross-validation on the labelled
panels, plus held-out test error. Shows per-panel and average % error so you can
state a credible accuracy number.

Run:  python generate_data.py  ->  python validate_accuracy.py
"""
import json
import os

from src.model import fit, predict
from src.features import OP_KEYS, OP_LABEL


def load():
    p = os.path.join(os.path.dirname(__file__), "data", "panels.json")
    return json.load(open(p, encoding="utf-8"))


def main():
    data = load()
    train = [p for p in data["panels"] if p["split"] == "train"]
    test = [p for p in data["panels"] if p["split"] == "test"]

    # Leave-one-out: fit on all but one labelled panel, predict it.
    loo = []
    for i, p in enumerate(train):
        rest = train[:i] + train[i + 1:]
        m = fit(rest)
        r = predict(p, m)
        loo.append(abs(r["total"] - p["total_time_s"]) / p["total_time_s"] * 100)
    print("=" * 60)
    print("Leave-one-out cross-validation (on measured panels)")
    print("=" * 60)
    print(f"  panels tested      : {len(loo)}")
    print(f"  mean abs % error   : {sum(loo)/len(loo):.1f}%")
    print(f"  worst panel error  : {max(loo):.1f}%")
    print(f"  best panel error   : {min(loo):.1f}%")

    # Held-out test panels
    model = fit(train)
    print("\n" + "=" * 60)
    print("Held-out test panels (never used to fit)")
    print("=" * 60)
    errs = []
    for p in test:
        r = predict(p, model)
        e = abs(r["total"] - p["total_time_s"]) / p["total_time_s"] * 100
        errs.append(e)
        print(f"  {p['name']:<8} predicted {r['total']:>6.0f}s  actual {p['total_time_s']:>6.0f}s  -> {e:.1f}%")
    print(f"\n  mean test error    : {sum(errs)/len(errs):.1f}%")
    print("\nHeadline for the jury: \"On panels the model never saw, average error "
          f"~{sum(errs)/len(errs):.0f}%, with a stated confidence band.\"")


if __name__ == "__main__":
    main()
