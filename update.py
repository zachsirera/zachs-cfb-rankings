# This is a file to update data as needed for each week as well as for the new season

# Import the needed files in the project directory.
import app
import teamlist
import tables




def update_weekly(year):
	'''This is a function to update all of the tables with the latest data. '''

	app.games(year)
	app.performance(year)
	app.style(year)
	app.SOR(year)
	app.points(year)
	app.rank()
	app.store_week()

	return



def update_yearly():
	''' This is a function to update all of the tables for the new season while storing historical data.'''

	# tables.populate_teams()
	# tables.conferences()

	pass



update_weekly(2019)