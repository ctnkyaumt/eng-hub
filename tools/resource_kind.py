"""Shared source classification; printable board games remain worksheets."""
import re
import unicodedata


def online_game(item):
    if item.get("file"):
        return False
    link = item.get("link", "")
    if re.search(r"\.(pdf|docx?|zip|jpe?g|png)(?:$|\?)", link, re.I):
        return False
    value = (link + " " + item.get("title", "")).lower().replace("ı", "i")
    value = "".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c))
    return bool(re.search(r"rgbenglish\.github\.io|wordwall\.net|learningapps\.org|eltarena|wordwars|duel mode|3te3|buzzer|oyun", value))
