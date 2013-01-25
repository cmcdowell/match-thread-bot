#!usr/bin/env python

# Special cases, where the team name does not fit the pattern in
# the Guardian's urls.
CHANGES = [('West Bromwich Albion', 'westbrom'),
           ('Manchester United', 'manchester-united'),
           ('Tottenham Hotspur', 'tottenham-hotspur'),
           ('FSV Mainz 05', 'fsvmainz'),
           ('Swansea City', 'swansea'),
           ('Queens Park Rangers', 'qpr'),
           ('Aston Villa', 'aston-villa'),
           (u'M\xe1laga CF', 'malaga'),
           ('FC Barcelona', 'barcelona'),
           (u'Atl\u00E9tico Madrid', 'atleticomadrid'),
           ('VfL Wolfsburg', 'wolfsburg'),
           ('VfB Stuttgart', 'stuttgart'),
           ('Shalke 04', 'shalke'),
           ('AS Roma', 'roma'),
           ('SC Freiburg', 'freiburg'),
           ('Getafe CF', 'getafe'),
           ('Valencia CF', 'valencia'),
           (u"Borussia M\u2019gladbach", 'borussiamoenchengladbach'),
           ('RCD Mallorca', 'realmallorca'),
           ('Sevilla FC', 'sevilla'),
           ('Hamburger SV', 'hamburg'),
           (u'1. FC N\u00FCrnberg', 'nurnberg'),
           ('SC Freiburg', 'freiburg'),
           ('Schalke 04', 'schalke'),
           ('Levante UD', 'levante')]

# How many minutes each reddit thread is updated for.
MATCH_LENGTH = 130

# The number of minutes before kick off a thread is supposed
# to be posted.
PRE_KICK_OFF = 5

SUBREDDIT = 'soccer'
