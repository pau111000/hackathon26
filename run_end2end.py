"""END-TO-END demo: synthetic video -> REAL computer vision -> timeline ->
time model. Proves the whole pipeline executes (no GPU needed).

Run:  python generate_data.py   (once)
      python run_end2end.py
"""
import json
import os

from src.synth_video import generate, ZONES
from src.vision_lite import detect_timeline
from src.features import OP_KEYS, OP_LABEL
from src.model import fit, predict

ZONE_LABEL = {"prep": "Prep / measuring", "frame": "Frame (profiles)",
              "boards": "Plasterboards", "fasten": "Fastening (screwing)"}


def load():
    p = os.path.join(os.path.dirname(__file__), "data", "panels.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    data = load()
    train = [p for p in data["panels"] if p["split"] == "train"]
    panel = next(p for p in train if p.get("op_times_s"))  # a labelled panel

    print("=" * 66)
    print(f"STEP 1 — analyse the (synthetic) video of panel {panel['name']}")
    print("=" * 66)
    frames, zones, spf, schedule = generate(panel)
    print(f"Generated {len(frames)} frames ({frames[0].shape[1]}x{frames[0].shape[0]} px), "
          f"{spf}s per frame.")

    timeline = detect_timeline(frames, zones, spf)
    print("\nReal CV output — detected activity timeline (by zone):")
    obs_total = 0.0
    for s in timeline:
        obs_total += s["dur_s"]
        print(f"   {ZONE_LABEL[s['zone']]:<22} {s['start_s']:>6.0f}s -> {s['end_s']:>6.0f}s "
              f"= {s['dur_s']:>5.0f}s")
    print(f"\n   Observed total from video : {obs_total:.0f} s")
    print(f"   Actual panel total        : {panel['total_time_s']:.0f} s "
          f"(diff {abs(obs_total - panel['total_time_s'])/panel['total_time_s']*100:.1f}%)")

    print("\n" + "=" * 66)
    print("STEP 2 — predict a NEW unseen panel with the time model")
    print("=" * 66)
    model = fit(train)
    test = next(p for p in data["panels"] if p["split"] == "test")
    r = predict(test, model)
    print(f"Panel {test['name']}: predicted {r['total']:.0f} s "
          f"(range {r['low']:.0f}-{r['high']:.0f}, +/-{r['pct']*100:.0f}%)  | "
          f"actual {test['total_time_s']:.0f} s")
    print("\nPipeline OK: video -> real CV timeline -> time model. "
          "Swap synth_video for vision_yolo + real footage at the event.")


if __name__ == "__main__":
    main()
