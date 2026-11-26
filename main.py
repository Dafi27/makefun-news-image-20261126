#!/usr/bin/env python3
"""news-image-20261126: draws a front-page summary of Thursday 26 November
2026 world news as a 1024x1024 PNG. Pure standard library, no network,
fully deterministic: two runs write byte-identical files.

Layout: masthead, one lead story, six story cards, a ticker strip, footer.
Everything is drawn with this file's own 5x7 bitmap font and its own
zlib PNG encoder.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, authored here. Each glyph is 7 rows of 5 bits ("1" = ink).
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "11001", "10101", "10011", "10011", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "a": ["00000", "00000", "01110", "00001", "01111", "10001", "01111"],
    "b": ["10000", "10000", "11110", "10001", "10001", "10001", "11110"],
    "c": ["00000", "00000", "01111", "10000", "10000", "10000", "01111"],
    "d": ["00001", "00001", "01111", "10001", "10001", "10001", "01111"],
    "e": ["00000", "00000", "01110", "10001", "11111", "10000", "01110"],
    "f": ["00110", "01000", "01000", "11110", "01000", "01000", "01000"],
    "g": ["00000", "01111", "10001", "10001", "01111", "00001", "01110"],
    "h": ["10000", "10000", "11110", "10001", "10001", "10001", "10001"],
    "i": ["00000", "00100", "00000", "01100", "00100", "00100", "01110"],
    "j": ["00000", "00010", "00000", "00110", "00010", "00010", "01100"],
    "k": ["10000", "10000", "10010", "10100", "11000", "10100", "10010"],
    "l": ["01100", "00100", "00100", "00100", "00100", "00100", "01110"],
    "m": ["00000", "00000", "11010", "10101", "10101", "10101", "10101"],
    "n": ["00000", "00000", "11110", "10001", "10001", "10001", "10001"],
    "o": ["00000", "00000", "01110", "10001", "10001", "10001", "01110"],
    "p": ["00000", "11110", "10001", "10001", "11110", "10000", "10000"],
    "q": ["00000", "01111", "10001", "10001", "01111", "00001", "00001"],
    "r": ["00000", "00000", "10110", "11001", "10000", "10000", "10000"],
    "s": ["00000", "00000", "01111", "10000", "01110", "00001", "11110"],
    "t": ["00000", "01000", "01000", "11110", "01000", "01000", "00110"],
    "u": ["00000", "00000", "10001", "10001", "10001", "10001", "01111"],
    "v": ["00000", "00000", "10001", "10001", "10001", "01010", "00100"],
    "w": ["00000", "00000", "10001", "10001", "10101", "10101", "01010"],
    "x": ["00000", "00000", "10001", "01010", "00100", "01010", "10001"],
    "y": ["00000", "10001", "10001", "10001", "01111", "00001", "01110"],
    "z": ["00000", "00000", "11111", "00010", "00100", "01000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["01110", "10001", "00001", "00110", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "00100", "00100", "00100"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00000", "00100"],
    ",": ["00000", "00000", "00000", "00000", "00000", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    ":": ["00000", "00000", "00100", "00000", "00000", "00100", "00000"],
    ";": ["00000", "00000", "00100", "00000", "00000", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "%": ["10001", "10010", "00010", "00100", "01000", "01001", "10001"],
    "&": ["01100", "10010", "10010", "01000", "10101", "10010", "01101"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "+": ["00000", "00100", "00100", "01110", "00100", "00100", "00000"],
    "=": ["00000", "00000", "01110", "00000", "01110", "00000", "00000"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "#": ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    "@": ["01110", "10001", "10111", "10101", "10111", "10000", "01110"],
    "*": ["00000", "01010", "00100", "11111", "00100", "01010", "00000"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    "[": ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
    "]": ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
    "<": ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    ">": ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    "\u2022": ["00000", "00000", "00000", "01110", "01110", "00000", "00000"],
    "\u2014": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "\u2013": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "\u2019": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
}
BLANK = ["00000"] * 7


def text_width(text, scale):
    """Pixel width of text at the given integer scale."""
    return len(text) * 6 * scale - scale


def wrap(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:(y * self.w + x1) * 3] = color * (x1 - x0)

    def rect_outline(self, x0, y0, x1, y1, color, t=1):
        self.fill_rect(x0, y0, x1, y0 + t, color)
        self.fill_rect(x0, y1 - t, x1, y1, color)
        self.fill_rect(x0, y0, x0 + t, y1, color)
        self.fill_rect(x1 - t, y0, x1, y1, color)

    def hline(self, x0, x1, y, color, t=1):
        self.fill_rect(x0, y, x1, y + t, color)

    def vline(self, x, y0, y1, color, t=1):
        self.fill_rect(x, y0, x + t, y1, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line with square brush of thickness t."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = t // 2
        while True:
            self.fill_rect(x - half, y - half, x - half + t, y - half + t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def filled_circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            dx = int((r * r - (y - cy) ** 2) ** 0.5) if abs(y - cy) <= r else 0
            self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, color)

    def circle_outline(self, cx, cy, r, color, t=2):
        for k in range(t):
            rr = r - k
            steps = max(8, rr * 6)
            for i in range(steps):
                import math
                a = 2 * math.pi * i / steps
                self.set(cx + int(rr * math.cos(a)), cy + int(rr * math.sin(a)), color)

    def triangle(self, pts, color):
        """Filled triangle from three (x, y) points."""
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)
        for y in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by) or (y == ymax and y == max(ay, by)):
                    xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
            if len(xs) >= 2:
                self.fill_rect(int(min(xs)), y, int(max(xs)) + 1, y + 1, color)

    def draw_text(self, x, y, text, scale, color):
        """Draw text at top-left (x, y); returns the pixel width drawn."""
        cx = x
        for ch in text:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       cx + col * scale + scale,
                                       y + row * scale + scale, color)
            cx += 6 * scale
        return cx - x - scale

    def draw_text_centered(self, cx, y, text, scale, color):
        w = text_width(text, scale)
        return self.draw_text(cx - w // 2, y, text, scale, color)


# -------------------------------------------------------------- icons -----
# Small pictograms drawn with the canvas primitives. Each takes the top-left
# corner of a square box and its size; all coordinates are relative.

def icon_flame(cv, x, y, s, c1, c2):
    # Teardrop flame: outer body + inner tongue.
    cx = x + s // 2
    cv.filled_circle(cx, y + int(s * 0.62), int(s * 0.30), c1)
    cv.triangle([(cx - int(s * 0.30), y + int(s * 0.62)),
                 (cx + int(s * 0.30), y + int(s * 0.62)),
                 (cx + int(s * 0.10), y + int(s * 0.08))], c1)
    cv.filled_circle(cx, y + int(s * 0.68), int(s * 0.15), c2)
    cv.triangle([(cx - int(s * 0.15), y + int(s * 0.68)),
                 (cx + int(s * 0.15), y + int(s * 0.68)),
                 (cx, y + int(s * 0.38))], c2)


def icon_jet(cv, x, y, s, c):
    # Side-view jet: fuselage, nose, swept wings, tail fin.
    cy = y + s // 2
    cv.fill_rect(x + int(s * 0.10), cy - int(s * 0.07),
                 x + int(s * 0.92), cy + int(s * 0.07), c)
    cv.triangle([(x + int(s * 0.88), cy - int(s * 0.07)),
                 (x + int(s * 0.88), cy + int(s * 0.07)),
                 (x + int(s * 1.00), cy)], c)
    cv.triangle([(x + int(s * 0.45), cy),
                 (x + int(s * 0.70), cy),
                 (x + int(s * 0.52), cy + int(s * 0.30))], c)
    cv.triangle([(x + int(s * 0.45), cy),
                 (x + int(s * 0.68), cy),
                 (x + int(s * 0.55), cy - int(s * 0.28))], c)
    cv.triangle([(x + int(s * 0.12), cy - int(s * 0.05)),
                 (x + int(s * 0.26), cy - int(s * 0.05)),
                 (x + int(s * 0.16), cy - int(s * 0.30))], c)


def icon_radiation(cv, x, y, s, c):
    # Trefoil: centre disc + three blades at 90/210/330 degrees.
    import math
    cx = x + s // 2
    cy = y + s // 2
    r = int(s * 0.34)
    for ang in (90, 210, 330):
        a = math.radians(ang)
        bx = cx + int(r * 0.62 * math.cos(a))
        by = cy - int(r * 0.62 * math.sin(a))
        cv.filled_circle(bx, by, int(s * 0.16), c)
        cv.line(cx, cy, bx, by, c, max(2, s // 12))
    cv.filled_circle(cx, cy, int(s * 0.11), c)
    cv.circle_outline(cx, cy, int(s * 0.44), c, max(2, s // 16))


def icon_satellite(cv, x, y, s, c):
    # Body + two solar panels + dish.
    cx = x + s // 2
    cy = y + s // 2
    cv.fill_rect(cx - int(s * 0.10), cy - int(s * 0.10),
                 cx + int(s * 0.10), cy + int(s * 0.10), c)
    cv.fill_rect(x + int(s * 0.02), cy - int(s * 0.16),
                 cx - int(s * 0.14), cy + int(s * 0.16), c)
    cv.fill_rect(cx + int(s * 0.14), cy - int(s * 0.16),
                 x + int(s * 0.98), cy + int(s * 0.16), c)
    cv.line(cx, cy - int(s * 0.10), cx + int(s * 0.22), cy - int(s * 0.34), c, 3)
    cv.filled_circle(cx + int(s * 0.24), cy - int(s * 0.36), int(s * 0.06), c)


def icon_umbrella(cv, x, y, s, c):
    # Rain umbrella: canopy arc, stick, hook, raindrops.
    cx = x + s // 2
    cy = y + int(s * 0.48)
    r = int(s * 0.34)
    for yy in range(cy - r, cy + 1):
        dx = int((r * r - (yy - cy) ** 2) ** 0.5)
        cv.fill_rect(cx - dx, yy, cx + dx + 1, yy + 1, c)
    cv.vline(cx, cy, y + int(s * 0.88), c, 3)
    cv.hline(cx, cx + int(s * 0.12), y + int(s * 0.88), c, 3)
    cv.vline(cx + int(s * 0.12), y + int(s * 0.80), y + int(s * 0.88), c, 3)
    for dx, dy in ((-0.38, 0.10), (0.38, 0.16), (-0.18, 0.02)):
        cv.fill_rect(cx + int(s * dx), y + int(s * dy),
                     cx + int(s * dx) + 3, y + int(s * dy) + 7, c)


def icon_oil(cv, x, y, s, c):
    # Pumpjack silhouette: base, tower, beam, horse head.
    base = y + int(s * 0.86)
    cv.fill_rect(x + int(s * 0.06), base, x + int(s * 0.94), base + int(s * 0.06), c)
    cv.line(x + int(s * 0.30), base, x + int(s * 0.52), y + int(s * 0.14), c, 4)
    cv.line(x + int(s * 0.52), y + int(s * 0.14), x + int(s * 0.62), base, c, 4)
    cv.line(x + int(s * 0.30), y + int(s * 0.22), x + int(s * 0.92), y + int(s * 0.10), c, 5)
    cv.filled_circle(x + int(s * 0.94), y + int(s * 0.14), int(s * 0.07), c)
    cv.vline(x + int(s * 0.94), y + int(s * 0.20), base - int(s * 0.10), c, 3)


def icon_globe(cv, x, y, s, c, c2):
    # Globe: outline, equator, meridian, land blobs.
    cx = x + s // 2
    cy = y + s // 2
    r = int(s * 0.44)
    cv.circle_outline(cx, cy, r, c, 3)
    cv.hline(cx - r, cx + r, cy, c, 2)
    cv.vline(cx, cy - r, cy + r, c, 2)
    cv.filled_circle(cx - int(s * 0.20), cy - int(s * 0.20), int(s * 0.10), c2)
    cv.filled_circle(cx + int(s * 0.18), cy + int(s * 0.16), int(s * 0.12), c2)
    cv.filled_circle(cx + int(s * 0.22), cy - int(s * 0.18), int(s * 0.07), c2)


# --------------------------------------------------------- PNG encoder ----
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    """Encode the canvas as a deterministic RGB PNG (filter 0 per row)."""
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        i = (yy * cv.w) * 3
        raw += cv.px[i:i + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ------------------------------------------------------------- palette ----
PAPER = bytes((247, 243, 234))
INK = bytes((26, 26, 26))
NAVY = bytes((18, 41, 77))
RED = bytes((179, 38, 30))
GOLD = bytes((201, 162, 39))
CARD = bytes((255, 253, 247))
MUTED = bytes((90, 90, 90))
TINT = bytes((233, 227, 211))
CREAM = bytes((247, 243, 234))
DARKNAVY = bytes((10, 26, 52))

# ------------------------------------------------------------- stories ----
# All events happened on, or were first reported on, Thursday 26 November
# 2026 (sources in the footer): Reuters world news summary, KCNA, the FCC,
# Egypt's health ministry.
LEAD_KICKER = "LEAD STORY \u2014 WASHINGTON"
LEAD_HEADLINE = "US PROPOSES SWEEPING NEW TARIFFS ON 14 TRADING PARTNERS"
LEAD_DECK = ("Trump unveils country-specific duties after an eight-month "
             "probe: China faces 20%, rising to 40% if the truce lapses on "
             "10 January. Nothing takes effect before a hearing on "
             "25 January.")

# (kicker, headline, body, icon)
STORIES = [
    ("EGYPT \u2014 DISASTER",
     "Tanker fire kills 31 on Cairo ring road",
     "A fuel tanker overturned and burst into flames on a Cairo highway. "
     "31 died, 21 hurt.",
     "flame"),
    ("SAUDI ARABIA \u2014 CONFLICT",
     "Houthis strike Saudi oil heartland",
     "Yemen's Houthis say they hit the Ras Tanura refinery and Riyadh's "
     "finance district. Oil rose.",
     "oil"),
    ("UKRAINE \u2014 WAR",
     "Ukraine says it hit five jets at airbase",
     "Kyiv says drones struck Savasleyka airfield in Russia, as missiles "
     "hit the capital.",
     "jet"),
    ("NORTH KOREA \u2014 NUCLEAR",
     "Kim orders wider nuclear spread",
     "Kim Jong Un told nuclear researchers to deploy tactical weapons more "
     "widely, KCNA said.",
     "radiation"),
    ("SPACE \u2014 TECHNOLOGY",
     "SpaceX cleared for a million satellites",
     "The FCC authorised up to a million satellites to run data centres "
     "in orbit. Scientists object.",
     "satellite"),
    ("UNITED STATES \u2014 THANKSGIVING",
     "Macy's 100th parade postponed in a first",
     "The centenary Thanksgiving parade in New York moves to Saturday as "
     "a nor'easter hits.",
     "umbrella"),
]

TICKER_1 = ("ALSO TODAY: US economy up 4.3% in Q3  \u2022  First Pakistani "
            "boards Tiangong")
TICKER_2 = "Nearly 2,000 migrants reach the Canary Islands in a day"
FOOTER = "As reported on Thursday 26 November 2026. Sources: Reuters, KCNA, FCC."

ICONS = {
    "flame": lambda cv, x, y, s: icon_flame(cv, x, y, s, RED, GOLD),
    "oil": lambda cv, x, y, s: icon_oil(cv, x, y, s, INK),
    "jet": lambda cv, x, y, s: icon_jet(cv, x, y, s, NAVY),
    "radiation": lambda cv, x, y, s: icon_radiation(cv, x, y, s, RED),
    "satellite": lambda cv, x, y, s: icon_satellite(cv, x, y, s, NAVY),
    "umbrella": lambda cv, x, y, s: icon_umbrella(cv, x, y, s, NAVY),
}


# -------------------------------------------------------------- layout ----
def draw_card(cv, x0, y0, w, h, kicker, headline, body, icon):
    cv.fill_rect(x0, y0, x0 + w, y0 + h, CARD)
    cv.rect_outline(x0, y0, x0 + w, y0 + h, NAVY, 1)
    cv.fill_rect(x0, y0, x0 + w, y0 + 4, RED)
    # icon box
    ix, iy, isize = x0 + 14, y0 + 18, 64
    cv.fill_rect(ix, iy, ix + isize, iy + isize, TINT)
    cv.rect_outline(ix, iy, ix + isize, iy + isize, NAVY, 1)
    ICONS[icon](cv, ix + 6, iy + 6, isize - 12)
    # kicker
    cv.draw_text(x0 + 92, y0 + 20, kicker, 2, RED)
    # headline, up to 3 lines
    lines = wrap(headline, 3, w - 92 - 14)
    yy = y0 + 42
    for ln in lines[:3]:
        cv.draw_text(x0 + 92, yy, ln, 3, INK)
        yy += 25
    # body, up to 3 lines
    blines = wrap(body, 2, w - 28)
    yy = y0 + 104
    for ln in blines[:3]:
        cv.draw_text(x0 + 14, yy, ln, 2, MUTED)
        yy += 17


def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.fill_rect(0, 0, W, 148, NAVY)
    icon_globe(cv, 906, 32, 84, CREAM, GOLD)
    cv.draw_text_centered(512, 22, "THE WORLD IN ONE DAY", 6, CREAM)
    cv.draw_text_centered(512, 82, "THURSDAY 26 NOVEMBER 2026", 3, GOLD)
    cv.draw_text_centered(512, 112, "THE DAY'S WORLD NEWS IN A SINGLE IMAGE",
                          2, CREAM)
    cv.hline(28, W - 28, 140, GOLD, 2)

    # ---- lead story ----
    lx0, ly0, lw, lh = 28, 164, W - 56, 228
    cv.fill_rect(lx0, ly0, lx0 + lw, ly0 + lh, CARD)
    cv.rect_outline(lx0, ly0, lx0 + lw, ly0 + lh, NAVY, 2)
    cv.fill_rect(lx0, ly0, lx0 + 10, ly0 + lh, RED)
    cv.draw_text(lx0 + 24, ly0 + 16, LEAD_KICKER, 2, RED)
    lines = wrap(LEAD_HEADLINE, 5, 660)
    yy = ly0 + 40
    for ln in lines:
        cv.draw_text(lx0 + 24, yy, ln, 5, INK)
        yy += 42
    icon_globe(cv, 800, ly0 + 40, 100, NAVY, GOLD)
    cv.draw_text_centered(850, ly0 + 146, "20% \u2013 40%", 3, RED)
    deck = wrap(LEAD_DECK, 2, lw - 48)
    yy = ly0 + 172
    for ln in deck:
        cv.draw_text(lx0 + 24, yy, ln, 2, MUTED)
        yy += 17

    # ---- six story cards ----
    cw, ch, gap = 474, 168, 16
    positions = [(28, 404), (518, 404),
                 (28, 588), (518, 588),
                 (28, 772), (518, 772)]
    for (x0, y0), (kicker, headline, body, icon) in zip(positions, STORIES):
        draw_card(cv, x0, y0, cw, ch, kicker, headline, body, icon)

    # ---- ticker ----
    cv.fill_rect(0, 952, W, 996, DARKNAVY)
    cv.draw_text(28, 958, TICKER_1, 2, CREAM)
    cv.draw_text(28, 976, TICKER_2, 2, GOLD)

    # ---- footer ----
    cv.draw_text_centered(512, 1004, FOOTER, 2, MUTED)

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    data = encode_png(cv)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
