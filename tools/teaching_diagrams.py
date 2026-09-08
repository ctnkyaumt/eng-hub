"""Small, original vector diagrams for calendars, frequency and computer actions."""
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "app/img/concepts"
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def text(x, y, value, size=24, color="#17334f"):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial,sans-serif" font-size="{size}" font-weight="700" fill="{color}">{html.escape(value)}</text>'


def write(name, body):
    DEST.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    (DEST / (slug + ".svg")).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 340"><rect width="500" height="340" rx="20" fill="#f4f8fc"/>' + body + '</svg>', encoding="utf-8")
    return "/app/img/concepts/" + slug + ".svg"


def diagrams():
    result = {}
    for day in DAY_NAMES + ["weekdays", "weekend"]:
        cells = text(250, 62, "A WEEK", 25)
        selected = list(range(5)) if day == "weekdays" else [5, 6] if day == "weekend" else [DAY_NAMES.index(day)]
        for n, label in enumerate(DAY_NAMES):
            x = 18 + n * 67
            color = "#087ea4" if n in selected else "#dbe5ec"
            cells += f'<rect x="{x}" y="115" width="62" height="120" rx="10" fill="{color}"/>'
            cells += text(x + 31, 164, label[:3], 18, "white" if n in selected else "#617588")
            if n in selected:
                cells += f'<path d="M{x+17} 192 l9 10 19 -24" fill="none" stroke="white" stroke-width="6"/>'
        result[day.lower()] = write(day, cells)
    for name, count in [("always", 10), ("usually", 8), ("often", 7), ("sometimes", 5), ("rarely", 1), ("never", 0), ("how often", -1)]:
        body = text(250, 65, "HOW OFTEN?" if count < 0 else "10 DAYS", 27)
        for n in range(10):
            x, y = 55 + n % 5 * 98, 132 + n // 5 * 95
            body += f'<circle cx="{x}" cy="{y}" r="32" fill="{"#087ea4" if n < count else "#dbe5ec"}"/>'
            body += text(x, y + 9, "?" if count < 0 else "✓" if n < count else "–", 30, "white" if n < count else "#617588")
        result[name] = write(name, body)
    holidays = {"19th may — youth and sports day": ("19", "MAY"), "23rd april — children's day": ("23", "APRIL"),
                "29th october — republic day": ("29", "OCTOBER"), "30th august — victory day": ("30", "AUGUST")}
    for name, (day, month) in holidays.items():
        body = '<rect x="52" y="55" width="396" height="235" rx="18" fill="white" stroke="#cbd5e1" stroke-width="3"/><path d="M52 113h396V73q0-18-18-18H70q-18 0-18 18z" fill="#d9283e"/>'
        body += text(250, 97, month, 28, "white") + text(250, 230, day, 100)
        result[name] = write(name, body)
    screen = '<rect x="42" y="40" width="416" height="245" rx="16" fill="white" stroke="#17334f" stroke-width="8"/><path d="M42 82h416" stroke="#17334f" stroke-width="6"/><circle cx="68" cy="60" r="6" fill="#fa765f"/>'
    for name in ["account", "sign in", "log on", "log off", "friend request", "social networking site"]:
        body = screen
        if name in ("friend request", "social networking site"):
            body += '<path d="M140 150L250 210 360 145" fill="none" stroke="#087ea4" stroke-width="7"/>'
            for x, y in [(140, 140), (250, 205), (360, 135)]:
                body += f'<circle cx="{x}" cy="{y}" r="28" fill="#087ea4"/><circle cx="{x}" cy="{y-8}" r="8" fill="white"/><path d="M{x-14} {y+15}q14-25 28 0" fill="white"/>'
            if name == "friend request": body += text(250, 120, "+ Add friend", 24)
        elif name == "log off":
            body += text(250, 167, "Signed out", 35) + text(250, 218, "Session ended", 23)
        else:
            body += text(250, 127, "My account" if name == "account" else "Sign in", 27)
            body += '<rect x="110" y="148" width="280" height="40" rx="5" fill="#e6eef5"/><rect x="110" y="198" width="280" height="40" rx="5" fill="#e6eef5"/>'
            body += text(250, 176, "username", 20) + text(250, 228, "••••••••", 25)
        result[name] = write(name, body)
    body = text(250, 62, "CALL ENDED", 28)
    body += '<path d="M125 210Q250 105 375 210" stroke="#d9283e" stroke-width="38" fill="none" stroke-linecap="round"/><rect x="97" y="191" width="74" height="54" rx="14" fill="#d9283e"/><rect x="329" y="191" width="74" height="54" rx="14" fill="#d9283e"/>'
    result["hang up"] = write("hang up", body)
    return result
