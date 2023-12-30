(*
 * Brings the program's Terminal window to the front.
 *
 * Loops through each Terminal window. If its name contains "main.py" or "savetabs", activate Terminal and set
 * that window to window 1.
 *)

tell application "Terminal"
	set windowList to every window
	repeat with myWindow in windowList
		if (name of myWindow) contains "savetabs" then
			activate
			set index of myWindow to 1
		else if (name of myWindow) contains "main.py" then
			activate
			set index of myWindow to 1
		end if
	end repeat
end tell
