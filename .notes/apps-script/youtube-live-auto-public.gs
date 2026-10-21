/**
 * Saving Vista School: YouTube live stream auto-fixer
 *
 * Problem: streams started from the YouTube phone app have "Allow embedding"
 * off (so the savingvistaschool.org player shows "This video is unavailable"),
 * and channels under 1,000 subscribers get their replay set to Private when
 * the stream ends.
 *
 * Fix: every 5 minutes, look at this channel's recent broadcasts. For any
 * broadcast that ACTUALLY went live in the last 2 days, make sure it is
 * Public and embeddable. Broadcasts that never started (dropped-connection
 * "Upcoming" shells) are ignored.
 *
 * Setup (one time, signed in to the Google account that owns the channel):
 *   1. Go to script.google.com > New project. Paste this file in. Save.
 *   2. Left sidebar: Services (+) > YouTube Data API v3 > Add
 *      (keep the identifier "YouTube").
 *   3. Pick "setup" in the function dropdown and click Run. Authorize.
 *      If asked to choose an account/channel, choose Saving Vista School.
 *   4. Pick "fixRecentLiveStreams" and Run once. Check the Execution log.
 * To stop it later: run "removeTriggers".
 */

var LOOKBACK_HOURS = 48;

function fixRecentLiveStreams() {
  var cutoff = Date.now() - LOOKBACK_HOURS * 3600 * 1000;

  var resp = YouTube.LiveBroadcasts.list('id,snippet,status', {
    broadcastStatus: 'all',
    broadcastType: 'all',
    maxResults: 25
  });
  var items = (resp && resp.items) || [];

  var ids = items.filter(function (b) {
    var started = b.snippet && b.snippet.actualStartTime;
    return started && new Date(started).getTime() >= cutoff;
  }).map(function (b) { return b.id; });

  if (!ids.length) {
    Logger.log('No broadcasts went live in the last ' + LOOKBACK_HOURS + 'h.');
    return;
  }

  var vids = YouTube.Videos.list('status,snippet', { id: ids.join(',') });
  (vids.items || []).forEach(function (v) {
    var s = v.status;
    if (s.privacyStatus === 'public' && s.embeddable === true) {
      Logger.log('OK already: ' + v.id + ' "' + v.snippet.title + '"');
      return;
    }
    // videos.update replaces the whole "status" part, so send back every
    // writable field we got, changing only privacy + embedding.
    var newStatus = {
      privacyStatus: 'public',
      embeddable: true,
      license: s.license,
      publicStatsViewable: s.publicStatsViewable,
      selfDeclaredMadeForKids: s.madeForKids === true
    };
    if (s.containsSyntheticMedia !== undefined) {
      newStatus.containsSyntheticMedia = s.containsSyntheticMedia;
    }
    try {
      YouTube.Videos.update({ id: v.id, status: newStatus }, 'status');
      Logger.log('FIXED: ' + v.id + ' "' + v.snippet.title + '" was ' +
                 s.privacyStatus + ', embeddable=' + s.embeddable);
    } catch (err) {
      Logger.log('FAILED on ' + v.id + ': ' + err);
    }
  });
}

function setup() {
  removeTriggers();
  ScriptApp.newTrigger('fixRecentLiveStreams').timeBased().everyMinutes(5).create();
  Logger.log('Trigger created: fixRecentLiveStreams every 5 minutes.');
}

function removeTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'fixRecentLiveStreams') ScriptApp.deleteTrigger(t);
  });
}
