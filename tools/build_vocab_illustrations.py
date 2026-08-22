#!/usr/bin/env python3
"""Generate clear vector diagrams for abstract Grade-5 vocabulary.

The source worksheets contain excellent object art but not unambiguous height,
weight, face-shape, or spoon-size comparisons. These deliberately simple SVGs
are generated locally so the USB build stays offline and reproducible.

Run: python tools/build_vocab_illustrations.py
"""

import os

from common import ROOT, ensure


DEST = os.path.join(ROOT, "app", "img", "vocab")


def svg(body):
    return ("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 400 240\" "
            "role=\"img\"><rect width=\"400\" height=\"240\" rx=\"24\" fill=\"#f8fafc\"/>"
            + body + "</svg>\n")


def face(hair):
    return ("<circle cx=\"200\" cy=\"132\" r=\"64\" fill=\"#f2b98c\" stroke=\"#17224a\" stroke-width=\"8\"/>"
            + hair
            + "<circle cx=\"177\" cy=\"135\" r=\"6\" fill=\"#17224a\"/>"
              "<circle cx=\"223\" cy=\"135\" r=\"6\" fill=\"#17224a\"/>"
              "<path d=\"M177 166 Q200 184 223 166\" fill=\"none\" stroke=\"#17224a\" stroke-width=\"7\" stroke-linecap=\"round\"/>")


def hair_straight(color):
    return (f"<path d=\"M140 130 V78 Q200 36 260 78 V130 L238 112 V72 H162 V112 Z\" "
            f"fill=\"{color}\" stroke=\"#17224a\" stroke-width=\"8\" stroke-linejoin=\"round\"/>")


def hair_wavy(color="#5b2c20"):
    return (f"<path d=\"M140 128 Q128 104 150 90 Q142 65 170 66 Q180 42 202 58 "
            f"Q224 42 234 66 Q262 65 254 90 Q276 104 260 128 L238 108 Q220 84 200 98 "
            f"Q180 84 162 108 Z\" fill=\"{color}\" stroke=\"#17224a\" stroke-width=\"8\"/>")


def hair_curly():
    circles = "".join(f'<circle cx="{x}" cy="{y}" r="24" fill="#5b2c20" stroke="#17224a" stroke-width="7"/>'
                      for x, y in ((150, 99), (168, 73), (199, 64), (231, 73), (250, 99)))
    return circles


def person(width, height, marker=None):
    top = 208 - height
    head_r = 25
    torso_top = top + head_r * 2 + 5
    torso_h = max(54, height - 82)
    left = 200 - width / 2
    marker_svg = ""
    if marker:
        marker_svg = (f'<path d="M{marker} 204 V{top}" stroke="#ef476f" stroke-width="7" stroke-linecap="round"/>'
                      f'<path d="M{marker-10} 204 H{marker+10} M{marker-10} {top} H{marker+10}" stroke="#ef476f" stroke-width="7"/>')
    return (marker_svg
            + f'<circle cx="200" cy="{top + head_r}" r="{head_r}" fill="#f2b98c" stroke="#17224a" stroke-width="7"/>'
              f'<rect x="{left}" y="{torso_top}" width="{width}" height="{torso_h}" rx="{min(width/2, 32)}" fill="#2f80ed" stroke="#17224a" stroke-width="8"/>'
              f'<path d="M180 202 V{torso_top+torso_h-4} M220 202 V{torso_top+torso_h-4}" stroke="#17224a" stroke-width="12" stroke-linecap="round"/>')


def face_shape(kind):
    shapes = {
        "round": '<circle cx="200" cy="126" r="74"',
        "oval": '<ellipse cx="200" cy="126" rx="62" ry="86"',
        "square": '<rect x="126" y="52" width="148" height="148" rx="18"',
    }
    return (shapes[kind] + ' fill="#f2b98c" stroke="#17224a" stroke-width="9"/>'
            '<circle cx="176" cy="120" r="7" fill="#17224a"/><circle cx="224" cy="120" r="7" fill="#17224a"/>'
            '<path d="M174 155 Q200 175 226 155" fill="none" stroke="#17224a" stroke-width="8" stroke-linecap="round"/>')


def spoon(length, bowl, color):
    x = 200
    top = 32
    return (f'<ellipse cx="{x}" cy="{top + bowl}" rx="{bowl * .72}" ry="{bowl}" fill="{color}" stroke="#17224a" stroke-width="8"/>'
            f'<rect x="{x-9}" y="{top + bowl*1.65}" width="18" height="{length}" rx="9" fill="{color}" stroke="#17224a" stroke-width="7"/>')


def write(name, body):
    with open(os.path.join(DEST, name + ".svg"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg(body))


def main():
    ensure(DEST)
    write("physical-straight", face(hair_straight("#5b2c20")))
    write("physical-wavy", face(hair_wavy()))
    write("physical-curly", face(hair_curly()))
    write("physical-dark", face(hair_straight("#20100d")))
    write("physical-fair", face(hair_straight("#d6b38a")))
    write("physical-blonde", face(hair_straight("#f4c542")))
    write("physical-thin", person(48, 170))
    write("physical-medium-weight", person(82, 170))
    write("physical-fat", person(124, 170))
    write("physical-short", person(68, 120, 305))
    write("physical-medium-height", person(68, 165, 305))
    write("physical-tall", person(68, 205, 305))
    write("physical-small", person(52, 105))
    write("physical-average", person(72, 155))
    write("physical-big", person(112, 195))
    write("physical-round", face_shape("round"))
    write("physical-oval", face_shape("oval"))
    write("physical-square", face_shape("square"))
    write("tablespoon", spoon(128, 45, "#a9b6c8"))
    write("teaspoon", spoon(104, 29, "#f6c453"))
    print("20 reviewed SVG illustrations -> " + DEST)


if __name__ == "__main__":
    main()
