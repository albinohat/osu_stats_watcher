## osu_player_stats_updater.py
## Author: Daniel "Albinohat" Mercado
## 
## This script creates checks the current version of local osu_stats_watcher and allows users to update to the newest version.
## TODO
## Add +/- updates for pp and rank.
## 

## Standard Imports
import re, subprocess, sys, time, urllib.request, urllib.parse, urllib.error

## Global Vars - Lazy Mode
bool_update = 0

if (len(sys.argv) != 2):
	print("\n    Invalid Usage. Please run this script via osu_stats_watcher -u|--update")
	time.sleep(3)
	sys.exit()

## Determine the version of the local osu_stats_watcher and the MRV (most recent version).
local_version  = re.match(r'\d+\.\d+\.\d+', sys.argv[1]).group(0)
newest_version = re.match(r'\d+\.\d+\.\d+', urllib.request.urlopen("https://raw.githubusercontent.com/albinohat/osu_stats_watcher/master/update.mrv").read()).group(0)

print("\n\nWelcome to the osu! Stats Updater!")

print("    Your OSW version is: " + local_version)
print("    The newest version is: " + newest_version)

local_list  = [int(x) for x in local_version.split(".")]
newest_list = [int(y) for y in newest_version.split(".")]

for x, y in map(None, local_list, newest_list):
	## Our version number is lower.
	if (x < y):
		bool_update = 1
		break
	
	## Our version number is higher.
	## This shouldn't happen in prod.
	if (x > y):
		break
		
if (bool_update == 0):
	print("\nYou have the most recent version and do not need to update at this time. Exiting in 3 seconds...")
	time.sleep(3)	
	sys.exit()
	
print("\nA new version is available. Would you like to download it? [Y/N]")
choice = input().lower()

if (choice == "y" or choice == "yes" or choice == ""):
	print("    Downloading...")
	new_package = urllib.request.urlretrieve("https://github.com/albinohat/osu_stats_watcher/blob/master/bin/osu_stats_watcher.exe?raw=true", "osu_stats_watcher.exe")
	print("    Download Complete!")
	
else:
	print("\nAborting update and exiting in 3 seconds...")
	time.sleep(3)
	sys.exit()
	
	





