This is a python package for pulling and parsing the matchmaking game stats supplied via the halo.infinite API on Autocode. I was curious about how CSR changes are applied to each player in lobbies with massive CSR ranges, so I wrote some code. I figured I would share the package I used to pull/organize the data.

Classes are included to represent various portions of the json responses from matches.list and matches.retrieve in the api. I do most of my analysis in pandas, 
so I focused on exporting those objects into list[dict]. There is also a command line tool to write them straight to csv if you don't care of having the objects
themselves.

The dependencies are pandas, numpy, and tqdm

I used configparser to read in three values, so you'll need to set up an .ini file for that. The variable "CONFIG_PATH" will point to the ini file. This should contain a section similar to:

[halo]  
dev_token: YOUR_AUTOCODE_TOKEN  
known_teammate_file_path: D:/Halo Stats/known_team.txt  
out_directory: D:/Halo Stats/  

~/known_team.txt is used to filter out games where you were part of a filename. Mine looks like:

Gamertag1  
Gamertag2  
GamertagEtc  

I have been using this code mostly to get a DataFrame, then doing additional preprocessing in a notebook. I added the CLI argument parsing mostly for convenience. 

The CLI help command shows the arguments and descriptions:

Save pvp match statistics from Halo API. 25 matches will be returned if less are requested.

positional arguments:  
  gamertag:         Required and case sensative  
  number_matches:   Number of matchmade pvp matches to pull starting with most recent. defaults to '-1' which will pull all available matchmade pvp matches  
  filename:         Output filename to store csv data. Directory is chosen by your python_config.ini  

options:  
  -h, --help:       show this help message and exit  
  --solo:           Exclude matches that contain players in your 'known_players.txt' file. Intended use is tracking matches where you queued without a fireteam. If used, '--gamertag_only' flag will be ignored. Will be result in less than 'number_matches' results due to exclusions  
  --gamertag_only:  Only store stats from 'gamertag' player and not everyone in the lobby  
