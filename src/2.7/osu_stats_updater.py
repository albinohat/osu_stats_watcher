## osu_player_stats_updater.py
## Author: Daniel "Albinohat" Mercado
## 
## This script creates checks the current version of local osu_stats_watcher and allows users to update to the newest version.
## TODO
## Add +/- updates for pp and rank.
## 

## Standard Imports
import re, sys, time, urllib

## update - This method updates the osu! Stats Watcher which called it.
def update():
	## Initialize the bool controlling whether or not to run a debug update.
	bool_debug = 0

	## Initialize the vars to hold the versions.
	local_version  = ""
	newest_version = ""

	## This bool tracks whether or not to update.
	bool_update = 0

	if (len(sys.argv) < 2 or len(sys.argv) > 3):
		print "\n    Invalid Usage. Please run this script via osu_stats_watcher -u|--update"
		time.sleep(3)
		sys.exit()

	## Sanitize version of quotes.
	if sys.argv[1].startswith('"') and sys.argv[1].endswith('"'):
		sys.argv[1] = sys.argv[1][1:-1]
	
	## Check for the debug option.
	if (len(sys.argv) == 3 and sys.argv[2] == "--update-debug"):
		print "\n    Entering debug mode!"
		bool_debug = 1
	
	## Determine the version of the local osu_stats_watcher and the MRV (most recent version).
	try:
		local_version = re.search(r'(\d+\.\d+\.\d+)', sys.argv[1]).group(0)

	except AttributeError:
		print "\n    Invalid local version. Exiting in 3 seconds..."
		print local_version
		time.sleep(3)		
		sys.exit()

	try:
		if (bool_debug == 0):
			newest_version = re.search(r'(\d+\.\d+\.\d+)', str(urllib.urlopen("https://raw.githubusercontent.com/albinohat/osu_stats_watcher/master/update.mrv?raw=true").read())).group(0)
		else:
			newest_version = re.search(r'(\d+\.\d+\.\d+)', str(urllib.urlopen("https://raw.githubusercontent.com/albinohat/osu_stats_watcher/master/update_test.mrv?raw=true").read())).group(0)			

	except AttributeError:
		print "\n    Invalid newest version. Exiting in 3 seconds..."
		print newest_version
		time.sleep(3)		
		sys.exit()
	
	print "\n\nWelcome to the osu! Stats Updater!"

	print "    Your OSW version is: " + local_version
	print "    The newest version is: " + newest_version

	## Break the version # into its 3 parts.
	local_list  = [int(x) for x in local_version.split(".")]
	newest_list = [int(y) for y in newest_version.split(".")]

	## Compare the local version and MRV.
	for x, y in map(None, local_list, newest_list):
		## Our version number is lower.
		if (x < y):
			bool_update = 1
			break
		
		## Our version number is higher.
		## This shouldn't happen in production.
		if (x > y):
			break
			
	if (bool_update == 0):
		print "\nYou have the most recent version and do not need to update at this time. Exiting in 3 seconds..."
		time.sleep(3)	
		sys.exit()
		
	print "\nA new version is available. Would you like to download it? [Y/N]"
	choice = raw_input().lower()

	if (choice == "y" or choice == "yes" or choice == ""):
		print "    Downloading..."
		new_package = urllib.urlretrieve("https://github.com/albinohat/osu_stats_watcher/blob/master/bin/osu_stats_watcher.exe?raw=true", "osu_stats_watcher.exe")
		print "    Download Complete!"
		
	else:
		print "\nAborting update and exiting in 3 seconds..."
		time.sleep(3)
		sys.exit()
	
def main():
	update()
	
if __name__ == "__main__":
	main()