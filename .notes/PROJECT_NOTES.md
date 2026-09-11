# Saving Vista School — project notes for Claude

Read this first in any new chat scoped to one page of this site. It's the
cross-cutting context every page-specific conversation should share, so we
don't have to re-explain it each time.

## What this site is

savingvistaschool.org — a static HTML/CSS/vanilla-JS site on GitHub Pages,
run by an independent nonprofit of concerned parents. It is about Vista
School (full legal name "Vista at Entrada School of Performing Arts and
Technology"), a K-9 charter school in Ivins, Utah. **This site is explicitly
NOT affiliated with, endorsed by, or operated by Vista School, its
administration, or the Utah State Charter School Board** — every page's
disclaimer bar says so and that must never be softened or removed.

## Repo / workflow

- Local path: `D:\Documents\saving-vista-school-site\site\` on Russ's
  Windows machine, reached from Claude via `device_bash` at
  `$HOME/mnt/saving-vista-school-site/site/`.
- GitHub remote: `NolanStaark/saving-vista-school`.
- Claude can `git commit` locally via `device_bash`, but **cannot `git push`**
  — the device's network egress proxy returns 403 on github.com. Russ must
  push himself after each session (remind him).
- If `git` commands fail with "Operation not permitted" on `.git/*.lock`
  files, or "File exists" / "cannot lock ref HEAD": call
  `device_request_delete_permission` on the connected folder root once per
  session, then `rm -f .git/index.lock .git/HEAD.lock` and retry.
- Renaming a public-facing page: `git mv old.html new.html`, update all nav
  links site-wide, and leave `old.html` as a redirect stub (meta refresh +
  `location.replace('new.html')`) so existing bookmarks/links don't break.

## Never publish / redact

- Never reintroduce previously-redacted contact info.
- Never publish: the "Kim Clegg" folder or the duplicate minor's photo in it.
- Never publish: Barry Burr's letter, or the "Andersen" screenshot.
These were flagged explicitly earlier in the project and the restriction
still stands even if not repeated in a given chat.

## Site pages (current)

- `index.html` — placeholder "Coming Soon" page, no nav, don't touch nav
  logic here.
- `letters.html` (renamed from `parent-letters.html`) — parent letters of
  concern, fed by a Google Apps Script Web App JSON API in front of a
  private Google Sheet (Tally.so submissions land in the Sheet; some
  letters are added manually). Has category filter chips
  (`.filter-bar .tag[data-category]`) + `initFilters()`/`applyFilter()`.
- `meetings.html` (renamed from `live-meetings.html`) — YouTube live-stream
  embed + auto-updated Board/Townhall meeting schedule. See "Meetings
  automation" below.
- `policies.html` — searchable aggregator of Utah/USBE/charter parental
  rights & policy resources (17 cards, 8 categories), with a text search
  box + the same filter-chip pattern.
- `media.html`, `about.html`, `404.html`, `home-full.html` — mostly static;
  keep their nav in sync when pages are added/renamed.
- `DEPLOY.md` — deployment notes.

## Meetings automation (as of this writing)

`meetings.html` no longer has any hand-maintained dates. A GitHub Actions
workflow (`.github/workflows/update-meetings.yml`, daily cron) runs
`scripts/update_meetings.py`, which:
1. Fetches Vista's own public Google Calendar's ICS feed (calendar ID
   `vistautah.com_848rd4r1ssm1rkme3mnr3ke9h4@group.calendar.google.com`),
   resolves recurrence with `recurring_ical_events` (handles one-off
   reschedules via `RECURRENCE-ID` overrides — Vista's stated "4th Tuesday"
   pattern is NOT reliable in practice, e.g. all-Monday stretches happen).
2. Classifies events as `board` or `townhall` by title regex.
3. Merges in Agenda/Minutes/Recording links from
   `vistautah.com/board-meetings` (Board only — Vista doesn't publish
   Townhall docs) by matching date.
4. Writes `assets/data/meetings.json`, which `meetings.html`'s inline JS
   fetches and renders (unified chronological list, "Next" badge, doc
   links, archive-year links to Vista's own per-year pages).

Both Board and Townhall meetings are stated (per Russ) to be held in the
**Vista School Gym** — note the calendar's own `LOCATION` field disagrees
(says "Choir Room" for many entries), so the script does NOT use
calendar LOCATION; the venue text is hardcoded from what Russ told us.
Flag to Russ if this venue ever needs re-confirming.

**GitHub Actions gotcha not yet confirmed fixed**: for the workflow's
`git push` step to succeed, repo Settings → Actions → General → Workflow
permissions must be set to "Read and write permissions." Check this if the
Action runs but the commit/push step fails.

Neither Claude's cloud container nor `device_bash` can reach
`vistautah.com` or `calendar.google.com`'s ICS endpoint directly (both
blocked by egress proxy allowlisting) — verified via the Claude Browser
tool's same-origin `fetch()` instead when testing was needed. The GitHub
Actions runner has normal internet access, so the script works fine there
even though it can't be locally tested from either of Claude's shells.

## Google account situation (migration planned, NOT done)

- The Google Sheet + Apps Script Web App backing `letters.html` currently
  live under `roslow82@gmail.com`.
- A separate `SavingVistaSchool@gmail.com` account holds a Drive folder for
  manually-added letters.
- Russ wants everything eventually migrated to the `SavingVistaSchool@gmail.com`
  account (Sheet ownership transfer, Apps Script **redeploy** — ownership
  transfer alone does not move a live deployment, it needs a fresh deploy
  producing a new URL — Tally reconnect, and updating the feed URL in
  `letters.html`). This requires Russ to sign into the new account himself;
  Claude cannot do the sign-in/authorization steps. Not started.

## Open / unconfirmed items

- Whether updating Brave's Shields content-filter lists actually fixed the
  YouTube live-stream embed (a documented Brave bug) — Russ hasn't
  confirmed either way.
- A "filters regressed" report on `letters.html` — logic tested correct,
  one unreproduced anomaly noted; ask for a screenshot + context if it
  recurs.
- Russ's idea to expand the site into "an aggregate site for all the news
  going on at Vista, so like Newsletters" — not yet scoped.
- A wording fix flagged earlier for `letters.html`'s submit-column intro
  paragraph, about parents' choice over whether their name is attached to
  a letter — unclear if this was ever resolved; confirm with Russ if still
  needed.

## Working style Russ has asked for

- Split work into separate chats per page/feature (this file exists so
  each one can get oriented fast) and use parallel subagents for
  independent pieces of a task where that helps.
- Do the most current research when researching anything; say plainly when
  something isn't known rather than guessing; never restate a claim from
  Vista's own materials as fact without verifying it (see the "4th
  Tuesday" schedule correction above — Russ caught that one).
