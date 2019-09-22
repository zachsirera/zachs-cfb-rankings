# This is a file to update data as needed for each week as well as for the new season

# Import the needed files in the project directory.
import teamlist
import tables
import analyze
import data



def update_weekly(year):
	'''This is a function to update all of the tables with the latest data. '''

	data.games(year)
	data.performance(year)
	data.style(year)
	data.SOR(year)
	data.points(year)
	data.rank()
	data.store_week()
	analyze.top25_plot()

	return



def update_yearly():
	''' This is a function to update all of the tables for the new season while storing historical data.'''

	# tables.populate_teams()
	# tables.conferences()

	pass



if __name__ == '__main__':
	
	update_weekly(2019)