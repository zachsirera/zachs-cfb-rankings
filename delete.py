import requests
import json
import urllib

# import support files in the project directory 
import helpers
import settings
import teamlist

# import other modules from packages that are needed
from lxml import html

def games(year):
	""" Parse game data from masseyratings.com and pass it into the games db """

	# Get score data for all games of P5 schools using html from lxml
	# This is the link for Massey's 2019 Data. 
	page  = requests.get('https://www.masseyratings.com/scores.php?s=308075&sub=11604&all=1')
	scores = html.fromstring(page.content)
	games = scores.xpath('//pre/text()')
	games_list = "--".join(games)

	# Put data in a readable list 
	games_rows = games_list.split('\n')

	# Delete last 4 lines from games_rows which do not represent any game data
	# This is the list that this program will iterate over to award points
	games_rows = games_rows[:-4]

	for index, rows in enumerate(games_rows):
		# Extract game data from rows
		date = rows[0:10]
		location = rows[10:12]
		team1 = rows[12:37].rstrip()
		score1 = int(rows[37:39])
		team2 = rows[41:66].rstrip()
		score2 = int(rows[66:68])
		team1conf = helpers.conf(team1)
		team2conf = helpers.conf(team2)
		team1tier = helpers.tier(team1conf)
		team2tier = helpers.tier(team2conf)
		year = year 

		print(date, location, team1, score1, team2, score2, team1conf, team2conf, team1tier, team2tier, year)

games(2019)