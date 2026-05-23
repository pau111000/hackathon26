# External datasets — validate the method on real video

We validate the computer-vision approach on **public assembly datasets** (real
people assembling things) before pointing it at Blufab's real footage.

> Do **not** commit these datasets to the repo — they are multi-GB and licensed.
> This file just references where to get them.

## IKEA-ASM (recommended starting point)
Real videos of people assembling furniture (profiles, screws), with 33 action
classes, object segmentation and pose — very close to "assembling a frame on a table".

- Download (Google Drive folder): https://drive.google.com/drive/folders/1xkDp--QuUVxgl4oJjhCDb2FWNZTkYANq
- Project page: https://ikeaasm.github.io/
- Size: large (e.g. pose annotations ~6.6 GB, segmentation ~13.7 GB; videos bigger).
- **License: CC BY-NC 4.0** — research/educational use with attribution, non-commercial.
- Citation: Ben-Shabat et al., *The IKEA ASM Dataset*, arXiv:2007.00394, 2020.

## Other options
- **Assembly101** — fine-grained assembly actions + timings, multi-view. https://assembly-101.github.io/
- **HA4M** — industrial assembly (gear), RGB+depth. https://www.nature.com/articles/s41597-022-01843-z
- **IndustReal / MECCANO** — industrial procedure-step recognition.

## How to use
On a machine with a GPU (e.g. Vicen's server, or a Mac with `device="mps"`):

```bash
pip install ultralytics supervision
python validate_vision_yolo.py path/to/clip.mp4
```

Compare the detected micro-operation timeline against the dataset's labels to
prove the method works on real video. Then point the same pipeline at Blufab's
real overhead videos at the event.
