from bs4 import BeautifulSoup
from list_replace import list_replace
from settings import CHANGES
from collections import namedtuple
from datetime import datetime
from urllib2 import urlopen, HTTPError, URLError


class Match(object):

    def __init__(self, row):
        self.kick_off = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        self.home_team = row[2]
        self.away_team = row[3]
        self.venue = row[4]
        self.played = row[6]
        self.home_url = list_replace([self.home_team], CHANGES)[0]
        self.away_url = list_replace([self.away_team], CHANGES)[0]

        stats_url_template = 'http://www.guardian.co.uk/football/match/{0}/{1}/{2}/{3}-v-{4}'
        events_url_template = 'http://www.guardian.co.uk/football/match-popup/{0}/{1}/{2}/{3}-v-{4}'

        self.stats_url = stats_url_template.format(self.kick_off.year,
                                                   datetime.strftime(self.kick_off,
                                                                     '%b').lower(),
                                                   str(self.kick_off.day).zfill(2),
                                                   self.home_url,
                                                   self.away_url)

        self.events_url = events_url_template.format(self.kick_off.year,
                                                     datetime.strftime(self.kick_off,
                                                                       '%b').lower(),
                                                     str(self.kick_off.day).zfill(2),
                                                     self.home_url,
                                                     self.away_url)

    def time_until_kick_off(self):
        return (self.kick_off - datetime.now()).total_seconds() / 60

    def time_after_kick_off(self):
        return -self.time_until_kick_off()

    def scrape_events(self):
        """
        Scrapes events from the target url.

        Returns a named tuple with minute, event_type, event
        """

        url = self.events_url
        print 'Scraping events form ', url

        output = namedtuple('output', 'minute event_type event')
        output.minute, output.event_type, output.event = [], [], []

        try:
            page = urlopen(url).read()
        except HTTPError as e:
            print "Can't find events page", e
            return output
        except URLError as e:
            print "Can't find events page", e
            return output

        soup = BeautifulSoup(page)

        # List of table rows with css class event
        table = soup.findAll('tr', {'class': 'event'})

        # Defines what's to be changed for /r/soccer's custom match thread
        # icons
        changes = [('SUB', '[](//#sub) Sub'),
                   ('RED CARD', '[](//#red) Red'),
                   ('YELLOW CARD', '[](//#yellow) Yellow'),
                   ('GOAL', '[](//#ball) **Goal**')]

        for row in table:
            try:
                output.minute.append(row.td.contents[0])
            except AttributeError:
                output.minute.append('')
            try:
                output.event_type.append(row.td.next_sibling.next_sibling.contents[1].contents[0])
            except AttributeError:
                output.event_type.append('')
            try:
                output.event.append(row.td.next_sibling.next_sibling.contents[2])
            except AttributeError:
                output.event.append('')

        # Replace the event types with custom event types defined above
        output.event_type = list_replace(output.event_type, changes)

        return output

    def scrape_stats(self):
        """
        Scrapes stats from target url.

        Returns a named tuple with stat, home, home_squad, away_squad, score
        referee, attendance
        """

        url = self.stats_url
        print 'Scraping stats from ', url

        output = namedtuple('output',
                            ['stat',
                            'home',
                            'home_squad',
                            'away_squad',
                            'score',
                            'referee',
                            'attendance'])

        output.stat, output.home, output.away = [], [], []

        (output.home_squad, output.away_squad, output.score,
         output.referee, output.attendance) = '', '', '', '', ''

        try:
            page = urlopen(url).read()
        except HTTPError as e:
            print "Can't find stats page", e
            return output
        except URLError as e:
            print "Can't find stats page", e
            return output

        soup = BeautifulSoup(page)

        # Grabs the stats for the match stats section
        table = soup.find('table',
                          {'summary': 'Corners, Goal attempts, Goals on target, Fouls and Offside match statistics'})
        try:
            rows = table.findAll('tr', {'class': 'section'})
        except AttributeError as e:
            rows = []
            print 'Stats table not found', e

        for row in rows:
            try:
                stat = row.findAll('span', {'class': 'number'})
                output.home.append(stat[0].contents[0])
                output.away.append(stat[1].contents[0])
                output.stat.append(row.th.contents[0])
            except AttributeError as e:
                output.home.append('')
                output.away.append('')
                output.stat.append('')
                print 'Stat not found', e

        # Grabs the squads for the lineups section
        table = soup.find('table', {'summary': 'List of players'})
        try:  # Really broad try statement, think about splitting this up.
            player_lists = table.findAll('ul')
            home_squad_html = player_lists[0].findAll('li')
            away_squad_html = player_lists[1].findAll('li')

            # Concatonates all players in the squad into one big string. Could
            # maybe append them to a list if I want to post the lineups as a table.
            for player in home_squad_html:
                output.home_squad += player.contents[0]

            for player in away_squad_html:
                output.away_squad += player.contents[0]

        except IndexError as e:
            print 'Could not find team lineups', e
        except AttributeError as e:
            print 'Could not find team lineups', e

        # Grabs the score
        score_html = soup.find('td', {'class': 'score'})
        try:
            score = score_html.contents[0].strip()
        except AttributeError as e:
            score = ''
            print 'Score not found', e
        except IndexError as e:
            score = ''
            print 'Score not found', e

        try:
            # Adds the half time score
            score += (' ' + score_html.span.contents[0].strip())
        except AttributeError as e:
            print 'Half time score not found', e
        except IndexError as e:
            print 'Half time Score not found', e

        output.score = score

        # Grabs the referee and the attendance
        table = soup.find('table',
                          {'summary': 'Referee, Venue and Attendance details'})

        try:
            data = table.findAll('td')
        except AttributeError as e:
            print 'No data', e
            data = []

        try:
            output.referee = data[0].contents[0]
        except IndexError as e:
            print 'Could not find referee', e

        try:
            output.attendance = data[2].contents[0]
        except IndexError as e:
            print 'Could not find attendance', e

        return output
