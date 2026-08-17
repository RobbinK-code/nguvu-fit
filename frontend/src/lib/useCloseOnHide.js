import { useEffect } from "react";

/**
 * Calls `onHide` whenever the page is backgrounded (screen locked, tab
 * switched, app minimized). Used to force-close any open video embed
 * before the OS suspends the page - on some Android WebView versions,
 * a video left actively decoding when the screen locks comes back
 * visually corrupted (static/noise) on resume. Closing it first avoids
 * leaving that decode surface in a bad state.
 */
export function useCloseOnHide(onHide) {
  useEffect(() => {
    function handleVisibilityChange() {
      if (document.hidden) onHide();
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [onHide]);
}
