import string

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
           ('SC Freiburg', 'freiburg'),
           ('Schalke 04', 'schalke'),
           ('Levante UD', 'levante')]

TEMPLATE = string.Template("""
Kickoff: $GMT, $CET, $EST  \n
Venue: $venue  \n
Referee: $referee  \n
Attendance: $attendance  \n
  \n
[Reddit Stream](http://www.reddit-stream.com/comments/$id)
/r/soccer [chat room](http://webchat.freenode.net/?channels=#reddit-soccer)

***  \n

Lineups

**$home_team**  \n

$home_squad

  \n
**$away_team**  \n

$away_squad

***  \n

**Match Stats**  \n

score: $score  \n

$stats_string
\n

***  \n

**Match Events**
  \n
$events_string

\n
***  \n
^^I'm ^^a ^^bot ^^that ^^makes ^^compact ^^match ^^threads ^^[feedback?](http://www.reddit.com/message/compose/?to=match-thread-bot&subject=feedback)
""")


stats_string = """**%s**|Statistic|**%s**
--:|:--:|:--  \n"""

comment = """
Streaming links
[Wiziwig](http://www.wiziwig.tv/competition.php?part=sports&discipline=football)  \n
[livefootballol.tv](http://www.livefootballol.tv)  \n
[First Row Sports](http://www.thefirstrow.eu/sport/football.html)  \n
"""
