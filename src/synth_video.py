"""Generate a SYNTHETIC top-down 'workstation' video (pure numpy, no heavy libs).

This stands in for the real Blufab overhead video so the computer-vision slice
has something real to process. Activity (a moving bright blob) happens in the
zone of each micro-operation, for a duration taken from the panel's example
times. The real system swaps this for the actual camera feed + YOLO.
"""
import numpy as np

from .features import OP_KEYS

H, W = 120, 160  # small frames keep it fast

# Rectangular zones of the table: (x0, y0, x1, y1)
ZONES = {
    "prep":   (0, 0, 160, 30),     # top band: jig setup, measuring
    "frame":  (0, 30, 80, 120),    # left: tracks, studs, noggins
    "boards": (80, 30, 160, 75),   # right-top: plasterboards
    "fasten": (80, 75, 160, 120),  # right-bottom: clinching, screwing
}

OP2ZONE = {
    "setup_jig": "prep", "turn_and_finish": "prep",
    "place_track": "frame", "place_stud": "frame", "place_noggin": "frame",
    "place_board": "boards", "drill_hole": "boards", "place_ceramic": "boards",
    "clinch_frame": "fasten", "screw_board": "fasten", "unscrew_exception": "fasten",
}


def generate(panel, sec_per_frame=2.0):
    """Return (frames, zones, sec_per_frame, schedule).

    schedule: list of (op_key, zone, n_frames, real_seconds) ground truth.
    """
    ot = panel.get("op_times_s", {})
    schedule = []
    for k in OP_KEYS:
        d = ot.get(k)
        if d:
            n = max(1, int(round(d / sec_per_frame)))
            schedule.append((k, OP2ZONE[k], n, d))

    rng = np.random.default_rng(0)
    frames = []
    t = 0
    for (k, zone, n, d) in schedule:
        x0, y0, x1, y1 = ZONES[zone]
        for _ in range(n):
            img = rng.integers(40, 60, size=(H, W), dtype=np.uint8)  # gray noisy table
            # a bright blob that moves a bit each frame -> creates motion in this zone
            cx = int(x0 + (x1 - x0) * (0.3 + 0.4 * abs(np.sin(t * 0.7))))
            cy = int(y0 + (y1 - y0) * (0.3 + 0.4 * abs(np.cos(t * 0.9))))
            img[max(0, cy - 5):cy + 5, max(0, cx - 5):cx + 5] = 255
            frames.append(img)
            t += 1
    return frames, ZONES, sec_per_frame, schedule
