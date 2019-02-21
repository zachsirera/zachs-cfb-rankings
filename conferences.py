# This is a program to rank FBS football teams and predict the outcomes of their matchups
# Zach Sirera

# import the necessary packages
import arrow
import requests
import psycopg2

# import support files in the project directory 
import helpers
import settings
import teamlist

# import other modules from packages that are needed
from lxml import html
from flask import Flask, render_template, session, request, redirect, url_for 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from math import exp, sqrt


# Necessary flask declaration
app = Flask(__name__) 

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

# Set up database
engine = create_engine(url)
db = scoped_session(sessionmaker(bind=engine))

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