# This is an extension of both app.py and helpers.py containing the necessary lists 



fbs_teams = [ 'Air Force', 'Akron', 'Alabama', 'UAB', 'Appalachian St', 'Arizona', 'Arizona St',
'Arkansas', 'Arkansas St', 'Army', 'Auburn', 'Ball St', 'Baylor', 'Boise St', 'Boston College',
'Bowling Green', 'Buffalo', 'BYU', 'California', 'UCLA', 'UCF','C Michigan', 'Charlotte', 'Cincinnati',
'Clemson', 'Coastal Car', 'Colorado', 'Colorado St', 'Connecticut', 'Duke', 'E Michigan', 'East Carolina',
'Florida Intl', 'Florida', 'FL Atlantic', 'Florida St', 'Fresno St', 'Georgia', 'Ga Southern', 'Georgia St', 
'Georgia Tech', 'Hawaii', 'Houston', 'Illinois', 'Indiana', 'Iowa', 'Iowa St', 'Kansas', 'Kansas St', 
'Kent', 'Kentucky', 'LSU', 'Louisiana Tech', 'ULL', 'ULM', 'Louisville', 'Marshall', 'Maryland', 
'Massachusetts', 'Memphis', 'Miami FL', 'Miami OH', 'Michigan', 'Michigan St', 'MTSU', 'Minnesota', 
'Mississippi', 'Mississippi St', 'Missouri', 'Navy', 'Nebraska', 'Nevada', 'UNLV', 'New Mexico', 
'New Mexico St', 'North Carolina', 'NC State', 'North Texas', 'N Illinois', 'Northwestern', 
'Notre Dame', 'Ohio', 'Ohio St', 'Oklahoma', 'Oklahoma St', 'Old Dominion', 'Oregon', 'Oregon St', 
'Penn St', 'Pittsburgh', 'Purdue', 'Rice', 'Rutgers', 'San Diego St',  'San Jose St', 'South Alabama', 
'South Carolina', 'South Florida', 'USC', 'SMU', 'Southern Miss', 'Stanford', 'Syracuse','TCU', 'Temple', 
'Tennessee', 'Texas', 'Texas A&M', 'Texas St', 'Texas Tech', 'UT San Antonio', 'Toledo', 'Troy', 'Tulane',
'Tulsa', 'Utah', 'Utah St', 'Vanderbilt', 'Virginia', 'Virginia Tech', 'Wake Forest', 'Washington', 
'Washington St', 'West Virginia', 'WKU', 'W Michigan', 'Wisconsin', 'Wyoming']

# And their conferences (in order of fbs_teams above)
conferences = ['Mountain West', 'MAC', 'SEC', 'C-USA', 'Sun Belt', 'Pac-12', 'Pac-12', 'SEC', 'Sun Belt', 
'Independent', 'SEC', 'MAC', 'Big 12', 'Mountain West', 'ACC', 'MAC', 'MAC', 'Independent', 'Pac-12', 
'Pac-12', 'American', 'MAC', 'C-USA', 'American', 'ACC', 'Sun Belt', 'Pac-12', 'Mountain West', 
'American', 'ACC', 'MAC', 'American', 'C-USA', 'SEC', 'C-USA', 'ACC', 'Mountain West', 'SEC', 
'Sun Belt', 'Sun Belt', 'ACC', 'Mountain West', 'American', 'Big Ten', 'Big Ten', 'Big Ten', 
'Big 12', 'Big 12', 'Big 12', 'MAC', 'SEC', 'SEC', 'C-USA', 'Sun Belt', 'Sun Belt', 'ACC', 'C-USA', 
'Big Ten', 'Independent', 'American', 'ACC', 'MAC', 'Big Ten', 'Big Ten', 'C-USA', 'Big Ten', 'SEC', 
'SEC', 'SEC', 'American', 'Big Ten', 'Mountain West', 'Mountain West', 'Mountain West', 'Independent', 
'ACC', 'ACC', 'C-USA', 'MAC', 'Big Ten', 'Independent', 'MAC', 'Big Ten', 'Big 12', 'Big 12', 'C-USA', 
'Pac-12', 'Pac-12', 'Big Ten', 'ACC', 'Big Ten', 'C-USA', 'Big Ten', 'Mountain West', 'Mountain West', 
'Sun Belt', 'SEC', 'American', 'Pac-12', 'American', 'C-USA', 'Pac-12', 'ACC', 'Big 12', 'American', 
'SEC', 'Big 12', 'SEC', 'Sun Belt', 'Big 12', 'C-USA', 'C-USA', 'MAC', 'Sun Belt', 'American', 
'American', 'Mountain West', 'SEC', 'ACC', 'ACC', 'ACC', 'Pac-12', 'Pac-12', 'Big 12', 
'C-USA', 'MAC', 'Big Ten', 'Mountain West']


# Create tiers for conferences
P5 = ['ACC', 'Big 12', 'Big Ten', 'Pac-12', 'SEC', 'Independent']
G5 = ['American', 'C-USA', 'MAC', 'Mountain West', 'Sun Belt']
# All other teams, FCS or lower, are treated as the same tier
# A team is only awarded the 10 points for beating a 'Lower' team and 2 points if shutout 


"""
# Create an ordered list of tiers for all fbs teams
tiers = []

for team in fbs_teams:
	teamtier = tier(team)
	tiers.ammend(teamtier)
"""


