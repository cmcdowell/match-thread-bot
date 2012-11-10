#!user/bin/env python

from bs4 import BeautifulSoup  # BeautifulSoup4
from urllib2 import urlopen, HTTPError

from collections import deque
from datetime import datetime, timedelta
from query import query_fixtures, list_replace
from time import sleep
import praw  # Python Reddit Api Wrapper


def main():

    post_queue = deque([])
    update_queue = deque([])

    # returns a list of fixtures for the day, ordered by datetime
    # fixtures are lists of the following form
    # [id in db table, datetime string yyyy-mm-dd hh:mm:ss, home team,
    # away team, venue, league, if played, home team's url portion,
    # away team's url portion]
    relevent_fixtures = query_fixtures()

    for fixture in relevent_fixtures:
        # add the returned fixtures to the queue with the most recent at the
        # right of the queue
        post_queue.appendleft(fixture)

    print post_queue

    r = praw.Reddit(user_agent='Match Thread Submiter for /r/soccer, by /u/Match-Thread-Bot')
    r.login()

    while True:

        if post_queue:
            time_until_kick_off = (datetime.strptime(post_queue[-1][1],
                                                     '%Y-%m-%d %H:%M:%S') -
                                   datetime.now()).total_seconds()
        else:
            # The following is a bit ugly. If the post_queue is empty
            # this stops an out of index error.
            time_until_kick_off = 45 * 60.0

        print '%f minutes until next kick off' % (time_until_kick_off / 60)

        if post_queue and time_until_kick_off < (45 * 60):
            post = post_queue.pop()
            home_team = post[2]
            away_team = post[3]
            title = 'Match Thread: %s v %s' % (home_team,
                                               away_team)
            content = construct_thread(post)

            # with open('debug%d.txt' % post[0], 'w') as f:
            #     f.write(content.encode('utf8'))
            #     print 'posting thread'
            submission = r.submit('reddit_api_test', title, content)
            print 'posting thread %s' % submission.title
            update_queue.appendleft((submission, post))
            print 'adding thread to update queue %s' % submission.title

        elif update_queue:
            for p in update_queue:
                print p
            print '\n'
            post = update_queue.pop()
            for p in update_queue:
                print p
            print '\n'

            # with open('debug%d.txt' % post[0], 'w') as f:
            #     f.write(construct_thread(post).encode('utf8'))
            #     print 'updating thread'

            post[0].edit(construct_thread(post[1]))
            print 'updating thread %s' % post[0].title
            # Time past kick off in seconds
            time_past_kick_off = float((datetime.now() -
                                        datetime.strptime(post[1],
                                                          '%Y-%m-%d %H:%M:%S')
                                        ).total_seconds())

            # Each match thread is updated for 180 minutes
            seconds_left = 180 * 60 - time_past_kick_off

            if seconds_left > 0:
                update_queue.appendleft(post)
                print ('adding thread %s to update queue %f minutes left' %
                       (post[0].title, (seconds_left / 60)))

        if not post_queue and not update_queue:
            print 'Finished'
            break

        sleep(600)


def scrape_stats(url):
    """
    Takes the url of the match stats page for the game on the guardian
    website. Returns a dictionary with keys stat, home value, away value,
    home squad, away squad, score, referee, attendance. home squad,
    away squad, score, referee, and attendence map to strings. stat,
    home value, and away value map to lists coaining ecach value in the
    order they appear on the given webpage.

    E.g.
    returned_dict['stat'] = [u'Posession', u'Corners', u'Fouls']
    returned_dict['home value'] = [u'68%', u'3', u'2']
    returned_dict['away value'] = [u'32%', u'0', u'3']

    Each elemet with in each list will be a unicode string if the list is
    not empty.
    """

    print url

    output = {'stat': [],
              'home value': [],
              'away value': [],
              'home squad': '',
              'away squad': '',
              'score': '',
              'referee': '',
              'attendance': ''}

    try:
        f = urlopen(url)
    except HTTPError as e:
        print "Can't find stats page", e
        return output

    page = f.read()

    # f = open('html/westhamunited-v-manchestercity.htm')
    # page = f.read()
    # f.close()

    soup = BeautifulSoup(page)

    # Grabs the stats for the match stats section
    table = soup.find('table', {'summary': 'Corners, Goal attempts, Goals on target, Fouls and Offside match statistics'})
    try:
        rows = table.findAll('tr', {'class': 'section'})
    except AttributeError as e:
        rows = []
        print 'Stats table not found', e

    for row in rows:
        try:
            stat = row.findAll('span', {'class': 'number'})
            output['home value'].append(stat[0].contents[0])
            output['away value'].append(stat[1].contents[0])
            output['stat'].append(row.th.contents[0])
        except AttributeError as e:
            output['home value'].append('')
            output['away value'].append('')
            output['stat'].append('')
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
            output['home squad'] += player.contents[0]

        for player in away_squad_html:
            output['away squad'] += player.contents[0]

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
        score += score_html.span.contents[0].strip()
    except AttributeError as e:
        print 'Half time score not found', e
    except IndexError as e:
        print 'Half time Score not found', e

    output['score'] = score

    # Grabs the referee and the attendance
    table = soup.find('table', {'summary': 'Referee, Venue and Attendance details'})

    try:
        data = table.findAll('td')
    except AttributeError as e:
        print 'No data', e
        data = []

    try:
        output['referee'] = data[0].contents[0]
    except IndexError as e:
        output['referee'] = ''
        print 'Could not find referee', e

    try:
        output['attendance'] = data[2].contents[0]
    except IndexError as e:
        output['attendance'] = ''
        print 'Could not find attendance', e

    return output


def scrape_events(url):

    """
    Given the url of a match events page from the guardian webiste,
    returns a dictionairy with keys min, event, event type
    (min meaning minute not minumum). Each key maps to a list
    containing each value in the order it apeared on the given webpage.

    e.g.
    """
    print url

    output = {'min': [],
              'event type': [],
              'event': []}

    try:
        f = urlopen(url)
    except HTTPError as e:
        print "Can't find events page", e
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
               ('GOAL', '[](//#ball) Goal')]

    for row in table:
        try:
            output['min'].append(row.td.contents[0])
        except AttributeError:
            output['min'].append('')
        try:
            output['event type'].append(row.td.next_sibling.next_sibling.contents[1].contents[0])
        except AttributeError:
            output['event type'].append('')
        try:
            output['event'].append(row.td.next_sibling.next_sibling.contents[2])
        except AttributeError:
            output['event'].append('')

    # Replace the event types with custom event types defined above
    output['event type'] = list_replace(output['event type'], changes)

    return output


def construct_thread(fixture):

    from settings import template, events_string, stats_string

    kick_off = datetime.strptime(fixture[1], '%Y-%m-%d %H:%M:%S')
    month = datetime.strftime(kick_off, '%b').lower()
    home, away = fixture[7], fixture[8]

    # The following esentially guesses what the url is going to be for each
    # match on the guardian website. Luckily their url's are fairly
    # predictable.
    stats = scrape_stats('http://www.guardian.co.uk/football/match/%s/%s/%02d/%s-v-%s' % (kick_off.year,
                                                                                          month,
                                                                                          kick_off.day,
                                                                                          home,
                                                                                          away))
    events = scrape_events('http://www.guardian.co.uk/football/match-popup/%s/%s/%02d/%s-v-%s' % (kick_off.year,
                                                                                                  month,
                                                                                                  kick_off.day,
                                                                                                  home,
                                                                                                  away))

    stats_string = stats_string % (fixture[2], fixture[3])  # (home team, away team)

    for i in range(len(events['min'])):
        events_string += '%s|%s|%s  \n' % (events['min'][i].strip(),
                                           events['event type'][i].strip(),
                                           events['event'][i].strip())

    for i in range(len(stats['stat'])):
        stats_string += '%s|%s|%s  \n' % (stats['home value'][i].strip(),
                                          stats['stat'][i].strip(),
                                          stats['away value'][i].strip())

    # TODO better hadling of timezones. This will break with DST.
    text = template % (datetime.strftime(kick_off, '%H:%M GMT'),
                       datetime.strftime(kick_off + timedelta(hours=1), '%H:%M CET'),
                       datetime.strftime(kick_off + timedelta(hours=5), '%H:%M EST'),
                       fixture[4],  # Venue
                       stats['referee'],
                       stats['attendance'],
                       fixture[2],  # Home Team
                       stats['home squad'],
                       fixture[3],  # Away Team
                       stats['away squad'],
                       stats['score'],
                       stats_string,
                       events_string)
    return text

if __name__ == '__main__':
    main()
