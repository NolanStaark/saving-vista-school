#!/usr/bin/env python3
"""
Pulls Vista School's next upcoming Board Meeting AND next upcoming Townhall
Meeting -- one of each, separately -- directly from Vista's own public
Google Calendar, and merges in Agenda/Minutes/Recording links from Vista's
board-meetings page where available, into assets/data/meetings.json so
meetings.html can show "what's next" for each meeting type at the top of
the page without anyone here updating it by hand.

Also scrapes the full current-year Board Meetings table (Date/Agenda/
Minutes/Recording, one row per meeting Vista has actually dated) from that
same board-meetings page into `current_year_board_meetings`, so
meetings.html can show a full-year table mirroring Vista's own page.
Board only -- Vista doesn't publish a Townhall equivalent. Rows on Vista's
page with no date yet (placeholder rows for meetings not yet scheduled)
are skipped since they carry no information.

Vista's calendar has real Google Calendar recurrence rules with per-meeting
overrides (a single occurrence can be moved without changing the recurring
series -- Vista's board meetings run monthly on a nominal "4th Tuesday" but
are frequently moved), so we resolve those with `recurring_ical_events`
rather than assuming a fixed weekday/time pattern.

Run on a schedule via .github/workflows/update-meetings.yml.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin
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
# Board gatherings Vista names something other than "Board Meeting" -- a
# retreat, work session or special meeting. These are still noticed board
# meetings and belong on the page, but we keep the distinguishing word so the
# site can label them rather than passing a retreat off as a regular business
# meeting. Deliberately conservative: the title must also say "board", so we
# never sweep in unrelated school events.
BOARD_ALT_RE = re.compile(r"\bboard\b.*?(retreat|work\s*session|special\s*meeting)"
                          r"|(retreat|work\s*session|special\s*meeting).*?\bboard\b",
                          re.IGNORECASE)
# A date cell on Vista's board page may carry a trailing qualifier, e.g.
# "October 09, 2026 Retreat" -- find the date inside the cell instead of
# requiring the cell to be nothing but a date.
DATE_IN_TEXT_RE = re.compile(r"([A-Za-z]{3,9}\.?\s+\d{1,2},\s*\d{4})")
QUALIFIER_RE = re.compile(r"\b(retreat|work\s*session|special\s*meeting)\b", re.IGNORECASE)


def meeting_label(text):
    """The distinguishing word for a non-regular board meeting, or None."""
    m = QUALIFIER_RE.search(text or "")
    if not m:
        return None
    return " ".join(w.capitalize() for w in m.group(1).split())


def fetch_text(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def classify(summary):
    """Returns (kind, label). `label` marks a board gathering that is not a
    regular business meeting (e.g. "Retreat"), otherwise None."""
    # Check townhall first: some of Vista's own event titles (e.g. "Vista
    # School Board Town Hall") contain both words, and those are townhalls.
    if TOWNHALL_RE.search(summary):
        return "townhall", None
    if BOARD_RE.search(summary):
        return "board", meeting_label(summary)
    if BOARD_ALT_RE.search(summary):
        return "board", meeting_label(summary)
    return None, None


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
        kind, label = classify(summary)
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
            "label": label,
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


def pick_next_board(calendar_next, board_rows):
    """The earliest upcoming board gathering across BOTH sources.

    Vista's board-meetings page sometimes carries a dated meeting their public
    calendar doesn't (the October 2026 board retreat, for one), so the page is
    treated as a second source for "what's next" rather than only as a place to
    find document links. When both sources list the same date the calendar entry
    wins -- only it carries a start time -- but it picks up the page's label."""
    today = datetime.now(DENVER).date().isoformat()
    upcoming = [r for r in board_rows if r.get("date") and r["date"] >= today]
    if not upcoming:
        return calendar_next
    earliest = min(upcoming, key=lambda r: r["date"])
    if calendar_next and calendar_next["date"] <= earliest["date"]:
        if (earliest["date"] == calendar_next["date"]
                and earliest.get("label") and not calendar_next.get("label")):
            calendar_next["label"] = earliest["label"]
        return calendar_next
    # The page has something sooner. It gives no start time, and meetings.html
    # already falls back to the usual 6pm when a time is absent, so leave it out
    # rather than inventing one.
    return {
        "type": "board",
        "summary": "Vista Board " + (earliest.get("label") or "Meeting"),
        "date": earliest["date"],
        "display_date": earliest["display_date"],
        "label": earliest.get("label"),
    }


def parse_board_page(html):
    """Pull the full current-year Board Meetings table (one row per meeting
    Vista has actually dated -- their page also includes blank placeholder
    rows for meetings not yet scheduled, which are skipped here since they
    carry no information) plus the list of archived-year page links, from
    Vista's own board-meetings page. This page only covers Board meetings
    -- Vista doesn't publish Townhall docs."""
    soup = BeautifulSoup(html, "html.parser")
    rows_ordered = []

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

            # Vista sometimes qualifies the date in the same cell, e.g.
            # "October 09, 2026 Retreat". Pull the date out of the cell rather
            # than requiring the whole cell to parse as one, or rows like that
            # get silently dropped.
            match = DATE_IN_TEXT_RE.search(date_text)
            if not match:
                continue
            iso_date = None
            for fmt in ("%B %d, %Y", "%b %d, %Y"):
                try:
                    iso_date = datetime.strptime(
                        match.group(1).replace(".", ""), fmt).date().isoformat()
                    break
                except ValueError:
                    continue
            if not iso_date:
                continue
            label = meeting_label(date_text)

            def link_or_none(cell):
                a = cell.find("a")
                if not a or not a.get("href"):
                    return None
                return urljoin(BOARD_PAGE_URL, a["href"])

            rows_ordered.append({
                "date": iso_date,
                "display_date": datetime.fromisoformat(iso_date).strftime("%B %-d, %Y"),
                "label": label,
                "agenda_url": link_or_none(cells[1]),
                "minutes_url": link_or_none(cells[2]),
                "recording_url": link_or_none(cells[3]),
            })

    rows_ordered.sort(key=lambda r: r["date"])
    docs_by_date = {r["date"]: {
        "agenda_url": r["agenda_url"],
        "minutes_url": r["minutes_url"],
        "recording_url": r["recording_url"],
    } for r in rows_ordered}

    archive_years = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if re.search(r"/\d{4}-\d{4}-board-meetings", href) and text and href not in seen:
            seen.add(href)
            archive_years.append({"label": text, "url": urljoin(BOARD_PAGE_URL, href)})

    return rows_ordered, docs_by_date, archive_years


def main():
    # Two independent sources, and either one can carry a run on its own:
    # the calendar has start times and townhalls, the board page sometimes has
    # a meeting the calendar doesn't (the Oct 2026 retreat). Neither fetch is
    # allowed to kill the run -- we only give up if BOTH end up empty, checked
    # after both have been consulted.
    meetings = []
    try:
        meetings = fetch_upcoming_meetings()
    except Exception as exc:
        print(f"Warning: couldn't fetch/parse Vista's calendar ({exc}); "
              f"falling back to their board-meetings page.", file=sys.stderr)

    next_board = next_of_type(meetings, "board")
    next_townhall = next_of_type(meetings, "townhall")

    current_year_board_meetings = []
    docs_by_date = {}
    archive_years = []
    try:
        board_html = fetch_text(BOARD_PAGE_URL)
        current_year_board_meetings, docs_by_date, archive_years = parse_board_page(board_html)
    except Exception as exc:
        print(f"Warning: couldn't fetch/parse Vista's board-meetings page ({exc}); "
              f"continuing with calendar dates only.", file=sys.stderr)

    next_board = pick_next_board(next_board, current_year_board_meetings)

    if not next_board and not next_townhall:
        # Don't overwrite a good file with an empty result if both sources are
        # briefly unreachable or their structure changed -- fail loudly so the
        # workflow surfaces it instead of the site silently going stale.
        print("No upcoming meetings resolved from Vista's calendar or board page "
              "-- not writing output.", file=sys.stderr)
        sys.exit(1)

    if next_board and next_board["date"] in docs_by_date:
        next_board.update(docs_by_date[next_board["date"]])

    # `updated_at` is when we last CHECKED (meetings.html shows it as "Schedule
    # last checked"), so it moves every run and the file is always rewritten --
    # that timestamp is the page's liveness signal and would be a lie if we
    # skipped the write. What we do instead is tell the workflow whether
    # anything *else* changed, so the commit message can say so and the history
    # stays readable at a glance.
    data = {
        "source": CALENDAR_ICS_URL,
        "board_page_source": BOARD_PAGE_URL,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "next_board": next_board,
        "next_townhall": next_townhall,
        "current_year_board_meetings": current_year_board_meetings,
        "archive_years": archive_years,
    }

    previous = None
    if OUTPUT_PATH.exists():
        try:
            previous = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous = None

    def schedule_only(d):
        return {k: v for k, v in (d or {}).items() if k != "updated_at"}

    schedule_changed = schedule_only(previous) != schedule_only(data)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"schedule_changed={'true' if schedule_changed else 'false'}\n")

    print("Schedule changed." if schedule_changed
          else "Schedule unchanged since the last run (timestamp refreshed).")
    print(f"Wrote next_board={next_board and next_board['date']}"
          f"{next_board and next_board.get('label') and ' (' + next_board['label'] + ')' or ''} "
          f"next_townhall={next_townhall and next_townhall['date']}, "
          f"{len(current_year_board_meetings)} current-year board meeting rows, "
          f"and {len(archive_years)} archive years to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
