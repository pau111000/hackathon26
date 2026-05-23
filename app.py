"""Blufab time estimator — Streamlit dashboard.

Run:  python generate_data.py   (once)
      pip install -r requirements.txt
      streamlit run app.py
"""
import json
import os

import streamlit as st

from src.features import OP_KEYS, OP_LABEL, counts
from src.model import fit, predict
from src.order_match import match_order

st.set_page_config(page_title="Blufab time estimator", page_icon="🛠️", layout="centered")


@st.cache_data
def load():
    path = os.path.join(os.path.dirname(__file__), "data", "panels.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


data = load()
panels = data["panels"]
train = [p for p in panels if p["split"] == "train"]
test = [p for p in panels if p["split"] == "test"]
model = fit(train)
pct = max(model["mape"], model["operator_spread"], 0.03)

st.title("Panel production-time estimator")
st.caption("Time per micro-operation and total for a stud-wall panel, from its features.")
st.info("Synthetic demo data (15 panels). The model learns seconds per micro-operation "
        "from labelled panels, then estimates any panel by counting its operations.", icon="ℹ️")

with st.expander("What the model learned (unit times)", expanded=False):
    st.table({"micro-operation": [OP_LABEL[k] for k in OP_KEYS],
              "learned s/unit": [round(model["unit_times"][k], 1) for k in OP_KEYS]})
    st.write(f"Training fit error: {model['mape']*100:.1f}%  ·  confidence band: ±{pct*100:.0f}%")

st.subheader("Estimate a panel")
names = ["Custom"] + [p["name"] + (" (unseen)" if p["split"] == "test" else "") for p in panels]
choice = st.selectbox("Pick a panel", names)

if choice != "Custom":
    base = panels[names.index(choice) - 1]
else:
    base = {"n_frames": 1, "n_studs": 4, "n_noggins": 1, "n_boards": 1, "height_mm": 2600}

c1, c2, c3 = st.columns(3)
fr = c1.slider("Metal frames", 1, 2, base["n_frames"])
stp = c2.slider("Studs", 2, 8, base["n_studs"])
ng = c3.slider("Noggins", 0, 6, base["n_noggins"])
c4, c5 = st.columns(2)
bd = c4.slider("Plasterboards", 1, 2, base["n_boards"])
h = c5.select_slider("Height (mm)", [2400, 2600, 2800, 3000], base["height_mm"])

panel = {"n_frames": fr, "n_studs": stp, "n_noggins": ng, "n_boards": bd, "height_mm": h}
panel["counts"] = counts(panel)
r = predict(panel, model)

m1, m2 = st.columns(2)
m1.metric("Total time", f"{r['total']:.0f} s", f"≈ {r['total']/60:.1f} min")
m2.metric("Range", f"{r['low']:.0f}–{r['high']:.0f} s", f"±{pct*100:.0f}%")

if choice != "Custom":
    st.write(f"Production order: **{match_order(base, data['production_orders'])}**")
    same = all(base.get(k) == panel.get(k) for k in ("n_frames", "n_studs", "n_noggins", "n_boards", "height_mm"))
    if same and base.get("total_time_s"):
        err = abs(r["total"] - base["total_time_s"]) / base["total_time_s"] * 100
        st.write(f"Actual measured: **{base['total_time_s']:.0f} s**  ·  error **{err:.1f}%**")

st.markdown("**Breakdown per micro-operation**")
st.table({
    "micro-operation": [OP_LABEL[k] for k in OP_KEYS if panel["counts"][k] > 0],
    "count": [panel["counts"][k] for k in OP_KEYS if panel["counts"][k] > 0],
    "time (s)": [round(r["per_op"][k]) for k in OP_KEYS if panel["counts"][k] > 0],
})

st.subheader("Validation on unseen panels")
rows = {"panel": [], "predicted (s)": [], "actual (s)": [], "error %": []}
for p in test:
    rp = predict(p, model)
    rows["panel"].append(p["name"])
    rows["predicted (s)"].append(round(rp["total"]))
    rows["actual (s)"].append(round(p["total_time_s"]))
    rows["error %"].append(round(abs(rp["total"] - p["total_time_s"]) / p["total_time_s"] * 100, 1))
st.table(rows)
