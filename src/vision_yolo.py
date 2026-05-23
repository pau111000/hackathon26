"""PRODUCTION computer-vision pipeline (skeleton).

This is the real-grade approach to run at the event on Blufab's overhead videos,
on a GPU (e.g. Vicen's server). It is NOT executed in the lightweight demo —
it needs ultralytics + a GPU + the real videos. The output is the SAME timeline
shape that vision_lite produces, so the rest of the system does not change.

Install (at the event):  pip install ultralytics
Approach:
  1) Calibrate the fixed camera (homography) to map pixels -> table millimetres.
  2) YOLO detects operators, tools, profiles, boards each frame.
  3) ByteTrack/BoT-SORT tracks them across frames.
  4) A state machine turns detections into micro-operation transitions + timings.
"""
from dataclasses import dataclass, field


# Panel assembly states (structural evolution of the panel).
STATES = ["EMPTY_TABLE", "FRAME_STARTED", "FRAME_DONE", "BOARDING", "FASTENING", "FINISHED"]


@dataclass
class StateMachine:
    state: str = "EMPTY_TABLE"
    events: list = field(default_factory=list)

    def update(self, detections, t):
        """Apply simple rules over detections to advance the state and log timed
        micro-operation events. Replace the heuristics below with the rules
        tuned on the real videos."""
        # Example rule sketch (pseudo-logic):
        # if many 'profile' objects appear and grow -> FRAME_STARTED ... FRAME_DONE
        # if 'board' object covers the frame -> BOARDING
        # if 'screwdriver' near board repeatedly -> FASTENING
        return self.events


def run(video_path, model_path="yolov8n.pt", conf=0.4):
    """Outline of the production run. Returns a timeline like vision_lite."""
    from ultralytics import YOLO  # imported lazily; only needed in production
    model = YOLO(model_path)
    sm = StateMachine()
    timeline = []
    # for result in model.track(source=video_path, tracker="bytetrack.yaml",
    #                           stream=True, conf=conf):
    #     detections = parse(result)
    #     sm.update(detections, t=result_time)
    # timeline = segments_from(sm.events)
    return timeline
