"""방 평면도(SVG)를 기획서 9장 배치 표에서 그린다.

건축 평면도 양식: 두꺼운 벽, 문 열림 호, 방 이름, 치수선, 「① 감방 평면도」 제목.
좌표는 기획서와 같다(x 오른쪽 +, z 출구 쪽 −, 단위 m). 위쪽이 출구 방향.

    python make_plans.py        # 이 폴더에 01_감방.svg ~ 10_탈출.svg 를 다시 만든다
"""
import math
import os

FLOORS = {1: "B5", 2: "B5", 3: "B4", 4: "B4", 5: "B3", 6: "B3", 7: "B2", 8: "B2", 9: "B1", 10: "1F"}
INK, GUARD, START, CHECK, NOTE = "#111", "#c22", "#36c", "#2a7", "#555"
FONT = "Malgun Gothic, Apple SD Gothic Neo, sans-serif"
WALL = 0.3


class Plan:
    def __init__(self, num, name, facility, x0, x1, z0, z1, scale=40, margin=80):
        self.num, self.name, self.facility = num, name, facility
        self.x0, self.x1, self.z0, self.z1 = x0, x1, z0, z1
        self.s, self.m = scale, margin
        self.w = (x1 - x0) * scale + margin * 2
        self.h = (z1 - z0) * scale + margin * 2 + 110
        self.under, self.body, self.over = [], [], []

    def X(self, x):
        return self.m + (x - self.x0) * self.s

    def Y(self, z):
        return self.m + (z - self.z0) * self.s

    def L(self, metres):
        return metres * self.s

    def text(self, x, z, s, size=11, color=INK, anchor="middle", dy=0, weight="normal", layer=None):
        (layer if layer is not None else self.over).append(
            f'<text x="{self.X(x):.1f}" y="{self.Y(z) + dy:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{color}" font-weight="{weight}">{s}</text>')

    # ---- structure ----
    def rect(self, x0, z0, x1, z1, fill=INK, stroke="none", sw=1, layer=None, extra=""):
        (layer if layer is not None else self.body).append(
            f'<rect x="{self.X(x0):.1f}" y="{self.Y(z0):.1f}" width="{self.L(x1 - x0):.1f}" '
            f'height="{self.L(z1 - z0):.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def outer(self, gaps=()):
        """Outer walls drawn outside the room. gaps: (side, a, b) with side in N/S/E/W."""
        t = WALL
        x0, x1, z0, z1 = self.x0, self.x1, self.z0, self.z1
        sides = {
            "N": (x0 - t, x1 + t, "h", z0 - t, z0),
            "S": (x0 - t, x1 + t, "h", z1, z1 + t),
            "W": (z0 - t, z1 + t, "v", x0 - t, x0),
            "E": (z0 - t, z1 + t, "v", x1, x1 + t),
        }
        for side, (a, b, kind, c0, c1) in sides.items():
            cuts = sorted((g[1], g[2]) for g in gaps if g[0] == side)
            segs, cur = [], a
            for g0, g1 in cuts:
                segs.append((cur, g0))
                cur = g1
            segs.append((cur, b))
            for s0, s1 in segs:
                if s1 - s0 <= 0:
                    continue
                if kind == "h":
                    self.rect(s0, c0, s1, c1)
                else:
                    self.rect(c0, s0, c1, s1)

    def wall(self, x0, z0, x1, z1):
        self.rect(x0, z0, x1, z1)

    def hwall(self, z, x0, x1, gaps=(), t=WALL):
        cur = x0
        for g0, g1 in sorted(gaps):
            self.rect(cur, z - t / 2, g0, z + t / 2)
            cur = g1
        self.rect(cur, z - t / 2, x1, z + t / 2)

    def door(self, x0, x1, z, inward=1):
        """Double door in a horizontal wall; inward=+1 swings toward +z, -1 toward -z."""
        r = (x1 - x0) / 2
        tip = z + inward * r
        sweep_l, sweep_r = (0, 1) if inward > 0 else (1, 0)
        X0, X1, Y, Yt, Xm = self.X(x0), self.X(x1), self.Y(z), self.Y(tip), self.X((x0 + x1) / 2)
        R = self.L(r)
        self.body.append(
            f'<g fill="none" stroke="{INK}"><line x1="{X0}" y1="{Y}" x2="{X0}" y2="{Yt}" stroke-width="1.5"/>'
            f'<line x1="{X1}" y1="{Y}" x2="{X1}" y2="{Yt}" stroke-width="1.5"/>'
            f'<path d="M{X0},{Yt} A{R},{R} 0 0,{sweep_l} {Xm},{Y}" stroke-width="0.8"/>'
            f'<path d="M{X1},{Yt} A{R},{R} 0 0,{sweep_r} {Xm},{Y}" stroke-width="0.8"/></g>')

    def link(self, side, label, sub=""):
        """Corridor stub label outside the N or S door."""
        if side == "N":
            self.text(0, self.z0 - 1.2, label, 11, NOTE)
            if sub:
                self.text(0, self.z0 - 1.2, sub, 9, NOTE, dy=13)
        else:  # beside the south door, clear of the dimension line
            self.text(1.4, self.z1, (label + " " + sub).strip(), 10, NOTE, "start", dy=28)

    def shutter(self, x0, x1, z, label="셔터"):
        self.rect(x0, z - 0.12, x1, z + 0.12, fill="#fff", stroke=INK, sw=1, extra='stroke-dasharray="5 3"')
        self.text((x0 + x1) / 2, z, label, 9, NOTE, dy=20)

    def bars(self, x0, x1, z, gap=0.36):
        self.body.append(f'<line x1="{self.X(x0)}" y1="{self.Y(z)}" x2="{self.X(x1)}" y2="{self.Y(z)}" stroke="{INK}"/>')
        n = int((x1 - x0) / gap)
        for i in range(n + 1):
            x = x0 + 0.08 + i * gap
            if x <= x1:
                self.body.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(z):.1f}" r="2.2" fill="{INK}"/>')

    def pit(self, x0, z0, x1, z1, label="구덩이", at=None):
        self.rect(x0, z0, x1, z1, fill="url(#hatch)", stroke=INK, sw=0.8, layer=self.under)
        x, z = at or ((x0 + x1) / 2, (z0 + z1) / 2)
        self.over.append(f'<rect x="{self.X(x) - 90:.1f}" y="{self.Y(z) - 12:.1f}" width="180" height="22" fill="#fff"/>')
        self.text(x, z, f"{label} · 폭 {z1 - z0:g}m", 12, INK, dy=4)

    def raised(self, x0, z0, x1, z1, label, fill="#e4e4e4"):
        self.rect(x0, z0, x1, z1, fill=fill, stroke=INK, sw=1.2, layer=self.under)
        self.text((x0 + x1) / 2, z1, label, 10, NOTE, dy=-6)

    def pen(self, cx, cz, size=2.4, label="우리 −1.2 · 바닥 전체 발판"):
        h = size / 2
        self.rect(cx - h, cz - h, cx + h, cz + h, fill="url(#plate)", stroke=INK, sw=2, layer=self.under)
        self.rect(cx - h + 0.12, cz - h + 0.12, cx + h - 0.12, cz + h - 0.12, fill="none", stroke=INK, sw=0.7, layer=self.under)
        self.text(cx, cz + h, label, 9, NOTE, dy=13)

    def plate(self, cx, cz, size=1.5, label="발판"):
        h = size / 2
        self.rect(cx - h, cz - h, cx + h, cz + h, fill="url(#plate)", stroke=INK, sw=1.2)
        self.text(cx, cz + h, label, 9, NOTE, dy=12)

    def connect(self, a, b):
        """Plate-to-door link line (7.2)."""
        self.under.append(f'<polyline points="{" ".join(f"{self.X(x):.1f},{self.Y(z):.1f}" for x, z in [a, *b])}" '
                          f'fill="none" stroke="#d9a400" stroke-width="1.5" stroke-dasharray="2 4"/>')

    # ---- objects ----
    def box(self, x, z, size=0.6, heavy=False):
        h = size / 2
        fill = "#bbb" if heavy else "#fff"
        X0, Y0, S = self.X(x - h), self.Y(z - h), self.L(size)
        self.body.append(f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{S:.1f}" height="{S:.1f}" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>'
                         f'<path d="M{X0:.1f},{Y0:.1f} l{S:.1f},{S:.1f} M{X0 + S:.1f},{Y0:.1f} l{-S:.1f},{S:.1f}" stroke="{INK}" stroke-width="0.7"/>')

    def boxes(self, pts, label="상자"):
        for x, z in pts:
            self.box(x, z)
        for x, z in pts:
            self.text(x, z + 0.3, label, 9, NOTE, dy=12)

    def guard(self, x, z, letter, note="", facing=None, fan=False, color=GUARD):
        cx, cy = self.X(x), self.Y(z)
        if fan and facing is not None:
            r, half = self.L(5), math.radians(40)
            a = math.radians(facing)
            p1 = (cx + r * math.sin(a - half), cy - r * math.cos(a - half))
            p2 = (cx + r * math.sin(a + half), cy - r * math.cos(a + half))
            self.under.append(f'<path d="M{cx:.1f},{cy:.1f} L{p1[0]:.1f},{p1[1]:.1f} A{r:.1f},{r:.1f} 0 0,1 {p2[0]:.1f},{p2[1]:.1f} Z" '
                              f'fill="{color}" fill-opacity="0.08" stroke="{color}" stroke-opacity="0.35" stroke-dasharray="3 3"/>')
        if facing is not None:
            a = math.radians(facing)
            tip = (cx + 24 * math.sin(a), cy - 24 * math.cos(a))
            l = (cx + 14 * math.sin(a - 0.5), cy - 14 * math.cos(a - 0.5))
            rr = (cx + 14 * math.sin(a + 0.5), cy - 14 * math.cos(a + 0.5))
            self.over.append(f'<path d="M{l[0]:.1f},{l[1]:.1f} L{tip[0]:.1f},{tip[1]:.1f} L{rr[0]:.1f},{rr[1]:.1f} Z" fill="{color}"/>')
        self.over.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="14" fill="#fff" stroke="{color}" stroke-width="2"/>')
        self.text(x, z, letter, 12, color, dy=4, weight="bold")
        if note:
            for i, line in enumerate(note.split("\n")):
                self.over.append(f'<text x="{cx + 18:.1f}" y="{cy - 18 + 12 * i:.1f}" font-size="{10 if i == 0 else 9}" fill="{color}">{line}</text>')

    def patrol(self, a, b, letter, note="", color=GUARD):
        """Patrol a <-> b; the guard starts at a and first walks toward b."""
        self.under.append(f'<line x1="{self.X(a[0]):.1f}" y1="{self.Y(a[1]):.1f}" x2="{self.X(b[0]):.1f}" y2="{self.Y(b[1]):.1f}" '
                          f'stroke="{color}" stroke-width="1.2" stroke-dasharray="6 4" marker-end="url(#arrow)"/>')
        dx, dz = b[0] - a[0], b[1] - a[1]
        self.guard(a[0], a[1], letter, note, facing=math.degrees(math.atan2(dx, -dz)))

    def start(self, x, z, label="P 시작"):
        self.over.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(z):.1f}" r="7" fill="{START}"/>')
        self.text(x, z, label, 10, START, dy=-12)

    def checkpoint(self, x, z, label="체크포인트"):
        self.over.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(z):.1f}" r="16" fill="none" stroke="{CHECK}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        self.text(x, z, "S", 11, CHECK, dy=4, weight="bold")
        self.over.append(f'<text x="{self.X(x) + 22:.1f}" y="{self.Y(z) + 4:.1f}" font-size="10" fill="{CHECK}">{label}</text>')

    def exit(self, x, z, label="출구"):
        cx, cy = self.X(x), self.Y(z)
        pts = " ".join(f"{cx + (12 if i % 2 == 0 else 5) * math.sin(math.pi * i / 5):.1f},"
                       f"{cy - (12 if i % 2 == 0 else 5) * math.cos(math.pi * i / 5):.1f}" for i in range(10))
        self.over.append(f'<polygon points="{pts}" fill="{CHECK}"/>')
        self.over.append(f'<text x="{cx + 16:.1f}" y="{cy + 4:.1f}" font-size="10" fill="{CHECK}" font-weight="bold">{label}</text>')

    def spot(self, x, z, label="쏘는 자리"):
        cx, cy = self.X(x), self.Y(z)
        self.over.append(f'<g stroke="{START}" fill="none" stroke-width="1.2"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="8"/>'
                         f'<path d="M{cx - 12:.1f},{cy:.1f} h24 M{cx:.1f},{cy - 12:.1f} v24"/></g>')
        self.over.append(f'<text x="{cx + 14:.1f}" y="{cy + 14:.1f}" font-size="9" fill="{START}">{label}</text>')

    def dashed(self, pts, color=NOTE, label="", at=None):
        self.under.append(f'<polyline points="{" ".join(f"{self.X(x):.1f},{self.Y(z):.1f}" for x, z in pts)}" '
                          f'fill="none" stroke="{color}" stroke-width="1" stroke-dasharray="5 4"/>')
        if label and at:
            self.text(at[0], at[1], label, 9, color, anchor="start")

    def room(self, x, z, name, sub=""):
        self.text(x, z, name, 16, INK, layer=self.under)
        if sub:
            self.text(x, z, sub, 10, NOTE, dy=16, layer=self.under)

    def dims(self, extra=()):
        y = self.Y(self.z1) + 48
        x = self.X(self.x0) - 40
        g = [f'<line x1="{self.X(self.x0)}" y1="{y}" x2="{self.X(self.x1)}" y2="{y}"/>',
             f'<line x1="{self.X(self.x0)}" y1="{y - 8}" x2="{self.X(self.x0)}" y2="{y + 8}"/>',
             f'<line x1="{self.X(self.x1)}" y1="{y - 8}" x2="{self.X(self.x1)}" y2="{y + 8}"/>',
             f'<line x1="{x}" y1="{self.Y(self.z0)}" x2="{x}" y2="{self.Y(self.z1)}"/>',
             f'<line x1="{x - 8}" y1="{self.Y(self.z0)}" x2="{x + 8}" y2="{self.Y(self.z0)}"/>',
             f'<line x1="{x - 8}" y1="{self.Y(self.z1)}" x2="{x + 8}" y2="{self.Y(self.z1)}"/>']
        self.over.append(f'<g stroke="{NOTE}" stroke-width="0.8">{"".join(g)}</g>')
        self.over.append(f'<text x="{(self.X(self.x0) + self.X(self.x1)) / 2}" y="{y + 16}" font-size="11" text-anchor="middle" fill="#333">{self.x1 - self.x0:.1f}</text>')
        ym = (self.Y(self.z0) + self.Y(self.z1)) / 2
        self.over.append(f'<text x="{x - 10}" y="{ym}" font-size="11" text-anchor="middle" fill="#333" transform="rotate(-90 {x - 10} {ym})">{self.z1 - self.z0:.1f}</text>')
        for (a, b, z, label) in extra:  # horizontal sub-dimension above z
            yy = self.Y(z)
            self.over.append(f'<g stroke="{NOTE}" stroke-width="0.6"><line x1="{self.X(a)}" y1="{yy}" x2="{self.X(b)}" y2="{yy}"/>'
                             f'<line x1="{self.X(a)}" y1="{yy - 5}" x2="{self.X(a)}" y2="{yy + 5}"/><line x1="{self.X(b)}" y1="{yy - 5}" x2="{self.X(b)}" y2="{yy + 5}"/></g>')
            self.over.append(f'<text x="{(self.X(a) + self.X(b)) / 2}" y="{yy - 4}" font-size="9" text-anchor="middle" fill="#333">{label}</text>')

    def svg(self):
        w, h = self.w, self.h
        ty = self.Y(self.z1) + 95
        cx = w / 2
        title = (f'<circle cx="{cx - 80}" cy="{ty - 6}" r="13" fill="none" stroke="{INK}" stroke-width="1.3"/>'
                 f'<text x="{cx - 80}" y="{ty - 1}" font-size="14" text-anchor="middle" fill="{INK}">{self.num}</text>'
                 f'<text x="{cx - 60}" y="{ty + 1}" font-size="20" fill="{INK}">{self.facility} 평면도</text>'
                 f'<line x1="{cx - 100}" y1="{ty + 13}" x2="{cx + 120}" y2="{ty + 13}" stroke="{INK}" stroke-width="1.5"/>'
                 f'<line x1="{cx - 100}" y1="{ty + 17}" x2="{cx + 120}" y2="{ty + 17}" stroke="{INK}" stroke-width="0.6"/>'
                 f'<text x="{cx + 10}" y="{ty + 33}" font-size="10" text-anchor="middle" fill="{NOTE}">{FLOORS[self.num]} · {self.num}번 방 「{self.name}」 · S : 1/100 · 단위 m · 💡 초안</text>')
        north = (f'<g transform="translate({w - 40},36)"><path d="M0,-14 L7,8 L0,3 L-7,8 Z" fill="{INK}"/>'
                 f'<text x="0" y="24" font-size="9" text-anchor="middle" fill="#333">출구</text></g>')
        defs = ('<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<line x1="0" y1="0" x2="0" y2="8" stroke="{INK}" stroke-width="0.6"/></pattern>'
                '<pattern id="plate" width="6" height="6" patternUnits="userSpaceOnUse">'
                '<rect width="6" height="6" fill="#fff7d6"/><circle cx="3" cy="3" r="0.9" fill="#d9a400"/></pattern>'
                f'<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
                f'<path d="M0,0 L10,5 L0,10 Z" fill="{GUARD}"/></marker></defs>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" font-family="{FONT}">'
                f'{defs}<rect width="{w:.0f}" height="{h:.0f}" fill="#fff"/>'
                + "".join(self.under) + "".join(self.body) + "".join(self.over) + north + title + "</svg>\n")


def room1():
    p = Plan(1, "감방", "피험체 격리실", -6, 6, 2, 13)
    p.outer([("N", -1, 1)]); p.door(-1, 1, 2); p.link("N", "통로", "→ 2번 냉각조 통로")
    p.wall(-1.6, 8.9, -1.4, 12.2); p.wall(1.4, 8.9, 1.6, 12.2); p.wall(-1.6, 12, 1.6, 12.2)
    p.bars(-1.4, 1.4, 8.9); p.text(1.8, 8.9, "철창 (간격 0.36)", 10, NOTE, "start", dy=4)
    p.room(3, 7.4, "관찰 구역", "12 × 11m")
    p.text(0, 11.5, "격리 칸", 13); p.text(0, 11.5, "2.8 × 3.1m · 천장 2.6m", 9, NOTE, dy=24)
    p.boxes([(-3.2, 3.4), (-2.2, 3.4), (3.2, 3.4)])
    p.checkpoint(0, 5, "체크포인트 (감방을 나오는 순간)")
    p.guard(0, 7.4, "A", "잠든 경비 (총)\nZz · 감방 쪽을 봄", facing=180)
    p.start(0, 10.8)
    p.dims()
    return p


def room2():
    p = Plan(2, "구덩이", "냉각조 연결 통로", -6, 6, -11, 5)
    p.outer([("N", -1, 1), ("S", -1, 1)]); p.door(-1, 1, -11); p.door(-1, 1, 5, inward=-1)
    p.link("N", "계단 ↑ B4", "→ 3번 관찰 복도"); p.link("S", "통로 ← 1번 격리실")
    p.pit(-6, -4, 6, 2, "냉각조 (구덩이)")
    p.patrol((-4.2, -5.4), (4.2, -5.4), "B", "순찰 경비 B · 1.5m/s")
    p.patrol((4.5, -8.4), (-4.5, -8.4), "D", "순찰 경비 D · 1.4m/s")
    p.boxes([(-4, 3.6), (4, 3.6)])
    p.spot(-2, 3.2, "쏘는 자리 = 착지 방향")
    p.dashed([(-2, 3.2), (-0.6, -4)], NOTE, "B가 달려와 멈추는 곳", (-0.4, -4.4))
    p.checkpoint(-0.6, -5.0, "건너편 체크포인트")
    p.start(0, 4.4, "통로에서 들어옴")
    p.dims()
    return p


def room3():
    p = Plan(3, "순찰 복도", "관찰 복도", -4, 4, -10, 10)
    p.outer([("N", -1, 1), ("S", -1, 1)]); p.door(-1, 1, -10); p.door(-1, 1, 10, inward=-1)
    p.link("N", "통로", "→ 4번 관제 데크"); p.link("S", "계단 ← B5")
    p.wall(-0.25, -7, 0.25, -2); p.text(0.4, -4.5, "장비 랙 (가림벽)", 10, NOTE, "start")
    p.guard(0, -8, "F", "경비 F · 움직이지 않음", facing=180, fan=True)
    p.patrol((-2.5, 6), (-2.5, -5), "E", "순찰 경비 E · 1.2m/s")
    p.rect(-2.75, -5, -2.25, -3.7, fill="#c22", layer=p.under, extra='fill-opacity="0.25"')
    p.text(-3.6, -4.3, "E가 여기서 쓰러지면 F가 봄", 9, GUARD, "start", dy=-34)
    p.boxes([(1.5, 7.5), (3, 7.5)])
    p.text(2.2, -1, "동쪽 길", 13, INK); p.text(-2.2, 2.2, "서쪽 길", 13, INK)
    p.start(0, 9); p.checkpoint(0, 9, "")
    p.dims()
    return p


def room4():
    p = Plan(4, "단상", "관제 데크", -6, 6, -7, 6)
    p.outer([("S", -1, 1)]); p.door(-1, 1, 6, inward=-1); p.link("S", "통로 ← 3번 관찰 복도")
    p.raised(-3, -6, 3, -2, "관측 데크 +2.5 (위층, 올라갈 수 없음)")
    p.exit(0, -5, "위층 계단 ↑ B3")
    p.patrol((-2.2, -3.4), (2.2, -3.4), "C", "단상 경비 C · 1.0m/s")
    p.dashed([(-6, -0.4), (6, -0.4)], START, "여기보다 남쪽에서만 C가 보임 (가장자리에서 1.6m)", (-5.8, -0.6))
    p.spot(0, 0.6)
    p.boxes([(-4.5, 2), (4.5, 2)])
    p.start(0, 5)
    p.dims()
    return p


def room5():
    p = Plan(5, "압력판", "시료 저장고", -6, 6, -6, 6)
    p.outer([("N", -4, -2), ("S", -1, 1)]); p.door(-1, 1, 6, inward=-1)
    p.shutter(-4, -2, -6, "셔터 (발판이 눌린 동안 열림)")
    p.link("S", "계단 ← B4 관제 데크")
    p.raised(2, -6, 6, -2, "저장 랙 +2.5", fill="#d2d2d2")
    p.box(3, -4, size=1.0, heavy=True); p.text(3, -3.4, "시료 컨테이너 (무게)", 9, NOTE, dy=10)
    p.wall(2, -0.15, 6, 0.15); p.text(4, 0.15, "가림벽", 9, NOTE, dy=12)
    p.plate(3, 3, label="무게 감지 반출대 (발판)"); p.connect((3, 3), [(-1.5, 3), (-1.5, -5.6), (-3, -5.6)])
    p.box(1, 3); p.text(1, 3.3, "상자", 9, NOTE, dy=12)
    p.spot(-1, -2)
    p.start(0, 5); p.checkpoint(-3, -7.4, "셔터를 지난 곳")
    p.dims()
    return p


def room6():
    p = Plan(6, "셔터", "오염 제거 에어록", -6, 6, -8, 6)
    p.outer([("N", 3, 5), ("S", -1, 1)]); p.door(3, 5, -8); p.door(-1, 1, 6, inward=-1)
    p.link("S", "통로 ← 5번 시료 저장고"); p.text(4, -9.2, "화물 엘리베이터 ↑ B2", 10, NOTE)
    p.hwall(-2, -6, 6, gaps=[(-1, 1)]); p.shutter(-1, 1, -2, "셔터 (우리가 눌린 동안 열림)")
    p.pen(0, 3, label="세척 피트 −1.2 · 바닥 전체 발판 (우리)"); p.connect((1.2, 3), [(2, 3), (2, -1.6), (1, -1.6)])
    p.patrol((-4, -5), (4, -5), "G", "순찰 경비 G · 1.2m/s")
    p.dashed([(-1.6, -5), (-1, -2), (0, 1.8)], START, "", None); p.dashed([(1.6, -5), (1, -2), (0, 1.8)], START)
    p.text(2.3, -4.2, "우리에서 보이는 구간", 9, START, "start")
    p.room(-3.5, 2, "오염 구역"); p.room(-3.5, -6.5, "청정 구역")
    p.start(0, 5.2)
    p.dims()
    return p


def room7():
    p = Plan(7, "던진 상자", "원심분리기 홀", -6, 6, -10, 6)
    p.outer([("N", -1, 1), ("S", -1, 1)]); p.door(-1, 1, -10); p.door(-1, 1, 6, inward=-1)
    p.link("N", "통로", "→ 8번 중앙 관제실"); p.link("S", "엘리베이터 ← B3")
    p.pit(-6, -5, 6, 2, "분리기 수직갱 (구덩이)")
    p.room(0, -7.8, "건너편", "쏠 것이 아무것도 없음")
    p.boxes([(-4.5, 3.5), (4.5, 3.5)])
    p.spot(0, 2.6, "던지는 자리")
    p.under.append(f'<path d="M{p.X(0)},{p.Y(2.3)} Q{p.X(0)},{p.Y(-3)} {p.X(0)},{p.Y(-6.4)}" fill="none" stroke="{START}" stroke-width="1.2" stroke-dasharray="6 4"/>')
    p.text(0.3, -1.5, "최대 던지기 ≈ 8.2m", 9, START, "start", dy=-30)
    p.start(0, 5); p.checkpoint(0, -6.4, "건너편 체크포인트")
    p.dims()
    return p


def room8():
    p = Plan(8, "소리 없는 손", "중앙 관제실", -6, 6, -9, 6)
    p.outer([("S", -1, 1)]); p.door(-1, 1, 6, inward=-1); p.link("S", "통로 ← 7번 원심분리기 홀")
    p.raised(-3, -7, 3, 0, "관제 데스크 섬 +2.5 (둘레를 걸어서 돎)")
    p.exit(0, -6, "천장 사다리 ↑ B1")
    p.guard(0, -4.5, "L", "경비 L · 남쪽을 봄", facing=180, fan=True)
    p.patrol((-2.4, -0.8), (2.4, -0.8), "M", "경비 M · 1.0m/s")
    p.spot(0, -8.2, "던지는 자리 (단상 뒤)")
    p.boxes([(-5, 4), (5, 4)])
    p.dashed([(-5, 4), (-4.5, -1), (-4.5, -8), (-0.6, -8.2)], START, "단상 밑 옆길", (-5.8, -3))
    p.start(0, 5)
    p.dims()
    return p


def room9():
    p = Plan(9, "연쇄", "피험 챔버", -6, 6, -13, 8)
    p.outer([("N", -1, 1), ("S", -1, 1)]); p.door(-1, 1, 8, inward=-1)
    p.shutter(-1, 1, -13, "출구 문 → 비상계단 ↑ 1F (부스 발판이 눌린 동안 열림)")
    p.link("S", "사다리 ← B2")
    p.pit(-6, -8, 6, 4, "챔버 하부 기계실 (구덩이)", at=(0, 2.4))
    p.rect(-1.25, -2, 1.25, 0, fill="url(#plate)", stroke=INK, sw=1)
    p.wall(-1.45, -2.2, 1.45, -2); p.wall(-1.45, -2, -1.25, 0); p.wall(1.25, -2, 1.45, 0)
    p.text(0, 0, "피험 부스 · 바닥 전체 발판 (남쪽만 열림)", 9, NOTE, dy=14)
    p.box(-0.7, -1)
    p.connect((0.6, -1), [(3.5, -1), (3.5, -12.6), (1, -12.6)])
    p.patrol((-4.5, -10.5), (4.5, -10.5), "Q", "순찰 경비 Q · 1.2m/s")
    p.rect(-2.4, -11, 2.4, -10, fill=GUARD, layer=p.under, extra='fill-opacity="0.08"')
    p.text(0, -9.6, "이쪽에서 Q가 안 보이는 구간 (부스 그림자)", 9, GUARD)
    p.start(0, 7)
    p.dims()
    return p


def room10():
    p = Plan(10, "탈출", "출입 검문소", -7, 7, -22, 9, scale=30)
    p.outer([("S", -1, 1)]); p.door(-1, 1, 9, inward=-1); p.link("S", "비상계단 ← B1")
    p.hwall(-9, -7, 7, gaps=[(-1, 1)]); p.shutter(-1, 1, -9, "출구 셔터 (우리가 눌린 동안 열림)")
    p.pit(-7, -18, 7, -12, "차단 해자 (구덩이)")
    p.room(-4.5, -10.8, "검문 대기실")
    p.guard(0, -20, "Z", "연구 책임자 Z", color=START)
    p.exit(4.5, -21, "지상 출구")
    p.pen(-4, -4, label="검색 피트 −1.2 · 바닥 전체 발판 (우리)"); p.connect((-2.8, -4), [(-1.5, -4), (-1.5, -8.6)])
    p.patrol((-5.5, -7), (5.5, -7), "R", "방탄 경비 R · 1.2m/s")
    p.patrol((-1, 2), (-6, 2), "T", "경비 T · 1.2m/s")
    p.boxes([(3, 5), (4.5, 5)])
    p.spot(-1.75, -10.5, "마지막 한 발")
    p.start(0, 8)
    p.dims()
    return p


ROOMS = [(room1, "01_감방"), (room2, "02_구덩이"), (room3, "03_순찰복도"), (room4, "04_단상"), (room5, "05_압력판"),
         (room6, "06_셔터"), (room7, "07_던진상자"), (room8, "08_소리없는손"), (room9, "09_연쇄"), (room10, "10_탈출")]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for make, name in ROOMS:
        with open(os.path.join(here, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(make().svg())
        print(name)
