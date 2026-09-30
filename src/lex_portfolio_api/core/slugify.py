import re
import unicodedata


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = name.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", name).strip("-")
