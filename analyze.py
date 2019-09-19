# This is a program to analyze the accuracy of the ranking algorithm. 

# Import the support files in the project directory
import dbparams
import settings

# Connect to the database
conn = dbparams.db_connect()
cur = conn.cursor()



########## 		Analysis functions		 ##########

def get_teams(year):
	''' This is a function to get the teams and their final rankings from a season and return the list.'''

	cur.execute("SELECT * FROM history")
	rows = cur.fetchall()

	teams = []

	for row in rows:
		data = {
			'team': row[0],
			'points': row[3]
		}

		teams.append(data)

	return teams




def get_games(year):
	''' This is a function to get the games from a chosen season and return the list.'''

	cur.execute("SELECT * FROM games WHERE year = %s", (year,))
	rows = cur.fetchall()

	games = []

	for row in rows:
		data = {
			'winner': row[0],
			'loser': row[2],
			'spread': row[1] - row[3]
		}

		games.append(data)

	return games



def analyze_accuracy(teams, games, year):
	''' This is a function to compare the game results with the ranking to understand accuracy.
	
	teams <list> is the list returned from get_teams()
	games <list> is the list returned from get_games()
	'''

	# Initialize a few variables
	right = 0
	wrong = 0
	same = 0

	# Iterate through game list
	for game in games:
		winner = game['winner']
		loser = game['loser']

		# Don't care about FCS teams
		if winner not in settings.fbs_teams:
			pass
		elif loser not in settings.fbs_teams:
			pass
		else:

			# Get the poll ratings of each team
			for team in teams:
				if team['team'] == winner:
					winners_rating = team['points']

			for team in teams:
				if team['team'] == loser:
					losers_rating = team['points']

			# Compare results with prediction
			if winners_rating == losers_rating:
				same += 1
			elif winners_rating > losers_rating:
				right += 1
			elif losers_rating > winners_rating:
				wrong +=1

	# Calculate accuracy
	accuracy = round(100 * (right / (right + wrong)), 1)

	return accuracy




def analyze_spread():
	''' This is a function to calculate the spread versus a team's rating for correlation'''

	table = []

	# Iterate through game list
	for game in games:
		winner = game['winner']
		loser = game['loser']
		spread = game['spread']
		
		# Don't care about FCS teams
		if winner not in settings.fbs_teams:
			pass
		elif loser not in settings.fbs_teams:
			pass
		else:

			# Get the poll ratings of each team
			for team in teams:
				if team['team'] == winner:
					winners_rating = team['points']

			for team in teams:
				if team['team'] == loser:
					losers_rating = team['points']


			ratio = winners_rating / losers_rating

			data = {
				'ratio': ratio,
				'spread': spread
			}

			table.append(data)

	return table







teams_list = get_teams(2018)
games_list = get_games(2018)

results = analyze_accuracy(teams_list, games_list, 2018)

# 
print(results)




