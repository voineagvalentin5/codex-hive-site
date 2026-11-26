"""Apply the same navigation to every page that uses the shared site header."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent / "docs"
LINKS = [
    ("Projects", "/apps-1/", {"apps-1"}),
    ("Research", "/research/", {
        "research", "ftf", "ufft", "lsfm-vs-hl-3", "fractalfs", "daphnis-wake",
        "technology-stack-draft", "correction-notice", "intro", "rules-for-use",
    }),
    ("Games", "/interactive/", {"interactive"}),
    ("Media", "/media/", {"media", "music", "podcasts"}),
    ("Journal", "/blog/", {"blog"}),
    ("Services", "/audit/", {"audit"}),
]
NAV = re.compile(r'(<nav class="site-nav" id="site-nav" aria-label="Main">).*?(</nav>)', re.S)
STYLE = '<link rel="stylesheet" href="/assets/hub/hub.css?v=1">'


def apply(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    if not NAV.search(html):
        return False

    page = path.relative_to(ROOT).parts[0]
    entries = []
    for label, href, active in LINKS:
        current = ' aria-current="page"' if page in active else ""
        action = ' class="btn hub-nav-action"' if label == "Services" else ""
        entries.append(f'      <a href="{href}"{action}{current}>{label}</a>')

    updated = NAV.sub(lambda match: f"{match[1]}\n" + "\n".join(entries) + f"\n    {match[2]}", html, count=1)
    if STYLE not in updated:
        updated = updated.replace("</head>", f"{STYLE}</head>", 1)
    if updated != html:
        path.write_text(updated, encoding="utf-8", newline="\n")
    return True


if __name__ == "__main__":
    count = sum(apply(path) for path in ROOT.rglob("*.html"))
    print(f"Shared navigation applied to {count} pages")
