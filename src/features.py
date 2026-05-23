"""Panel -> micro-operation counts.

Aligned with the official Casais/Blufab brief: stages are framing, positioning,
boarding, screwing and transitions; panel variables include dimensions, number
of profiles/boards, DRILLINGS and CLADDING/CERAMIC (the brief lists cladding
type, ceramic and drillings as inputs).

Key insight: the set of micro-operations is fixed; how many times each happens
scales with the panel. Learn the time per micro-operation -> estimate any panel
by counting its operations from the drawing/BOM.
"""

# (key, label, stage)
MICRO_OPS = [
    ("setup_jig",         "Set up jig",                "framing"),
    ("place_track",       "Place track (canal)",       "framing"),
    ("place_stud",        "Place stud (montante)",     "positioning"),
    ("place_noggin",      "Place noggin",              "positioning"),
    ("clinch_frame",      "Clinch / screw frame",      "screwing"),
    ("place_board",       "Place plasterboard",        "boarding"),
    ("screw_board",       "Screw board",               "screwing"),
    ("drill_hole",        "Drill hole",                "boarding"),
    ("place_ceramic",     "Place ceramic",             "boarding"),
    ("turn_and_finish",   "Turn, label & palletize",   "transitions"),
    ("unscrew_exception", "Unscrew (exception)",       "exception"),
]
OP_KEYS = [k for k, _, _ in MICRO_OPS]
OP_LABEL = {k: l for k, l, _ in MICRO_OPS}
OP_STAGE = {k: s for k, _, s in MICRO_OPS}


def counts(panel: dict) -> dict:
    """Counts of each micro-operation, derived from the drawing/BOM features."""
    n_frames = panel.get("n_frames", 1)
    studs = panel["n_studs"]
    noggins = panel["n_noggins"]
    boards = panel["n_boards"]
    height = panel["height_mm"]
    drillings = panel.get("n_drillings", 0)
    cladding = panel.get("cladding", "standard")

    tracks = 2 * n_frames
    screws_per_line = max(2, round(height / 300))
    screws = boards * studs * screws_per_line
    junctions = studs * 2 + noggins * 2
    ceramic = boards if cladding == "ceramic" else 0

    return {
        "setup_jig": 1,
        "place_track": tracks,
        "place_stud": studs,
        "place_noggin": noggins,
        "clinch_frame": junctions,
        "place_board": boards,
        "screw_board": screws,
        "drill_hole": drillings,
        "place_ceramic": ceramic,
        "turn_and_finish": 1,
        "unscrew_exception": round(0.05 * screws),
    }
