# Deploying Saving Vista School to GitHub Pages (free, custom domain)

This gets savingvistaschool.org live at **$0/month**, hosted on GitHub Pages, while your domain stays registered (and its DNS managed) at Wix — no nameserver migration needed.

## 1. Create a free GitHub account
Go to github.com and sign up (skip if you already have one).

## 2. Create a new repository
- Click **New repository**.
- Name it anything, e.g. `saving-vista-school`.
- Set it to **Public** (required for free GitHub Pages).
- Don't add a README/gitignore — leave it empty.

## 3. Upload the site files
- On the repo page, click **Add file → Upload files**.
- Drag in every file/folder from this package (`index.html`, `letters.html`, `media.html`, `live-meetings.html`, `about.html`, `style.css`, and the `assets` folder).
- Scroll down, click **Commit changes**.

## 4. Turn on GitHub Pages
- In the repo, go to **Settings → Pages**.
- Under "Build and deployment," set **Source** to `Deploy from a branch`.
- Branch: `main`, folder: `/ (root)` → **Save**.
- GitHub will give you a temporary URL like `https://yourusername.github.io/saving-vista-school/` — check it loads before moving on.

## 5. Add your custom domain
- Still in **Settings → Pages**, under "Custom domain," enter `savingvistaschool.org` → **Save**.
- This automatically creates a `CNAME` file in your repo — don't delete it.

## 6. Point your domain at GitHub (in Wix)
- Log into Wix → **Domains** → select `savingvistaschool.org` → **Manage DNS Records** (this works even though the domain isn't connected to a Wix site).
- Add these **four A records** (all pointing the root domain to GitHub's servers):

  | Type | Host | Value |
  |---|---|---|
  | A | @ | 185.199.108.153 |
  | A | @ | 185.199.109.153 |
  | A | @ | 185.199.110.153 |
  | A | @ | 185.199.111.153 |

- Add this **CNAME record** so `www.savingvistaschool.org` also works:

  | Type | Host | Value |
  |---|---|---|
  | CNAME | www | yourusername.github.io |

- Remove/replace any conflicting default A or CNAME records Wix put on the root (`@`) or `www` host.

## 7. Wait, then enable HTTPS
- DNS changes can take anywhere from a few minutes up to 24 hours to propagate.
- Once `savingvistaschool.org` loads your site, go back to **Settings → Pages** on GitHub and check **Enforce HTTPS** (may take a bit to become available — GitHub needs to issue a certificate first).

## Updating the site later
When there's a new letter, photo, video, or a change to the schedule/embed codes:
1. Send the new files/info in this chat.
2. I'll update the relevant HTML file(s) and hand you the changed file(s) back.
3. On GitHub, open the repo, click into that file, click the pencil (**Edit**) icon (or use **Add file → Upload files** to replace it), and **Commit changes**. The live site updates automatically within a minute or two — no redeploying needed.

## Setting up anonymous letter submissions (Tally.so)

1. Go to https://tally.so and create a free account.
2. Create a new form with:
   - A **File Upload** field, labeled something like "Letter (PDF, photo, or scan)"
   - An optional short text field for extra context
   - **Do not add Name or Email fields** if you want submissions to default to anonymous.
3. Publish the form. Click **Share** and copy the form ID from the link
   (it's the part after `tally.so/r/`).
4. Open `letters.html`, find the `<iframe src="https://tally.so/embed/FORM_ID...`
   line, and replace `FORM_ID` with your real form ID.
5. Submissions land in your private Tally dashboard (tally.so/forms) — nothing is public
   until your team reviews it and manually adds it to this page.
6. Tally's free plan: unlimited forms/submissions, no login required for submitters,
   10MB per uploaded file. If you ever need larger files or true submitter anonymity from
   Tally's own server logs (not just from the public), let me know — there are more
   specialized (but more complex) whistleblower-grade tools for that.

## Notes
- The Parent Letters and Media pages currently show an empty-state placeholder — they're ready to fill in as soon as real letters/photos are sent over.
- The Live Meetings page needs your YouTube **Channel ID** (and a playlist ID for past meetings) dropped into `live-meetings.html` — see the comments in that file.
- The Contact form on the About page is currently visual-only (it doesn't send email yet) — say the word if you want it wired up to actually deliver messages (Formspree/Getform have free tiers for this).
