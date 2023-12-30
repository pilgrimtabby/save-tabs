(*
 * Return list of tab urls of window with index (item 1 of argv).
 *
 * Make sure Chrome is running, then get tabs of window with the index passed in from the command line.
 *)


on run argv
	if application id "com.google.Chrome" is running then tell application id "com.google.Chrome"
		set windowIndex to (item 1 of argv) as number
		return (URL of tabs of window windowIndex as list)
	end tell
end run
