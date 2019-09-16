# This is a file to hold all of the functions responsible for creating tables in the heroku database.
# Most of these functions may only be used once.

# Import the necessary modules
import psycopg2

# Import the support files in the project directory
import helpers
import teamlist
import settings
import dbparams


# Connect to the database
conn = dbparams.db_connect()
cur = conn.cursor()


####### The following functions are to make the tables needed to store the data for the app. #######




def make_teams():
    ''' This is a function to create the teams table to hold all data for each team in the FBS. '''

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




def make_games():
    ''' This is a function to create a table in the database to hold games data '''

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
    



def make_history():
    ''' This is a function to create a table in the database to hold historical data for the final Top 25 rankings at the end of the 
    season. '''

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




def make_weekly():
    ''' This is a function to create the weekly table to hold a weekly tracker of Top 25 '''

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




######### The following functions are to pre-populate the tables with necessary info. #########




def populate_teams():
    ''' This is a function to initially populate the teams table from the list at teamlist.py '''

    for row in teamlist.teams:
        team = row['team']
        cur.execute("SELECT * FROM teams WHERE team = %s", (team,))
        cur.fetchall()

        if cur.rowcount == 0:
            cur.execute("INSERT INTO teams (team) VALUES (%s)", (team,))
            conn.commit()

    return




def update_conferences():
    ''' This is a function to update the teams table with each team's conference data '''

    for row in teamlist.teams:
        team = row['team']
        conference = row['conference']
        
        cursor.execute("UPDATE teams SET conference = %s WHERE team = %s", (conference, team))

    conn.commit()

    return  




def wins_n_losses():
    ''' This is a function to update a teams wins and losses by cross referencing tables'''


    cur.execute("SELECT * FROM games WHERE year = %s", (2019,))
    rows = cur.fetchall()

    winners = []
    losers = []

    for row in rows:
        winners.append(row[0])
        losers.append(row[2])

    for team in winners:
        wins =  winners.count(team)
        cur.execute("UPDATE weekly SET wins = %s WHERE team = %s", (wins, team))

    for team in losers:
        losses = losers.count(team)
        cur.execute("UPDATE weekly SET losses = %s WHERE team = %s", (losses, team))

    conn.commit()

    return




def null_to_zero():
    '''This is a function to replace all null variables in the wins and losses columns with 0s. 

    Should have done this at the beginning.... Would have been easier. Will keep for next season. 
    '''

    cur.execute("SELECT * FROM teams")
    rows = cur.fetchall()

    for row in rows:
        team = row[0]
        wins = row[1]
        losses = row[2]

        if wins == None:
            new_wins = 0
        else:
            new_wins = wins

        if losses == None:
            new_losses = 0
        else:
            new_losses = losses

        cur.execute("UPDATE teams SET wins = %s, losses = %s WHERE team = %s", (new_wins, new_losses, team))


    conn.commit()

    return



