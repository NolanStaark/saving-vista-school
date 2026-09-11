#!/usr/bin/env python3
"""
Pulls Vista School's Board Meeting and Townhall Meeting dates/times from
Vista's own public Google Calendar -- the source Vista itself keeps current,
including one-off reschedules -- and merges in Agenda/Minutes/Recording
links from Vista's board-meetings page where available, into
assets/data/meetings.json so meetings.html can render always-current dates
without anyone here updating them by hand.

Vista's calendar has real Google Calendar recurrence rules with per-meeting
overrides (a single occurrence can be moved without changing the recurring
series), so we resolve those with `recurring_ical_events` rather than
assuming a fixed weekday/time pattern -- Vista's own stated "4th Tuesday"
description has not held in practice (e.g. meetings moved to Mondays for a
stretch in 2026).

Run on a schedule via .github/workflows/update-meetings.yml.
"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events
import requests
from bs4 import BeautifulSoup

CALENDAR_ICS_URL = (
    "https://calendar.google.com/calendar/ical/"
    "vistautah.com_848rd4r1ssm1rkme3mnr3ke9h4%40group.calendar.google.com/public/basic.ics"
)
BOARD_PAGE_URL = "https://www.vistautah.com/board-meetings"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "assets" / "data" / "meetings.json"
USER_AGENT = "Mozilla/5.0 (compatible; SavingVistaSchoolBot/1.0; +https://savingvistaschool.org)"
DENVER = ZoneInfo("America/Denver")

PAST_WINDOW_DAYS = 14
FUTURE_WINDOW_DAYS = 270

TOWNHALL_RE = re.compile(r"town\s*hall", re.IGNORECASE)
BOARD_RE = re.compile(r"board meeting", re.IGNORECASE)


def fetch_text(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def classify(summary):
    if TOWNHALL_RE.search(summary):
        return "townhall"
    if BOARD_RE.search(summary):
        return "board"
    return None


def fetch_calendar_meetings():
    ics_text = fetch_text(CALENDAR_ICS_URL)
    calendar = icalendar.Calendar.from_ical(ics_text)

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=PAST_WINDOW_DAYS)
    end = now + timedelta(days=FUTURE_WINDOW_DAYS)

    occurrences = recurring_ical_events.of(calendar).between(start, end)

    meetings = []
    for event in occurrences:
        summary = str(event.get("SUMMARY", ""))
        kind = classify(summary)
        if not kind:
            continue

        dt = event["DTSTART"].dt
        if isinstance(dt, datetime):
            local_dt = dt.astimezone(DENVER)
        else:
            local_dt = datetime(dt.year, dt.month, dt.day, tzinfo=DENVER)

        meetings.append({
            "type": kind,
            "summary": summary,
            "date": local_dt.date().isoformat(),
            "display_date": local_dt.strftime("%B %-d, %Y"),
            "time": local_dt.strftime("%-I:%M %p"),
            "_sort_key": local_dt.isoformat(),
        })

    seen = set()
    deduped = []
    for m in meetings:
        key = (m["type"], m["date"], m["time"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(m)

    deduped.sort(key=lambda m: m["_sort_key"])
    for m in deduped:
        del m["_sort_key"]
    return deduped


def parse_board_page(html):
    soup = BeautifulSoup(html, "html.parser")
    docs_by_date = {}

    for table in soup.find_all("table"):
        header_cells = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if not any("date" in h for h in header_cells) or not any("agenda" in h for h in header_cells):
            continue

        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            date_text = cells[0].get_text(strip=True)
            if not date_text:
                continue

            iso_date = None
            for fmt in ("%B %d, %Y", "%b %d, %Y"):
                try:
                    iso_date = datetime.strptime(date_text, fmt).date().isoformat()
                    break
                except ValueError:
                    continue
            if not iso_date:
                continue

            def link_or_none(cell):
                a = cell.find("a")
                return a.get("href") if a and a.get("href") else None

            docs_by_date[iso_date] = {
                "agenda_url": link_or_none(cells[1]),
                "minutes_url": link_or_none(cells[2]),
                "recording_url": link_or_none(cells[3]),
            }

    archive_years = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if re.search(r"/\d{4}-\d{4}-board-meetings", href) and text and href not in seen:
            seen.add(href)
            archive_years.append({"label": text, "url": href})

    return docs_by_date, archive_years


def main():
    meetings = fetch_calendar_meetings()
    if not meetings:
        print("No meetings resolved from Vista's calendar -- not writing output.", file=sys.stderr)
        sys.exit(1)

    docs_by_date = {}
    archive_years = []
    try:
        board_html = fetch_text(BOARD_PAGE_URL)
        docs_by_date, archive_years = parse_board_page(board_html)
    except Exception as exc:
        print(f"Warning: couldn't fetch/parse Vista's board-meetings page ({exc}); "
              f"continuing with calendar dates only.", file=sys.stderr)

    for m in meetings:
        if m["type"] == "board" and m["date"] in docs_by_date:
            m.update(docs_by_date[m["date"]])

    data = {
        "source": CALENDAR_ICS_URL,
        "board_page_source": BOARD_PAGE_URL,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "meetings": meetings,
        "archive_years": archive_years,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(meetings)} meetings and {len(archive_years)} archive years to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
