# This script creates a table in the database to hold teams data

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


cur.execute("""CREATE TABLE teams(
    team text PRIMARY KEY,
    wins int,
    losses int,
    points real,
    SOR real,
    rank real,
    avg_pf real,
    sd_pf real,
    avg_pa real,
    sd_pa real
	)
	""")
conn.commit()

def populate_teams():
    """ populate teams table with list of fbs teams """
    for team in settings.fbs_teams:
        cursor.execute("SELECT * FROM teams WHERE team = %s", (team,))
        cursor.fetchall()

        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO teams (team) VALUES (%s)", (team,))
            conn.commit()

