# requires: Pillow numpy
from .. import loader

import io
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

BASE = 0x2800
INVERT_MAP = {chr(BASE + c): chr(BASE + (c ^ 0xFF)) for c in range(256)}


class ascii_lib(loader.Library):
    developer = "@SunnexGB"

    def resize(self, img):
        if img.width > 768:
            img = img.resize((768, int(img.height * 768 / img.width)), Image.LANCZOS)
        w = img.width - img.width % 4
        h = img.height - img.height % 4
        if w != img.width or h != img.height:
            img = img.resize((w, h), Image.LANCZOS)
        return img

    def mode(self, img, threshold, contrast):
        gray = img.convert("L")
        edges = ImageOps.invert(gray.filter(ImageFilter.FIND_EDGES))
        contrast_img = ImageEnhance.Contrast(img).enhance(contrast).convert("L")
        e = np.array(edges, dtype=np.float32) / 255.0
        c = np.array(contrast_img, dtype=np.float32) / 255.0
        blended = Image.fromarray((e * c * 255).astype(np.uint8), "L")
        t = int(threshold * 255)
        processed = blended.point(lambda p: 255 if p > t else 0, "L")
        return processed, t

    def braille(self, img, threshold, width):
        cw = width * 2
        o = -(-round(cw * img.height / img.width) // 4)
        ch = 4 * o
        px = np.array(img.resize((cw, ch), Image.LANCZOS).convert("L"))
        order = [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1),(3,0),(3,1)]
        rows = []
        for rs in range(0, ch, 4):
            line = []
            for cs in range(0, cw, 2):
                grays = [
                    int(px[rs+dy, cs+dx]) if (rs+dy < ch and cs+dx < cw) else 255
                    for dy, dx in order
                ]
                bits = list(reversed([1 if g < threshold else 0 for g in grays]))
                code = int("".join(str(b) for b in bits), 2)
                line.append(chr(BASE + code))
            rows.append("".join(line))
        return rows

    def trim(self, lines):
        blank = "\u2800"
        while lines and all(c == blank for c in lines[0]):
            lines = lines[1:]
        while lines and all(c == blank for c in lines[-1]):
            lines = lines[:-1]
        if not lines:
            return lines
        left = min(next((i for i,c in enumerate(r) if c!=blank), len(r)) for r in lines)
        right = min(next((i for i,c in enumerate(reversed(r)) if c!=blank), len(r)) for r in lines)
        return [r[left: len(r)-right if right else len(r)] for r in lines]

    def invert(self, lines):
        return ["".join(INVERT_MAP.get(c,c) for c in l) for l in lines]

    def fit(self, img, threshold, chars, width):
        lo, hi = 5, 200
        best = ""
        for _ in range(14):
            mid = (lo + hi)//2
            lines = self.trim(self.braille(img, threshold, mid))
            art = "\n".join(lines)
            if len(art) <= chars:
                best = art
                lo = mid + 1
            else:
                hi = mid - 1
        return best

    def convert(self, data, width=50, threshold=0.65, contrast_boost=2.0, invert=False, target_chars=0):
        buf = io.BytesIO(data)
        img = Image.open(buf)
        img.load()
        buf.close()
        img = img.convert("RGB")
        img = self.resize(img)
        processed, t = self.mode(img, threshold, contrast_boost)
        if target_chars > 0:
            art = self.fit(processed, t, target_chars, width)
        else:
            art = "\n".join(self.trim(self.braille(processed, t, width)))
        if invert and art:
            art = "\n".join(self.invert(art.split("\n")))
        return art