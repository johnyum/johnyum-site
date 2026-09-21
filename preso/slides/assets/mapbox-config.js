// Mapbox public token for Trip Creator. This file IS committed — it is the runtime token
// source the static page reads (window.MAPBOX_TOKEN), so the same value serves localhost
// and the live site. A pk.* token is a *public* token (it ships to the browser by design);
// restrict it by URL in the Mapbox account rather than by hiding it.
//
// ROTATED 2026-09-20 to a URL-RESTRICTED token (johnyum.com, www.johnyum.com,
// localhost). Verified: tiles return 200 from those origins and 403 from any
// other referer or from a bare request, so the string is inert off-site and
// safe to commit. The Default public token it replaces cannot be restricted —
// Mapbox does not allow it — so that one should be deleted from the account.
//
// Earlier: ROTATED 2026-08-28. The previous token (id cmq7k8uzc00nd2tptybzncuw0) started returning
// 401 "Not Authorized - Invalid Token" on every endpoint — tiles, styles and Directions —
// which read on the page as a blank globe with markers floating over nothing, on the LIVE
// site as well as locally. Worth knowing for next time: the browser console showed a wall
// of 429s, which pointed at rate limiting or a blown quota and was a red herring — those
// were retries against a dead token. `curl` on one tile URL named the real cause in one
// request, and a matching Referer ruled out a URL restriction. Check the token before
// blaming the quota.
window.MAPBOX_TOKEN = 'pk.eyJ1Ijoiam9obnl1bSIsImEiOiJjbXVhaTl3dm4wM2UwMnlweXh4d2traG91In0.FFGorwGFPHXrtIS17vMpEw';
