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
 * It also renames the stream to match the channel's existing titles, e.g.
 * "Vista Townhall Meeting — October 20, 2026" or
 * "Vista Board Meeting — October 27, 2026". Any other title (phone-app
 * default or typed by hand) is replaced.
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

  // Remember today's meetings so the fixer knows what to name each stream.
  PropertiesService.getScriptProperties().setProperty('meetings', JSON.stringify(todays));
  var starts = todays.map(function (m) { return new Date(m.start); });

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

  var startedAt = {};
  ((resp && resp.items) || []).forEach(function (b) {
    if (b.snippet && b.snippet.actualStartTime) startedAt[b.id] = new Date(b.snippet.actualStartTime).getTime();
  });

  var vids = YouTube.Videos.list('status,snippet', { id: ids.join(',') });
  (vids.items || []).forEach(function (v) {
    var s = v.status;
    var sn = v.snippet;
    var newTitle = titleFor_(startedAt[v.id]);
    var rename = newTitle && sn.title !== newTitle;

    if (s.privacyStatus === 'public' && s.embeddable === true && !rename) {
      Logger.log('OK already: ' + v.id + ' "' + sn.title + '"');
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
    // Same for "snippet": resend title, description, tags, category, language.
    var newSnippet = {
      title: rename ? newTitle : sn.title,
      description: sn.description || '',
      categoryId: sn.categoryId
    };
    if (sn.tags) newSnippet.tags = sn.tags;
    if (sn.defaultLanguage) newSnippet.defaultLanguage = sn.defaultLanguage;
    try {
      YouTube.Videos.update({ id: v.id, snippet: newSnippet, status: newStatus }, 'snippet,status');
      Logger.log('FIXED: ' + v.id + ' "' + sn.title + '"' + (rename ? ' -> "' + newTitle + '"' : '') +
                 ' (was ' + s.privacyStatus + ', embeddable=' + s.embeddable + ')');
    } catch (err) {
      Logger.log('FAILED on ' + v.id + ': ' + err);
    }
  });
}

/** Title for a stream that started at startMs, based on today's meeting(s). */
function titleFor_(startMs) {
  if (!startMs) return null;
  var meetings = JSON.parse(PropertiesService.getScriptProperties().getProperty('meetings') || '[]');
  var day = Utilities.formatDate(new Date(startMs), TZ, 'yyyy-MM-dd');
  var sameDay = meetings.filter(function (m) {
    return Utilities.formatDate(new Date(m.start), TZ, 'yyyy-MM-dd') === day;
  });
  if (!sameDay.length) return null;
  // If two meetings share a day, pick the one whose start is closest.
  sameDay.sort(function (a, b) { return Math.abs(a.start - startMs) - Math.abs(b.start - startMs); });
  var m = sameDay[0];
  var name = m.type === 'townhall' ? 'Vista Townhall Meeting' : 'Vista Board Meeting';
  if (m.label) name += ' (' + m.label + ')';
  return name + ' \u2014 ' + m.display_date;
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
