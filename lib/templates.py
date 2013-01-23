#!usr/bin/env python
import string


template = string.Template("""
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

comment = """
Streaming links \n
[Wiziwig](http://www.wiziwig.tv/competition.php?part=sports&discipline=football)  \n
[livefootballol.tv](http://www.livefootballol.tv)  \n
[First Row Sports](http://www.thefirstrow.eu/sport/football.html)  \n
"""

stats_string = """**{0}**|Statistic|**{1}**
--:|:--:|:--  \n"""
