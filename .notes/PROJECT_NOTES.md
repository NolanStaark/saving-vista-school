# Saving Vista School — project notes for Claude

**This file lives in `.notes/` on purpose, not the repo root.** GitHub Pages for this site is set to "Deploy from a branch" (main, root) with no `.nojekyll` file, so Jekyll runs its default build, which excludes anything starting with `.` or `_` but NOT plain root files. A file like this sitting at the repo root -- especially one naming people whose content we're specifically trying to keep unpublished -- would be publicly fetchable at savingvistaschool.org/PROJECT_NOTES.md. Keep this (and DEPLOY.md) inside a dot-prefixed folder; never move either back to the root.

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
- Never publish: from the "Vista Website Media" Google Drive folder
  (shared with savingvistaschool@gmail.com by kimmeeg@gmail.com, Sept
  2026) -- `IMG8185657956546708511.jpg`, a screenshot naming a specific
  minor student and their private attendance/absence record, and
  `IMG2050795870800228188.jpg`, a near-duplicate from the same
  absence-confirmation flow. Neither has been used anywhere on the site.
  That same Drive folder also contained two Google Docs ("Monroe doc",
  "HaroldNet") that are just links to a 2022 HeraldNet article about the
  Monroe School District, WA -- NOT unrelated/misplaced as they first
  appeared: Vista's current Executive Director, Dr. Justin Blasko, is the
  same person as the Monroe superintendent in that article (confirmed via
  St. George News' Aug. 2023 coverage of his hiring). See the
  `home-full.html` note below -- this background is now written up there,
  sourced, not just linked.
- Never publish: `policies-absence.jpg` from that same "Vista Website
  Media" Drive folder (added Sept 10, 2026, by kimmeeg@gmail.com) --
  another screenshot naming a specific minor student ("Iosefa Tanielu")
  and their private attendance/absence record. Same pattern as the two
  images already listed above. Found while sourcing images for
  `policies.html`; excluded, not used anywhere on the site. Worth a
  heads-up to whoever's adding files to that Drive folder -- this is the
  third image of this exact type to show up there.

These were flagged explicitly earlier in the project and the restriction
still stands even if not repeated in a given chat.

## Site pages (current)

- `index.html` — still the placeholder "Coming Soon" page, no nav, don't
  touch nav logic here. A full replacement home page has been built and is
  staged in `home-full.html` (see below), ready to swap in — Russ asked to
  hold off on making it live for now. To swap it in later: replace
  `index.html`'s content with `home-full.html`'s (or `git mv` it over,
  updating the self-referencing nav links/`href="index.html"` as needed),
  then update this note and (optionally) remove the now-redundant
  `home-full.html`.
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
  box + the same filter-chip pattern. Sept 2026: added visuals -- an inline
  SVG "scales" graphic in the page-header (matches the letters.html
  `.page-header-graphic` convention), a per-category inline SVG icon
  (`.cat-icon`, Feather-style, matches the icon set already used in
  letters.html's category badges) on every filter-bar button and card
  badge, and two screened photos from the "Vista Website Media" Drive
  folder under `assets/policies/`: `dress-code-bottoms.jpg` (Vista's own
  dress-code policy, "Bottoms" section, with a parent's highlight on the
  rear-pockets requirement -- embedded in the "Vista's own board-adopted
  policies" card) and `absence-reason-options.jpg` (the excused-absence
  reason list from Vista's parent-portal app, cropped to drop the phone
  chrome -- embedded in "Compulsory education & truancy"). New CSS:
  `.policy-card-image` in style.css, plus `.filter-bar .tag` gained
  `display:inline-flex` for the icon+label pairing.
- `media.html`, `about.html`, `404.html` — mostly static; keep their nav
  in sync when pages are added/renamed.
- `home-full.html` — the finished replacement home page (hero + "Why This
  Site Exists" mission blurb + feature cards for Letters/Meetings/
  Policies/Media + a "Next Meeting" teaser pill fed by
  `assets/data/meetings.json`, same file `meetings.html` uses + a "Get
  Involved" CTA linking to `letters.html#submit-a-letter` and
  `about.html#contact`). NOT live yet — Russ wants to hold off swapping it
  in for `index.html`. Its shared CSS (`.hero-actions`, `.btn-primary`,
  `.btn-secondary`, `.btn-outline`, `.home-next-meeting`) is already in
  style.css (harmless/unused until swapped in).

  Also has an "A Closer Look at Vista's Leadership" section (Sept 2026,
  per Russ: "the home page is the crux of presenting the information
  we have gathered transparently") -- a sourced writeup of Executive
  Director Dr. Justin Blasko's background as former Monroe School
  District (WA) superintendent (placed on leave Dec. 2021 after an
  investigation substantiated bullying/misconduct complaints, resigned
  July 2022 with a ~$396k severance; cites St. George News, HeraldNet,
  Seattle Times -- see the exhibit-sources block in the HTML for exact
  links), plus supporting images in `assets/leadership/`: Vista's own
  org chart, two parent-compiled Transparent Utah charts on teacher
  tenure/exits vs. director-change years (captioned as parent-compiled,
  not independently produced/verified by this site), two Vista-School
  Facebook posts announcing administrative hires, a July 2026 Board
  enrollment slide, and a parent's Board letter requesting a salary
  audit with the author's name/phone number cropped out of the image
  (she was fine with her name being used, but Russ asked afterward to
  redact it anyway -- don't re-add it without checking with him again).
  New shared CSS for this: `.exhibit-intro`, `.exhibit-subhead`,
  `.exhibit-subhead-note`, `.exhibit-grid`, `.exhibit-card`,
  `.exhibit-caption`, `.exhibit-sources` (also unused until swapped in).
- `.notes/DEPLOY.md` — deployment notes (moved here for the same publishing-exposure reason as this file).

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

## Defamation-risk screening for letters (do this before publishing any new letter)

As of Sept 2026, a full read-through of the 18 letters then-published on
`letters.html` found most are fine (framed as the author's own opinion or
first-hand experience, or aimed at "the administration"/"the board"
collectively). A few named specific individuals (not the school, not the
author) and asserted damaging claims -- dishonesty, cover-ups, bias,
unethical conduct -- as flat fact rather than opinion, mostly resting on
secondhand/hearsay sourcing. Those were left published as-is (Russ's call),
but a disclaimer was added to `letters.html` (linking to `about.html#contact`
for correction requests) and this checklist exists so *new* submissions get
screened before they're moved from `assets/letters/` into
`assets/letters-archive/`:

- Does it name a specific person other than the author (a teacher, a
  specific staff/board member -- not "the administration" collectively)?
- If so, does it assert something damaging about that person as a stated
  fact ("he covered it up") rather than clearly-framed opinion/experience
  ("it felt to me like...", "I was told...", "in my view...")?
- Is the claim about that person's official actions/votes (lower risk --
  school officials are limited-purpose public figures for their official
  conduct) or about their private character/conduct (higher risk)?
- Is the claim sourced to the author's own direct experience, or to
  secondhand/hearsay reports ("colleagues told me...")? Hearsay stated as
  fact is the highest-risk pattern seen so far.
- Accusations of illegal conduct, financial impropriety, dishonesty, or
  abuse deserve the closest look regardless of source.

None of this is legal advice -- Russ has been told to get an actual Utah
attorney to review the site's publishing practices as it grows, especially
given growing traffic. This checklist is a non-lawyer screening aid, not a
substitute for that review.

Note: `about.html`'s contact section was updated (Sept 2026) -- the
placeholder phone/email/address were replaced with the nonprofit's real
contact info (email only: `savingvistaschool@gmail.com`; Russ confirmed
there's no phone or mailing address). The "Send a Message" form now posts
to FormSubmit.co (`action="https://formsubmit.co/savingvistaschool@gmail.com"`,
no account signup needed -- just an email confirmation on first real
submission) with a `_subject`, `_next` redirect back to
`about.html?sent=1#contact`, and a `_honey` spam honeypot field. The
"contact us" link in the letters disclaimer now dead-ends at a working
channel.

## Letters page: filters removed (Sept 2026 decision)

The recipient filter bar ("To Vista Administration" / "To the School Board" /
"To the State Charter School Board" / "General Concern") was REMOVED from
letters.html on purpose -- do not add it back without talking to Russ.

Why: of the 18 published letters, 7 were tagged State Charter Board, 7
"General Concern" (a catch-all, not a recipient), 4 School Board, and 0 "To
Vista Administration" -- so that button returned an empty list to anyone who
clicked it. Most of these letters went to more than one recipient anyway, so
filtering on a single recipient narrowed almost nothing and misrepresented
the letters. The page is now a straight reverse-chronological archive; each
card still shows its recipient as a badge.

Notes for whoever touches this next:
- `.filter-bar` and `.tag` CSS in style.css is STILL USED by policies.html.
  Do not delete those rules. `.letter-count` and `.no-results` are now unused
  but were left in place rather than risk a shared-stylesheet edit.
- The JS `initFilters()` function was replaced by `updateCounts()`, which only
  keeps the "18 Letters Published" banner numbers in sync once feed-loaded
  letters are prepended to the static ones.
- 7 letters still carry a "General Concern" badge, which reads oddly now that
  it stands alone as a label rather than a filter. Open question for Russ.
- If filtering ever comes back, the useful axis is subject matter (bullying &
  student safety, leadership & governance, transparency & communication, staff
  & culture, arts & curriculum, special ed & academic support) with letters
  allowed to carry MULTIPLE tags -- not a single recipient.

## Letters page: assets/letters/ and assets/letters-archive/ are legacy, unused (Sept 2026)

Confirmed while fixing a stale HTML comment in letters.html: these two
repo folders (leftover from before the Tally+Sheet+Apps-Script feed
existed) are NOT part of the current publish flow. Nothing in any HTML/JS/
Python in this repo references them anymore (only the old comment did,
now rewritten). Every file in assets/letters-archive/ is a pre-migration
duplicate of a letter that's since been re-uploaded to the "Letters"
Google Drive folder and linked from the Sheet's "Letter (PDF, photo, or
scan)" column instead (same filenames, same content, checked directly).
Don't add new letter files to either folder -- they won't do anything.
The real flow is: Tally submission or manual Sheet row -> team reviews +
puts the file on Google Drive -> Sheet row's Status set to "Published"
with a Display Title -> the Apps Script feed picks it up automatically.
(Left the old files in place rather than deleting them, same as the old
.jpg leadership charts -- harmless to keep around for reference.)

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
- When a concern Russ raises rests on a legal claim, use the most
  *defensible* framing rather than the first/strongest-sounding one --
  verify which law/rule actually applies (research it, don't assume) and
  reframe the concern through that, hedged as a question ("worth asking")
  rather than asserted as fact. Example: Russ read the absence-reason
  screenshot on policies.html as a HIPAA issue; HIPAA doesn't reach K-12
  schools' own attendance records (FERPA does, per HHS/ED joint guidance)
  -- so the point got reframed as a Utah Student Data Protection Act
  (§53E-9) data-minimization question instead, added as a `.policy-card-note`
  under that image. Standing instruction, not a one-off.


## Home page: leadership charts recreated (Sept 2026)

The phone-photo hand-drawn charts in `home-full.html`'s "A Closer Look at
Vista's Leadership" section were redrawn as clean landscape PNG charts
(matplotlib, site color palette) using the exact data read off the original
photos -- same numbers, same "compiled by parents, not independently
verified" framing, just legible:
- `assets/leadership/teacher-experience-exiting-chart.png` (was
  `teacher-experience-exiting-chart.jpg`)
- `assets/leadership/teacher-exits-chart.png` (was `teacher-exits-chart.jpg`)
- `assets/leadership/enrollment-by-grade-chart.png` (was
  `enrollment-numbers-2026.jpg`, a blurry projector-screen photo)
- `assets/leadership/enrollment-trend-chart.png` -- NEW: official 5-year
  Oct-1 enrollment (2022-2026: 1099/1113/1117/1115/1088), pulled from the
  Utah State Charter School Board's own dashboard for Vista
  (`ucap.schools.utah.gov/SCSB/SchoolDashboard/186115`, via its
  `GetSchoolsEnrollmentHistory` API) -- an independent, non-parent-compiled
  source, added per Russ.
- `assets/leadership/salary-comparison-chart.png` -- NEW: redraws the
  salary table from the parent's letter as a bar chart. The letter photo
  (`salary-audit-request-letter.jpg`, name/phone already redacted) is kept
  alongside it as the primary-source document.

The old `.jpg` chart/table files are still in the repo (unused/unreferenced)
in case anyone wants to diff against the originals.

Also added: a small self-contained inline-glossary tooltip mechanism in
`home-full.html` (CSS block after the stylesheet link, JS block before
`</body>`) that auto-wraps the first mention of a defined term (currently
`LEA`, `Title IX`) in the page's visible text with a dotted-underline
hover/focus tooltip. Neither term is actually used in the home page copy
yet -- it's dormant until one appears naturally in the text, per Russ ("if
they're going to be used"). Deliberately scoped to this one page rather
than style.css/site-wide; copy the block if another page wants the same
pattern.

Added a DocumentCloud link (the actual independent investigation report
into Blasko at Monroe SD) to the Sources list, found via a Google Doc
("Monroe doc") in the "Vista Website Media" Drive folder that was just a
link to it.

**Pending, not yet added:** Russ asked for a quoted pull-quote on the
Blasko blurb -- "Just don't google him" -- said to have been told to him by
former Vista board members (the ones who hired Blasko, no longer on the
board) -- not a published/attributable quote. Flagged back to Russ as
hearsay from unnamed sources per the defamation-screening checklist above;
holding off pending his call on how (or whether) to present it. Whoever
picks this up next: don't add it without checking with Russ first.

## Drive folder images renamed by page (Sept 2026) -- flag for other chats

Russ renamed images in the "Vista Website Media" Google Drive folder
(shared by kimmeeg@gmail.com, folder ID `1EnKnibWZSRLLtwTY0XhWYZGBA5O2KaOK`)
with a page prefix (`home-`, `policy-`/`policies-`, `meetings-`) to indicate
where each belongs; a few are unprefixed because no page has been decided
yet: `alman` (Chad Allman Facebook announcement -- duplicate of
`assets/leadership/allman-assistant-principal-announcement.jpg`, already
used on the home page), `giles.jpg`, `giles-bio`, and `org-chart.jpg`
(duplicate of `assets/leadership/vista-org-chart.jpg`, already used on the
home page). Left untouched -- don't assign them a page without checking
with Russ.

**Important flag, applies regardless of which page/chat is working:** one
file in that same Drive folder, now renamed `policies-absence`
(file ID `1BQYPMqd_VVbuwF4eWA4IO46hsnWweSVF`), shows an absence-confirmation
screen naming a specific minor student ("Absence for Josefa Tanielu...").
This matches the description in the "Never publish / redact" list above of
the two flagged images from this same folder (a screenshot naming a minor
student's private attendance/absence record) closely enough that it should
be treated as covered by that restriction until Russ confirms otherwise --
**do not publish it** on policies.html or anywhere else without checking
with him first. (A second, generic absence-reason-categories screenshot in
the same folder, `policy-absense-reasons`, does NOT name a student and
looks fine.)
