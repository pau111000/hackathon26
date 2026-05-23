"""Match a panel to its production order (the 15% MES-integration criterion).

In the real system you correlate the drawing/panel id with the production-order
extract. Here we match by panel name, with a dimensional fallback.
"""


def match_order(panel, orders):
    for o in orders:
        if panel["name"] in o.get("panels", []):
            return o["order_id"]
    # Fallback: nearest by area (placeholder for richer drawing-based matching).
    if not orders:
        return None
    return orders[0]["order_id"]
