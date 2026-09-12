#!/usr/bin/env python3
"""
Keeps the "Letters Submitted" count-banner numbers in letters.html roughly
in sync with reality, so the on-load count-up animation (see letters.html's
inline script) starts from a real, recent number instead of always
starting from 0.

This is a fallback seed, not the source of truth: the live page still
fetches the Apps Script feed on every visit and corrects the displayed
number if it's moved since this last ran. That means it's fine for this to
run infrequently (see .github/workflows/update-letter-count.yml) -- worst
case, a visitor briefly sees last run's number before the live feed
corrects it a moment later.

Run on a schedule via .github/workflows/update-letter-count.yml.
"""
import re
import sys
from pathlib import Path

import requests

LETTERS_HTML_PATH = Path(__file__).resolve().parent.parent / "letters.html"
FEED_URL_RE = re.compile(r"var LETTERS_FEED_URL = '([^']+)';")
USER_AGENT = "Mozilla/5.0 (compatible; SavingVistaSchoolBot/1.0; +https://savingvistaschool.org)"


def get_feed_url(html):
    match = FEED_URL_RE.search(html)
    if not match:
        sys.exit("Could not find LETTERS_FEED_URL in letters.html")
    return match.group(1)


def get_total_submitted(feed_url):
    resp = requests.get(feed_url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict) or not isinstance(data.get("totalSubmitted"), int):
        sys.exit(
            "Feed response didn't include a numeric totalSubmitted field "
            "-- has the Apps Script's response shape changed?"
        )
    return data["totalSubmitted"]


def update_span(html, elem_id, new_value):
    # Matches the count-banner spans regardless of attribute order, as long
    # as id comes before data-count in the tag (that's how letters.html
    # writes them): <span ... id="X" data-count="18" ...>18</span>
    pattern = re.compile(
        r'(<span\b[^>]*\bid="{}"[^>]*\bdata-count=")\d+("[^>]*>)\d+(</span>)'.format(
            re.escape(elem_id)
        )
    )
    new_html, count = pattern.subn(
        r"\g<1>{0}\g<2>{0}\g<3>".format(new_value), html
    )
    if count != 1:
        sys.exit(
            "Expected exactly one #{} span in letters.html, found {} "
            "-- markup may have changed, update this script's pattern.".format(
                elem_id, count
            )
        )
    return new_html


def main():
    html = LETTERS_HTML_PATH.read_text(encoding="utf-8")
    feed_url = get_feed_url(html)
    total = get_total_submitted(feed_url)

    updated = update_span(html, "total-count-banner", total)
    updated = update_span(updated, "total-count-banner-2", total)

    if updated == html:
        print("Letter count unchanged ({}); nothing to write.".format(total))
        return

    LETTERS_HTML_PATH.write_text(updated, encoding="utf-8")
    print("Updated letters.html seed count to {}.".format(total))


if __name__ == "__main__":
    main()
