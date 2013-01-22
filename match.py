from datetime import datetime


class Match(object):

    def __init__(self, row):
        self.kick_off = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        self.home_team = row[2]
        self.away_team = row[3]
        self.venue = row[4]
        self.played = row[6]
