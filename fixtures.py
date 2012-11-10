#!usr/bin/env python

from bs4 import BeautifulSoup
from dateutil import parser, rrule
from urllib2 import urlopen
import sqlite3
import re
import datetime


con = sqlite3.connect('fixtures.db')
leagues = ['premier-league', 'spanish-liga', 'german-bundesliga', 'italian-serie-a']


def scrape_fixtures(month, year, league):
    """Scrapes football fixtures from eurosport website

    Args:
        month:
            Month of the year you would like to retrive the
            fixtures for. Must be an iteger less than or equal
            to 2 digits long. E.g. 01 for January
        year:
            Year you would like to retreive the fixtures for.
            Must be 4 didgit integer e.g. 2012
        league:
            League you would like to scrape fixtures from. Must
            be a string.
    Returns:
        A dictionairy of lists; keys 'kick off', 'home team',
        'away team', 'venue'."""

    matches_for_month = {'kick off': [],
                         'home team': [],
                         'away team': [],
                         'venue': []}

    #This is kind of janky, and doesn't work for competitions with group stages
    try:
        url = 'http://uk.eurosport.yahoo.com/football/%s/2012-2013/results/%d_%02d.html' % (league, year, month)
        page = urlopen(url)
        soup = BeautifulSoup(page.read())
        tables = soup.findAll('table', 'fixtures-results')  # Makes list containing the html for each day

        for table in tables:
            rows = table.tr.find_next_siblings('tr', {'class': 'fixture'})  # Makes a list where each element is the html for a match

            for row in rows:
                # Retrives the teams, kickoff time, and venue for each match
                # TODO implement using beautifulsoup instead of regex

                matches_for_month['kick off'].append(parser.parse(str(year) + ' ' + re.search(r'<abbr.+>(.+)</abbr>', str(row)).group(1)))
                matches_for_month['home team'].append(re.search(r'<span class="home">(.+)</span>', str(row)).group(1))
                matches_for_month['away team'].append(re.search(r'<span class="away">(.+)</span>', str(row)).group(1))
                matches_for_month['venue'].append(re.search(r'<td class="venue.+">(.+)</td>', str(row)).group(1))

        return matches_for_month
    except:
        print 'Error no url %s' % url

with con:

    cursor = con.cursor()
    cursor.execute('DROP TABLE IF EXISTS fixtures_tbl;')
    cursor.execute("""CREATE TABLE fixtures_tbl (
        id INTEGER PRIMARY KEY,
        kick_off TEXT NOT NULL,
        home_team VARCHAR(30) NOT NULL,
        away_team VARCHAR(30) NOT NULL,
        venue VARCHAR(100) NOT NULL,
        league VARCHAR(30) NOT NULL,
        played INTEGER NOT NULL);""")

    for league in leagues:
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=datetime.datetime(2012, 11, 01),
                              until=datetime.datetime(2013, 06, 30)):
            matches = scrape_fixtures(dt.month, dt.year, league)
            try:

                for i in range(len(matches['home team'])):

                    cursor.execute("""INSERT INTO fixtures_tbl (kick_off, home_team, away_team, venue, league, played)
                                VALUES(?, ?, ?, ?, ?, 0);""", (unicode(str(matches['kick off'][i]), 'UTF_8'),
                                                                        unicode(matches['home team'][i], 'UTF_8'),
                                                                            unicode(matches['away team'][i], 'UTF_8'),
                                                                            unicode(matches['venue'][i], 'UTF_8'),
                                                                            unicode(league, 'UTF_8')))
            except:
                print 'Janky as fuck'
