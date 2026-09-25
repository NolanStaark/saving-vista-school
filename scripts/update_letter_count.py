#!/usr/bin/env python3
"""
Keeps the letter-count numbers baked into letters.html (and its Spanish
counterpart, es/letters.html -- same feed) in sync with reality:

  * "Total Letters Submitted" -- the two count-banner spans
    (#total-count-banner, #total-count-banner-2), from the feed's
    totalSubmitted field.
  * "Published" letters shown on the page -- the number of rows the feed
    returns (Status = Published). In letters.html that's every
    <span class="live-letter-count">; in es/letters.html it's
    <span id="visible-letters-count">.

These are fallback seeds, not the source of truth: the live page still
fetches the Apps Script feed on every visit and corrects the displayed
numbers. Baking fresh numbers in just means that (a) the on-load count-up
animation starts from a real number, and (b) a visitor who hits the page
while Google's feed is down still sees current-ish counts instead of stale
ones.

Google's Apps Script web apps occasionally fail a request (seen in practice:
a ~40s wait, then a 404 on the one-time script.googleusercontent.com redirect
URL). So each run retries a few times, starting from the /exec URL each time
to get a fresh redirect. If every attempt fails, the run logs a warning and
exits successfully WITHOUT touching the files -- a missed refresh of a
fallback number isn't worth a failed-workflow email. Markup mismatches (the
script can't find the spans it expects) still fail loudly, because that's a
real bug that needs fixing.

Run on a schedule via .github/workflows/update-letter-count.yml.
"""
import re
import sys
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
LETTERS_HTML_PATH = REPO_ROOT / "letters.html"
LETTERS_HTML_ES_PATH = REPO_ROOT / "es" / "letters.html"
FEED_URL_RE = re.compile(r"var LETTERS_FEED_URL = '([^']+)';")
USER_AGENT = "Mozilla/5.0 (compatible; SavingVistaSchoolBot/1.0; +https://savingvistaschool.org)"

MAX_ATTEMPTS = 3
RETRY_WAIT_SECONDS = [10, 30]  # wait before attempt 2, attempt 3
REQUEST_TIMEOUT_SECONDS = 60


def get_feed_url(html):
    match = FEED_URL_RE.search(html)
    if not match:
        sys.exit("Could not find LETTERS_FEED_URL in letters.html")
    return match.group(1)


def fetch_counts_once(feed_url):
    resp = requests.get(
        feed_url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT_SECONDS
    )
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise ValueError("feed response isn't a JSON object")
    total = data.get("totalSubmitted")
    items = data.get("items")
    if not isinstance(total, int) or isinstance(total, bool):
        raise ValueError("feed response has no numeric totalSubmitted field")
    if not isinstance(items, list):
        raise ValueError("feed response has no items list")
    return total, len(items)


def fetch_counts(feed_url):
    """Returns (total_submitted, published_count), or None if every attempt failed."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return fetch_counts_once(feed_url)
        except (requests.RequestException, ValueError) as err:
            print("Attempt {}/{} to read the letters feed failed: {}".format(
                attempt, MAX_ATTEMPTS, err))
            if attempt < MAX_ATTEMPTS:
                wait = RETRY_WAIT_SECONDS[attempt - 1]
                print("Retrying in {}s...".format(wait))
                time.sleep(wait)
    return None


def replace_span_numbers(html, pattern, new_value, what, label, exactly=None):
    """Replace the digits captured between group 1 and group 2 of `pattern`."""
    new_html, count = pattern.subn(r"\g<1>{}\g<2>".format(new_value), html)
    if count == 0 or (exactly is not None and count != exactly):
        sys.exit(
            "Expected {} {} in {}, found {} -- markup may have changed, "
            "update this script's pattern.".format(
                exactly if exactly is not None else "at least one", what, label, count
            )
        )
    return new_html


def total_banner_pattern(elem_id):
    # <span ... id="X" data-count="18" ...>18</span> -- id before data-count,
    # which is how both letters pages write them. Both numbers get replaced.
    return re.compile(
        r'(<span\b[^>]*\bid="{}"[^>]*\bdata-count=")\d+("[^>]*>)\d+(</span>)'.format(
            re.escape(elem_id)
        )
    )


def update_total_banner(html, elem_id, total, label):
    new_html, count = total_banner_pattern(elem_id).subn(
        r"\g<1>{0}\g<2>{0}\g<3>".format(total), html
    )
    if count != 1:
        sys.exit(
            "Expected exactly one #{} span in {}, found {} "
            "-- markup may have changed, update this script's pattern.".format(
                elem_id, label, count
            )
        )
    return new_html


LIVE_COUNT_CLASS_RE = re.compile(
    r'(<span\b[^>]*\bclass="live-letter-count"[^>]*>)\d+(</span>)'
)
VISIBLE_COUNT_ID_RE = re.compile(
    r'(<span\b[^>]*\bid="visible-letters-count"[^>]*>)\d+(</span>)'
)


def update_file(path, label, total, published, published_pattern, published_what,
                published_exactly=None):
    html = path.read_text(encoding="utf-8")
    updated = update_total_banner(html, "total-count-banner", total, label)
    updated = update_total_banner(updated, "total-count-banner-2", total, label)
    updated = replace_span_numbers(
        updated, published_pattern, published, published_what, label, published_exactly
    )
    if updated != html:
        path.write_text(updated, encoding="utf-8")
        print("Updated {}: {} submitted, {} published.".format(label, total, published))
    else:
        print("{} unchanged ({} submitted, {} published).".format(label, total, published))


def main():
    feed_url = get_feed_url(LETTERS_HTML_PATH.read_text(encoding="utf-8"))
    counts = fetch_counts(feed_url)
    if counts is None:
        # GitHub Actions shows ::warning:: lines as a yellow annotation on the
        # run, without failing it.
        print("::warning::Couldn't read the letters feed after {} attempts; "
              "left the baked-in counts as they were. The live page still "
              "loads real numbers from the feed on every visit.".format(MAX_ATTEMPTS))
        return
    total, published = counts

    update_file(LETTERS_HTML_PATH, "letters.html", total, published,
                LIVE_COUNT_CLASS_RE, "span.live-letter-count")
    if LETTERS_HTML_ES_PATH.exists():
        update_file(LETTERS_HTML_ES_PATH, "es/letters.html", total, published,
                    VISIBLE_COUNT_ID_RE, "#visible-letters-count span",
                    published_exactly=1)


if __name__ == "__main__":
    main()
