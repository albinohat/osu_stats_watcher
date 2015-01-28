## osu_player_stats_watcher.py
## Author: Daniel "Albinohat" Mercado
## 
## This script creates a text file containing some quick user statistics to display on a Twitch stream.

## TODO
## Add +/- updates for pp and rank.
## 

## Standard Imports
import json, os, re, sys, threading, time

## Add the osu-apy path.
sys.path.append("../../../osu-apy/2.7")

## Third-party Imports
import osu_apy

## Version - Gets updated at each push.
VERSION = "0.5.5b Released 2015-01-28"

## Global Variables - Lazy Mode

## Initialize a list to check that all the required attributes are present.
config_bools = [0, 0, 0, 0, 0, 0, 0, 0, 0]

bool_config   = 0
bool_help     = 0
bool_stdout   = 0
bool_version  = 0
bool_change   = 0
bool_exit     = 0
bool_show     = 1
bool_diff     = 1

change_text   = ""
username      = ""
gametype      = ""

current_rank  = ""
current_pp    = ""
current_acc   = ""

previous_rank = ""
previous_pp   =	""
previous_acc  = ""

## WriteDiffThread - A thread which writes the diffs to the required files.
class WriteDiffThread(threading.Thread):
	## __init__ - Initializes the attributes of the WriteDiffThread instance.
	def __init__(self):
		threading.Thread.__init__(self)
		self.start()

	## run - This method calls the writeDiff method.
	def run(self):
		writeDiff()

## writeDiff - Writes the differences in rank, PP and accuracy to text files.	
def writeDiff():
	## Reset the change bool and text.
	change_text = "\n== Stats Change @ " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " =="	
	bool_change = 0

	## This file's text will display as green and contain improvements.
	try:
		green_file = open(diff_improve_path, "w+")
		
	except IOError:
		print("\n    Error: Unable to write to \"" + diff_improve_path + ".\" Please ensure you have the rights to write there.")
		sys.exit()
		
	## This file's text will display as red and contain declines.
	try:
		red_file   = open(diff_degrade_path, "w+")

	except IOError:
		print("\n    Error: Unable to write to \"" + diff_degrade_path + ".\" Please ensure you have the rights to write there.")
		sys.exit()
	
	## Write a blank line to each file.
	green_file.write(" \n")
	red_file.write(" \n")

	## Only compare if the previous values aren't empty and if a change has occurred.
	if (previous_rank != "" and previous_pp != "" and previous_acc != ""):
		new_rank = current_rank - previous_rank
		## Improvement
		if (new_rank < 0):
			if (bool_stdout == 1):
				change_text += "\n    Rank: " + str(current_rank) + " (+" + str(new_rank)[1:] + ")"
			green_file.write("+" + str(new_rank)[1:] + "\n")
			red_file.write(" \n")
			
			bool_change = 1
		## Decline
		elif (new_rank > 0):
			if (bool_stdout == 1):
				change_text += "\n    Rank: " + str(current_rank) + " (-" + str(new_rank) + ")"
			red_file.write("-" + str(new_rank) + "\n")
			green_file.write(" \n")

			bool_change = 1
		## No Change. 
		else:
			green_file.write(" \n")
			red_file.write(" \n")

		new_pp = current_pp - previous_pp
		## Improvement
		if (new_pp > 0):
			if (bool_stdout == 1):
				change_text += "\n    PP: " + str(current_pp).split(".", 1)[0] + " (+" + str(new_pp)[:str(new_pp).find(".") + 3] + ")"

			green_file.write("+" + str(new_pp)[:str(new_pp).find(".") + 3] + "\n")
			red_file.write(" \n")	

			bool_change = 1
		## Decline
		elif (new_pp < 0):
			if (bool_stdout == 1):
				change_text += "\n    PP: " + str(current_pp).split(".", 1)[0] + " (" + str(new_pp)[:str(new_pp).find(".") + 3] + ")"

			red_file.write(str(new_pp)[:str(new_pp).find(".") + 3] + "\n")
			green_file.write(" \n")
			
			bool_change = 1
		## No Change. 
		else:
			green_file.write(" \n")
			red_file.write(" \n")

		new_acc = current_acc - previous_acc
		## Improvement
		if (new_acc > 0):
			if (bool_stdout == 1):
				change_text += "\n    Accuracy: " + str(current_acc)[:str(current_acc).find(".") + 3] + "%" + " (+" + str(new_acc)[:str(new_acc).find(".") + 3] + ")"

			green_file.write("+" + str(new_acc)[:str(new_acc).find(".") + 3])
			red_file.write(" \n")

			bool_change = 1	
		## Decline
		elif (new_acc < 0):
			if (bool_stdout == 1):
				change_text += "\n    Accuracy: " + str(current_acc)[:str(current_acc).find(".") + 3] + "%" + " (" + str(new_acc)[:str(new_acc).find(".") + 3] + ")"

			red_file.write(str(new_acc)[:str(new_acc).find(".") + 3])
			green_file.write(" \n")

			bool_change = 1
		## No Change. Don't write anything.

	green_file.close()
	red_file.close()

	if (bool_stdout == 1 and bool_change == 1):
		print(change_text)

	## Sleep then clear and close the files.
	for i in range(int(diff_refresh) * 4):
		if (bool_exit == 1):
			return

		time.sleep(0.25)

	green_file = open(diff_improve_path, "w+")
	red_file   = open(diff_degrade_path, "w+")

	green_file.write(" \n \n \n ")
	red_file.write(" \n \n \n ")

	green_file.close()
	red_file.close()	

## writeStats - Writes the player stats to a text file.
def writeStats():
	## Open the file displayed on stream, write to it and close it.
	## Line 1 - Username
	## Line 2 - PP Rank
	## Line 3 - PP
	## Line 4 - Accuracy (Truncated to 2 decimal places.)	

	try:
		stats_file = open(stats_path, "w+")

	except IOError:
		print("\n    Error: Unable to write to \"" + stats_path + ".\" Please ensure you have the rights to write there.")
		sys.exit()

	stats_file.write(str(username) + "\n")
	stats_file.write("Rank:" + str(current_rank) + "\n")
	stats_file.write("PP: " + str(current_pp).split(".", 1)[0] + "\n")
	stats_file.write("Acc: " + str(current_acc)[:str(current_acc).find(".") + 3] + "%")
	stats_file.close()

## Validate # of CLA
if (len(sys.argv) < 2 or len(sys.argv) > 4):
	print("\n    Invalid Syntax. Use -h for help.")
	sys.exit()

else:
	## Parse through the CLA, ignoring [0] since it it is the filename.
	## bool_help set to 1 will cause the script to exit.
	for arg in sys.argv:
		if (arg != sys.argv[0]):
			if (arg == "-h" or arg == "--help"):
				bool_help = 1
			elif (arg == "-v" or arg == "--version"):
				bool_version = 1
			elif (arg == "-s" or arg == "--stdout"):
				bool_stdout = 1
			elif (arg == "--no-diff"):
				bool_diff = 0
			elif (re.match("--?\w+", arg.lower())):
				print("\n    Invalid Syntax. Use -h for help.")
				sys.exit()

			else:
				if (os.path.isfile(arg)):
					try:
						config_json = json.load(open(arg, "r"))
						bool_config = 1

					except IOError:
						print("\n    Error: Unable to open file: \"" + config_path + "\"")
						sys.exit()

					except ValueError:
						print("\n    Error: Invalid JSON. Please replace all '\\' in save_dir with \"\\\\\" or '/'")
						sys.exit()

					## Parse through the configuration file.
					for key, value in config_json.items():
						if (key == "api_key"):
							api_key = value
							config_bools[0] = 1
						
						elif (key == "username"):
							username = value
							config_bools[1] = 1
						
						elif (key == "save_dir"):
							save_dir = re.sub("^\\$", "\\\\", value)
							if (save_dir[-1] != "\\"):
								save_dir += "\\"

							config_bools[2] = 1

						elif (key == "gametype"):
							gametype = value
							config_bools[3] = 1
						
						elif (key == "stats_refresh"):
							stats_refresh = value
							config_bools[4] = 1

						elif (key == "stats_file"):
							stats_file = value
							config_bools[5] = 1

						elif (key == "diff_refresh"):
							diff_refresh = value
							config_bools[6] = 1

						elif (key == "diff_improve_file"):
							diff_improve_file = value
							config_bools[7] = 1
							
						elif (key == "diff_degrade_file"):
							diff_degrade_file = value
							config_bools[8] = 1

						else:
							print("\n    Invalid attribute \"" + key + "\" See the osu-apy wiki for more information.\n")
							sys.exit()

				else:
					print("\n    Error. Unable to open file \"" + arg + "\"")
					sys.exit()

## Print out the help dialog.
if (bool_help == 1):
	print("\n    Usage: " + sys.argv[0] + " [options] config_file\n")
	print("    Options")
	print("        -h | --help - Prints out this help.")
	print("        -s | --stdout - Prints out stat changes to STDOUT in addition to the text files.")
	print("        -v | --version - Prints out the version you are using.")
	print("        --no-diff - Changes in stats won't be updated in separate text files. Stat-only mode.")
	print("\nconfig_file - The JSON file containing the settings for the script.")

## Print out the version.
if (bool_version == 1):
	## Put a line between help and version.
	print("\n    Version " + VERSION)

## Exit if either help or version was specified.
if (bool_help == 1 or bool_version == 1):
	sys.exit()

## Exit if there was no config file specified.
if (bool_config == 0):
	print("\n    Invalid Syntax. Use -h for help.")
	sys.exit()

## Exit if there are missing configuration entires.
for each in config_bools:
	if (each == 0):
		print("\n    Invalid configuration. At least one required attribute is missing. See the osu-apy wiki for more information.")
		sys.exit()	

## Exit if the save path does not exist or we cannot access it.
if (os.path.isdir(save_dir) == 0):
	print("\n    Invalid configuration. \"" + save_dir + "\" is not a valid directory. Would you like to try to create it? Y/N (Default = Y)")
	choice = input().lower()
	
	if (choice == "y" or choice == "yes" or choice == ""):
		try: 
			os.makedirs(save_dir)
			
		except IOError:
			print("\n    Error: Unable to write to \"" + diff_degrade_path + ".\" Please ensure you have the rights to write there.")
			sys.exit()

	else:
		sys.exit()

## Exit if the gametype value is not between 0 and 3
if (gametype < 0 or gametype > 3):
	print("\n    Invalid Configuration. gametype must be between 0 and 3.")
	sys.exit()

## Exit if the stats_refresh is smaller than 10 seconds.
if (float(stats_refresh) < 10):
	print("\n    Invalid configuration. stats_refresh must be at least 10.")
	sys.exit()
	
## Exit if stats_refresh is smaller than diff_refresh.
if (float(stats_refresh) <= float(diff_refresh)):
	print("\n    Invalid configuration. diff_refresh must be smaller than stats_refresh.")
	sys.exit()	

## Build the full paths to the save files.
stats_path        = save_dir + stats_file
diff_improve_path = save_dir + diff_improve_file
diff_degrade_path = save_dir + diff_degrade_file

while(1):
	try:
		stats_json = ""
		## Request player stats from the server.
		try:
			stats_json = json.loads(osu_apy.get_user(api_key, username, str(gametype), "string", ""))
			
			## Exit if the player request does not exist.
			if (str(stats_json) == "[]"):
				print("\n    Invalid configuration. The user \"" + username + "\" does not exist.")
				sys.exit()

			current_rank = int(stats_json[0]["pp_rank"])
			current_pp   = float(stats_json[0]["pp_raw"])
			current_acc  = float(stats_json[0]["accuracy"])

		except IOError:
			print("\n    Unable to connect to osu!api. Will retry again in " + str(stats_refresh) + " seconds.")
		
		except ValueError:
			## Exit if the API key is invalid.
			print(str(stats_json))
			print("\n    Invalid JSON returned from osu!api. Will retry again in " + str(stats_refresh) + " seconds.")

		## Only print out that the script is running if the config is valid.
		if (bool_show == 1):
			print("\nosu! Stats Watcher is running. Press CTRL+C to exit.")
			bool_show = 0

		## Write the current stats to a text file.
		writeStats()

		## write the difference in stats to a text file if enabled.
		if (bool_diff == 1):
			WriteDiffThread()

		## Update once per minute.
		time.sleep(float(stats_refresh))

		## Fill in the previous values to compare.
		previous_rank = current_rank
		previous_pp   =	current_pp
		previous_acc  = current_acc

	except KeyboardInterrupt:
		print("\nCTRL+C Detected. Exiting...")

		## Signal to the child thread to exit.
		bool_exit = 1

		## Exit main.
		sys.exit()
