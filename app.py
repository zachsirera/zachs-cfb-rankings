# This is a program to rank FBS football teams and predict the outcomes of their matchups
# Zach Sirera

# import the necessary packages
import requests
import psycopg2
import json
import urllib
import datetime
import arrow
import os

# import support files in the project directory 
import helpers
import settings
import teamlist
import dbparams

# import other modules from packages that are needed
from lxml import html
from flask import Flask, render_template, session, request, redirect, url_for 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from math import exp, sqrt, ceil



# Necessary flask declaration
app = Flask(__name__) 


# Connect to the database
conn = dbparams.db_connect()
cursor = conn.cursor()


# Get today's date
global updated
updated = arrow.now().format('YYYY-MM-DD')





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

	year = 2019
	label = "Top 25 - " + str(year)
	
	return render_template("teams.html", rankings = rows, updated = updated, label = label)





@app.route('/teams', methods=['GET', 'POST'])
def all_teams():
	""" This route will display a table of all 128 FBS teams and their records, ranks, and scores. """

	cursor.execute("SELECT * FROM teams")
	rows = cursor.fetchall()

	rows.sort(key=lambda x: x[4])

	year = 2019
	label = "All Teams - " + str(year)
	
	return render_template("teams.html", rankings = rows, updated = updated, label = label)




@app.route('/games', methods=['GET', 'POST'])
def all_games():
	""" This route will display all game data up until this point in the season that the code is executed. """

	year = 2019

	cursor.execute("SELECT * FROM games WHERE year = %s", (year,))
	rows = cursor.fetchall()

	rows.sort(key = lambda x: x[4])

	label = "All Games - " + str(year)

	return render_template("games.html", games = rows, updated = updated, label = label)




@app.route('/chart', methods=['GET', 'POST'])
def chart():
	""" This route will generate a bar graph to graphically depict the score breakdown of the top 25 """

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

	year = 2019

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
	cursor.execute("SELECT * FROM games WHERE winning_team = %s AND year = %s", (team, year))
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
	

	cursor.execute("SELECT * FROM games WHERE losing_team = %s AND year = %s", (team, 2019))
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

	year = 2019
	label = conference + " - " + str(year)
	
	return render_template("teams.html", rankings = rows, updated = updated, label = label)



	
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
	day1 = datetime.date(2019, 9, 1)

	# This is commented out. No longer needed as the season has ended. 

	# Get today's date 
	now = datetime.date.today()

	# Calculate the most recent week of the season that rankings will have been published
	# This will be passed to the ESPN api
	delta = now - day1
	weeks = ceil((delta.days / 7) + 1)


	# Compile the url for the ESPN rankings API
	url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/rankings?"
	params = {"seasons": 2019, "weeks": weeks, "types": 2}

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





@app.route("/history/<year>", methods=['GET'])
def history(year):

	cursor.execute("SELECT * FROM history WHERE year = %s", (year,))
	rows = cursor.fetchall()

	rows.sort(key=lambda x: x[4])

	label = str(year) + ' - Final Rankings'

	return render_template("teams.html", rankings = rows, label = label)





@app.route("/week/<week>", methods = ['GET'])
def week(week):

	cursor.execute("SELECT * FROM weekly WHERE week = %s", (week,))
	rows = cursor.fetchall()

	if len(rows) == 0:
		error = "No data available for this week."
		return render_template("error.html", Error = error)

	rows.sort(key=lambda x: x[4])

	year = 2019
	label = str(year) + " Season - Week " + str(week)

	week_obj = [int(week) - 1, int(week) + 1, int(week)]

	return render_template("teams.html", rankings = rows, label = label, week_obj = week_obj)






if __name__ == '__main__':
    app.run()







