#!user/bin/env python

from bs4 import BeautifulSoup  # BeautifulSoup4
from urllib2 import urlopen, HTTPError, URLError

from collections import deque, namedtuple
from datetime import datetime, timedelta
from praw.errors import APIException
from time import sleep
from settings import comment
import praw  # Python Reddit Api Wrapper
import sqlite3
import re


def thread_exists(home, away, r):

    home = max(home.split(), key=len)
    away = max(away.split(), key=len)
    sleep(1)
    subreddit = r.get_subreddit('soccer')
    for submission in subreddit.get_new(limit=20):
        if re.search(r'Match Thread.*%s.*%s.*' % (home, away), submission.title):
            return True
    return False


def list_replace(lst, changes):
    team_string = '+'.join(lst)
    for change in changes:
        team_string = team_string.replace(change[0], change[1])
    team_string = team_string.lower()
    team_string = team_string.replace(' ', '')

    return team_string.split('+')


def query_fixtures():
    """
    Returns a list of fixtures for the next 24 hours. Each fixture is a list
    containing [id in db, datetime of kick off as a string format YYYY-MM-DD
    hh:mm:ss, home team as string, away team as string, venue as string, league
    as string, played as integer 1 being True 0 being False, home team url,
    away team url]
    """

    changes = [('West Bromwich Albion', 'westbrom'),
               ('Manchester United', 'manchester-united'),
               ('Tottenham Hotspur', 'tottenham-hotspur'),
               ('Swansea City', 'swansea'),
               ('Queens Park Rangers', 'qpr'),
               ('Aston Villa', 'aston-villa'),
               (u'M\xe1laga CF', 'malaga'),
               ('FC Barcelona', 'barcelona'),
               (u'Atl\u00E9tico Madrid', 'atleticomadrid'),
               ('VfL Wolfsburg', 'wolfsburg'),
               ('VfB Stuttgart', 'stuttgart'),
               ('Shalke 04', 'shalke'),
               ('As Roma', 'roma'),
               ('Getafe CF', 'getafe'),
               ('Valencia CF', 'valencia'),
               ('Levante UD', 'levante')]

    con = sqlite3.connect('fixtures.db')
    cursor = con.cursor()

    # This query wont be in the finished version, this is just for testing. The
    # query in the finished version will retrive all of the fixtures for the
    # next 24 hours.

    with con:
        cursor.execute("""
                       select * from fixtures_tbl where
                       id is 11;
                       """)

        rows = cursor.fetchall()
        fixture_list = [list(row) for row in rows]

        home_list = [record[2] for record in fixture_list]
        away_list = [record[3] for record in fixture_list]

        home_list = list_replace(home_list, changes)
        away_list = list_replace(away_list, changes)

        for i, row in enumerate(fixture_list):
            row.append(home_list[i])
            row.append(away_list[i])

        return fixture_list


def main():

    update_queue = deque([])
    post_queue = deque(query_fixtures())

    r = praw.Reddit(user_agent='Match Thread Submiter for /r/soccer, by /u/Match-Thread-Bot')
    r.login()  # Login details in praw.ini file

    while True:

        if post_queue:
            time_until_kick_off = (datetime.strptime(post_queue[-1][1],
                                                     '%Y-%m-%d %H:%M:%S') -
                                   datetime.now()).total_seconds()
        else:
            # The following is a bit ugly. If the post_queue is empty
            # this stops an out of index error.
            time_until_kick_off = 5 * 60.0

        print '%f minutes until next kick off' % (time_until_kick_off / 60)
        print 'Length of post queue: %d' % len(post_queue)

        if post_queue and time_until_kick_off < (5 * 60):
            post = post_queue.pop()
            home_team = post[2]
            away_team = post[3]
            title = 'Match Thread: %s v %s' % (home_team,
                                               away_team)
            content = construct_thread(post)

            if not thread_exists(home_team, away_team, r):
                try:
                    submission = r.submit('chessporn', title, content)
                except APIException as e:
                    post_queue.append(post)
                    print 'Could not submit thread', e
                except URLError as e:
                    post_queue.append(post)
                    print 'Could not submit thread', e
                else:
                    print 'posting thread %s' % submission.title

                    submission.add_comment(comment)

                    update_queue.appendleft((submission, post))
                    print 'adding thread to update queue %s' % submission.title
            else:
                print 'Thread %s already exists' % title

        elif update_queue:
            print 'length of update queue: %d' % len(update_queue)
            post = update_queue.pop()

            try:
                post[0].edit(construct_thread(post[1],
                                              submission_id=post[0].id))
            except APIException as e:
                update_queue.append(post)
                print 'Could not update thread', e
            except URLError as e:
                update_queue.append(post)
                print 'Could not update thread', e
            else:
                print 'updating thread %s' % post[0].title
                # Time past kick off in seconds
                time_past_kick_off = float((datetime.now() -
                                            datetime.strptime(post[1][1],
                                                              '%Y-%m-%d %H:%M:%S')
                                            ).total_seconds())

                # Each match thread is updated for 180 minutes
                seconds_left = 180 * 60 - time_past_kick_off

                if seconds_left > 0:
                    update_queue.appendleft(post)
                    print ('adding thread %s to update queue %f minutes left' %
                           (post[0].title, (seconds_left / 60)))

        if not post_queue and not update_queue:
            print '\n Finished!'
            break

        print '\n'
        sleep(20)


def scrape_stats(url):
    """
    Scrapes stats from target url.

    Returns a named tuple with stat, home, home_squad, away_squad, score
    referee, attendance
    """

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
        f = urlopen(url)
    except HTTPError as e:
        print "Can't find stats page", e
        return output
    except URLError as e:
        print "Can't find stats page", e
        return output

    page = f.read()
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


def scrape_events(url):

    """
    Scrapes events from the target url.

    Returns a named tuple with minute, event_type, event
    """
    print 'Scraping events form ', url

    output = namedtuple('output', 'minute event_type event')
    output.minute, output.event_type, output.event = [], [], []

    try:
        f = urlopen(url)
    except HTTPError as e:
        print "Can't find events page", e
        return output
    except URLError as e:
        print "Can't find stats page", e
        return output

    page = f.read()
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


def construct_thread(fixture, submission_id='#'):

    from settings import template, stats_string

    kick_off = datetime.strptime(fixture[1], '%Y-%m-%d %H:%M:%S')
    month = datetime.strftime(kick_off, '%b').lower()
    home, away = fixture[7], fixture[8]

    # The following esentially guesses what the url is going to be for each
    # match on the guardian website. Luckily their url's are fairly
    # predictable.
    stats = scrape_stats('http://www.guardian.co.uk/football/match/%s/%s/%02d/%s-v-%s' %
                         (kick_off.year,
                          month,
                          kick_off.day,
                          home,
                          away))

    events = scrape_events('http://www.guardian.co.uk/football/match-popup/%s/%s/%02d/%s-v-%s' %
                           (kick_off.year,
                            month,
                            kick_off.day,
                            home,
                            away))

    stats_string = stats_string % (fixture[2], fixture[3])  # (home team, away team)
    events_string = ''

    for i in range(len(events.minute)):
        events_string += '%s %s %s  \n' % (events.minute[i].strip(),
                                           events.event_type[i].strip(),
                                           events.event[i].strip())

    for i in range(len(stats.stat)):
        stats_string += '%s|%s|%s  \n' % (stats.home[i].strip(),
                                          stats.stat[i].strip(),
                                          stats.away[i].strip())

    # TODO better hadling of timezones. This will break with DST.
    text = template % (datetime.strftime(kick_off,
                                         '%H:%M GMT'),
                       datetime.strftime(kick_off + timedelta(hours=1),
                                         '%H:%M CET'),
                       datetime.strftime(kick_off + timedelta(hours=5),
                                         '%H:%M EST'),
                       fixture[4],  # Venue
                       stats.referee,
                       stats.attendance,
                       submission_id,
                       fixture[2],  # Home Team
                       stats.home_squad,
                       fixture[3],  # Away Team
                       stats.away_squad,
                       stats.score,
                       stats_string,
                       events_string)
    return text

if __name__ == '__main__':
    main()
