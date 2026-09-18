#!/usr/bin/env python3
"""
Build script for savingvistaschool.org's English/Spanish page pairs.

Why this exists: every translated page used to be a fully independent copy
of its English original, so any structural/layout change had to be
hand-mirrored into the Spanish file. This script generates BOTH language
versions of a page from one shared template (i18n/templates/<page>.html.tmpl)
plus per-language string tables (i18n/locales/<lang>/common.json and
i18n/locales/<lang>/<page>.json). From now on, a layout change happens once,
in the template; a wording change happens once, in the locale JSON.

Usage:
    python3 scripts/build_pages.py            # build all configured pages
    python3 scripts/build_pages.py about       # build just one page

Run this from the repo root (the "site" folder). After running, review the
diff (git diff) before committing -- the script only writes files, it
doesn't stage or commit anything.
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://savingvistaschool.org"

# Every page currently built by this script. Add an entry here (plus a
# template + locale files) to migrate another page off hand-duplicated HTML.
PAGES = ["about"]

LOCALES = {
    "en": {
        "prefix": "",             # asset-path prefix from this page's own location
        "out_dir": "",            # where the English file lives, relative to repo root
        "other_href": "es/{page}.html",   # relative link TO the other language's copy
        "other_lang": "es",
    },
    "es": {
        "prefix": "../",
        "out_dir": "es",
        "other_href": "../{page}.html",
        "other_lang": "en",
    },
}

# Small flag glyphs used by the language switcher. Not translatable text,
# so they live here rather than in the locale JSON files.
US_FLAG_SVG = (
    '<svg viewBox="0 0 20 20" aria-hidden="true"><rect width="20" height="20" fill="#fff"/>'
    '<rect y="0" width="20" height="1.54" fill="#B22234"/><rect y="3.08" width="20" height="1.54" fill="#B22234"/>'
    '<rect y="6.15" width="20" height="1.54" fill="#B22234"/><rect y="9.23" width="20" height="1.54" fill="#B22234"/>'
    '<rect y="12.31" width="20" height="1.54" fill="#B22234"/><rect y="15.38" width="20" height="1.54" fill="#B22234"/>'
    '<rect y="18.46" width="20" height="1.54" fill="#B22234"/><rect width="10.5" height="10.77" fill="#3C3B6E"/>'
    '<circle cx="2.6" cy="2.4" r="0.55" fill="#fff"/><circle cx="5.6" cy="2.4" r="0.55" fill="#fff"/>'
    '<circle cx="8.6" cy="2.4" r="0.55" fill="#fff"/><circle cx="4.1" cy="4.6" r="0.55" fill="#fff"/>'
    '<circle cx="7.1" cy="4.6" r="0.55" fill="#fff"/><circle cx="2.6" cy="6.8" r="0.55" fill="#fff"/>'
    '<circle cx="5.6" cy="6.8" r="0.55" fill="#fff"/><circle cx="8.6" cy="6.8" r="0.55" fill="#fff"/>'
    '<circle cx="4.1" cy="9.0" r="0.55" fill="#fff"/><circle cx="7.1" cy="9.0" r="0.55" fill="#fff"/></svg>'
)
MX_FLAG_SVG = (
    '<svg viewBox="0 0 20 20" aria-hidden="true"><rect width="20" height="20" fill="#fff"/>'
    '<rect x="0" width="6.7" height="20" fill="#006847"/><rect x="13.3" width="6.7" height="20" fill="#CE1126"/>'
    '<circle cx="10" cy="10" r="1.7" fill="#8B5E3C"/></svg>'
)
FLAG_SVG = {"en": US_FLAG_SVG, "es": MX_FLAG_SVG}

TOKEN_RE = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")


def load_locale(lang: str, page: str) -> dict:
    """Merge common.json + <page>.json for one language into {'common': ..., page: ...}."""
    locales_dir = REPO_ROOT / "i18n" / "locales" / lang
    common = json.loads((locales_dir / "common.json").read_text(encoding="utf-8"))
    page_strings = json.loads((locales_dir / f"{page}.json").read_text(encoding="utf-8"))
    return {"common": common, page: page_strings}


def lookup(context: dict, dotted_key: str) -> str:
    value = context
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(f"Template references unknown key: {{{{ {dotted_key} }}}}")
        value = value[part]
    return str(value)


def render(template_text: str, context: dict) -> str:
    def replace(match: re.Match) -> str:
        return lookup(context, match.group(1))

    return TOKEN_RE.sub(replace, template_text)


def build_page(page: str) -> list[Path]:
    template_path = REPO_ROOT / "i18n" / "templates" / f"{page}.html.tmpl"
    template_text = template_path.read_text(encoding="utf-8")

    page_url = {lang: f"{SITE_URL}/{cfg['out_dir'] + '/' if cfg['out_dir'] else ''}{page}.html"
                for lang, cfg in LOCALES.items()}

    written = []
    for lang, cfg in LOCALES.items():
        t = load_locale(lang, page)
        context = {
            "t": t,
            "lang": lang,
            "prefix": cfg["prefix"],
            "page_url_en": page_url["en"],
            "page_url_es": page_url["es"],
            "page_url_self": page_url[lang],
            "form_next_url": f"{page_url[lang]}?sent=1#contact",
            "other_page_url": cfg["other_href"].format(page=page),
            "other_lang": cfg["other_lang"],
            "own_flag_svg": FLAG_SVG[lang],
            "other_flag_svg": FLAG_SVG[cfg["other_lang"]],
        }
        output = render(template_text, context)
        out_path = REPO_ROOT / cfg["out_dir"] / f"{page}.html" if cfg["out_dir"] else REPO_ROOT / f"{page}.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        written.append(out_path)
    return written


def main() -> None:
    requested = sys.argv[1:] or PAGES
    unknown = [p for p in requested if p not in PAGES]
    if unknown:
        print(f"Unknown page(s): {', '.join(unknown)}. Configured pages: {', '.join(PAGES)}", file=sys.stderr)
        sys.exit(1)

    all_written = []
    for page in requested:
        all_written.extend(build_page(page))

    for path in all_written:
        print(f"wrote {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
