(*
 * Get mode of window with index (item 1 of argv).
 *
 * Make sure Chrome is running, then check the window with the index passed in from the command line.
 * Possible return values are "normal" and "incognito".
 *)


on run argv
	if application id "com.google.Chrome" is running then tell application id "com.google.Chrome"
		set windowIndex to (item 1 of argv) as number
		return mode of window windowIndex
	end tell
end run
