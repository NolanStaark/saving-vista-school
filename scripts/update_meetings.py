#!/usr/bin/env python3
"""
Pulls Vista School's next upcoming Board Meeting AND next upcoming Townhall
Meeting -- one of each, separately -- directly from Vista's own public
Google Calendar, and merges in Agenda/Minutes/Recording links from Vista's
board-meetings page where available, into assets/data/meetings.json so
meetings.html can show "what's next" for each meeting type at the top of
the page without anyone here updating it by hand.

Vista's calendar has real Google Calendar recurrence rules with per-meeting
overrides (a single occurrence can be moved without changing the recurring
series -- Vista's board meetings run monthly on a nominal "4th Tuesday" but
are frequently moved), so we resolve those with `recurring_ical_events`
rather than assuming a fixed weekday/time pattern.

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

# How far ahead to look for the next occurrence of each meeting type. Board
# meetings run roughly monthly and Townhalls less often, so this comfortably
# covers finding one of each even around breaks/holidays.
FUTURE_WINDOW_DAYS = 270

TOWNHALL_RE = re.compile(r"town\s*hall", re.IGNORECASE)
BOARD_RE = re.compile(r"board meeting", re.IGNORECASE)


def fetch_text(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def classify(summary):
    # Check townhall first: some of Vista's own event titles (e.g. "Vista
    # School Board Town Hall") contain both words, and those are townhalls.
    if TOWNHALL_RE.search(summary):
        return "townhall"
    if BOARD_RE.search(summary):
        return "board"
    return None


def fetch_upcoming_meetings():
    """Returns all upcoming Board/Townhall occurrences within the window,
    chronologically, resolved directly from Vista's calendar (recurrence +
    per-occurrence overrides included)."""
    ics_text = fetch_text(CALENDAR_ICS_URL)
    calendar = icalendar.Calendar.from_ical(ics_text)

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=FUTURE_WINDOW_DAYS)

    occurrences = recurring_ical_events.of(calendar).between(now, end)

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
            # An all-day event would give a plain date -- shouldn't happen
            # for these meetings, but don't crash if Vista ever adds one.
            local_dt = datetime(dt.year, dt.month, dt.day, tzinfo=DENVER)

        meetings.append({
            "type": kind,
            "summary": summary,
            "date": local_dt.date().isoformat(),
            "display_date": local_dt.strftime("%B %-d, %Y"),
            "time": local_dt.strftime("%-I:%M %p"),
            "_sort_key": local_dt.isoformat(),
        })

    # De-duplicate identical (type, date, time) entries -- Vista's calendar
    # has some near-duplicate events for the same real-world meeting.
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


def next_of_type(meetings, kind):
    for m in meetings:
        if m["type"] == kind:
            return m
    return None


def parse_board_page(html):
    """Pull Agenda/Minutes/Recording links (keyed by date) and the list of
    archived-year page links from Vista's own board-meetings page. This page
    only covers Board meetings -- Vista doesn't publish Townhall docs."""
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
    meetings = fetch_upcoming_meetings()
    next_board = next_of_type(meetings, "board")
    next_townhall = next_of_type(meetings, "townhall")

    if not next_board and not next_townhall:
        # Don't overwrite a good file with an empty result if the calendar
        # is briefly unreachable or its structure changed -- fail loudly so
        # the workflow surfaces it instead of silently going stale.
        print("No upcoming meetings resolved from Vista's calendar -- not writing output.", file=sys.stderr)
        sys.exit(1)

    docs_by_date = {}
    archive_years = []
    try:
        board_html = fetch_text(BOARD_PAGE_URL)
        docs_by_date, archive_years = parse_board_page(board_html)
    except Exception as exc:
        # Doc links and the archive list are a bonus, not the source of
        # truth for dates -- don't fail the whole run over them.
        print(f"Warning: couldn't fetch/parse Vista's board-meetings page ({exc}); "
              f"continuing with calendar dates only.", file=sys.stderr)

    if next_board and next_board["date"] in docs_by_date:
        next_board.update(docs_by_date[next_board["date"]])

    data = {
        "source": CALENDAR_ICS_URL,
        "board_page_source": BOARD_PAGE_URL,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "next_board": next_board,
        "next_townhall": next_townhall,
        "archive_years": archive_years,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Wrote next_board={next_board and next_board['date']} "
          f"next_townhall={next_townhall and next_townhall['date']} "
          f"and {len(archive_years)} archive years to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
