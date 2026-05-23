"""Lightweight, REAL computer-vision timeline detector (pure numpy).

It looks at where motion happens on the table (frame-to-frame differences,
per zone) and turns that into a timeline of operations with start/end/duration.
This is genuine CV (motion segmentation) — just classic instead of deep, so it
runs anywhere with no GPU. In production we swap this for YOLO + tracking, but
the OUTPUT shape (a timeline of timed operations) is identical.
"""
import numpy as np


def detect_timeline(frames, zones, sec_per_frame, thresh=6.0):
    """Return a list of segments: {zone, start_s, end_s, dur_s}."""
    active = []
    prev = None
    for img in frames:
        cur = img.astype(np.int16)
        if prev is None:
            active.append(None)
            prev = cur
            continue
        diff = np.abs(cur - prev)
        prev = cur
        best, best_v = None, 0.0
        for z, (x0, y0, x1, y1) in zones.items():
            v = float(diff[y0:y1, x0:x1].mean())
            if v > best_v:
                best_v, best = v, z
        active.append(best if best_v > thresh else None)

    segments = []
    i = 0
    while i < len(active):
        z = active[i]
        if z is None:
            i += 1
            continue
        j = i
        while j < len(active) and active[j] == z:
            j += 1
        segments.append({
            "zone": z,
            "start_s": round(i * sec_per_frame, 1),
            "end_s": round(j * sec_per_frame, 1),
            "dur_s": round((j - i) * sec_per_frame, 1),
        })
        i = j
    return segments
