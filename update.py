# This is a file to update data as needed for each week as well as for the new season

# Import the needed files in the project directory.
import teamlist
import tables
import analyze
import data



def update_weekly(year):
	'''This is a function to update all of the tables with the latest data. '''

	data.games(year)
	print("Games retrieved. Calculating performance...")
	data.performance(year)
	print("Performance done. Calculating style...")
	data.style(year)
	print("Style done. Calculating SOR...")
	data.SOR(year)
	print("SOR done. Awarding points...")
	data.points(year)
	print("Points done. Ranking...")
	data.rank()
	print("Ranks done. Storing data in history...")
	data.store_week()
	print("Data stored. Generating plot...")
	analyze.top25_plot()
	print("Done. Visit https://zachs-cfb-rankings.herokuapp.com")

	return



def update_yearly():
	''' This is a function to update all of the tables for the new season while storing historical data.'''

	# tables.populate_teams()
	# tables.conferences()

	pass



if __name__ == '__main__':
	
	update_weekly(2019)