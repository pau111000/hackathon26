"""VALIDATE THE VISION ON REAL VIDEO — run this on your Mac (M3 Pro).

Goal: prove the computer-vision approach works on real assembly footage BEFORE
the event, using a public dataset (IKEA-ASM or Assembly101) or any short
top-down assembly clip. It detects + tracks objects and turns "activity per
zone" into a timeline of operations with durations — the same output our
pipeline expects.

This is NOT run in the prep sandbox (no GPU). On your Mac:

    pip install ultralytics supervision
    # download a short clip from IKEA-ASM (https://ikeaasm.github.io/) or
    # Assembly101 (https://assembly-101.github.io/), or any overhead assembly video
    python validate_vision_yolo.py path/to/clip.mp4
"""
import sys

import numpy as np

# Define table zones as fractions of the frame (x0,y0,x1,y1) in 0..1.
# Tune these to the camera once you have the real footage.
ZONES = {
    "prep":   (0.0, 0.0, 1.0, 0.25),
    "frame":  (0.0, 0.25, 0.5, 1.0),
    "boards": (0.5, 0.25, 1.0, 0.6),
    "fasten": (0.5, 0.6, 1.0, 1.0),
}


def run(video_path, conf=0.35, motion_zone_thresh=0.04):
    from ultralytics import YOLO
    model = YOLO("yolov8n.pt")  # small + fast; runs on Apple GPU via device="mps"

    active_per_frame = []
    fps = 25.0
    # model.track streams results; we use detections to find the busiest zone.
    for res in model.track(source=video_path, tracker="bytetrack.yaml",
                           device="mps", stream=True, conf=conf, verbose=False):
        if res.boxes is None or res.boxes.xyxyn is None:
            active_per_frame.append(None)
            continue
        boxes = res.boxes.xyxyn.cpu().numpy()  # normalised xyxy
        # count detections whose centre falls in each zone
        counts = {z: 0 for z in ZONES}
        for (x1, y1, x2, y2) in boxes:
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            for z, (zx0, zy0, zx1, zy1) in ZONES.items():
                if zx0 <= cx <= zx1 and zy0 <= cy <= zy1:
                    counts[z] += 1
        z = max(counts, key=counts.get)
        active_per_frame.append(z if counts[z] > 0 else None)
        if hasattr(res, "speed") and res.speed.get("fps"):
            fps = res.speed["fps"] or fps

    # segment into a timeline
    segs, i = [], 0
    while i < len(active_per_frame):
        z = active_per_frame[i]
        if z is None:
            i += 1
            continue
        j = i
        while j < len(active_per_frame) and active_per_frame[j] == z:
            j += 1
        segs.append({"zone": z, "start_s": round(i / fps, 1),
                     "end_s": round(j / fps, 1), "dur_s": round((j - i) / fps, 1)})
        i = j
    return segs


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: python validate_vision_yolo.py path/to/clip.mp4")
        sys.exit(0)
    for s in run(path):
        print(s)
    print("\nIf the timeline matches the dataset's labels, the method is validated. "
          "At the event, point this at Blufab's overhead video.")
