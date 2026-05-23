"""Parametric time model.

total_time = sum over micro-ops ( count_i * unit_time_i )

PRIMARY METHOD `fit()` — recover the time PER micro-operation by averaging the
count-normalised measured times across labelled panels. This matches what
Blufab actually provides (manually measured per-operation example times) and
gives clean, explainable unit times that don't get tangled when operations
always co-occur. It:
  * gives a time PER micro-operation (what Blufab asked for),
  * generalises to unseen panels (count ops from the drawing, multiply),
  * improves as more measured panels are added (just re-fit),
  * is explainable, cheap to run, and easy to maintain (pure Python).

ALTERNATIVE `fit_from_totals()` — ridge least squares using only total times
(for panels where you have a total but not per-op times, e.g. derived from a
video). Kept for the harder video-only case.
"""
import math

from .features import OP_KEYS


def fit(panels):
    """Fit unit times from per-operation measured times (each panel has
    'counts' and 'op_times_s')."""
    unit = {}
    rel_spread = []
    for k in OP_KEYS:
        ratios = [p["op_times_s"][k] / p["counts"][k]
                  for p in panels
                  if p["counts"].get(k, 0) > 0 and k in p.get("op_times_s", {})]
        if ratios:
            mean = sum(ratios) / len(ratios)
            unit[k] = mean
            if mean > 0 and len(ratios) > 1:
                sd = math.sqrt(sum((r - mean) ** 2 for r in ratios) / (len(ratios) - 1))
                rel_spread.append(sd / mean)
        else:
            unit[k] = 0.0

    # Confidence band: how much totals vary on the training panels.
    errs = []
    for p in panels:
        pred = sum(p["counts"][k] * unit[k] for k in OP_KEYS)
        if p.get("total_time_s"):
            errs.append(abs(pred - p["total_time_s"]) / p["total_time_s"])
    mape = sum(errs) / len(errs) if errs else 0.05
    return {"unit_times": unit, "mape": mape,
            "operator_spread": (sum(rel_spread) / len(rel_spread)) if rel_spread else 0.0}


def predict(panel, model):
    """Predict per-micro-op time + total + a confidence range for one panel."""
    c = panel["counts"]
    unit = model["unit_times"]
    per_op = {k: c.get(k, 0) * unit.get(k, 0.0) for k in OP_KEYS}
    total = sum(per_op.values())
    # Confidence band reflects both fit error and operator-to-operator variation.
    pct = max(model.get("mape", 0.0), model.get("operator_spread", 0.0), 0.03)
    return {
        "per_op": per_op,
        "total": total,
        "low": total * (1 - pct),
        "high": total * (1 + pct),
        "pct": pct,
    }


# ---------------------------------------------------------------------------
# Alternative: recover unit times from TOTAL times only (ridge least squares).
# ---------------------------------------------------------------------------
def _solve(A, b):
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        if abs(pv) < 1e-12:
            continue
        for r in range(n):
            if r != col:
                f = M[r][col] / pv
                for cc in range(col, n + 1):
                    M[r][cc] -= f * M[col][cc]
    return [M[i][n] / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0 for i in range(n)]


def fit_from_totals(panels, ridge=1.0):
    rows = [[p["counts"][k] for k in OP_KEYS] for p in panels]
    y = [p["total_time_s"] for p in panels]
    k = len(OP_KEYS)
    XtX = [[sum(rows[r][i] * rows[r][j] for r in range(len(rows))) for j in range(k)]
           for i in range(k)]
    for i in range(k):
        XtX[i][i] += ridge
    Xty = [sum(rows[r][i] * y[r] for r in range(len(rows))) for i in range(k)]
    w = _solve(XtX, Xty)
    return {"unit_times": {OP_KEYS[i]: max(0.0, w[i]) for i in range(k)}, "mape": 0.07,
            "operator_spread": 0.0}
