import math

def dist(v1, v2):
    return math.sqrt(sum((a - b)**2 for a, b in zip(v1, v2)))

A = 1.715731736910394
B = 0.371214042564360
C = 1.353737018062712
sqrt2 = math.sqrt(2)

verts = [
    (1, 1, C), (-1, 1, C), (-1, -1, C), (1, -1, C),      # 0, 1, 2, 3
    (sqrt2*A, 0, B), (-sqrt2*A, 0, B),                  # 4, 5
    (0, sqrt2*A, B), (0, -sqrt2*A, B),                  # 6, 7
    (A, A, -B), (-A, A, -B), (-A, -A, -B), (A, -A, -B), # 8, 9, 10, 11
    (sqrt2, 0, -C), (-sqrt2, 0, -C),                    # 12, 13
    (0, sqrt2, -C), (0, -sqrt2, -C)                     # 14, 15
]

edges = []
for i in range(len(verts)):
    for j in range(i + 1, len(verts)):
        d = dist(verts[i], verts[j])
        if math.isclose(d, 2.0, rel_tol=1e-3):
            edges.append(tuple(sorted((i, j))))

triangles = []
for i in range(len(verts)):
    for j in range(i + 1, len(verts)):
        for k in range(j + 1, len(verts)):
            if tuple(sorted((i, j))) in edges and tuple(sorted((j, k))) in edges and tuple(sorted((i, k))) in edges:
                triangles.append((i, j, k))

squares = []
for i in range(len(verts)):
    for j in range(i + 1, len(verts)):
        for k in range(j + 1, len(verts)):
            for l in range(k + 1, len(verts)):
                v_subset = [i, j, k, l]
                e_subset = [e for e in edges if e[0] in v_subset and e[1] in v_subset]
                if len(e_subset) == 4:
                    counts = {}
                    for u, v in e_subset:
                        counts[u] = counts.get(u, 0) + 1
                        counts[v] = counts.get(v, 0) + 1
                    if all(c == 2 for c in counts.values()):
                        # Order indices in cycle
                        cycle = [i]
                        remaining = [j, k, l]
                        while remaining:
                            for r in remaining:
                                if tuple(sorted((cycle[-1], r))) in edges:
                                    cycle.append(r)
                                    remaining.remove(r)
                                    break
                        squares.append(tuple(cycle))

print("TRIANGLES:", triangles)
print("SQUARES:", squares)
