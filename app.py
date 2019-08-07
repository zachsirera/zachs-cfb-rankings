# This is a program to rank FBS football teams and predict the outcomes of their matchups
# Zach Sirera

# import the necessary packages

import requests
import psycopg2
import json
import urllib
import datetime
import arrow

# import support files in the project directory 
import helpers
import settings
import teamlist

# import other modules from packages that are needed
from lxml import html
from flask import Flask, render_template, session, request, redirect, url_for 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from math import exp, sqrt, ceil



# Necessary flask declaration
app = Flask(__name__) 

# Extract database credentials from private file
with open("dbparams.txt", "r") as file:
    data = file.readlines()

    params = []
    for line in data:
        words = line.split()
        params.append(words)

    host1 = str(params[0])
    host = host1[2:-2]

    database1 = str(params[1])
    database = database1[2:-2]

    user1 = str(params[2])
    user = user1[2:-2]

    password1 = str(params[3])
    password = password1[2:-2]

    url1 = str(params[4])
    url = url1[2:-2]

# Close dbparams.txt
file.close()

# Set up database
engine = create_engine(url)
db = scoped_session(sessionmaker(bind=engine))

# Establish connection to PostgreSQL database
try:
	conn = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
except:
	print("Database connection not made")

# Establish a cursor to navigate the database
cursor = conn.cursor()

# Get today's date
global updated
updated = arrow.now().format('YYYY-MM-DD')


def games():
	""" Parse game data from masseyratings.com and pass it into the games db """

	# Get score data for all games of P5 schools using html from lxml 
	page  = requests.get('https://www.masseyratings.com/scores.php?s=300937&sub=11604&all=1')
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

		# Look for games that feature the winning team on the day played, ie only insert new games. 
		cursor.execute("SELECT * FROM games WHERE winning_team = %s AND game_date = %s", (team1, date))
		cursor.fetchall()

		# Add new games to games db.
		if cursor.rowcount == 0:
			cursor.execute("""INSERT INTO games (winning_team, winning_score, losing_team, losing_score, game_date, winning_location)
							VALUES (%s, %s, %s, %s, %s,%s)""", (team1, score1, team2, score2, date, location))

			# Add wins to each team's record in teams db
			cursor.execute("SELECT wins FROM teams WHERE team = %s", (team1,))
			row = cursor.fetchall()
			if cursor.rowcount == 0:
				cursor.execute("UPDATE teams SET wins = 1 WHERE team = %s", (team1,))
			else:
				cursor.execute("UPDATE teams SET wins = wins + 1 WHERE team = %s", (team1,))

			# Add losses to each team's record in teams db
			cursor.execute("SELECT losses FROM teams WHERE team = %s", (team2,))
			if cursor.rowcount == 0:
				cursor.execute("UPDATE teams SET losses = 1 WHERE team = %s", (team2,))
			else:
				cursor.execute("UPDATE teams SET losses = losses + 1 WHERE team = %s", (team2,))

	# Commit changes to database
	conn.commit()


def performance():
	""" Compile previous performance stats for each team """
	# These are reevaluated every week as averages change
	
	for each_team in teamlist.teams:
		team = each_team['team']

		points_for = []
		points_against = []
		weights = []
		wts_sqrd = []

		# Need to convert this to append scores to lists

		# Get teams wins
		cursor.execute("SELECT wins FROM teams WHERE team = %s", (team,))
		wins = cursor.fetchall()
		if wins == 'NULL':
			wins = 0

		# Get teams losses
		cursor.execute("SELECT losses FROM teams WHERE team = %s", (team,))
		losses = cursor.fetchall()
		if losses == 'NULL':
			losses = 0

		if wins + losses == 0:
			continue

		# Get the points for in a win
		cursor.execute("SELECT winning_score FROM games WHERE winning_team = %s", (team,))
		rows = cursor.fetchall()
		count = cursor.rowcount
		for i in range(count):
			points_for.append(rows[i][0])


		# Get the points for in a loss
		cursor.execute("SELECT losing_score FROM games WHERE losing_team = %s", (team,))
		rows = cursor.fetchall()
		count = cursor.rowcount
		for i in range(count):
			points_for.append(rows[i][0])


		# Get the points against in a win
		cursor.execute("SELECT losing_score FROM games WHERE winning_team = %s", (team,))
		rows = cursor.fetchall()
		count = cursor.rowcount
		for i in range(count):
			points_against.append(rows[i][0])


		# Get the points against in a loss
		cursor.execute("SELECT losing_score FROM games WHERE losing_team = %s", (team,))
		rows = cursor.fetchall()
		count = cursor.rowcount
		for i in range(count):
			points_against.append(rows[i][0])

		# Assign weight factors
		##########     This needs to be expanded further     ########## 
		for score in points_for:
			weight = 1
			weights.append(weight)
			wts_sqrd.append(weight ** 2)


		# Calculate averages of points for and points against
		pf_sum = 0
		pa_sum = 0
		PF_num = 0
		PA_num = 0
		num = 0
		wt_sum = sum(weights)
		wts_sqrd_sum = sum(wts_sqrd)
		denom = wt_sum - (wts_sqrd_sum / wt_sum)


		for index, score in enumerate(points_for):
			pf_sum += weights[index] * points_for[index]
			pa_sum += weights[index] * points_against[index] 

		PF_avg = pf_sum / wt_sum
		PA_avg = pa_sum / wt_sum

		for index, score in enumerate(points_for):
			PF_num += weights[index] * (points_for[index] - PF_avg) ** 2
			PA_num += weights[index] * (points_against[index] - PA_avg) ** 2

		PF_SD = sqrt(PF_num / denom)
		PA_SD = sqrt(PA_num / denom)


		# Update teams DB with PF_avg and PA_avg
		cursor.execute("UPDATE teams SET avg_pf = %s, avg_pa = %s, sd_pf = %s, sd_pa = %s WHERE team = %s", (PF_avg, PA_avg, PF_SD, PA_SD, team))

	# Commit changes to database
	conn.commit()

	
def style():
	""" Award style points to all teams, regardless of outcome """

	# Get game data for games which have not yet been "styled" 
	# Style points remain the same throughout the season, they only need to be calculated twice
	cursor.execute("SELECT * FROM games WHERE winning_style IS NULL")
	rows = cursor.fetchall()

	for index, row in enumerate(rows):
		team1 = rows[index][0]
		team2 = rows[index][2]
		score1 = rows[index][1]
		score2 = rows[index][3]
		location = rows[index][5]
		game_date = rows[index][4]

		team1conf = helpers.conf(team1)
		team2conf = helpers.conf(team2)
		team1tier = helpers.tier(team1)
		team2tier = helpers.tier(team2)




		######################################
		# Point stucture is as follows:

		# Points for winning the game: 

		# Win game 						10 pts


		# Points for how a team played:
		# These can be won by either team, provided neither team is in the 'Lower' tier

		# Score 40 or more				1  pts
		# Score 50 or more 				1  pts
		# Hold them to 20 or less 		1  pts
		# Hold them to 10 or less 		1  pts
		# Shut them out 				3  pts
		# Win by 20 					1  pts
		# Win by 30 					1  pts
		# Win by 40 					1  pts

		# The only criteria that results in a loss of points: 

		# Lose to lower 'level' team   -5  pts

		# College football games cannot end in a tie.

		######################################

		

		# Points for each game are the summation of all point-awarding criteria. 
		# Teams can also earn points in a loss.

		# Initialize "points"
		# By default, team1 is always the winner of the game.
		team1_style = 10
		team2_style = 0

		# As stated above, these style points can only be earned in wins over G5 or P5 teams:
		if team2tier != 'Lower':
			if helpers.winby20(score1, score2):
				team1_style += 1

			if helpers.winby30(score1, score2):
				team1_style += 1

			if helpers.winby40(score1, score2):
				team1_style += 1

			if helpers.score40(score1):
				team1_style += 1

			if helpers.score40(score2):
				team2_style += 1

			if helpers.score50(score1):
				team1_style += 1

			if helpers.score50(score2):
				team2_style += 1

			if helpers.hold20(score1):
				team2_style += 1

			if helpers.hold10(score1):
				team2_style += 1

			if helpers.hold20(score2):
				team1_style += 1

			if helpers.hold10(score2):
				team1_style += 1

		# These points can be won by teams at any tier
		if helpers.shutout(score2):
			team1_style += 3

		if helpers.roadwin(location):
			team1_style += 2

		if helpers.lowerloss(team2, team1):
			team1_style -= 5

		# Update games database with game data
		if team1tier != 'Lower':
			cursor.execute("UPDATE games SET winning_style = %s WHERE game_date = %s AND winning_team = %s", (team1_style, game_date, team1))

		if team2tier != 'Lower':
			cursor.execute("UPDATE games SET losing_style = %s WHERE game_date = %s AND losing_team = %s", (team2_style, game_date, team2))

	# Commit changes to database
	conn.commit()



def SOR():
	""" 
	Calculate a weighting factor for a team's performance based on the perceived strength of the opponent.
	SOR is revisited after every week, unlike style, or performance, which are updated only for the new games added. 
	"""

	cursor.execute("SELECT * FROM games WHERE winning_style IS NOT NULL")
	rows = cursor.fetchall()

	for index, row in enumerate(rows):

		# Extract game data from rows
		# By default team1 is the winning team
		team1 = rows[index][0]
		team2 = rows[index][2]
		date = rows[index][4]

		team1conf = helpers.conf(team1)
		team2conf = helpers.conf(team2)
		team1tier = helpers.tier(team1)
		team2tier = helpers.tier(team2)

		if team1tier == 'Lower':
		    team1rank = 129
		else:
		    cursor.execute("SELECT rank FROM teams WHERE team = %s", (team1,))
		    team1rank_list = cursor.fetchone()
		    team1rank = team1rank_list[0]
		    if team1rank == None:
		        team1rank = 128

		if team2tier == 'Lower':
		    team2rank = 129
		else:
		    cursor.execute("SELECT rank FROM teams WHERE team = %s", (team2,))
		    team2rank_list = cursor.fetchone()
		    team2rank = team2rank_list[0]
		    if team2rank == None:
		        team2rank = 128


		# Determine the Strength of Record for each performance
		if team2tier == 'G5':
		    # A team gets 0.5 for beating a G5 school
		    team1SOR = 1.5
		    # A team will get additional points for beating a team that is in the top 25 and/or is higher ranked
		    if helpers.beattop25(team2rank):
		        team1SOR += 0.5
		    if helpers.beathigherranked(team1rank, team2rank):
		        team1SOR += 0.5
		elif team2tier == 'P5':
		    # A team gets 1 for beating a P5 school
		    team1SOR = 2
		    if helpers.beattop25(team2rank):
		        team1SOR += 0.5
		    if helpers.beathigherranked(team1rank, team2rank):
		        team1SOR += 0.5
		else:
		    # If a team beats a Lower tier school the multiplier is limited to 1. 
		    team1SOR = 1

		# Same thing goes for team2, however, by definition they are the losers, so the 'beat' functions are not executed. 
		if team1tier == 'G5':
		    team2SOR = 1.5
		elif team1tier == 'P5':
		    team2SOR = 2
		else: 
		    team2SOR = 1


		# Append the game DataFrame with SOR data 
		cursor.execute("UPDATE games SET winning_sor = %s WHERE winning_team = %s AND game_date = %s", (team1SOR, team1, date))
		cursor.execute("UPDATE games SET losing_sor = %s WHERE losing_team = %s AND game_date = %s", (team2SOR, team2, date))

	# Commit changes to database
	conn.commit()




def points():
	""" Calculate the number a points a team should earn for their performance based on style and SOR """

	cursor.execute("SELECT * FROM games")
	rows = cursor.fetchall()

	for index, row in enumerate(rows):

	    # Get critical game information
	    team1 = row[0]
	    team2 = row[2]
	    date = row[4]

	    if team1 not in settings.fbs_teams:
	        total_1 = 0
	    else:
	        if team2 not in settings.fbs_teams:
	            total_2 = 0
	        else: 
	            # Get the style points for the game
	            team1_style = row[6]
	            team2_style = row[7]

	            # Get SOR for the game
	            team1_sor = row[8]
	            team2_sor = row[9]

	            
	            # Calculate game totals for each team
	            total_1 = row[6] * row[8]
	            total_2 = row[7] * row[9]
	            
	        # Update database with totals
	        if team1 in settings.fbs_teams:
	            cursor.execute("UPDATE games SET winning_total = %s WHERE winning_team = %s AND game_date = %s", 
	                            (total_1, team1, date))
	        if team2 in settings.fbs_teams:
	            cursor.execute("UPDATE games SET losing_total = %s WHERE winning_team = %s AND game_date = %s", 
	                            (total_2, team1, date))

	# Commit changes to database
	conn.commit()


	# Update a team's points in the teams database
	for each_team in teamlist.teams:
	    team = each_team['team']

	    cursor.execute("SELECT SUM(winning_total) FROM games WHERE winning_team = %s", (team,))
	    winning_points_list = cursor.fetchone()
	    winning_points = winning_points_list[0]

	    if winning_points == None:
	        winning_points = 0

	    cursor.execute("SELECT SUM(losing_total) FROM games WHERE losing_team = %s", (team,))
	    losing_points_list = cursor.fetchone()
	    losing_points = losing_points_list[0]

	    if losing_points == None:
	        losing_points = 0

	    team_points = winning_points + losing_points

	    # Update the database with a team's total
	    cursor.execute("UPDATE teams SET points = %s WHERE team = %s", (team_points, team))

	conn.commit()




def rank():
	""" Rank all teams in teams databse based on the number of points they have at this point. """

	cursor.execute("SELECT * FROM teams")
	rows = cursor.fetchall()

	teams_list = []

	for index, row in enumerate(rows):
		team = row[0]
		points = row[3]

		# Create a dict to hold each team's name and the amount of points they have accumulated up until now
		data = {
		"team": team, 
		"points": points
		}

		# Append the teams data to the points list
		teams_list.append(data)

	# Once the full points list is complete, sort by points in descending order 
	ranks = sorted(teams_list, key = lambda k: k['points'], reverse = True)

	# Update the ranks list with the rank of the team at this point
	for index, row in enumerate(ranks):
		rank = index + 1
		ranks[index].update({"rank": rank})

	# Once the ranks have been assigned, update teams database with the current ranks
	for index, row in enumerate(ranks):
		team = ranks[index]["team"]
		rank = ranks[index]["rank"]
		cursor.execute("UPDATE teams SET rank = %s WHERE team = %s", (rank, team))

	# Commit changes to database
	conn.commit()

'''
def sos():
	"""Compile a team's strength of schedule and rank"""


	# Create an empty list
	teams_points = []

	# Get all teams points
	for team in settings.fbs_teams:
		cursor.execute("SELECT points FROM teams WHERE team = %s", (team,))
		points = cursor.fetchone()

		data = {
			'team': team,
			'points': points
		}

		teams_points.append(data)

	# Compile the SOS points for each team
	for team in settings.fbs_teams:

		# Create an empty list to hold game dicts
		opponents_points = []

		cursor.execute("SELECT losing_team FROM games WHERE winning_team = %s", (team,))
		rows = cursor.fetchall()

		# Get the data for games where team won
		for row in rows:
			# print(row)
			data = {
				'team': team,
				'points': row[3]
			}

			opponents_points.append(data)

		cursor.execute("SELECT winning_team FROM games WHERE losing_team = %s", (team,))
		rows = cursor.fetchall()

		# Get the data for games where team lost
		for row in rows:
			data = {
				'team': team,
				'points': row[3]
			}

			opponents_points.append(data)

		# Initialize SOS variable
		sos = 0 

		for row in opponents_points:
			sos += row['points']

		data = {
			'team': team,
			'sos':  sos
		}

		teams_points.append(data)

	ranks = sorted(teams_points, key = lambda k: k['sos'], reverse = True)

	for index, row in enumerate(ranks):
		rank = index + 1
		ranks[index].update({"rank": rank})

	for team in teams_points:
		team = teams_points['team']
		sos = teams_points['rank']
		cursor.execute("UPDATE teams SET sos = %s WHERE team = %s", (sos, team))

	conn.commit()
'''




####### All app routes are held below to be handled by flask #######
 

@app.route('/', methods=['GET'])
def top_25():
	""" 
	This route will display a table of the top 25 FBS teams and their records, ranks, and scores. 
	This is the default routing when visiting the web page
	"""

	cursor.execute("SELECT * FROM teams WHERE rank <= '25'")
	rows = cursor.fetchall()

	rows.sort(key=lambda x: x[4])
	
	return render_template("teams.html", rankings = rows, updated = updated)




@app.route('/update', methods=['GET'])
def update():
	""" Update all databases with data from the most recent games and recalculate the necessary stats """

	# Get today's date 
	global updated
	updated = arrow.now().format('YYYY-MM-DD')

	# Carry out these functions to update all the various data after the most recent games
	games()
	performance()
	style()
	SOR()
	points()
	rank()
	# sos()

	# Once complete, redirect the user to the page displaying the current top 25 
	return redirect('/')





@app.route('/teams', methods=['GET', 'POST'])
def all_teams():
	""" This route will display a table of all 128 FBS teams and their records, ranks, and scores. """

	cursor.execute("SELECT * FROM teams")
	rows = cursor.fetchall()

	rows.sort(key=lambda x: x[4])
	
	return render_template("teams.html", rankings = rows, updated = updated)




@app.route('/games', methods=['GET', 'POST'])
def all_games():
	""" This route will display all game data up until this point in the season that the code is executed. """

	cursor.execute("SELECT * FROM games")
	rows = cursor.fetchall()

	rows.sort(key = lambda x: x[4])

	return render_template("games.html", games = rows, updated = updated)




@app.route('/chart', methods=['GET', 'POST'])
def chart():
	""" This route will generate a bar graph to graphically depict the score breakdown of the top 25 """

	#plot = top_25.plot.barh(x='Team', y='Points')
	#fig.savefig("plot.png")

	return render_template("chart.html")




@app.route('/method', methods=['GET'])
def method():
	""" This route will display the poll methodology document """

	return render_template("method.html")




@app.route('/predict', methods=['GET', 'POST'])
def predict():
	""" This route will predict the outcome of a matchup between two teams """

	# if a user clicked a link to get here, render the empty page and allow them to select the two teams
	if request.method == "GET": 

		return render_template("predict.html", fbs_teams = settings.fbs_teams)

	# Once the user has submitted the forms with their two teams to compare
	else: 

		
		class outcome:
			def __init__(self, team1, team2, favored, prob, spread):
				self.team1 = team1
				self.team2 = team2
				self.favored = favored
				self.probability = prob
				self.spread = spread


		class team:
			def __init__(self, PF_avg, PF_SD, PA_avg, PA_SD):
				self.PF_avg = PF_avg
				self.PF_SD = PF_SD
				self.PA_avg = PA_avg
				self.PA_SD = PA_SD

		team1 = request.form.get("team1")
		team2 = request.form.get("team2")

		# Ensure that the user selected two different teams
		if team1 == team2:
			error = "Cannot predict the outcome of a team versus itself."
			return render_template("error.html", Error = error)

		# Get the performance stats for both teams
		cursor.execute("SELECT * FROM teams WHERE team = %s", (team1,))
		rows = cursor.fetchone()

		team1_PF_avg = round(rows[5], 1)
		team1_PF_SD = round(rows[6], 1)
		team1_PA_avg = round(rows[7], 1)
		team1_PA_SD = round(rows[8], 1)
		team1_points = rows[3]

		cursor.execute("SELECT * FROM teams WHERE team = %s", (team2,))
		rows = cursor.fetchone()

		team2_PF_avg = round(rows[5], 1)
		team2_PF_SD = round(rows[6], 1)
		team2_PA_avg = round(rows[7], 1)
		team2_PA_SD = round(rows[8], 1)
		team2_points = rows[3]

		# Create team objects for html page rendering
		team1_obj = team(team1_PF_avg, team1_PF_SD, team1_PA_avg, team1_PA_SD)
		team2_obj = team(team2_PF_avg, team2_PF_SD, team2_PA_avg, team2_PA_SD)

		# Calculate the x' ratio for the two teams, remember which team is favored
		if team1_points == team2_points or team1_points > team2_points:
			X = team1_points / team2_points 
			favored = team1
		else:
			X = team2_points / team1_points
			favored = team2


		# Calculate the probability that the favored team will win.
		# k is the steepness of the logistic curve. This is obtained from a fit of historical data.
		k = -1.09
		y = 0.735
		prob = round(100 * (1 / (1 + exp(k * (X - y)))), 2)

		# Calculate the projected spread
		# b is the slope of a fit line. This is obtained from a fit of historical data
		b = 4.38
		spread = round(b * X, 1)

		# Create an object with all the necessary attributes to render the webpage
		outcome_obj = outcome(team1, team2, favored, prob, spread)

		# Render the predicted template
		return render_template("predicted.html", results = outcome_obj, team1 = team1_obj, team2 = team2_obj)



@app.route("/team/<team>", methods = ['GET', 'POST'])
def team(team):
	''' Display the performance of a team so far this season '''

	team_str = str(team)

	if team_str not in settings.fbs_teams:
		error = "The team you selected is an FCS team. This site only tracks FBS teams"
		return render_template("error.html", Error = error)

	class team_data:
		def __init__(self, team, wins, losses, rank, points, conference, avg_pf, avg_pa):
			self.team = team
			self.wins = wins
			self.losses = losses
			self.rank = rank
			self.points = points
			self.conference = conference
			self.avg_pf = avg_pf
			self.avg_pa = avg_pa


	# Create an empty list to hold game objects
	games_list = []

	# Select the team's results so far this season
	cursor.execute("SELECT * FROM teams WHERE team = %s", (team,))
	team_info = cursor.fetchone()

	wins = team_info[1]
	losses = team_info[2]
	rank = round(team_info[4])
	points = team_info[3]
	conference = team_info[9]
	avg_pf = team_info[5]
	avg_pa = team_info[7]

	team_obj = team_data(team, wins, losses, rank, points, conference, avg_pf, avg_pa)

	# Select the team's record so far this season, both wins and losses
	cursor.execute("SELECT * FROM games WHERE winning_team = %s", (team,))
	team_win_info = cursor.fetchall()

	for row in team_win_info:

		opponent = row[2]

		cursor.execute("SELECT rank FROM teams WHERE team = %s", (opponent,))
		op_rank_list = cursor.fetchone()
		if op_rank_list == None:
			op_rank = 129
		else: 
			op_rank = round(op_rank_list[0])

		data = {
			"date": row[4],
			"opponent": row[2],
			"points_for": row[1],
			"points_against": row[3],
			"outcome": "W",
			"opponent_rank": op_rank
		}

		games_list.append(data)
	

	cursor.execute("SELECT * FROM games WHERE losing_team = %s", (team,))
	team_loss_info = cursor.fetchall()
	
	for row in team_loss_info:

		opponent = row[0]

		cursor.execute("SELECT rank FROM teams WHERE team = %s", (opponent,))
		op_rank_list = cursor.fetchone()
		if op_rank_list == None:
			op_rank = 129
		else: 
			op_rank = round(op_rank_list[0])

		data = {
			"date": row[4],
			"opponent": row[0],
			"points_for": row[3],
			"points_against": row[1],
			"outcome": "L",
			"opponent_rank": op_rank
		}	

		games_list.append(data)

	# Sort the list of games by date
	games_list_sorted =sorted(games_list, key = lambda k: k['date'])

	# Render the team template with the necessary team info
	return render_template("team.html", team = team_obj, game_list = games_list_sorted)





@app.route("/conference/<conference>", methods = ['GET'])
def conference(conference):
	''' Display the rankings of all members of a conference '''

	cursor.execute("SELECT * FROM teams WHERE conference = %s", (conference,))
	rows = cursor.fetchall()

	rows.sort(key=lambda x: x[4])
	
	return render_template("teams.html", rankings = rows, updated = updated, conference = conference)



	
@app.route("/search", methods = ['POST'])
def search():
	''' Allow the user to type in the name of a team in the search bar and get their information '''

	search_team = request.form.get("search_team")

	if search_team not in settings.fbs_teams:
		error = "Please enter a valid FBS team name"
		return render_template("error.html", Error = error)

	else:
		return redirect(url_for('team', team = search_team))
	



@app.route("/compare/<poll>", methods = ['GET'])
def compare(poll):
	''' Compare the results of the poll to other established polls in the sport '''

	# This is the first sunday of the cfb season. All weeks following this will end on a sunday.
	day1 = datetime.date(2018, 9, 2)

	# This is commented out. No longer needed as the season has ended. 

	# # Get today's date 
	# now = datetime.date.today()

	# # Calculate the most recent week of the season that rankings will have been published
	# # This will be passed to the ESPN api
	# delta = now - day1
	# weeks = ceil((delta.days / 7) + 1)

	weeks = 12


	# Compile the url for the ESPN rankings API
	url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/rankings?"
	params = {"seasons": 2018, "weeks": 1, "types": 2}

	new_url = url + urllib.parse.urlencode(params)

	# Begin parsing API output
	with urllib.request.urlopen(new_url) as url:
		data = json.loads(url.read().decode())
		data_json = json.dumps(data, indent=4)
		data_dict = json.loads(data_json)
		rankings = data_dict["rankings"]

	# Create an empty list to hold data
	poll_ranks = []

	# Get the top 25 of Zach's poll
	cursor.execute("SELECT * FROM teams WHERE rank <= 25")
	zachs_poll = cursor.fetchall()

	zachs_poll.sort(key=lambda x: x[4])

	# Get the top 25 of the chosen poll
	if poll == 'CFP Rankings':

		try:
			ranks = rankings[0]
		except: 
			error = "CFP Rankings data not yet available"
			return render_template("error.html", Error = error)

		form_ranks = json.dumps(ranks, indent=4)
		form_ranks_dict = json.loads(form_ranks)
		all_ranks = form_ranks_dict["ranks"]

		for i in range(25):
			team = all_ranks[i]["team"]["location"]
			poll_ranks.append(team)

	elif poll == 'AP Poll':
		
		try:
			ranks = rankings[1]
		except:
			error = "AP Poll data not yet available"
			return render_template("error.html", Error = error)

		form_ranks = json.dumps(ranks, indent=4)
		form_ranks_dict = json.loads(form_ranks)
		all_ranks = form_ranks_dict["ranks"]

		for i in range(25):
			team = all_ranks[i]["team"]["location"]
			poll_ranks.append(team)

	elif poll == 'Coaches Poll':

		try: 
			ranks = rankings[2]
		except:
			error = "Coaches Poll data not yet available"
			return render_template("error.html", Error = error)
		form_ranks = json.dumps(ranks, indent=4)
		form_ranks_dict = json.loads(form_ranks)
		all_ranks = form_ranks_dict["ranks"]

		for i in range(25):
			team = all_ranks[i]["team"]["location"]
			poll_ranks.append(team)


	comparison = []

	for i in range(25):
		team = {
			"rank": i + 1,
			"zachs": zachs_poll[i][0],
			"other": poll_ranks[i]
		}

		comparison.append(team)


	# Render this data in a template
	return render_template("compare.html", Poll = poll, table = comparison)




if __name__ == '__main__':
    app.run()







