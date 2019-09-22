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



# Connect to the database
conn = dbparams.db_connect()
cursor = conn.cursor()



# Get today's date
global updated
updated = arrow.now().format('YYYY-MM-DD')


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

		# Look for games that feature the winning team on the day played, ie only insert new games. 
		cursor.execute("SELECT * FROM games WHERE winning_team = %s AND game_date = %s", (team1, date))
		cursor.fetchall()

		# Add new games to games db.
		if cursor.rowcount == 0:
			cursor.execute("""INSERT INTO games (winning_team, winning_score, losing_team, losing_score, game_date, winning_location, year)
							VALUES (%s, %s, %s, %s, %s, %s, %s)""", (team1, score1, team2, score2, date, location, year))

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



def performance(year):
	""" Compile previous performance stats for each team """
	# These are reevaluated every week as averages change

	# year = 2019
	
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

		# Get the points for in a win
		cursor.execute("SELECT winning_score FROM games WHERE winning_team = %s AND year = %s", (team, year))
		rows = cursor.fetchall()
		count = cursor.rowcount
		for i in range(count):
			points_for.append(rows[i][0])


		# Get the points for in a loss
		cursor.execute("SELECT losing_score FROM games WHERE losing_team = %s AND year = %s", (team, year))
		rows = cursor.fetchall()
		count = cursor.rowcount
		for i in range(count):
			points_for.append(rows[i][0])


		# Get the points against in a win
		cursor.execute("SELECT losing_score FROM games WHERE winning_team = %s AND year = %s", (team, year))
		rows = cursor.fetchall()
		count = cursor.rowcount
		for i in range(count):
			points_against.append(rows[i][0])


		# Get the points against in a loss
		cursor.execute("SELECT losing_score FROM games WHERE losing_team = %s AND year = %s", (team, year))
		rows = cursor.fetchall()
		count = cursor.rowcount
		for i in range(count):
			points_against.append(rows[i][0])		

		# print(team, points_for, points_against)

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
		if denom == 0:
			denom = 1



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

	return




def style(year):
	""" Award style points to all teams, regardless of outcome """

	# year = 2019

	# Get game data for games which have not yet been "styled" 
	# Style points remain the same throughout the season, they only need to be calculated twice
	cursor.execute("SELECT * FROM games WHERE winning_style IS NULL AND year = %s", (year,))
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

	return





def SOR(year):
	""" 
	Calculate a weighting factor for a team's performance based on the perceived strength of the opponent.
	SOR is revisited after every week, unlike style, or performance, which are updated only for the new games added. 
	"""

	# year = 2019

	cursor.execute("SELECT * FROM games WHERE winning_style IS NOT NULL AND year = %s", (year,))
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

	return





def points(year):
	""" Calculate the number a points a team should earn for their performance based on style and SOR """

	# year = 2019

	cursor.execute("SELECT * FROM games WHERE year = %s", (year,))
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

	    cursor.execute("SELECT SUM(winning_total) FROM games WHERE winning_team = %s AND year = %s", (team, year))
	    winning_points_list = cursor.fetchone()
	    winning_points = winning_points_list[0]

	    if winning_points == None:
	        winning_points = 0

	    cursor.execute("SELECT SUM(losing_total) FROM games WHERE losing_team = %s AND year = %s", (team, year))
	    losing_points_list = cursor.fetchone()
	    losing_points = losing_points_list[0]

	    if losing_points == None:
	        losing_points = 0

	    team_points = winning_points + losing_points

	    # Update the database with a team's total
	    cursor.execute("UPDATE teams SET points = %s WHERE team = %s", (team_points, team))

	conn.commit()

	return





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

	return




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

	return



'''



def store_week():

	cursor.execute("SELECT MAX(week) FROM weekly")
	last_week = cursor.fetchone()

	if last_week[0] == None:
		this_week = 1
	else:
		this_week = last_week[0] + 1

	cursor.execute("SELECT * FROM teams WHERE rank <= '25'")
	rows = cursor.fetchall()

	for row in rows:

		cursor.execute("INSERT INTO weekly (team, wins, losses, points, rank, week) VALUES (%s, %s, %s, %s, %s, %s)", (row[0], row[1], 
						row[2], row[3], row[4], this_week))
	
	conn.commit()

	return


	