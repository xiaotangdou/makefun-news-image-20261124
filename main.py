#!/usr/bin/env python3
"""Sum up 24 November 2026 world news in one image. Stdlib only, no network, deterministic."""
import os, struct, zlib, binascii

W, H = 1024, 1024
# 5x7 bitmap font, uppercase + digits + basic punctuation
FONT = {
'A': ["01110","10001","10001","11111","10001","10001","10001"],
'B': ["11110","10001","10001","11110","10001","10001","11110"],
'C': ["01110","10001","10000","10000","10000","10001","01110"],
'D': ["11110","10001","10001","10001","10001","10001","11110"],
'E': ["11111","10000","10000","11110","10000","10000","11111"],
'F': ["11111","10000","10000","11110","10000","10000","10000"],
'G': ["01110","10001","10000","10111","10001","10001","01111"],
'H': ["10001","10001","10001","11111","10001","10001","10001"],
'I': ["01110","00100","00100","00100","00100","00100","01110"],
'J': ["00111","00010","00010","00010","00010","10010","01100"],
'K': ["10001","10010","10100","11000","10100","10010","10001"],
'L': ["10000","10000","10000","10000","10000","10000","11111"],
'M': ["10001","11011","10101","10101","10001","10001","10001"],
'N': ["10001","11001","10101","10011","10001","10001","10001"],
'O': ["01110","10001","10001","10001","10001","10001","01110"],
'P': ["11110","10001","10001","11110","10000","10000","10000"],
'Q': ["01110","10001","10001","10001","10101","10010","01101"],
'R': ["11110","10001","10001","11110","10100","10010","10001"],
'S': ["01111","10000","10000","01110","00001","00001","11110"],
'T': ["11111","00100","00100","00100","00100","00100","00100"],
'U': ["10001","10001","10001","10001","10001","10001","01110"],
'V': ["10001","10001","10001","10001","10001","01010","00100"],
'W': ["10001","10001","10001","10101","10101","11011","10001"],
'X': ["10001","10001","01010","00100","01010","10001","10001"],
'Y': ["10001","10001","01010","00100","00100","00100","00100"],
'Z': ["11111","00001","00010","00100","01000","10000","11111"],
'0': ["01110","10001","10011","10101","11001","10001","01110"],
'1': ["00100","01100","00100","00100","00100","00100","01110"],
'2': ["01110","10001","00001","00110","01000","10000","11111"],
'3': ["11111","00010","00100","00010","00001","10001","01110"],
'4': ["00010","00110","01010","10010","11111","00010","00010"],
'5': ["11111","10000","11110","00001","00001","10001","01110"],
'6': ["00110","01000","10000","11110","10001","10001","01110"],
'7': ["11111","00001","00010","00100","01000","01000","01000"],
'8': ["01110","10001","10001","01110","10001","10001","01110"],
'9': ["01110","10001","10001","01111","00001","00010","01100"],
' ': ["00000","00000","00000","00000","00000","00000","00000"],
'.': ["00000","00000","00000","00000","00000","01100","01100"],
',': ["00000","00000","00000","00000","01100","00100","01000"],
'-': ["00000","00000","00000","01110","00000","00000","00000"],
"'": ["00100","00100","01000","00000","00000","00000","00000"],
'/': ["00001","00010","00010","00100","01000","01000","10000"],
'(': ["00010","00100","01000","01000","01000","00100","00010"],
')': ["01000","00100","00010","00010","00010","00100","01000"],
'!': ["00100","00100","00100","00100","00100","00000","00100"],
'?': ["01110","10001","00001","00110","00100","00000","00100"],
':': ["00000","01100","01100","00000","01100","01100","00000"],
'%': ["11001","11010","00010","00100","01000","01011","10011"],
}

STORIES = [
    ("01  MYANMAR", "14 NATIONS BACK ICJ", "Rohingya genocide ruling", "UK, Spain, Canada, Australia and ten others affirmed the court's decision.", (176, 42, 42)),
    ("02  UNITED NATIONS", "UN CHIEF WANTS AI RULES", "in a year", "Guterres calls for a multilateral framework to limit AI risks.", (15, 42, 68)),
    ("03  LIBYA / UKRAINE", "UKRAINE SAYS IT SANK A", "Russian warship", "Sea-drone attack at a Libya base; the UN seeks a probe.", (180, 120, 20)),
    ("04  UNITED STATES", "STATES SUE MUSK FIRMS", "over Grok images", "Oregon and Virginia sue over sexualised images made with Grok.", (20, 90, 90)),
    ("05  NEPAL", "5.6 QUAKE NEAR CHINA", "border", "A 5.6 magnitude earthquake struck Koshi province.", (90, 60, 140)),
    ("06  DENMARK", "SCHOOL PHONES BANNED", "to grade 10", "Denmark bans phones in schools after poor PISA results.", (20, 110, 40)),
]

class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))
    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = yy * self.w * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                i = base + xx * 3
                self.px[i:i+3] = bytes(c)
    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for r in range(7):
                for col in range(5):
                    if glyph[r][col] == '1':
                        self.rect(cx + col * scale, y + r * scale, scale, scale, color)
            cx += 6 * scale
        return cx
    def text_width(self, s, scale):
        return len(s) * 6 * scale

def wrap(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) <= max_chars:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def png_bytes(c):
    raw = b"".join(b"\x00" + bytes(c.px[y * c.w * 3:(y + 1) * c.w * 3]) for y in range(c.h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", binascii.crc32(t + d) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")

def main():
    cv = Canvas(W, H, (247, 243, 234))
    NAVY = (15, 42, 68); GOLD = (201, 162, 39); WHITE = (255, 255, 255); INK = (20, 20, 20); GREY = (90, 90, 90)
    cv.rect(0, 0, W, 168, NAVY)
    cv.rect(0, 168, W, 6, GOLD)
    cv.text(36, 36, "THE WORLD IN ONE IMAGE", 4, WHITE)
    cv.text(36, 100, "TUESDAY 24 NOVEMBER 2026", 3, GOLD)
    cv.text(36, 136, "SIX STORIES  -  SIX REGIONS AND FIELDS", 2, WHITE)
    # 2 cols x 3 rows
    for i, (tag, h1, h2, sub, col) in enumerate(STORIES):
        bx = 24 + (i % 2) * 500
        by = 196 + (i // 2) * 268
        cv.rect(bx, by, 476, 248, WHITE)
        cv.rect(bx, by, 476, 8, col)
        cv.rect(bx, by + 24, 10, 200, col)
        cv.text(bx + 28, by + 28, tag, 2, col)
        y = by + 62
        for line in wrap(h1, 22):
            cv.text(bx + 28, y, line, 3, INK); y += 26
        if h2:
            for line in wrap(h2, 22):
                cv.text(bx + 28, y, line, 3, INK); y += 26
        y += 6
        for line in wrap(sub, 36):
            cv.text(bx + 28, y, line, 2, GREY); y += 18
    cv.rect(0, H - 44, W, 44, NAVY)
    cv.text(36, H - 32, "SOURCES: SCMP, QATAR TRIBUNE, MANILA TIMES, HORIZON  -  24 NOV 2026", 2, WHITE)
    data = png_bytes(cv)
    for path in ("/output/entry.png", "output/entry.png"):
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "wb") as f: f.write(data)
            print(f"wrote {path} {len(data)} bytes {W}x{H}")
            return
        except OSError as e:
            print(f"cannot write {path}: {e}")
    raise SystemExit("no writable output")

if __name__ == "__main__":
    main()
