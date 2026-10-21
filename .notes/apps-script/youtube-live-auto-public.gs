/**
 * Saving Vista School: YouTube live stream auto-fixer
 *
 * Problem: streams started from the YouTube phone app have "Allow embedding"
 * off (so the savingvistaschool.org player shows "This video is unavailable"),
 * channels under 1,000 subscribers get their replay set to Private when the
 * stream ends, and the phone app gives every stream the same default title.
 *
 * What it does: only on meeting days, from 15 min before the scheduled start
 * until 4 hours after it, every 10 minutes, for any broadcast that ACTUALLY
 * went live in the last 2 days (empty "Upcoming" shells are ignored):
 *   - Title: "Vista Townhall Meeting — October 20, 2026" /
 *            "Vista Board Meeting — October 27, 2026" (replaces any title)
 *   - Visibility Public, Allow embedding on
 *   - Category Nonprofits & Activism, Standard YouTube License,
 *     not made for kids, no AI-altered content, no paid promotion,
 *     like counts shown, recording date = the day it streamed
 *   - Custom thumbnail (Board or Town Hall image from the site)
 *   - Added to the "Board Meetings" / "Town Hall Meetings" playlist
 *
 * Settings YouTube's API can't change (comments, who can comment, moderation,
 * sort order, Shorts remixing, React live, automatic chapters/places/concepts)
 * come from the channel's Upload defaults in YouTube Studio instead.
 *
 * Meeting dates/times come from the site's own schedule file (the same data
 * meetings.html uses), which a GitHub Action refreshes daily from Vista's
 * public calendar.
 *
 * Setup (one time, signed in to the Google account that owns the channel):
 *   1. Go to script.google.com > New project. Paste this file in. Save.
 *   2. Left sidebar: Services (+) > YouTube Data API v3 > Add
 *      (keep the identifier "YouTube").
 *   3. Pick "setup" in the function dropdown and click Run. Authorize.
 *      If asked to choose an account/channel, choose Saving Vista School.
 *   4. Pick "fixPastMeetings" and Run once: applies the settings + thumbnail
 *      to the Sept 29 and Oct 20 recordings. Check the Execution log.
 * To stop everything later: run "removeAllTriggers".
 */

var SCHEDULE_URL = 'https://savingvistaschool.org/assets/data/meetings.json';
var THUMBNAIL_URLS = {
  board: 'https://savingvistaschool.org/assets/youtube/thumb-board.png',
  townhall: 'https://savingvistaschool.org/assets/youtube/thumb-townhall.png'
};
var PLAYLIST_NAMES = { board: 'Board Meetings', townhall: 'Town Hall Meetings' };
var CATEGORY_ID = '29';     // Nonprofits & Activism
var TZ = 'America/Denver';
var BEFORE_MIN = 15;        // start watching 15 min before scheduled start
var AFTER_HOURS = 4;        // keep watching until 4 h after scheduled start
var CHECK_EVERY_MIN = 10;   // how often to check during the window
var LOOKBACK_HOURS = 48;    // which broadcasts count as "recent"

// ---------------------------------------------------------------- schedule

/** Runs every morning: if a meeting is today, schedule the watch window. */
function dailyScheduleCheck() {
  var data = JSON.parse(UrlFetchApp.fetch(SCHEDULE_URL).getContentText());
  var today = Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd');
  var todays = [data.next_board, data.next_townhall]
    .filter(function (m) { return m && m.date === today; })
    .map(function (m) {
      return {
        type: m.type,
        label: m.label || null,
        display_date: m.display_date || m.date,
        start: Utilities.parseDate(m.date + ' ' + (m.time || '6:00 PM'), TZ, 'yyyy-MM-dd h:mm a').getTime()
      };
    })
    .sort(function (a, b) { return a.start - b.start; });

  if (!todays.length) { Logger.log('No meeting today (' + today + ').'); return; }

  // Remember today's meetings so the fixer knows what each stream is.
  PropertiesService.getScriptProperties().setProperty('meetings', JSON.stringify(todays));

  var windowStart = new Date(todays[0].start - BEFORE_MIN * 60000);
  var windowEnd = new Date(todays[todays.length - 1].start + AFTER_HOURS * 3600000);
  PropertiesService.getScriptProperties().setProperty('windowEnd', String(windowEnd.getTime()));

  deleteTriggersFor_('startWatching');
  if (windowStart.getTime() <= Date.now()) {
    startWatching();
  } else {
    ScriptApp.newTrigger('startWatching').timeBased().at(windowStart).create();
  }
  Logger.log('Meeting today. Watching ' + windowStart + ' to ' + windowEnd);
}

/** Fires 15 min before the meeting: starts the every-10-minute checks. */
function startWatching() {
  deleteTriggersFor_('startWatching');
  deleteTriggersFor_('watchTick');
  ScriptApp.newTrigger('watchTick').timeBased().everyMinutes(CHECK_EVERY_MIN).create();
  watchTick();
}

/** Runs every 10 min during the window; removes itself when the window ends. */
function watchTick() {
  fixRecentLiveStreams();
  var end = Number(PropertiesService.getScriptProperties().getProperty('windowEnd') || 0);
  if (Date.now() > end) {
    deleteTriggersFor_('watchTick');
    Logger.log('Watch window over; stopped checking.');
  }
}

// ---------------------------------------------------------------- the fix

/** Recent broadcasts that went live during a scheduled meeting -> fix them. */
function fixRecentLiveStreams() {
  var cutoff = Date.now() - LOOKBACK_HOURS * 3600 * 1000;
  var resp = YouTube.LiveBroadcasts.list('id,snippet', {
    broadcastStatus: 'all', broadcastType: 'all', maxResults: 25
  });
  var started = ((resp && resp.items) || []).filter(function (b) {
    var t = b.snippet && b.snippet.actualStartTime;
    return t && new Date(t).getTime() >= cutoff;
  });
  if (!started.length) { Logger.log('No broadcasts went live in the last ' + LOOKBACK_HOURS + 'h.'); return; }

  started.forEach(function (b) {
    var startMs = new Date(b.snippet.actualStartTime).getTime();
    var meeting = meetingFor_(startMs);
    if (!meeting) { Logger.log('Skipped ' + b.id + ': not on a scheduled meeting day.'); return; }
    applyAll_(b.id, meeting, startMs);
  });
}

/**
 * One-time catch-up for recordings made before this script existed.
 * Add more lines here if needed: [videoId, 'board'|'townhall', 'Month D, YYYY', 'YYYY-MM-DD'].
 */
function fixPastMeetings() {
  [
    ['DsthRuW6L0o', 'board',    'September 29, 2026', '2026-09-29'],
    ['kXhaGvnHEA4', 'townhall', 'October 20, 2026',   '2026-10-20']
  ].forEach(function (r) {
    var startMs = Utilities.parseDate(r[3] + ' 6:00 PM', TZ, 'yyyy-MM-dd h:mm a').getTime();
    applyAll_(r[0], { type: r[1], label: null, display_date: r[2], start: startMs }, startMs);
  });
}

/** Everything for one video: details, thumbnail, playlist. */
function applyAll_(videoId, meeting, startMs) {
  var v = (YouTube.Videos.list('snippet,status', { id: videoId }).items || [])[0];
  if (!v) { Logger.log('Video ' + videoId + ' not found.'); return; }
  var sn = v.snippet, s = v.status;
  var title = titleFor_(meeting);

  // videos.update replaces each part it is given, so resend every writable
  // field we want to keep (description, tags, language) alongside the changes.
  var snippet = { title: title, description: sn.description || '', categoryId: CATEGORY_ID };
  if (sn.tags) snippet.tags = sn.tags;
  if (sn.defaultLanguage) snippet.defaultLanguage = sn.defaultLanguage;

  var status = {
    privacyStatus: 'public',
    embeddable: true,
    license: 'youtube',
    publicStatsViewable: true,
    selfDeclaredMadeForKids: false,
    containsSyntheticMedia: false
  };

  var recordingDetails = {
    recordingDate: Utilities.formatDate(new Date(startMs), 'UTC', "yyyy-MM-dd'T'HH:mm:ss'Z'")
  };

  try {
    YouTube.Videos.update({ id: videoId, snippet: snippet, status: status, recordingDetails: recordingDetails },
                          'snippet,status,recordingDetails');
    Logger.log('UPDATED ' + videoId + ': "' + sn.title + '" -> "' + title + '" (was ' + s.privacyStatus +
               ', embeddable=' + s.embeddable + ')');
  } catch (err) {
    Logger.log('FAILED details on ' + videoId + ': ' + err);
  }

  // Paid promotion = No. Separate call so a problem here can't block the rest.
  try {
    YouTube.Videos.update({ id: videoId, paidProductPlacementDetails: { hasPaidProductPlacement: false } },
                          'paidProductPlacementDetails');
  } catch (err) {
    Logger.log('Note: could not set paid promotion on ' + videoId + ' (usually already "No"): ' + err);
  }

  setThumbnailOnce_(videoId, meeting.type);
  addToPlaylist_(videoId, meeting.type);
}

// ---------------------------------------------------------------- helpers

/** The scheduled meeting a stream that started at startMs belongs to. */
function meetingFor_(startMs) {
  var meetings = JSON.parse(PropertiesService.getScriptProperties().getProperty('meetings') || '[]');
  var day = Utilities.formatDate(new Date(startMs), TZ, 'yyyy-MM-dd');
  var sameDay = meetings.filter(function (m) {
    return Utilities.formatDate(new Date(m.start), TZ, 'yyyy-MM-dd') === day;
  });
  if (!sameDay.length) return null;
  // If two meetings share a day, pick the one whose start is closest.
  sameDay.sort(function (a, b) { return Math.abs(a.start - startMs) - Math.abs(b.start - startMs); });
  return sameDay[0];
}

/** e.g. "Vista Townhall Meeting — October 20, 2026" */
function titleFor_(m) {
  var name = m.type === 'townhall' ? 'Vista Townhall Meeting' : 'Vista Board Meeting';
  if (m.label) name += ' (' + m.label + ')';
  return name + ' — ' + m.display_date;
}

/** Upload the Board/Town Hall thumbnail, once per video. */
function setThumbnailOnce_(videoId, type) {
  var props = PropertiesService.getScriptProperties();
  var key = 'thumb_' + videoId;
  if (props.getProperty(key)) return;
  var url = THUMBNAIL_URLS[type];
  if (!url) return;
  try {
    var blob = UrlFetchApp.fetch(url).getBlob().setContentType('image/png');
    YouTube.Thumbnails.set(videoId, blob);
    props.setProperty(key, '1');
    Logger.log('Thumbnail set on ' + videoId + ' (' + type + ').');
  } catch (err) {
    Logger.log('FAILED thumbnail on ' + videoId + ': ' + err);
  }
}

/** Add the video to the Board or Town Hall playlist (found by name) once. */
function addToPlaylist_(videoId, type) {
  var wanted = PLAYLIST_NAMES[type];
  if (!wanted) return;
  var playlistId = null, pageToken;
  do {
    var pl = YouTube.Playlists.list('snippet', { mine: true, maxResults: 50, pageToken: pageToken });
    (pl.items || []).forEach(function (p) {
      if (!playlistId && p.snippet.title.trim().toLowerCase() === wanted.toLowerCase()) playlistId = p.id;
    });
    pageToken = pl.nextPageToken;
  } while (!playlistId && pageToken);
  if (!playlistId) { Logger.log('Playlist "' + wanted + '" not found; skipped.'); return; }

  var existing = YouTube.PlaylistItems.list('id', { playlistId: playlistId, videoId: videoId });
  if (existing.items && existing.items.length) return;
  try {
    YouTube.PlaylistItems.insert({
      snippet: { playlistId: playlistId, resourceId: { kind: 'youtube#video', videoId: videoId } }
    }, 'snippet');
    Logger.log('Added ' + videoId + ' to playlist "' + wanted + '".');
  } catch (err) {
    Logger.log('FAILED adding ' + videoId + ' to "' + wanted + '": ' + err);
  }
}

// ---------------------------------------------------------------- setup

/** One-time setup: daily schedule check at ~5 AM Mountain, plus a check now. */
function setup() {
  removeAllTriggers();
  ScriptApp.newTrigger('dailyScheduleCheck').timeBased().atHour(5).everyDays(1).inTimezone(TZ).create();
  dailyScheduleCheck();
  Logger.log('Setup done: daily check at ~5 AM ' + TZ + '.');
}

function removeAllTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
}

function deleteTriggersFor_(fnName) {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === fnName) ScriptApp.deleteTrigger(t);
  });
}
