## osu_player_stats_watcher.py
## Author: Daniel "Albinohat" Mercado
## 
## This script creates a text file containing some quick user statistics to display on a Twitch stream.

## TODO
## Add +/- updates for pp and rank.
## 

## Standard Imports
import json, os, re, subprocess, sys, threading, time, urllib

## Add the osu-apy path.
sys.path.append("../../../osu-apy/2.7")

## Third-party Imports
import osu_apy

## WriteDiffThread - A thread which writes the diffs to the required files.
class WriteDiffThread(threading.Thread):
	## __init__ - Initializes the attributes of the WriteDiffThread instance.
	def __init__(self, bool_diff, bool_stdout, bool_exit, diff_refresh, diff_improve_path, diff_degrade_path, current_rank, current_pp, current_acc, previous_rank, previous_pp, previous_acc):
		threading.Thread.__init__(self)
		
		## Create local copies of the variables passed in.
		self.bool_diff, self.bool_stdout, self.bool_exit, self.diff_refresh, self.diff_improve_path, self.diff_degrade_path, self.current_rank, self.current_pp, self.current_acc, self.previous_rank, self.previous_pp, self.previous_acc = bool_diff, bool_stdout, bool_exit, diff_refresh, diff_improve_path, diff_degrade_path, current_rank, current_pp, current_acc, previous_rank, previous_pp, previous_acc

		#print "  In WriteDiffThread.__init__()"  
		#print "   Variable values"
		#print "    " + str([self.bool_diff, self.bool_stdout, self.bool_exit, self.diff_refresh, self.diff_improve_path, self.diff_degrade_path, self.current_rank, self.current_pp, self.current_acc, self.previous_rank, self.previous_pp, self.previous_acc])

		self.start()

	## run - This method calls the writeDiff method.
	def run(self):
		while (self.bool_exit == 0):
			## Write the differences to the file and/or STDOUT.
			self.writeDiff()

	## writeDiff - Writes the differences in rank, PP and accuracy to text files.	
	def writeDiff(self):
		try:
			if (self.current_rank == 0 or self.current_pp == 0.0 or self.current_acc == 0.0):
				return
			
			#print "  In WriteDiffThread.writeDiff()"
			#print "   Variable values"
			#print "    " + str([self.bool_diff, self.bool_stdout, self.bool_exit, self.diff_refresh, self.diff_improve_path, self.diff_degrade_path, self.current_rank, self.current_pp, self.current_acc, self.previous_rank, self.previous_pp, self.previous_acc])

			## Reset the change bool and text.
			self.change_text = "\n== Stats Change @ " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " =="	
			self.bool_change = 0

			if (self.bool_diff == 1):
				## This file's text will display as green and contain improvements.
				try:
					self.green_file = open(self.diff_improve_path, 'w+')

				except IOError:
					print "\n    Error: Unable to write to \"" + self.diff_improve_path + ".\" Please ensure you have the rights to write there."
					sys.exit()

			if (self.bool_diff == 1):			
				## This file's text will display as red and contain declines.
				try:
					self.red_file = open(self.diff_degrade_path, 'w+')

				except IOError:
					print "\n    Error: Unable to write to \"" + self.diff_degrade_path + ".\" Please ensure you have the rights to write there."
					sys.exit()

			## Write a blank line to each file.\
			if (self.bool_diff == 1):
				self.green_file.write(" \n")
				self.red_file.write(" \n")

			## Only compare if the previous values aren't empty and if a change has occurred.
			if (self.previous_rank != "" and self.previous_pp != "" and self.previous_acc != ""):
				self.new_rank = self.current_rank - self.previous_rank

				## Improvement
				if (self.new_rank < 0):
					if (self.bool_stdout == 1):
						self.change_text += "\n    Rank: " + str(self.current_rank) + " (+" + str(self.new_rank)[1:] + ")"

					if (self.bool_diff == 1):
						self.green_file.write("+" + str(self.new_rank)[1:] + "\n")
						self.red_file.write(" \n")
					
					self.bool_change = 1

				## Decline
				elif (self.new_rank > 0):
					if (self.bool_stdout == 1):
						self.change_text += "\n    Rank: " + str(self.current_rank) + " (-" + str(self.new_rank) + ")"

					if (self.bool_diff == 1):
						self.red_file.write("-" + str(self.new_rank) + "\n")
						self.green_file.write(" \n")

					self.bool_change = 1

				## No Change. 
				else:
					if (self.bool_diff == 1):
						self.green_file.write(" \n")
						self.red_file.write(" \n")

				self.new_pp = self.current_pp - self.previous_pp

				## Improvement
				if (self.new_pp > 0.01):
					if (self.bool_stdout == 1):
						self.change_text += "\n    PP: " + str(self.current_pp).split(".", 1)[0] + " (+" + str(self.new_pp)[:str(self.new_pp).find(".") + 3] + ")"

					if (self.bool_diff == 1):
						self.green_file.write("+" + str(self.new_pp)[:str(self.new_pp).find(".") + 3] + "\n")
						self.red_file.write(" \n")	

					self.bool_change = 1

				## Decline
				elif (self.new_pp < -0.01):
					if (self.bool_stdout == 1):
						self.change_text += "\n    PP: " + str(self.current_pp).split(".", 1)[0] + " (" + str(self.new_pp)[:str(self.new_pp).find(".") + 3] + ")"

					if (self.bool_diff == 1):
						self.red_file.write(str(self.new_pp)[:str(self.new_pp).find(".") + 3] + "\n")
						self.green_file.write(" \n")
					
					self.bool_change = 1

				## No Change. 
				else:
					if (self.bool_diff == 1):
						self.green_file.write(" \n")
						self.red_file.write(" \n")

				self.new_acc = self.current_acc - self.previous_acc
				## Improvement
				if (self.new_acc > 0.01):
					if (self.bool_stdout == 1):
						self.change_text += "\n    Accuracy: " + str(self.current_acc)[:str(self.current_acc).find(".") + 3] + "% (+" + str(self.new_acc)[:str(self.new_acc).find(".") + 6] + ")"

					if (self.bool_diff == 1):
						self.green_file.write("+" + str(self.new_acc)[:str(self.new_acc).find(".") + 3])
						self.red_file.write(" \n")

					self.bool_change = 1

				## Decline
				elif (self.new_acc < -0.01):
					if (self.bool_stdout == 1):
						self.change_text += "\n    Accuracy: " + str(self.current_acc)[:str(self.current_acc).find(".") + 3] + "% (" + str(self.new_acc)[:str(self.new_acc).find(".") + 6] + ")"

					self.red_file.write(str(self.new_acc)[:str(self.new_acc).find(".") + 3])
					self.green_file.write(" \n")

					self.bool_change = 1

				## No Change. Don't write anything.

			if (self.bool_diff == 1):
				self.green_file.close()
				self.red_file.close()

			if (self.bool_stdout == 1 and self.bool_change == 1):
				print self.change_text

			## Sleep then clear and close the files.
			for i in range(int(self.diff_refresh) * 4):
				if (self.bool_exit == 1):
					sys.exit()

				time.sleep(0.25)

			if (self.bool_diff == 1):
				self.green_file = open(self.diff_improve_path, 'w+')
				self.red_file   = open(self.diff_degrade_path, 'w+')

				self.green_file.write(" \n \n \n ")
				self.red_file.write(" \n \n \n ")

				self.green_file.close()
				self.red_file.close()

			sys.exit()

		except KeyboardInterrupt:				
			sys.exit()
			
## getStats - This method hits the osu!api and returns player stats.
##
## api_key  - An osu!api key. One can be obtained from https://osu.ppy.sh/p/api
## gametype - The gametype to look up stats for. See osu!api or osu!apy documentation.
## username - The osu! username to look up stats for.
def getStats(api_key, username, gametype):
	## Request player stats from the osu!api.
	try:
		stats_json = json.loads(osu_apy.get_user(api_key, username, str(gametype), "string", ""))
		
		## Exit if the player request does not exist.
		if (str(stats_json) == "[]"):
			print "\n    Invalid configuration. The user \"" + username + "\" does not exist."
			sys.exit()

		return int(stats_json[0]["pp_rank"]), float(stats_json[0]["pp_raw"]), float(stats_json[0]["accuracy"])

	## Unable to connect to osu!api
	except IOError:
		print "\n    Unable to connect to osu!api. Will retry again in " + str(stats_refresh) + " seconds."

		return 0, 0.0, 0.0

	## Invalid JSON returned from osu!api
	except ValueError:
		## Exit if the API key is invalid.
		print "\n    Invalid JSON returned from osu!api. Will retry again in " + str(stats_refresh) + " seconds."
		
		return 0, 0.0, 0.0

	except KeyboardInterrupt:		
		return 0, 0.0, 0.0
			
## parseConfig - Validates the command line arguments and parses through them.
##
## VERSION       - A string containing the current version.
## bool_config   - A bool controlling whether a config file was present.
## bool_diff     - A bool controlling whether to place stat diffs in text files.
## bool_help     - A bool controlling whether or not to display the help.
## bool_stdout   - A bool controlling whether or not to display stat changes in the console.
## bool_update   - A bool controlling whether or not to run osu! Stats Updater.
## bool_version  - A bool controlling whether or not to display the version.
## bool_testdiff - A bool controlling whether or not to write dummy data to diff files for OBS testing.
def parseConfig(VERSION, bool_config, bool_diff, bool_help, bool_stdout, bool_update, bool_version, bool_testdiff):
	try:
		## Initialize a list to check that all the required attributes are present.
		config_bools = [0, 0, 0, 0, 0, 0, 0, 0, 0]

		## Validate # of CLA
		if (len(sys.argv) < 2 or len(sys.argv) > 5):
			print "\n    Invalid Syntax. Use -h for help."
			sys.exit()

		else:
			## Parse through the CLA, ignoring [0] since it it is the filename.
			## bool_help set to 1 will cause the script to exit.
			for arg in sys.argv:
				temp = arg.lower()
				if (arg != sys.argv[0]):
					if (temp == "-h" or temp == "--help"):
						bool_help = 1
					elif (temp == "-v" or temp == "--version"):
						bool_version = 1
					elif (temp == "--no-stdout"):
						bool_stdout = 0
					elif (temp == "--no-diff"):
						bool_diff = 0
					elif (temp == "--test-diff"):
						bool_testdiff = 1
					elif (temp == "-u" or temp == "--update"):
						bool_update = 1						
					elif (re.match("--?\w+", temp)):
						print "\n    Invalid Syntax. Use -h for help."
						sys.exit()

					else:
						if (os.path.isfile(arg)):
							## Normalize (possibly invalid) save_dir attribute to use /.
							config_file = open(arg, "r+")
							config_text = config_file.read()		
							config_text = re.sub(r'\\\\|\\', r'/', config_text)
							config_text = re.sub(r'\{\{', r'\{', config_text)
							config_text = re.sub(r'\{\{', r'\{', config_text)
							config_text = re.sub(r'\}\}', r'\}', config_text)

							## Overwrite the file with the new data.
							config_file.seek(0)
							config_file.write(config_text)
							config_file.close()

							try:
								config_json = json.load(open(arg, "r"))
								bool_config = 1

							except IOError:
								print "\n    Error: Unable to open file: \"" + config_path + "\""
								sys.exit()

							except ValueError:
								print "\n    Error: Invalid JSON. Please replace all '\\' in save_dir with \"\\\\\" or '/'"
								sys.exit()

							## Parse through the configuration file.
							for key, value in config_json.iteritems():
								if (key == "api_key"):
									api_key = value
									config_bools[0] = 1
								
								elif (key == "username"):
									username = value
									config_bools[1] = 1
								
								elif (key == "save_dir"):
									save_dir = value + "/"
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
									print "\n    Invalid attribute \"" + key + "\" See the osu-apy wiki for more information.\n"
									sys.exit()

						else:
							print "\n    Error. Unable to open file \"" + arg + "\""
							sys.exit()

		## Print out the help dialog.
		if (bool_help == 1):
			print "\n    Usage: " + sys.argv[0] + " [options] config_file\n"
			print "    Options"
			print "        -h | --help - Prints out this help."
			print "        -u | --update - Checks for a new version of OSW to download."
			print "        -v | --version - Prints out the version you are using."
			print "        --no-stdout - Changes in stats won't be sent to STDOUT."
			print "        --no-diff - Changes in stats won't be updated in separate text files."
			print "        --test-diff - Writes dummy data to the diff files for OBS testing and exits."
			print "\nconfig_file - The JSON file containing the settings for the script."

		## Print out the version.
		if (bool_version == 1):
			## Put a line between help and version.
			print "\n    Version " + VERSION

		if (bool_update == 1):
			if (os.path.isfile("osu_stats_updater.exe") == 0):
				print "osu! Stats Updater not found. Download now? [Y/N]"
				choice = raw_input().lower()

				if (choice == "y" or choice == "yes" or choice == ""):
					print "    Downloading..."
					new_package = urllib.urlretrieve("https://github.com/albinohat/osu_stats_watcher/blob/master/bin/osu_stats_updater.exe?raw=true", "osu_stats_updater.exe")
					print "    Download Complete!"
					
				else:
					print "\n    Aborting Update and exiting..."
					sys.exit()
				
			print "\n    Launching updater..."
			ud_pid = subprocess.Popen(["osu_stats_updater.exe", "\"" + VERSION + "\""], shell=True).pid
			
		## Exit if either help or version was specified.
		if (bool_help == 1 or bool_version == 1 or bool_update == 1):
			sys.exit()

		## Exit if there was no config file specified.
		if (bool_config == 0):
			print "\n    Invalid Syntax. Use -h for help."
			sys.exit()

		## Exit if there are missing configuration entires.
		for each in config_bools:
			if (each == 0):
				print "\n    Invalid configuration. At least one required attribute is missing. See the osu-apy wiki for more information."
				sys.exit()	

		## Exit if the save path does not exist or we cannot access it.
		if (os.path.isdir(save_dir) == 0):
			print "\n    Invalid configuration. \"" + save_dir + "\" is not a valid directory. Would you like to try to create it? Y/N (Default = Y)"
			choice = raw_input().lower()
			
			if (choice == "y" or choice == "yes" or choice == ""):
				try: 
					os.makedirs(save_dir)
					
				except IOError:
					print "\n    Error: Unable to write to \"" + diff_degrade_path + ".\" Please ensure you have the rights to write there."
					sys.exit()

			else:
				sys.exit()

		## Exit if the gametype value is not between 0 and 3
		if (gametype < 0 or gametype > 3):
			print "\n    Invalid Configuration. gametype must be between 0 and 3."
			sys.exit()

		## Exit if the stats_refresh is smaller than 10 seconds.
		if (float(stats_refresh) < 10):
			print "\n    Invalid configuration. stats_refresh must be at least 10."
			sys.exit()

		## Exit if stats_refresh is smaller than diff_refresh.
		if (float(stats_refresh) <= float(diff_refresh)):
			print "\n    Invalid configuration. diff_refresh must be smaller than stats_refresh."
			sys.exit()	

		## Build the full paths to the save files.
		stats_path        = save_dir + stats_file
		diff_improve_path = save_dir + diff_improve_file
		diff_degrade_path = save_dir + diff_degrade_file

		## Write dummy data to the diff files for OBS testing.
		if (bool_testdiff == 1):
			testDiff(diff_improve_path, diff_degrade_path)
		
		## Return all of the configuration entries to be used.
		#print "Parsed CLAs & Config"
		#print str([bool_stdout, bool_diff, api_key, username, gametype, stats_refresh, diff_refresh, stats_path, diff_improve_path, diff_degrade_path])
		
		return bool_stdout, bool_diff, api_key, username, gametype, stats_refresh, diff_refresh, str(stats_path), str(diff_improve_path), str(diff_degrade_path)

	except KeyboardInterrupt:
		sys.exit()

## testDiff - Writes to the diff files to allow for testing in OBS.
## diff_improve_path - The path to the improvement diff file.
## diff_degrade_path - The path to the degrade diff file.
def testDiff(diff_improve_path, diff_degrade_path):
	print "\n    Diff Test Enabled. Press CTRL+C to exit."

	try:
		green_file = open(diff_improve_path, 'w+')
		green_file.write(" \n+TEST\n \n+TEST")
		green_file.close()

		red_file = open(diff_degrade_path, 'w+')
		red_file.write(" \n \n-TEST\n ")
		red_file.close()
		
		while (1):
			time.sleep(1)

	## When CTRL+C is hit, blank the files again and exit.
	except KeyboardInterrupt:
		print "\nCTRL+C Detected. Exiting..."

		green_file = open(diff_improve_path, 'w+')
		red_file   = open(diff_degrade_path, 'w+')

		green_file.write(" \n \n \n ")
		red_file.write(" \n \n \n ")

		green_file.close()
		red_file.close()

		sys.exit()
		
## writeStats - Writes the player stats to a text file.
## name - The osu! username to look up stats for.
## rank - The user's current world rank.
## pp   - The user's current performance points (PP)
## acc  - The user's current accuracy. 
def writeStats(name, rank, pp, acc, path):
	## Open the file displayed on stream, write to it and close it.
	## Line 1 - Username
	## Line 2 - PP Rank
	## Line 3 - PP
	## Line 4 - Accuracy (Truncated to 2 decimal places.)	
	try:
		if (rank == 0 or pp == 0.0 or acc == 0.0):
			return

		if (rank == "" or pp == "" or acc == ""):
			return

		stats_file = open(path, 'w+')

		stats_file.write(str(name) + "\n")
		stats_file.write("Rank: " + str(rank) + "\n")
		stats_file.write("PP: " + str(pp).split(".", 1)[0] + "\n")
		stats_file.write("Acc: " + str(acc)[:str(acc).find(".") + 3] + "%")
		stats_file.close()

	except IOError:
		print "\n    Error: Unable to write to \"" + path + ".\" Please ensure you have the rights to write there."
		sys.exit()

	except KeyboardInterrupt:
		sys.exit()
	
## main - The main loop of the code.
def main():
	## Version - Gets updated at each git push.
	VERSION = "0.7.6b released on 2015-02-16"

	## Booleans determining code flow.
	bool_config     = 0
	bool_diff       = 1
	bool_exit       = 0
	bool_help       = 0
	bool_init_stats = 1
	bool_stdout     = 1
	bool_update     = 0
	bool_version    = 0
	bool_testdiff   = 0

	## The player stats of interest.
	username        = ""
	gametype        = ""
	
	## These variables hold the last known values of stats of interest used for comparisons.
	previous_rank   = ""
	previous_pp     = ""
	previous_acc    = ""

	## Maintain a list of threads.
	threads = []
	
	## Parse through the CLA and store all of the configuration values.
	bool_stdout, bool_diff, api_key, username, gametype, stats_refresh, diff_refresh, stats_path, diff_improve_path, diff_degrade_path = parseConfig(VERSION, bool_config, bool_diff, bool_help, bool_stdout, bool_update, bool_version, bool_testdiff)

	## Only print out that the script is running if the config is valid.
	print "\nosu! Stats Watcher is running. Press CTRL+C to exit."

	## Get the initial stats.
	start_rank, start_pp, start_acc = getStats(api_key, username, gametype)
	current_rank, current_pp, current_acc = getStats(api_key, username, gametype)

	while(1):
		try:
			## Request the player's stats.
			current_rank, current_pp, current_acc = getStats(api_key, username, gametype)
			
			## Write the current stats to a text file.
			writeStats(username, current_rank, current_pp, current_acc, stats_path)

			## write the difference in stats to a text file if enabled.
			current_diff_thread = WriteDiffThread(bool_diff, bool_stdout, bool_exit, diff_refresh, diff_improve_path, diff_degrade_path, current_rank, current_pp, current_acc, previous_rank, previous_pp, previous_acc)
		
			threads.append(current_diff_thread)
			
			## Update once per minute.
			time.sleep(float(stats_refresh))

			## Fill in the previous values to compare.
			previous_rank = current_rank
			previous_pp   =	current_pp
			previous_acc  = current_acc
			
			threads.remove(current_diff_thread)

		except KeyboardInterrupt:
			print "\nCTRL+C Detected. Exiting..."

			if (bool_stdout == 1):
				session_rank = current_rank - start_rank
				session_pp   = current_pp - start_pp
				session_acc  = current_acc - start_acc

				print "\n== Session Summary =="

				## Improve
				if (session_rank < 0):
					print "    Rank: " + str(current_rank) + " (+" + str(session_rank)[1:] + ")"
				## Degrade
				elif (session_rank > 0):
					print "    Rank: " + str(current_rank) + " (-" + str(session_rank) + ")"
				## No change
				else:
					print "    Rank: " + str(current_rank) + " (No change)"

				## Improve				
				if (session_pp > 0):
					print "    PP: " + str(current_pp)[:str(current_pp).find(".") + 3] + " (+" + str(session_pp)[:str(session_pp).find(".") + 3] + ")"
				## Degrade
				elif (session_pp < 0):
					
					print "    PP: " + str(current_pp)[:str(current_pp).find(".") + 3] + " (" + str(session_pp)[:str(session_pp).find(".") + 3] + ")"
				## No change
				else:
					print "    PP: " + str(current_pp)[:str(current_pp).find(".") + 3] + " (No change)"

				## Improve
				if (session_acc > 0):
					print "    Accuracy: " + str(current_acc)[:str(current_acc).find(".") + 3] + "% (+" + str(session_acc)[:str(session_acc).find(".") + 6] + ")"
				## Degrade
				elif (session_acc < 0):
					print "    Accuracy: " + str(current_acc)[:str(current_acc).find(".") + 3] + "% (" + str(session_acc)[:str(session_acc).find(".") + 6] + ")"
				## No change
				else:
					print "    Accuracy: " + str(current_acc)[:str(current_acc).find(".") + 6] + "% (No change)"	
		
			## Signal to the child thread to exit.
			for each in threads:
				each.bool_exit = 1

			## Exit main.
			sys.exit()

## This will prevent main() from running unless explicitly called.
if __name__ == "__main__":
	main()
