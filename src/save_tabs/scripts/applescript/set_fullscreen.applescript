(*
 * Set Google Chrome to fullscreen.
 *
 * First, wait until Chrome is actually running, in front, and has a window open.
 * Sometimes errors are thrown because Chrome is not yet open, so this loop runs for about 5
 * seconds regardless of errors thrown.
 *
 * Then, tell System Events to make the frontmost process (Google Chrome in this case) fullscreen. 
 * This may not work if this program doesn't have accessibility access.
 *)

-- Wait until Chrome is running, in front, and has a window open
repeat 2000 times -- try for roughly 5 seconds
	try
		if application id "com.google.Chrome" is running then
			if frontmost of application id "com.google.Chrome" then
				if window 1 of application id "com.google.Chrome" exists then
					exit repeat
				end if
			end if
		end if
	on error -- ignore errors (if this block doesnt work, it doesnt matter too much)
	end try
end repeat
tell application "System Events" -- Set fullscreen
	tell front window of (first process whose frontmost is true) to set value of attribute "AXFullScreen" to true
	delay 1
end tell
