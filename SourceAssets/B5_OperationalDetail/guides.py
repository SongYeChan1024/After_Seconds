"""Read-only routing helpers for walk_plan.py AST loading. Author ???."""
def dense(ps, step=0.09):
    out = []
    for a, b in zip(ps, ps[1:]):
        a, b = (np.array(a), np.array(b))
        n = max(1, math.ceil(np.linalg.norm(b - a) / step))
        out.extend(((a + (b - a) * i / n).tolist() for i in range(n)))
    return out + [list(ps[-1])]

def path(room, start, end, code, departure=False):
    g = grids[room]
    n = g['size']
    step = g['step']

    def world(p):
        return [g['cx'] + (p[0] - g['half']) * step, g['cz'] + (p[1] - g['half']) * step]

    def ok(p):
        return 0 <= p[0] < n and 0 <= p[1] < n and (g['flags'][p[1] * n + p[0]] == '1') and (not reserved[room].get(p, set()) - {code})

    def nearest(pt):
        p = (round((pt[0] - g['cx']) / step) + g['half'], round((pt[1] - g['cz']) / step) + g['half'])
        cand = [(math.dist(world((p[0] + dx, p[1] + dz)), pt), (p[0] + dx, p[1] + dz)) for dx in range(-11, 12) for dz in range(-11, 12) if ok((p[0] + dx, p[1] + dz))]
        if not cand:
            raise RuntimeError(('No endpoint', room, code, pt))
        return min(cand)[1]
    a, b = (nearest(start), nearest(end))
    todo = [(0, a)]
    cost = {a: 0}
    prev = {}
    found = False
    while todo:
        _, p = heapq.heappop(todo)
        if p == b:
            found = True
            break
        for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            q = (p[0] + dx, p[1] + dz)
            if not ok(q) or (dx and dz and (not ok((p[0] + dx, p[1])) or not ok((p[0], p[1] + dz)))):
                continue
            val = cost[p] + math.hypot(dx, dz)
            if val < cost.get(q, 1000000000.0):
                cost[q] = val
                prev[q] = p
                heapq.heappush(todo, (val + math.dist(q, b), q))
    if not found and departure:
        reachable = {b}
        todo2 = [b]
        while todo2:
            pp = todo2.pop()
            for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                qq = (pp[0] + dx, pp[1] + dz)
                if ok(qq) and qq not in reachable:
                    reachable.add(qq)
                    todo2.append(qq)
        best = min(reachable, key=lambda p: math.dist(world(p), start))
        return path(room, world(best), end, code)
    if not found:
        raise RuntimeError(('No route', room, code, a, b))
    ps = [b]
    while ps[-1] != a:
        ps.append(prev[ps[-1]])
    ps = ps[::-1]
    simple = [ps[0]]
    i = 0
    while i < len(ps) - 1:
        k = i + 1
        for j in range(i + 2, len(ps)):
            seg = dense([world(ps[i]), world(ps[j])], step * 0.3)
            if all((ok((round((q[0] - g['cx']) / step) + g['half'], round((q[1] - g['cz']) / step) + g['half'])) for q in seg)):
                k = j
            else:
                break
        simple.append(ps[k])
        i = k
    return [world(p) for p in simple]
