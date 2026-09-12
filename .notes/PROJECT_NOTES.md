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


## Home page: org chart rebuilt again + enrollment chart axis (Sept 2026)

Two follow-up rounds after the initial chart recreation (see above):

**Org chart** -- the first AI-recreated version (graphviz) packed all 14
third-tier reports into one very wide row, so the whole chart shrank to
illegible text once the image scaled down to page width. Replaced with a
hand-laid-out PIL version: each of the three branches (Giles/Perkes/
Bradshaw) renders as a single-file indented outline (like a folder tree),
so no connector line ever passes behind an unrelated box and the canvas
stays narrow enough for large, legible text. Generator script:
`make_orgchart_v4.py` pattern (not committed to the repo -- built in a
scratch cloud session each time; ask if you need to regenerate it).

Also, per Russ: **pulled current titles from vistautah.com instead of the
board-meeting chart's wording.** Confirmed via vistautah.com's
Administration, Staff, and Counselors pages:
- Marilyn Russell: ELL -> **ESL Coordinator**
- Katelynn George: Title I -> **Title 1 Coordinator**
- LaNessa Stevens: Instructional Coach -> **Learning Coach**
- Bruce Hatch: IT Specialist -> **Assessment Director / IT Specialist**
- Marie Ehlers: 7-9 College & Career Counselor -> **Head School Counselor (7-9)**
- Danielle Robb: Social Worker -> **School Social Worker**
- Nicole Richins: Student Council Advisor -> **College & Career Readiness /
  Student Council Adviser**

**Flag for Russ (acted on a default, needs his confirmation):** the original
chart's "Cori Fix / Special Education" box doesn't match the site --
vistautah.com's SPED Personnel page lists **Alicia Hutchinson** as SPED
Coordinator and doesn't mention Cori Fix at all. Swapped in Alicia
Hutchinson/SPED Coordinator by default (told Russ in chat I'd do this unless
he said otherwise); he hadn't responded as of this note. If he wants it
reverted or the box dropped instead, that's a one-line data change in the
org chart generator's GILES_TREE list.

Also fixed a diagonal connector jog under each branch head (looked like a
spacing bug) -- now a clean right-angle elbow like the rest of the chart.

**Enrollment trend chart** -- per Russ, the 2025->2026 decline (1115->1088)
wasn't visually obvious on a 0-1,300 axis. Changed the y-axis to start at
1,000 instead of 0 so the year-to-year change reads clearly, and added an
axis-break mark plus a caption note ("the vertical axis starts at 1,000,
not 0...") so the zoom is disclosed rather than hidden -- same actual
numbers, just a closer-in view. Standard, defensible practice as long as
the truncation is flagged, which it now is both visually and in text.

Commits: `617cc19` (line chart + first org chart legibility pass),
`fe45f68` (title corrections + connector fix + axis zoom).


## Home page: leadership source-photo jpgs relocated (Sept 2026)

The four original phone-photo charts that the redrawn .png charts replaced
(`teacher-exits-chart.jpg`, `teacher-experience-exiting-chart.jpg`,
`vista-org-chart.jpg`, `enrollment-numbers-2026.jpg`) were unused/unreferenced
directly in `assets/leadership/` -- confirmed via a repo-wide grep that
nothing references the `.jpg` paths. Moved (not deleted, per the earlier
note above about keeping them for diffing) into
`assets/leadership/source-photos/`. If you're looking for them, that's
where they are now. `allman-assistant-principal-announcement.jpg`,
`giles-deputy-director-announcement.jpg`, and `salary-audit-request-letter.jpg`
were left in place (out of scope for this pass; salary-audit-request-letter.jpg
is still actively referenced).

## Site-wide basics added: favicon, OG/Twitter tags, robots.txt, sitemap.xml (Sept 2026)

Added the standard metadata basics that were missing across every page
(commit `15de92e`):

- **Favicon**: `assets/favicon.svg` (navy rounded-square background,
  `#003e56`, with the white envelope + gold-dot graphic already used as
  the `.page-header-graphic` on `letters.html`, reused rather than
  designing something new, per Russ's instruction) + `assets/favicon.ico`
  (multi-res 16/32/48/64, built with PIL) + `assets/apple-touch-icon.png`
  (180x180). A copy of `favicon.ico` also sits at the repo root
  (`/favicon.ico`) for browsers/crawlers that probe that path directly
  regardless of `<link rel="icon">` tags. All three are linked in every
  page's `<head>`, including the two redirect stubs (favicon links only
  there, no OG tags -- they're not content to share).
- **OG / Twitter Card tags**: `og:type`, `og:site_name`, `og:url`,
  `og:title`, `og:description`, `og:image` (+ width/height),
  `twitter:card` (`summary_large_image`), `twitter:title`,
  `twitter:description`, `twitter:image` added to every real page's
  `<head>` (index, home-full, letters, meetings, policies, media, about,
  404), reusing each page's existing `<title>`/`<meta name="description">`
  text verbatim rather than writing new copy. `home-full.html` got these
  too even though it's not swapped in for `index.html` yet -- harmless
  now, saves redoing this when it goes live -- but it's still excluded
  from the sitemap below since `index.html` is the current real homepage.
- **Shared social-preview image**: `assets/social-preview.png` (1200x630,
  navy/gold, same envelope graphic + "Saving Vista School" wordmark),
  referenced as `og:image`/`twitter:image` on every page. Built with
  cairosvg (installed via pip in the device_bash shell for this task).
- **robots.txt** (repo root): `Allow: /` for all user agents + a
  `Sitemap:` line pointing at `sitemap.xml`.
- **sitemap.xml** (repo root): lists the 6 real public pages (home,
  letters, meetings, policies, media, about) with `lastmod`/`changefreq`/
  `priority`. Deliberately excludes the `live-meetings.html`/
  `parent-letters.html` redirect stubs, `home-full.html` (not live), and
  `404.html`, per Russ's instruction.

Nothing here touches `style.css` or `assets/js/` -- those were mid-edit
by a concurrent chat when this work was done; this chat's `git add` was
scoped to only the files it created/edited, confirmed via `git status`
before and after commit.

## Favicon replaced: parent-and-child icon (Sept 2026, supersedes note above)

Russ didn't like the envelope-graphic favicon (reused from letters.html's
page header) noted above -- asked for something that reflects "a
concerned parent" instead. Replaced with a purpose-built icon: a parent
and child figure holding hands (simple white line silhouette, navy
`#003e56` rounded-square background, two small gold `#eca73a` accent
dots), same treatment/format as before -- `assets/favicon.svg` +
`assets/favicon.ico` (multi-res, also copied to repo root `/favicon.ico`)
+ `assets/apple-touch-icon.png` (180x180). `assets/social-preview.png`
(the shared OG/Twitter image) was also rebuilt with the same new icon so
the two stay visually consistent. All three kept their original
filenames, so no HTML changes were needed -- every page's existing
favicon/OG `<link>`/`<meta>` tags already point at these paths. Commit
`25f1b90`.

## Mobile hamburger nav added (Sept 2026)

The 6-link nav no longer just wraps onto extra crowded lines on phones --
below 768px it collapses into a hamburger button that opens the nav as a
dropdown panel under the navy header (bars animate into an X on open).
Desktop (>768px) look is unchanged. Confirmed with Russ up front: dropdown
panel (not full-screen overlay), 768px breakpoint, animated X.

- Markup: every real page's header (`home-full`, `letters`, `policies`,
  `media`, `meetings`, `about`, `404` -- not `index.html`, which has no
  nav yet per the placeholder-page note above) got a
  `<button class="nav-toggle" aria-expanded aria-controls="primary-nav">`
  with three `.nav-toggle-bar` spans, and `nav.main-nav` gained
  `id="primary-nav"`.
- CSS: new `.nav-toggle`/`.nav-toggle-bar` rules + a `@media (max-width:
  768px)` block in `style.css` (hides the toggle above that width so
  desktop is byte-for-byte the same nav CSS as before).
- JS: new shared `assets/js/nav.js` (loaded via `<script src="assets/js/
  nav.js" defer>` at the end of `<body>` on each page) -- toggles
  `.nav-open` + `aria-expanded`, closes on link click / Escape / resize
  back past 768px.
- Verified with Playwright in a scratch copy of the site (device_bash
  can't reach the built-in browser over localhost, and the built-in
  browser can't open file:// -- staged the files into the cloud
  workspace's container just for this screenshot/interaction test, never
  fed anything back from there): desktop nav pixel-identical across all
  7 pages, mobile open/close/animate/Escape/resize-reset all behave.

**Flag for other chats -- concurrent git activity nearly lost this
work:** while committing, another chat's git operations on this same
repo (a favicon/OG-tags commit, then a "swap gold dots for stars" commit)
raced with this chat's `git add`/`git commit` on the shared working tree
and `.git` directory. Symptoms hit, in order: (1) a plain `git add
style.css assets/js/nav.js` staged half a dozen unrelated files too
(favicons, letters.html, policies.html) -- always re-run `git status
--short` right after `git add` and `git reset` (not `--hard`) if it shows
anything beyond what you meant to add; (2) stale zero-byte `.git/
{HEAD,index}.lock` / `.git/refs/heads/main.lock` needed `device_request_
delete_permission` + `rm -f` before git would run at all, matching the
gotcha noted above; (3) most seriously, this chat's first nav commit
(`528d459`) was cleanly made, confirmed in `git log`, then *silently
vanished from history* less than a minute later -- `git log` showed a
different HEAD with no trace of it, evidently because a concurrent
chat's git command rewrote/reset the branch. The file content wasn't
lost (still sat uncommitted in the shared working tree), so it was just
re-committed as `574f65b` on top of the new HEAD, verified twice a few
seconds apart. If a commit you just made isn't in `git log` a minute
later, that's what happened -- diff your working tree against HEAD
before assuming your edits are gone, they're probably still sitting
there uncommitted. Also noticed mid-session: `style.css` is CRLF
line-endings (unlike the HTML files, which are LF) -- if you edit it
with a plain Python read/write, `open(..., "w")` normalizes to LF and
turns the whole file into a 1000+ line diff. Reading with
`newline=None` and writing back with `.replace("\n", "\r\n")` keeps it
CRLF and the diff sane.

Given how much git-collision risk showed up in a single session, worth
raising with Russ: consider not running multiple chats that commit to
this repo at the same moment, or having each push to origin promptly so
a lost/orphaned local commit is recoverable from the remote.

## Favicon redesigned again: reaching-figure-and-star icon (Sept 2026, supersedes both notes above)

Russ shared Vista School's actual "Rising Stars" mascot logo (a maroon
reaching figure + red star, official school branding) and asked us to
echo that motif -- but confirmed (via a direct question, given the
affiliation/trademark sensitivity) that he wanted **original art
inspired by the motif**, not a close copy of the school's actual mascot.
Replaced the parent-and-child favicon with: a single figure reaching up
toward a star, drawn in the site's own stroke-icon style (white outline
on navy `#003e56`, gold `#eca73a` star) -- deliberately different pose/
proportions/technique from Vista's filled maroon silhouette, so it reads
as our own mark, not theirs. Same three files as before, same filenames
(`assets/favicon.svg`/`.ico`, `assets/apple-touch-icon.png`,
`favicon.ico` at repo root), `assets/social-preview.png` rebuilt to
match.

Also, since the site's mascot theme is "Rising Stars," swapped the small
gold accent-dot circles for 5-point star polygons everywhere they
appeared: the two in the new favicon, plus the two each on letters.html's
and policies.html's `.page-header-graphic` SVGs (same position/size,
still `var(--gold)`).

**Git note for whoever's next:** while committing this, ran into real
lock contention with another concurrent chat editing style.css/nav.js/
meetings.html at the same moment (both chats hitting `.git/index.lock`
and `.git/refs/heads/main.lock` back to back). One of my own commits
briefly became a "dangling" commit (object created, but the ref update
lost the race) -- recovered by finding it via `git fsck` and pointing
`refs/heads/main` at it with `git update-ref` (confirmed via
`git merge-base --is-ancestor` that it was a clean fast-forward first).
Also found the shared index had picked up stale/reverted entries for a
few of my files mid-race (worktree and HEAD were both correct throughout
-- only the index briefly disagreed) -- fixed by re-`git add`-ing just
those paths. No content was lost on either side; the other chat's mobile-
nav commit (`574f65b`) landed cleanly on top right after. `git fsck` also
turned up an unrelated dangling `WIP on main` stash-commit (harmless,
auto-created by a `git stash`) and one dangling commit from Sept 11
(`38b5d9e`, "Link the Board Meeting schedule...") that predates this
session and was never investigated -- flagging in case that one's actual
lost work someone still wants; not touched here since it's outside this
task's scope.

Commits: `63b0d4e` (reaching-figure-and-star redesign + star accents).

## Icon added to the home page(s) too (Sept 2026)

Russ asked for the reaching-figure-and-star icon on the home page as
well (not just the favicon/OG image). Since it wasn't clear whether
"home page" meant the live placeholder or the staged redesign, asked --
answer was both. Added it as a faint background watermark (same
`.page-header-graphic` treatment as letters.html/policies.html: 104x104,
16% opacity, top-right of the band, hidden below 1080px) in:
- `home-full.html`'s hero (white stroke, matches its navy gradient bg).
- `index.html`'s under-construction box (navy stroke instead of white,
  since that page's background is light -- same faint-watermark effect,
  recolored). Needed `position:relative` on `.under-construction`, added
  inline in index.html's own `<style>` block (not shared CSS, so no
  cross-chat collision risk there).
- `style.css` gained a small new `.hero { position:relative;
  overflow:hidden; }` rule, appended as a separate block at the end of
  the file rather than edited into the existing `.hero {}` block, to
  avoid colliding with the other chat's concurrent edits to that same
  file. Commit `b789fb1`.

## Home-page icon was drifting too far right -- fixed (Sept 2026)

Russ flagged the icon added in the previous note as "too far to the
right." Root cause: it was positioned absolute relative to the
full-width `.hero`/`.under-construction` band, instead of the centered
1080px `.container` that `.page-header-graphic` normally anchors to on
every other page (`.page-header .container { position:relative; }` is
what actually does that there, not `.page-header` itself) -- so on wide
screens it sat near the browser edge instead of the content column edge.

Fixed by mirroring that exact pattern:
- `style.css`: added `.hero .container { position:relative; z-index:1; }`.
- `index.html`: restructured so `.box` is now wrapped in a `.container`
  div (previously `.under-construction` only had `.box`, no `.container`
  at all) with the icon as `.container`'s first child; also needed
  `.under-construction .container { width:100% }` since
  `.under-construction` is `display:flex` and its child would otherwise
  shrink-wrap to `.box`'s width rather than filling the available space.

Verified with Playwright screenshots (rendered locally in a scratch
container, not committed) at 900/1100/1600px: icon sits in the side
gutter next to the text at wide widths, no overlap, and still hides
below 1080px like every other page. Commit `9d0da9c`.

## Icon rounded out to every page (Sept 2026)

Russ asked to make sure all pages have the icon. Before this it was only
on letters.html/policies.html (original) plus index.html/home-full.html
(added earlier this session). Added it to the rest of the real content
pages too:
- meetings.html, media.html, about.html: white-stroke version, dropped
  into their existing `.page-header > .container`, no CSS changes needed.
- 404.html: navy-stroke version (light background, like index.html),
  needed `position:relative;z-index:1` added inline on its `.container`
  since 404 doesn't use the shared `.page-header` class.

Left the two redirect stubs (`live-meetings.html`, `parent-letters.html`)
alone -- they already have the favicon `<link>` tags but no visual
content worth decorating (they redirect immediately). Every real page +
both stubs now have the favicon links; every real page now shows the
icon. Verified all four newly-touched pages with Playwright screenshots
at 1600px before committing. Commit `34dc07f`.

## Corrected: page-specific icons, not the mascot everywhere (Sept 2026)

Russ corrected the previous note -- he wanted a distinct, page-specific
icon per page (like letters.html's mail icon, policies.html's scales),
not the reaching-figure-and-star mascot copy-pasted onto every header.
Replaced what was added to meetings/media/about/404 with:
- meetings.html: screen/play-button icon ("watch live").
- media.html: camera icon (rounded-square lens, not a circle).
- about.html: speech-bubble icon ("get in touch").
- 404.html: a question mark whose dot is a small gold star instead of a
  circle -- fits both the "?" and the site's Rising Stars motif.

All use stroke-width 4 (matching the original letters/policies icons'
weight, not the bolder favicon weight) and the same two gold
corner-accent stars as everywhere else. The mascot icon (reaching figure
+ star) stays only on the favicon/OG image and the home page(s), where
it functions as the site's actual brand mark rather than a page topic
icon. Commit `930c043`.
