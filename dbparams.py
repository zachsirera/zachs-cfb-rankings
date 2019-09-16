import psycopg2


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
		# Establish a cursor to navigate the database
		conn = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
	except:
		print("Database connection not made")

	return conn