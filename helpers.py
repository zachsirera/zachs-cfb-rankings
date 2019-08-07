# This is helpers.py, an extension of app.py containing the necessary functions to run rankings.py

import teamlist

# Create the necessary functions to determine how to award points. Point value and criteria picked arbitrarily.

def winby20(x, y):
	"""If a team wins by 20, they are awarded 2 points. 

	x is the score of the winning team, y is the score of the losing team 
	"""
	if x >= (y + 20):
		return True
	else:
		return False

def winby30(x, y):
	"""If a team wins by 30, they are awarded an additional 2 points.

	x is the score of the winning team, y is the score of the losing team
	"""
	if x >= (y + 30):
		return True
	else:
		return False

def winby40(x, y):
	"""If a team wins by 40, they are awarded an additional 2 points. 

	x is the score of the winning team, y is the score of the losing team
	"""
	if x >= (y + 40):
		return True	
	else:
		return False

def score40(x):
	"""If a team scores 40, they are awarded 2 points. 

	x is the score of the winning team
	"""
	if x >= 40:
		return True
	else: 
		return False

def score50(x):
	"""If a team scores 50, they are awarded an additional 2 points.

	x is the score of the winning team
	"""
	if x >= 50:
		return True
	else: 
		return False
 
def hold20(y):
	"""If a team gives up 20 or less, they are awarded 2 points.

	y is the score of the losing team
	"""	
	if y <= 20:
		return True
	else: 
		return False

def hold10(y):
	"""If a team gives up 10 or less, they are awarded an additional 2 points. 
	
	y is the score of the losing team 
	"""
	if y <= 10:
		return True
	else: 
		return False

def shutout(y):
	"""If a team shuts out their opponent, they are awarded 4 points. 
	
	y is the score of the losing team 
	"""
	if y == 0:
		return True
	else: 
		return False

def beathigherranked(a, b):
	"""If a team beats a team ranked higher than they are, they are awarded 10 points. 
	
	a is the rank of the winning team, b is the rank of the losing team
	"""
	if a < b:
		return True
	else: 
		return False

def beattop25(b):
	"""If a team beats a team in the top 25, regardless of the rank of the winning team, they are awarded 10 points. 

	b is the rank of the losing team
	"""
	if b <= 25:
		return True
	else: 
		return False

def roadwin(c):
	"""If a team beats a team on the road or neutral site, they are awarded 2 points 
	
	c is the location classifier of the winning team
	"""
	if c != " @":
		return True
	else: 
		return False

def tier(x):
	"""Return the team's conference tier
	
	x is the name of team
	"""
	team = teamlist.info(x)
	return team['tier']

def P5win(x):
	"""Determine if a team beat a P5 team

	x is name of the losing team
	"""
	if tier(x) == 'P5':
		return True
	else:
		return False

def G5win(x):
	"""Determine if a team beat a G5 team

	x is the name of the losing team
	"""
	if tier(x) == 'G5':
		return True
	else: 
		return False

def lowerwin(x):
	"""Determine if a team beat a lower tier team
	
	x is the name of the losing team
	"""
	if tier(x) == 'Lower':
		return True
	else: 
		return False

def lowerloss(x, y):
	"""Determine if a team lost to a lower tier team
	
	x is the name of the losing team, y is the name of the winning team
	"""
	if tier(x) == 'P5' and tier(y) == 'G5':
		return True
	if tier(x) == 'P5' and tier(y) == 'Lower':
		return True
	if tier(x) == 'G5' and tier(y) == 'Lower':
		return True
	else: 
		return False

def conf(x):
	"""Determine a teams conference

	x is the name of a team
	"""
	team = teamlist.info(x)
	return team['conference']

def db_connect():
	''' This is a function to connect to the PostgreSQL db'''

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

	try:
		conn = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
		# Establish a cursor to navigate the database
		cur = conn.cursor()
	except:
		print("Database connection not made")

	return cur





