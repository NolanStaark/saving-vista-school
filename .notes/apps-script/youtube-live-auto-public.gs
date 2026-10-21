/**
 * Saving Vista School: YouTube live stream auto-fixer
 *
 * Problem: streams started from the YouTube phone app have "Allow embedding"
 * off (so the savingvistaschool.org player shows "This video is unavailable"),
 * and channels under 1,000 subscribers get their replay set to Private when
 * the stream ends.
 *
 * Fix: only on meeting days, from 15 min before the scheduled start until
 * 4 hours after it, check every 10 minutes. Any broadcast that ACTUALLY went
 * live in the last 2 days gets set to Public + embeddable. Broadcasts that
 * never started (dropped-connection "Upcoming" shells) are ignored.
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
 *   4. Optional test: pick "fixRecentLiveStreams" and Run once, then check
 *      the Execution log (it will also fix any stream from the last 2 days).
 * To stop everything later: run "removeAllTriggers".
 */

var SCHEDULE_URL = 'https://savingvistaschool.org/assets/data/meetings.json';
var TZ = 'America/Denver';
var BEFORE_MIN = 15;        // start watching 15 min before scheduled start
var AFTER_HOURS = 4;        // keep watching until 4 h after scheduled start
var CHECK_EVERY_MIN = 10;   // how often to check during the window
var LOOKBACK_HOURS = 48;    // which broadcasts count as "recent"

/** Runs every morning: if a meeting is today, schedule the watch window. */
function dailyScheduleCheck() {
  var data = JSON.parse(UrlFetchApp.fetch(SCHEDULE_URL, { muteHttpExceptions: false }).getContentText());
  var today = Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd');
  var starts = [data.next_board, data.next_townhall]
    .filter(function (m) { return m && m.date === today; })
    .map(function (m) {
      return Utilities.parseDate(m.date + ' ' + (m.time || '6:00 PM'), TZ, 'yyyy-MM-dd h:mm a');
    })
    .sort(function (a, b) { return a - b; });

  if (!starts.length) { Logger.log('No meeting today (' + today + ').'); return; }

  var first = starts[0];
  var last = starts[starts.length - 1];
  var windowStart = new Date(first.getTime() - BEFORE_MIN * 60000);
  var windowEnd = new Date(last.getTime() + AFTER_HOURS * 3600000);
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

/** The actual fix: recent broadcasts that went live -> Public + embeddable. */
function fixRecentLiveStreams() {
  var cutoff = Date.now() - LOOKBACK_HOURS * 3600 * 1000;

  var resp = YouTube.LiveBroadcasts.list('id,snippet,status', {
    broadcastStatus: 'all',
    broadcastType: 'all',
    maxResults: 25
  });
  var ids = ((resp && resp.items) || []).filter(function (b) {
    var started = b.snippet && b.snippet.actualStartTime;
    return started && new Date(started).getTime() >= cutoff;
  }).map(function (b) { return b.id; });

  if (!ids.length) { Logger.log('No broadcasts went live in the last ' + LOOKBACK_HOURS + 'h.'); return; }

  var vids = YouTube.Videos.list('status,snippet', { id: ids.join(',') });
  (vids.items || []).forEach(function (v) {
    var s = v.status;
    if (s.privacyStatus === 'public' && s.embeddable === true) {
      Logger.log('OK already: ' + v.id + ' "' + v.snippet.title + '"');
      return;
    }
    // videos.update replaces the whole "status" part, so send back every
    // writable field, changing only privacy + embedding.
    var newStatus = {
      privacyStatus: 'public',
      embeddable: true,
      license: s.license,
      publicStatsViewable: s.publicStatsViewable,
      selfDeclaredMadeForKids: s.madeForKids === true
    };
    if (s.containsSyntheticMedia !== undefined) newStatus.containsSyntheticMedia = s.containsSyntheticMedia;
    try {
      YouTube.Videos.update({ id: v.id, status: newStatus }, 'status');
      Logger.log('FIXED: ' + v.id + ' "' + v.snippet.title + '" was ' + s.privacyStatus + ', embeddable=' + s.embeddable);
    } catch (err) {
      Logger.log('FAILED on ' + v.id + ': ' + err);
    }
  });
}

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
