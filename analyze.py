# This is a program to analyze the accuracy of the ranking algorithm. 

# Import the necessary modules.
import numpy as np
import matplotlib.pyplot as plt
import os


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




def analyze_spread(teams, games):
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

			data = [ratio, spread]
			table.append(data)

	return table




def spread_plot(teams, games):
	''' This is a function to generate a plot demonstrating the spread as a function of the ranking '''

	# Check if the spread.png plot already exits, if so, delete it.
	if os.path.exists("static/spread.png"):
		os.remove("static/spread.png")
	else:
		pass

	# Get data and arrange it into a numpy array
	spread_table = analyze_spread(teams_list, games_list)
	spread_array = np.array(spread_table)

	# Generate plot variables
	x = spread_array[:, 0]
	y = spread_array[:, 1]
	z = np.polyfit(x, y, 1)
	p = np.poly1d(z)

	# Format and save plot
	plt.scatter(x, y)
	plt.ylabel("Margin of Victory")
	plt.xlabel("Winner Rating/Loser Rating")
	plt.plot([1,1],[0,63], 'k-')
	plt.plot(x,p(x),"r--")
	plt.savefig('static/spread.png')

	return




def top25_plot():
	''' This is a function to generate a bar graph to visualize team's relative ratings.'''

	# Check if the top25.png plot already exits, if so, delete it.
	if os.path.exists("static/top25.png"):
		os.remove("static/top25.png")
	else:
		pass

	plot_list = []

	# Retrieve rankings data
	cur.execute("SELECT * FROM teams WHERE rank <= '25'")
	rows = cur.fetchall()

	# Organize 
	for row in rows:
		team = {
			'team': row[0], 
			'rating': row[3]
		}

		plot_list.append(team)

	# Sort by rating
	ranks = sorted(plot_list, key = lambda k: k['rating'], reverse = True)

	# Create lists for matplotlib
	x = []
	y = []

	for index, team in enumerate(ranks):
		x.append(team['team'])
		y.append(team['rating'])

	# Format plot
	fig = plt.figure(num=1)
	fig.set_figheight(6)
	fig.set_figwidth(10)
	pos = np.arange(len(x))
	plt.bar(pos, y, align='center', tick_label=x)
	plt.gcf().subplots_adjust(bottom=0.33)
	plt.xticks(rotation='vertical')

	# Save plot 
	fig.savefig("static/top25.png")

	return


top25_plot()

# teams_list = get_teams(2018)
# games_list = get_games(2018)	

# spread_plot(teams_list, games_list)

# results = analyze_accuracy(teams_list, games_list, 2018)

# 
# print(results)




