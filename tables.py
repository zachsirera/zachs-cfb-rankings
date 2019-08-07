# This is a file to hold all of the functions responsible for creating tables in the heroku database.
# Most of these functions may only be used once.

# Import the necessary modules
import psycopg2

# Import the support files in the project directory
import helpers
import teamlist
import settings







def games():
    ''' This is a function to create a table in the database to hold games data '''

    # Establish connection to PostgreSQL database
    try:
    	conn = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
    	# Establish a cursor to navigate the database
    	cur = conn.cursor()
    except:
    	print("Database connection not made")

    # Create desired table
    cur.execute("""CREATE TABLE games(
        winning_team text,
        winning_score int,
        losing_team text,
        losing_score int,
        game_date date,
        winning_location text,
        winning_style real,
        losing_style real,
        winning_sor real,
        losing_sor real,
        winning_total real,
        losing_total real
    	)
    	""")
    conn.commit()

    return
    




def history():
    ''' This is a function to create a table in the database to hold historical data for the final Top 25 rankings at the end of the 
    season. '''

    # Establish connection to PostgreSQL database
    try:
        conn = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
        # Establish a cursor to navigate the database
        cur = conn.cursor()
    except:
        print("Database connection not made")

    # Create desired table
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

    return  





def conferences():
    ''' This is a function to update the teams table with each team's conference data '''

    import teamlist

    # Establish connection to PostgreSQL database
    try:
        conn = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
    except:
        print("Database connection not made")

    # Establish a cursor to navigate the database
    cursor = conn.cursor()



    for row in teamlist.teams:
        team = row['team']
        conference = row['conference']
        
        cursor.execute("UPDATE teams SET conference = %s WHERE team = %s", (conference, team))

    conn.commit()

    return  





def teams():
    ''' This is a function to create the teams table to hold all data for each team in the FBS. '''

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

    return




def populate_teams():
    ''' This is a function to initially populate the teams table from the list at teamlist.py '''

    import settings

    for team in settings.fbs_teams:
        cursor.execute("SELECT * FROM teams WHERE team = %s", (team,))
        cursor.fetchall()

        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO teams (team) VALUES (%s)", (team,))
            conn.commit()

    return



def weekly():
    ''' This is a function to create the weekly table to hold a weekly tracker of Top 25 '''

    # Establish connection to PostgreSQL database
    try:
        conn = psycopg2.connect(f"host={host} dbname={database} user={user} password={password}")
        # Establish a cursor to navigate the database
        cur = conn.cursor()
    except:
        print("Database connection not made")

    cur.execute("""CREATE TABLE weekly(
        team text PRIMARY KEY,
        wins int,
        losses int,
        points real,
        rank real,
        week real
        )
        """)
    conn.commit()

    return









