"""Low walls (block movement, not sight) around walkable floor that borders a drop."""
import numpy as np, cv2, math
import paintkit as K
def ledge_walls(m, gaps=(), q=4, eps=1.6):
    lab, ids = K.material_map(m)
    walk = (lab >= 2).astype(np.uint8)[::q, ::q] * 255
    walk = cv2.morphologyEx(walk, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cs, _ = cv2.findContours(walk, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    S = 100 / q; gw, gh = m.w, m.h; n = 0
    for c in cs:
        if cv2.contourArea(c) < S * S * 0.6: continue
        a = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float) / S
        pts = list(map(tuple, a)) + [tuple(a[0])]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if (x0 < 0.15 and x1 < 0.15) or (y0 < 0.15 and y1 < 0.15) or (x0 > gw - 0.3 and x1 > gw - 0.3) or (y0 > gh - 0.3 and y1 > gh - 0.3): continue
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            if any(gx0 <= mx <= gx1 and gy0 <= my <= gy1 for gx0, gy0, gx1, gy1 in gaps): continue
            m.walls.append({"c": [round(x0 * 100), round(y0 * 100), round(x1 * 100), round(y1 * 100)], "kind": "invisible", "sight": "none"}); n += 1
    return n
