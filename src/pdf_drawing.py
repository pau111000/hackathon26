"""Read a panel's features from its technical-drawing PDF (with a safe fallback).

At the event the drawings are vector PDFs in Portuguese. This tries to pull the
numbers automatically (dimensions + counts) via text + regex. If the PDF is odd
or the numbers aren't in the text layer, it returns None so the caller falls
back to manual entry / panel_features.csv — so it never blocks the demo.
"""
import re

# Portuguese + English terms -> regex fragments.
# Label-first patterns use [ \t:=]* (NEVER newlines) so the number must be on the
# same line as its label; number-first patterns use [ \t]* for the same reason.
PATTERNS = {
    "height_mm": [r"altura[ \t:=]*([0-9]{3,4})", r"height[ \t:=]*([0-9]{3,4})"],
    "width_mm":  [r"largura[ \t:=]*([0-9]{3,4})", r"width[ \t:=]*([0-9]{3,4})"],
    "n_studs":   [r"montantes[ \t:=]*([0-9]+)", r"studs[ \t:=]*([0-9]+)",
                  r"([0-9]+)[ \t]*montantes", r"([0-9]+)[ \t]*studs"],
    "n_noggins": [r"travessas[ \t:=]*([0-9]+)", r"noggins[ \t:=]*([0-9]+)",
                  r"([0-9]+)[ \t]*travessas", r"([0-9]+)[ \t]*noggins"],
    "n_boards":  [r"placas[ \t:=]*([0-9]+)", r"boards[ \t:=]*([0-9]+)",
                  r"([0-9]+)[ \t]*placas", r"([0-9]+)[ \t]*boards"],
    "n_frames":  [r"marcos[ \t:=]*([0-9]+)", r"frames[ \t:=]*([0-9]+)",
                  r"([0-9]+)[ \t]*marcos", r"([0-9]+)[ \t]*frames"],
}


def _find(text, pats):
    for p in pats:
        m = re.search(p, text)
        if m:
            return int(m.group(1))
    return None


def features_from_text(text):
    t = text.lower()
    name = None
    m = re.search(r"(p[qt][a-z0-9]+)", t)  # panel code like PQT9
    if m:
        name = m.group(1).upper()
    feats = {k: _find(t, pats) for k, pats in PATTERNS.items()}
    feats["name"] = name
    if feats.get("n_frames") is None:
        feats["n_frames"] = 1  # sensible default
    return feats


def extract_features(pdf_path):
    """Return a features dict, or None if confidence is too low (-> use fallback)."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
    except Exception:
        return None
    feats = features_from_text(text)
    # Need at least studs + boards + a dimension to trust it.
    if feats.get("n_studs") and feats.get("n_boards") and feats.get("height_mm"):
        return feats
    return None  # not confident -> caller uses manual / CSV fallback


# --- helper to create a SAMPLE drawing PDF (for testing the reader) ---
def make_sample_pdf(path, panel):
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(path)
    c.setFont("Helvetica", 12)
    lines = [
        "Projeto: Bathroom block A",
        f"Painel: {panel['name']}",
        f"Altura: {panel['height_mm']} mm    Largura: {panel.get('width_mm', 1500)} mm",
        f"Marcos: {panel['n_frames']}",
        f"Montantes: {panel['n_studs']}",
        f"Travessas: {panel['n_noggins']}",
        f"Placas: {panel['n_boards']}",
    ]
    y = 760
    for ln in lines:
        c.drawString(60, y, ln)
        y -= 22
    c.save()


if __name__ == "__main__":
    import json, os, tempfile
    here = os.path.dirname(__file__)
    panels = json.load(open(os.path.join(here, "..", "data", "panels.json")))["panels"]
    p = panels[8]  # PQT9
    tmp = os.path.join(tempfile.gettempdir(), "sample_drawing.pdf")
    try:
        make_sample_pdf(tmp, p)
        print("Sample PDF created. Extracted features:")
        print(extract_features(tmp))
        print("Real spec was:", {k: p[k] for k in ("name", "n_frames", "n_studs", "n_noggins", "n_boards", "height_mm")})
    except Exception as e:
        print("reportlab not available, testing text parser directly instead:", e)
        txt = f"Painel: {p['name']} Altura: {p['height_mm']} mm Montantes: {p['n_studs']} Travessas: {p['n_noggins']} Placas: {p['n_boards']} Marcos: {p['n_frames']}"
        print(features_from_text(txt))
