
function getDeviceIcon(userAgent) {
  if (userAgent.match(/iPhone/i))
    return '#icon-iphone';
  if (userAgent.match(/iPad/i))
    return '#icon-ipad';
  if (userAgent.match(/android/i))
    return '#icon-android';
  return '#icon-laptop';
}
