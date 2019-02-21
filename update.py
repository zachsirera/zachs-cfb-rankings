# This is a program to udpdate the teams and games databases with all necessary data.
# This will be scheduled in the future, so updates can be administered automatically.

from app import update
from twilio.rest import Client

# Update the teams and games databases
try:
	update()

	account_sid = "AC140510f2c06269fc388c0ed7453482ed"
	auth_token  = "21fb039f77f28b66df4d9ee12f26ff90"

	client = Client(account_sid, auth_token)

	message = client.messages.create(
	    to="+19857786225", 
	    from_="+19852009526",
	    body="Zach's CFB Poll has been updated")

except:
	account_sid = "AC140510f2c06269fc388c0ed7453482ed"
	auth_token  = "21fb039f77f28b66df4d9ee12f26ff90"

	client = Client(account_sid, auth_token)

	message = client.messages.create(
	    to="+19857786225", 
	    from_="+19852009526",
	    body="There was an error updating Zach's CFB Poll")


update()