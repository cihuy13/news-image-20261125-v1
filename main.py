#!/usr/bin/env python3
"""news-image-20261125 entry: Wednesday 25 November 2026 in one image.

Draws a one-page newspaper front page (1024x1024 PNG) summing up the
world news of Wednesday 25 November 2026: 50 verified stories, 10 regions,
19 fields, a UTC timeline, drawn scenes for the top 13 stories, a world map
with numbered pins, and a DATE CHECK box naming what was left out because
it happened on another day.

Stdlib + Pillow only. No network, no clock, no randomness: two runs write
byte-identical PNGs. Writes only <MAKEFUN_OUTPUT_DIR or /output>/entry.png.
"""
import os
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14                      # outer margin
CW = W - 2 * M              # content width = 996

PAPER = (246, 241, 229)
INK = (20, 20, 20)
NAVY = (20, 33, 61)
RED = (185, 28, 28)
GOLD = (180, 83, 9)
TEAL = (15, 118, 110)
PANEL = (255, 253, 246)
LINE = (201, 191, 168)
MUTED = (90, 84, 70)
WHITE = (255, 255, 255)
CREAM = (238, 231, 214)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default(size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
SERIF = lambda s: font("DejaVuSerif.ttf", s)             # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)         # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)                # noqa: E731


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill, spacing=3, align="left"):
    lines = wrap(draw, text, fnt, max_w)
    for line in lines:
        if align == "center":
            lx = x + (max_w - draw.textlength(line, font=fnt)) / 2
        else:
            lx = x
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def centre(draw, cx, y, text, fnt, fill):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text,
              font=fnt, fill=fill)
    return y + fnt.size


# ---------------------------------------------------------------- stories
# (num, region, field, tag, city, headline, body) for the 13 drawn panels.
# tag: O=OFFICIAL, C=CONFIRMED, R=REPORTED, CL=CLAIM
PANELS = [
    (1, "N. America", "Trade", "O", "WASHINGTON - TRADE",
     "US proposes tariffs of up to 20% on 14 economies",
     "China faces the top 20% rate; Vietnam up to 35%, India up to 25%, EU "
     "15% cap stays. Hearings 25 January; nothing in force yet."),
    (2, "East & SE Asia", "Markets", "C", "SEOUL - TOKYO - TAIPEI - MARKETS",
     "AI doubts sink Asian chip stocks: Kospi closes -6.2%",
     "Kospi ends at 4,697.51; SK Hynix -11.1%, Samsung -9.9%, Taiex -4.8%, "
     "Nikkei -2.8%. Tuesday's 6.3% rebound wiped out in a day."),
    (3, "East & SE Asia", "Space", "O", "JIUQUAN, CHINA - SPACE",
     "Pakistan's first astronaut docks at China's space station",
     "Muhammad Zeeshan Ali, 40, first foreigner on Tiangong, flew on "
     "Shenzhou-24 with Tang Hongbo and Wu Yi; launch 08:18, docked 11:56 "
     "Beijing time. Stays 5 to 10 days."),
    (4, "Middle East", "War", "CL", "HORMUZ - WAR AT SEA",
     "Iran says two tankers hit mines and burn",
     "IRGC Navy says the ships took an 'unauthorised route'; no vessel "
     "named, no casualties given, not independently confirmed."),
    (5, "Middle East", "War", "R", "RAS TANURA - WAR",
     "Saudis down Houthi drones after Hodeidah strike",
     "Coalition: 4 drones downed over Ras Tanura, 7 in all, no injuries. "
     "Houthis claim the refinery was hit."),
    (6, "Europe", "War", "R", "SAMARA - WAR",
     "Ukrainian drones set two refineries ablaze",
     "Syzran and Kuibyshev, both Rosneft, burn; 1 killed, 145 drones downed. "
     "Savasleyka also hit: 3 MiG-31s, 2 Su-34s."),
    (7, "Europe", "War", "R", "UKRAINE - WAR",
     "Russian strikes kill 7, cut power in 5 regions",
     "A DTEK thermal plant halted; Zaporizhzhia nuclear plant on diesel "
     "after losing its last power line."),
    (8, "Oceania", "Diplomacy", "O", "CANBERRA - DIPLOMACY",
     "Solomon Islands signs security pact with Australia",
     "Australia is 'primary security partner'; no foreign bases allowed. "
     "A$740m over 10 years."),
    (9, "Europe", "Energy", "O", "LONDON - ENERGY",
     "UK energy price cap to rise 26% in January",
     "Ofgem: typical bill £1,723 to £2,166 a year from 1 January."),
    (10, "South Asia", "Labour", "O", "DHAKA - LABOUR",
     "Garment workers offered higher minimum wage",
     "Wage board: 12,500 to 17,000 taka (+36%) a month, 4-2 vote; from "
     "December, paid from January."),
    (11, "N. Africa", "Disaster", "R", "GIZA - DISASTER",
     "Fuel tanker fire kills at least 31 near Cairo",
     "Tanker overturned and exploded on a ring road; 21 injured, Health "
     "Ministry says."),
    (12, "Middle East", "War", "R", "GAZA CITY - WAR",
     "Israeli strike kills Hamas security chief",
     "Abu al-Awf, his wife and two daughters die in Shati camp."),
    (13, "Sub-Saharan Africa", "Justice", "C", "CAPE TOWN - JUSTICE",
     "Court lifts 'Farmgate' ruling against Ramaphosa",
     "Judges void the 2022 panel report that opened the way to impeachment."),
]

WHY = {
    1: "WHY IT MATTERS  The widest US tariff salvo of the year; allies and "
       "rivals alike must negotiate by January.",
    2: "WHY IT MATTERS  Investors doubt the AI spending boom will ever pay "
       "for itself.",
    3: "WHY IT MATTERS  China's station takes its first foreign guest; "
       "Pakistan's first in orbit.",
}

# (num, region, field, tag, one-line text <= 44 chars incl. tag)
ALSO = [
    (14, "Latin America", "Crime", "R", "Cartagena: Hostages freed in siege [R]"),
    (15, "East & SE Asia", "Diplomacy", "R", "Pyongyang: Swiss envoy given 48 hrs [R]"),
    (16, "Europe", "Tech", "R", "Brussels: EU proposes 650bn euro fund [R]"),
    (17, "Europe", "Economy", "R", "London: Poundland collapses, 11,000 jobs [R]"),
    (18, "Middle East", "Politics", "C", "Jerusalem: Knesset advances Oct 7 inquiry [C]"),
    (19, "Middle East", "Rights", "R", "Gaza: Amnesty urges ICC genocide probe [R]"),
    (20, "Europe", "Diplomacy", "R", "Kyiv: Zelensky seeks 115bn euro aid for 2027 [R]"),
    (21, "Europe", "Diplomacy", "R", "Warsaw: Poland plans border no-fly zone [R]"),
    (22, "East & SE Asia", "Disaster", "R", "Bogor: 9 dead, 17 trapped in gold mine [R]"),
    (23, "East & SE Asia", "Tech", "R", "Hong Kong: URBTIX hack exposes 1.3m [R]"),
    (24, "East & SE Asia", "Politics", "R", "Shanghai: China probes Politburo member [R]"),
    (25, "N. America", "Diplomacy", "R", "Ottawa: Carney denies Trump criticism [R]"),
    (26, "N. Africa", "War", "R", "Benghazi: 2 Libyan officers die of wounds [R]"),
    (27, "Europe", "Labour", "R", "Paris: Eurostar strike cancels trains [R]"),
    (28, "N. America", "Markets", "C", "New York: Dow +0.3% to 50,183 [C]"),
    (29, "Middle East", "Justice", "C", "Tel Aviv: Judges urge dropping graft case [C]"),
    (30, "Oceania", "Economy", "O", "Sydney: Australia inflation jumps to 4.9% [O]"),
    (31, "East & SE Asia", "Justice", "R", "Kuala Lumpur: Regulator sues Google [R]"),
    (32, "Global", "Science", "O", "Space: Hera finds crater left by DART [O]"),
    (33, "Europe", "Sport", "C", "Lisbon: Sporting 2-2 Man United [C]"),
    (34, "East & SE Asia", "Markets", "R", "Tokyo: Chip stocks fall; Advantest -12.9% [R]"),
    (35, "South Asia", "Disaster", "R", "Karachi: Building collapse kills 3 [R]"),
    (36, "N. America", "Markets", "C", "S&P -0.3% to 7,183; Nasdaq -0.6% [C]"),
    (37, "N. America", "Economy", "O", "Washington: US Q3 GDP revised up to 4.3% [O]"),
    (38, "Sub-Saharan Africa", "Diplomacy", "R", "Khartoum: Sudan rejects Ethiopia talks [R]"),
    (39, "Sub-Saharan Africa", "War", "R", "Sudan: RSF drones kill 19 in Blue Nile [R]"),
    (40, "Europe", "Politics", "R", "Madrid: Spain heads to snap election [R]"),
    (41, "Global", "Climate", "R", "World: COP31 climate talks fail [R]"),
    (42, "N. America", "Disaster", "R", "Mississippi: 6 die in plane crash off coast [R]"),
    (43, "Global", "Rights", "O", "UN: 47,000 women killed by partner or kin [O]"),
    (44, "N. America", "Justice", "C", "Brooklyn: Huawei guilty on 10 of 12 (Tue) [C]"),
    (45, "South Asia", "Justice", "R", "New Delhi: Court voids Gandhi assets check [R]"),
    (46, "Latin America", "Politics", "O", "Brasilia: Lula signs public accounts law [O]"),
    (47, "Latin America", "Justice", "R", "Mexico City: Sheinbaum seeks extradition [R]"),
    (48, "Oceania", "Rights", "O", "Canberra: Apology to LGBTQIA+ troops [O]"),
    (49, "Middle East", "Humanitarian", "O", "Aden: UN: 364,000 displaced in August [O]"),
    (50, "Global", "Rights", "O", "World: 16 days of activism begin [O]"),
]

REGION_ORDER = ["N. America", "Latin America", "Europe", "Middle East",
                "N. Africa", "Sub-Saharan Africa", "South Asia",
                "East & SE Asia", "Oceania", "Global"]
REGION_SHORT = {"N. America": "N. AMERICA", "Latin America": "LATIN AM.",
                "Europe": "EUROPE", "Middle East": "MIDDLE EAST",
                "N. Africa": "N. AFRICA", "Sub-Saharan Africa": "SUB-SAH. AFRICA",
                "South Asia": "SOUTH ASIA", "East & SE Asia": "EAST & SE ASIA",
                "Oceania": "OCEANIA", "Global": "GLOBAL"}
REGION_COLORS = {
    "N. America": (185, 28, 28), "Latin America": (217, 119, 6),
    "Europe": (29, 78, 216), "Middle East": (180, 83, 9),
    "N. Africa": (5, 150, 105), "Sub-Saharan Africa": (101, 163, 13),
    "South Asia": (219, 39, 119), "East & SE Asia": (13, 148, 136),
    "Oceania": (124, 58, 237), "Global": (71, 85, 105),
}

TAG_FULL = {"O": "OFFICIAL", "C": "CONFIRMED", "R": "REPORTED",
            "CL": "CLAIM"}
TAG_COLOR = {"O": (5, 150, 105), "C": (29, 78, 216), "R": (180, 83, 9),
             "CL": (185, 28, 28)}

BIG_NUMBERS = [
    ("20%", "top proposed US tariff\non China"),
    ("-6.2%", "Kospi close, worst\nin AI sell-off"),
    ("+26%", "UK energy price cap\nfrom 1 January"),
    ("31", "killed in Cairo\ntanker fire"),
    ("9", "dead, 17 trapped\nin Java gold pit"),
]

TIMELINE = ("THE DAY IN UTC  |  00:18 Shenzhou-24 lifts off  ·  03:56 "
            "Tiangong docks  ·  05:30 Taiex -4.8%  ·  06:30 Kospi -6.2%  ·  "
            "06:35 Crew enters  ·  10:59 Ofgem +26%  ·  13:00 US tariffs "
            "proposed")

DATE_CHECK = ("DATE CHECK  -  Left out, not 25 November: Riyadh tower "
              "strike, 11 hurt (Tue 24)  -  Nvidia's 5.9% fall (Tue 24, US)  "
              "-  US Thanksgiving (Thu 26, not yet). Every story here "
              "happened, or was first reported, on Wednesday 25 November "
              "2026.")

LEGEND = ("OFFICIAL an authority's own word  -  CONFIRMED two or more major "
          "outlets  -  REPORTED press report  -  CLAIM one side's account, "
          "unverified")
SOURCES = ("Sources: Reuters, AP, AFP, BBC, Al Jazeera, Xinhua, Yonhap, "
           "USTR, Ofgem, CMSA, UN. Every drawing original.")

# map pins: story num -> (x, y) inside the map box (fractions of box)
PINS = {1: (0.16, 0.28), 2: (0.90, 0.26), 3: (0.82, 0.20),
        4: (0.68, 0.34), 5: (0.72, 0.46), 6: (0.70, 0.18),
        7: (0.58, 0.20), 8: (0.90, 0.78), 9: (0.47, 0.15),
        10: (0.80, 0.36), 11: (0.52, 0.44), 12: (0.62, 0.56),
        13: (0.57, 0.76)}


# ---------------------------------------------------------------- scenes
def flame(draw, cx, base, w, h, color=(220, 60, 20)):
    pts = [(cx - w / 2, base), (cx - w / 4, base - h * 0.55),
           (cx - w / 8, base - h * 0.35), (cx, base - h),
           (cx + w / 8, base - h * 0.45), (cx + w / 4, base - h * 0.6),
           (cx + w / 2, base)]
    draw.polygon(pts, fill=color)
    draw.ellipse([cx - w / 6, base - h * 0.45, cx + w / 6, base - h * 0.1],
                 fill=(245, 158, 11))


def scene_ship(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(58, 110, 165))
    draw.rectangle([x, y + h * 0.62, x + w, y + h], fill=(32, 74, 120))
    # hull
    draw.polygon([(x + 8, y + h * 0.55), (x + w - 8, y + h * 0.55),
                  (x + w - 26, y + h * 0.82), (x + 26, y + h * 0.82)],
                 fill=(30, 30, 34))
    cols = [(185, 28, 28), (217, 119, 6), (29, 78, 216), (5, 150, 105),
            (219, 39, 119), (124, 58, 237)]
    labels = ["CHINA", "EU", "INDIA", "VIETNAM", "", ""]
    cw = (w - 40) / 6
    for i in range(6):
        cx0 = x + 20 + i * cw
        draw.rectangle([cx0, y + h * 0.22, cx0 + cw - 3, y + h * 0.53],
                       fill=cols[i], outline=(255, 255, 255))
        if labels[i]:
            f = SANS_B(8)
            tw = draw.textlength(labels[i], font=f)
            draw.text((cx0 + (cw - 3 - tw) / 2, y + h * 0.33),
                      labels[i], font=f, fill=WHITE)
    # badge
    bx, by, br = x + w - 52, y + 8, 26
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=WHITE,
                 outline=RED, width=2)
    f = SANS_B(9)
    for i, t in enumerate(["UP TO", "20%"]):
        tw = draw.textlength(t, font=f)
        draw.text((bx - tw / 2, by - 12 + i * 11), t, font=f, fill=RED)


def scene_chart(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(17, 24, 39))
    for gy in range(1, 4):
        gyv = y + h * gy / 4
        draw.line([(x + 6, gyv), (x + w - 6, gyv)], fill=(55, 65, 81))
    pts = [(x + 12, y + h * 0.30), (x + w * 0.25, y + h * 0.38),
           (x + w * 0.40, y + h * 0.34), (x + w * 0.55, y + h * 0.55),
           (x + w * 0.70, y + h * 0.62), (x + w * 0.85, y + h * 0.82),
           (x + w - 12, y + h * 0.86)]
    draw.line(pts, fill=(239, 68, 68), width=3)
    for px, py in pts[1:-1]:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(245, 158, 11))
    f = SANS_B(11)
    draw.text((x + 10, y + 6), "KOSPI  -6.2%", font=f, fill=WHITE)
    f2 = SANS_B(10)
    draw.text((x + w - 118, y + h - 20), "4,697.51", font=f2,
              fill=(245, 158, 11))
    # chip
    cx, cy = x + w - 34, y + 22
    draw.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], fill=(55, 65, 81),
                   outline=(148, 163, 184))
    draw.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=(239, 68, 68))
    f3 = SANS_B(9)
    draw.text((x + 10, y + h - 20), "SK HYNIX -11.1%   SAMSUNG -9.9%",
              font=f3, fill=(248, 113, 113))


def scene_space(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(10, 20, 48))
    stars = [(0.08, 0.2), (0.2, 0.12), (0.35, 0.25), (0.55, 0.1),
             (0.7, 0.22), (0.85, 0.12), (0.92, 0.3), (0.45, 0.08),
             (0.62, 0.32), (0.15, 0.4)]
    for sx, sy in stars:
        draw.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1,
                      y + h * sy + 1], fill=WHITE)
    # Earth curve (a chord clipped to the scene box: only the upper half
    # of the ellipse is drawn, so nothing spills past the scene edges)
    draw.pieslice([x, y + h * 0.55, x + w, y + h * 1.45], 180, 360,
                  fill=(37, 99, 235))
    draw.arc([x, y + h * 0.55, x + w, y + h * 1.45], 180, 360,
             fill=(147, 197, 253), width=2)
    # solar panels
    draw.rectangle([x + w * 0.06, y + h * 0.38, x + w * 0.30, y + h * 0.52],
                   fill=(59, 130, 246), outline=(191, 219, 254))
    draw.rectangle([x + w * 0.70, y + h * 0.38, x + w + w * 0.0 - 20,
                    y + h * 0.52], fill=(59, 130, 246),
                   outline=(191, 219, 254))
    # station core + capsule
    draw.rectangle([x + w * 0.32, y + h * 0.30, x + w * 0.68, y + h * 0.58],
                   fill=(226, 232, 240), outline=(100, 116, 139))
    draw.rectangle([x + w * 0.42, y + h * 0.16, x + w * 0.58, y + h * 0.30],
                   fill=(203, 213, 225), outline=(100, 116, 139))
    f = SANS_B(9)
    draw.text((x + w * 0.34, y + h * 0.40), "TIANGONG", font=f, fill=NAVY)
    # flags
    draw.rectangle([x + 10, y + h - 24, x + 34, y + h - 8], fill=(20, 90, 50))
    draw.rectangle([x + 10, y + h - 24, x + 16, y + h - 8], fill=WHITE)
    draw.rectangle([x + 40, y + h - 24, x + 64, y + h - 8], fill=(222, 41, 16))
    draw.text((x + 70, y + h - 24), "SHENZHOU-24", font=SANS_B(9),
              fill=WHITE)


def mini_scene(draw, x, y, w, h, kind, label):
    bg = {"tanker": (30, 58, 95), "drone": (68, 64, 60),
          "refinery": (101, 67, 33), "power": (51, 65, 85),
          "treaty": (15, 118, 110), "bill": (120, 53, 15),
          "factory": (87, 83, 78), "fire": (127, 29, 29),
          "camp": (100, 116, 139), "court": (55, 48, 163)}[kind]
    draw.rectangle([x, y, x + w, y + h], fill=bg)
    if kind == "tanker":
        draw.rectangle([x, y + h * 0.55, x + w, y + h], fill=(23, 42, 71))
        draw.polygon([(x + 14, y + h * 0.45), (x + w - 14, y + h * 0.45),
                      (x + w - 28, y + h * 0.72), (x + 28, y + h * 0.72)],
                     fill=(15, 15, 18))
        flame(draw, x + w * 0.32, y + h * 0.48, 16, 16)
        flame(draw, x + w * 0.68, y + h * 0.48, 13, 13)
    elif kind == "drone":
        draw.rectangle([x + w * 0.2, y + h * 0.3, x + w * 0.8, y + h * 0.55],
                       fill=(87, 83, 78))
        draw.ellipse([x + w * 0.42, y + h * 0.12, x + w * 0.58, y + h * 0.3],
                     fill=(214, 211, 209))
        draw.line([(x + w * 0.5, y + h * 0.3), (x + w * 0.5, y + h * 0.55)],
                  fill=(214, 211, 209), width=2)
    elif kind == "refinery":
        for i, bx in enumerate([0.12, 0.38, 0.64]):
            draw.rectangle([x + w * bx, y + h * 0.42, x + w * (bx + 0.2),
                            y + h * 0.85], fill=(214, 211, 209))
        flame(draw, x + w * 0.22, y + h * 0.42, 14, 14)
        flame(draw, x + w * 0.74, y + h * 0.42, 14, 14)
    elif kind == "power":
        draw.line([(x + w * 0.3, y + h * 0.9), (x + w * 0.5, y + h * 0.15),
                   (x + w * 0.7, y + h * 0.9)], fill=(226, 232, 240), width=3)
        draw.line([(x + w * 0.18, y + h * 0.5), (x + w * 0.82, y + h * 0.5)],
                  fill=(226, 232, 240), width=2)
        draw.polygon([(x + w * 0.55, y + h * 0.08), (x + w * 0.45,
                      y + h * 0.45), (x + w * 0.55, y + h * 0.45),
                      (x + w * 0.45, y + h * 0.8), (x + w * 0.62,
                      y + h * 0.38), (x + w * 0.52, y + h * 0.38)],
                     fill=(245, 158, 11))
    elif kind == "treaty":
        draw.rectangle([x + w * 0.14, y + h * 0.25, x + w * 0.42, y + h * 0.6],
                       fill=(0, 82, 165))
        draw.rectangle([x + w * 0.58, y + h * 0.25, x + w * 0.86, y + h * 0.6],
                       fill=(0, 122, 94))
        draw.polygon([(x + w * 0.42, y + h * 0.25), (x + w * 0.5, y + h * 0.42),
                      (x + w * 0.58, y + h * 0.25)], fill=(245, 158, 11))
    elif kind == "bill":
        draw.rectangle([x + w * 0.15, y + h * 0.28, x + w * 0.85, y + h * 0.72],
                       fill=(254, 243, 199), outline=(180, 83, 9), width=2)
        draw.ellipse([x + w * 0.42, y + h * 0.34, x + w * 0.58, y + h * 0.66],
                     outline=(180, 83, 9), width=2)
    elif kind == "factory":
        draw.polygon([(x + w * 0.12, y + h * 0.85), (x + w * 0.12, y + h * 0.4),
                      (x + w * 0.3, y + h * 0.4), (x + w * 0.3, y + h * 0.55),
                      (x + w * 0.48, y + h * 0.55), (x + w * 0.48, y + h * 0.4),
                      (x + w * 0.66, y + h * 0.4), (x + w * 0.66, y + h * 0.85)],
                     fill=(68, 64, 60))
        draw.rectangle([x + w * 0.72, y + h * 0.2, x + w * 0.8, y + h * 0.85],
                       fill=(87, 83, 78))
    elif kind == "fire":
        draw.rectangle([x, y + h * 0.7, x + w, y + h], fill=(68, 64, 60))
        flame(draw, x + w * 0.3, y + h * 0.72, 26, 30)
        flame(draw, x + w * 0.7, y + h * 0.72, 20, 22)
    elif kind == "camp":
        draw.rectangle([x + w * 0.15, y + h * 0.45, x + w * 0.85, y + h * 0.85],
                       fill=(120, 113, 108))
        draw.polygon([(x + w * 0.1, y + h * 0.48), (x + w * 0.5, y + h * 0.2),
                      (x + w * 0.9, y + h * 0.48)], fill=(87, 83, 78))
    elif kind == "court":
        draw.rectangle([x + w * 0.45, y + h * 0.2, x + w * 0.55, y + h * 0.85],
                       fill=(226, 232, 240))
        draw.rectangle([x + w * 0.2, y + h * 0.2, x + w * 0.8, y + h * 0.32],
                       fill=(226, 232, 240))
    f = SANS_B(11)
    tw = draw.textlength(label, font=f)
    tx = x + (w - tw) / 2
    ty = y + h - 16
    draw.rectangle([tx - 4, ty - 2, tx + tw + 4, ty + 13], fill=(0, 0, 0))
    draw.text((tx, ty), label, font=f, fill=WHITE)


MINI_KIND = {4: ("tanker", "2 TANKERS"), 5: ("drone", "7 DRONES DOWN"),
             6: ("refinery", "2 REFINERIES"), 7: ("power", "5 REGIONS"),
             8: ("treaty", "TREATY SIGNED"), 9: ("bill", "£2,166"),
             10: ("factory", "17,000 TAKA"), 11: ("fire", "31 DEAD"),
             12: ("camp", "SHATI CAMP"), 13: ("court", "RULING")}


# ---------------------------------------------------------------- drawing
def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(232, 224, 200),
                   outline=LINE)
    # rough continents (fractions of the box)
    def poly(fracs, fill):
        pts = [(x + w * fx, y + h * fy) for fx, fy in fracs]
        draw.polygon(pts, fill=fill)
    tan = (203, 187, 150)
    poly([(0.03, 0.12), (0.28, 0.08), (0.33, 0.22), (0.28, 0.38),
          (0.18, 0.42), (0.10, 0.32), (0.02, 0.22)], tan)          # N America
    poly([(0.22, 0.48), (0.32, 0.45), (0.34, 0.62), (0.28, 0.82),
          (0.23, 0.68)], tan)                                       # S America
    poly([(0.47, 0.10), (0.58, 0.08), (0.60, 0.22), (0.52, 0.28),
          (0.46, 0.2)], tan)                                        # Europe
    poly([(0.48, 0.32), (0.60, 0.30), (0.62, 0.52), (0.56, 0.72),
          (0.50, 0.58)], tan)                                       # Africa
    poly([(0.61, 0.08), (0.95, 0.06), (0.97, 0.30), (0.85, 0.45),
          (0.72, 0.38), (0.62, 0.25)], tan)                         # Asia
    poly([(0.80, 0.62), (0.92, 0.60), (0.93, 0.72), (0.82, 0.74)], tan)
    # pins
    fnum = SANS_B(8)
    for num, (fx, fy) in sorted(PINS.items()):
        px, py = x + w * fx, y + h * fy
        r = 8
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=WHITE, width=1)
        t = str(num)
        tw = draw.textlength(t, font=fnum)
        draw.text((px - tw / 2, py - 6), t, font=fnum, fill=WHITE)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    all_stories = [(n, r, f) for (n, r, f, *_rest) in
                   [(p[0], p[1], p[2]) for p in PANELS]]
    all_stories += [(n, r, f) for (n, r, f, _t, _s) in ALSO]
    assert len(all_stories) == 50, len(all_stories)
    assert sorted(n for n, _r, _f in all_stories) == list(range(1, 51))
    reg_counts = Counter(r for _n, r, _f in all_stories)
    field_counts = Counter(f for _n, _r, f in all_stories)

    # ---- top bar
    d.rectangle([0, 0, W, 22], fill=NAVY)
    top = ("THE WORLD IN ONE DAY  -  50 STORIES  -  10 REGIONS  -  "
           "%d FIELDS  -  ALL FIRST REPORTED ON WEDNESDAY 25 NOVEMBER 2026"
           % len(field_counts))
    centre(d, W // 2, 4, top, SANS_B(12), WHITE)

    # ---- masthead
    centre(d, W // 2, 26, "Wednesday 25 November 2026", SERIF_B(54), INK)
    # red rule under masthead
    d.line([(M, 84), (W - M, 84)], fill=RED, width=2)
    centre(d, W // 2, 90,
           "US proposes tariffs on 14 economies  -  AI doubts sink Asian "
           "chip stocks  -  Pakistan's first astronaut docks at Tiangong",
           SERIF(16), RED)

    # ---- region strip
    y = 114
    seg_w = CW / len(REGION_ORDER)
    for i, reg in enumerate(REGION_ORDER):
        x0 = M + i * seg_w
        col = REGION_COLORS[reg]
        d.rectangle([x0, y, x0 + seg_w - 1, y + 15], fill=col)
        label = "%s %d" % (REGION_SHORT[reg], reg_counts[reg])
        f = SANS_B(9)
        centre(d, x0 + seg_w / 2, y + 2, label, f, WHITE)
    # ---- fields line (single line; shrink font until it fits)
    y = 134
    fields_txt = "  ·  ".join(
        "%s %d" % (fld, field_counts[fld])
        for fld in sorted(field_counts, key=lambda f: -field_counts[f]))
    fsize = 10
    while fsize > 7 and text_w(d, fields_txt, SANS(fsize)) > CW:
        fsize -= 1
    d.text((M, y), fields_txt, font=SANS(fsize), fill=MUTED)

    # ---- big numbers
    y = 156
    cell_w = CW / 5
    fnum = SERIF_B(30)
    flab = SANS(10)
    for i, (num, lab) in enumerate(BIG_NUMBERS):
        x0 = M + i * cell_w
        if i:
            d.line([(x0, y + 2), (x0, y + 34)], fill=LINE, width=1)
        centre(d, x0 + cell_w / 2, y, num, fnum, RED if i in (0, 1, 2) else INK)
        ly = y + 32
        for line in lab.split("\n"):
            centre(d, x0 + cell_w / 2, ly, line, flab, MUTED)
            ly += 12
    d.line([(M, 212), (W - M, 212)], fill=INK, width=1)

    # ---- UTC timeline
    y = 216
    d.rectangle([M, y, W - M, y + 18], fill=NAVY)
    f = SANS_B(10)
    tw = text_w(d, TIMELINE, f)
    if tw > CW - 8:
        f = SANS(10)
    d.text((M + 6, y + 3), TIMELINE, font=f, fill=WHITE)

    # ---- heroes
    hy = 240
    hw = (CW - 2 * 12) / 3
    hero_scene = {1: scene_ship, 2: scene_chart, 3: scene_space}
    for i, p in enumerate(PANELS[:3]):
        num, _reg, _fld, tag, city, head, body = p
        x0 = M + i * (hw + 12)
        d.rectangle([x0, hy, x0 + hw, hy + 232], fill=PANEL, outline=LINE)
        hero_scene[num](d, x0 + 1, hy + 1, hw - 2, 104)
        # number badge
        bx, by = x0 + 14, hy + 118
        d.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=RED)
        t = str(num)
        d.text((bx - text_w(d, t, SANS_B(11)) / 2, by - 8), t,
               font=SANS_B(11), fill=WHITE)
        # dateline + tag
        tf = SANS_B(9)
        tag_txt = TAG_FULL[tag]
        tw = text_w(d, tag_txt, tf)
        d.rectangle([x0 + hw - tw - 14, hy + 110, x0 + hw - 6, hy + 126],
                    fill=TAG_COLOR[tag])
        d.text((x0 + hw - tw - 10, hy + 111), tag_txt, font=tf, fill=WHITE)
        d.text((x0 + 30, hy + 111), city, font=tf, fill=RED)
        yy = draw_wrapped(d, x0 + 8, hy + 130, head, SANS_B(15), hw - 16,
                          INK, spacing=1)
        yy = draw_wrapped(d, x0 + 8, yy + 2, body, SANS(10), hw - 16,
                          INK, spacing=1)
        why = WHY[num]
        draw_wrapped(d, x0 + 8, hy + 232 - 26, why, SANS(9), hw - 16,
                     MUTED, spacing=1)

    # ---- small rows (panels 4-13)
    def small_row(panels, y0, height):
        pw = (CW - 4 * 10) / 5
        for i, p in enumerate(panels):
            num, _reg, _fld, tag, city, head, body = p
            x0 = M + i * (pw + 10)
            d.rectangle([x0, y0, x0 + pw, y0 + height], fill=PANEL,
                        outline=LINE)
            kind, label = MINI_KIND[num]
            mini_scene(d, x0 + 1, y0 + 1, pw - 2, 52, kind, label)
            bx, by = x0 + 12, y0 + 64
            d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=RED)
            t = str(num)
            d.text((bx - text_w(d, t, SANS_B(10)) / 2, by - 7), t,
                   font=SANS_B(10), fill=WHITE)
            tf = SANS_B(8)
            tag_txt = TAG_FULL[tag]
            tw = text_w(d, tag_txt, tf)
            d.rectangle([x0 + pw - tw - 12, y0 + 56, x0 + pw - 4, y0 + 70],
                        fill=TAG_COLOR[tag])
            d.text((x0 + pw - tw - 8, y0 + 57), tag_txt, font=tf, fill=WHITE)
            d.text((x0 + 26, y0 + 57), city, font=tf, fill=RED)
            yy = draw_wrapped(d, x0 + 6, y0 + 72, head, SANS_B(12),
                              pw - 12, INK, spacing=0)
            draw_wrapped(d, x0 + 6, yy + 1, body, SANS(9), pw - 12, INK,
                         spacing=0)

    small_row(PANELS[3:8], 478, 140)
    small_row(PANELS[8:13], 624, 140)

    # ---- bottom: map + also list
    by = 772
    d.text((M, by), "WHERE IT HAPPENED", font=SANS_B(11), fill=INK)
    d.text((M + 352, by), "ALSO ON WEDNESDAY 25 NOVEMBER",
           font=SANS_B(11), fill=INK)
    d.line([(M, by + 16), (M + 330, by + 16)], fill=INK, width=1)
    d.line([(M + 352, by + 16), (W - M, by + 16)], fill=INK, width=1)
    draw_map(d, M, by + 20, 330, 140)
    # legend under map
    ly = by + 164
    d.text((M, ly), "Pins = story numbers  -  C CONFIRMED  R REPORTED  "
                    "O OFFICIAL  CL CLAIM", font=SANS(9), fill=MUTED)

    # also list: 3 columns x 13 rows
    ax = M + 352
    aw = W - M - ax
    col_w = (aw - 2 * 8) / 3
    f9 = SANS(9)
    for idx, item in enumerate(ALSO):
        col = idx // 13
        row = idx % 13
        x0 = ax + col * (col_w + 8)
        y0 = by + 20 + row * 12
        num, _r, _f, _t, text = item
        d.text((x0, y0), text, font=f9, fill=INK)

    # ---- footer
    fy = 946
    d.rectangle([M, fy, W - M, fy + 40], fill=CREAM, outline=RED)
    d.rectangle([M, fy, M + 4, fy + 40], fill=RED)
    draw_wrapped(d, M + 10, fy + 3, DATE_CHECK, SANS_B(9), CW - 20, INK,
                 spacing=1)
    d.text((M, fy + 46), LEGEND, font=SANS(9), fill=MUTED)
    d.text((M, fy + 60), SOURCES, font=SANS(9), fill=MUTED)
    d.text((M, fy + 60), "", font=SANS(9), fill=MUTED)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    img.save(os.path.join(outdir, "entry.png"), format="PNG",
             optimize=True)


if __name__ == "__main__":
    main()
