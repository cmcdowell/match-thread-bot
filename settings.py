#!usr/bin/env python

# Special cases, where the team name does not fit the pattern in
# the Guardian's urls.
CHANGES = [
    ('AS Roma', 'roma'),
    ('Aston Villa', 'aston-villa'),
    ('FC Barcelona', 'barcelona'),
    ('FSV Mainz 05', 'fsvmainz'),
    ('Getafe CF', 'getafe'),
    ('Hamburger SV', 'hamburg'),
    ('Hannover 96', 'hannover'),
    ('Levante UD', 'levante'),
    ('Manchester United', 'manchester-united'),
    ('Queens Park Rangers', 'qpr'),
    ('RCD Espanyol', 'espanyol'),
    ('RCD Mallorca', 'realmallorca'),
    ('SC Freiburg', 'freiburg'),
    ('SC Freiburg', 'freiburg'),
    ('Schalke 04', 'schalke'),
    ('Sevilla FC', 'sevilla'),
    ('Shalke 04', 'shalke'),
    ('Swansea City', 'swansea'),
    ('Tottenham Hotspur', 'tottenham-hotspur'),
    ('Valencia CF', 'valencia'),
    ('VfB Stuttgart', 'stuttgart'),
    ('VfL Wolfsburg', 'wolfsburg'),
    ('West Bromwich Albion', 'westbrom'),
    (u"Borussia M\u2019gladbach", 'borussiamoenchengladbach'),
    (u'1. FC N\u00FCrnberg', 'nurnberg'),
    (u'Atl\u00E9tico Madrid', 'atleticomadrid'),
    (u'M\xe1laga CF', 'malaga'),
]

# How many minutes each reddit thread is updated for.
MATCH_LENGTH = 130

# The number of minutes before kick off a thread is supposed
# to be posted.
PRE_KICK_OFF = 5

SUBREDDIT = 'soccer'
