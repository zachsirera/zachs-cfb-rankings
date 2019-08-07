# This script creates a table in the database to hold historical data for final Top 25 rankings

import psycopg2

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

print(host)
print(database)
print(user)
print(password)

# Establish connection to PostgreSQL database
try:
	conn = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
	# Establish a cursor to navigate the database
	cur = conn.cursor()
except:
	print("Database connection not made")

cur.execute("""CREATE TABLE history(
    team text PRIMARY KEY,
    wins int,
    losses int,
    points real,
    rank real,
    season real
    )
    """)
conn.commit()