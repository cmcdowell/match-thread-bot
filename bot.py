#!user/bin/env python

from lib import Match, Queue
from lib.templates import template, comment
from settings import MATCH_LENGTH, PRE_KICK_OFF

from datetime import datetime, timedelta
from praw.errors import APIException
from sys import argv
from time import sleep
from urllib2 import URLError
import praw  # Python Reddit Api Wrapper
import re
import sqlite3


def thread_exists(home, away, r):

    home = max(home.split(), key=len)
    away = max(away.split(), key=len)
    sleep(1)
    subreddit = r.get_subreddit('soccer')
    for submission in subreddit.get_new(limit=25):
        if re.search(r'^Match Thread.*%s.*%s.*' % (home, away), submission.title):
            return True
    return False


def query_fixtures():
    """
    Returns a Queue of Match objects.
    """

    con = sqlite3.connect('fixtures.db')
    cursor = con.cursor()
    # This query wont be in the finished version, this is just for testing. The
    # query in the finished version will retrive all of the fixtures for the
    # next 24 hours.

    with con:
        cursor.execute(argv[1])

        rows = cursor.fetchall()
        fixture_queue = Queue(len(rows))

        for row in rows:
            fixture_queue.enqueue(Match(row))

        return fixture_queue


def construct_thread(match, submission_id='#'):

    from lib.templates import stats_string

    kick_off = match.kick_off

    stats = match.scrape_stats()
    events = match.scrape_events()

    stats_string = stats_string % (match.home_team, match.away_team)
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
    context = {'GMT': datetime.strftime(kick_off,
                                        '%H:%M GMT'),
               'CET': datetime.strftime(kick_off + timedelta(hours=1),
                                        '%H:%M CET'),
               'EST': datetime.strftime(kick_off + timedelta(hours=-5),
                                        '%H:%M EST'),
               'venue': match.venue,
               'referee': stats.referee,
               'attendance': stats.attendance,
               'id': submission_id,
               'home_team': match.home_team,
               'home_squad': stats.home_squad,
               'away_team': match.away_team,
               'away_squad': stats.away_squad,
               'score': stats.score,
               'stats_string': stats_string,
               'events_string': events_string}

    return template.substitute(context)


def main():

    post_queue = query_fixtures()
    update_queue = Queue(len(post_queue))

    r = praw.Reddit(user_agent='Match Thread Submiter for /r/soccer, by /u/Match-Thread-Bot')
    r.login()  # Login details in praw.ini file

    while True:

        if not post_queue.empty():
            time_until_kick_off = post_queue.latest().time_until_kick_off()
        else:
            time_until_kick_off = 0

        print '{0} minutes until next kick off.'.format(time_until_kick_off)
        print 'Length of post queue:\t{0}'.format(len(post_queue))
        print 'Length of update queue:\t{0}'.format(len(update_queue))

        if not post_queue.empty():
            time_until_kick_off = post_queue.latest().time_until_kick_off()
        else:
            time_until_kick_off = 0

        if not post_queue.empty() and time_until_kick_off < (PRE_KICK_OFF):
            post = post_queue.dequeue()
            title = 'Match Thread: {0} v {1}'.format(post.home_team,
                                                     post.away_team)
            if not thread_exists(post.home_team, post.away_team, r):

                content = construct_thread(post)
                try:
                    submission = r.submit('chessporn', title, content)
                except APIException as e:
                    print 'Could not submit thread', e
                except URLError as e:
                    print 'Could not submit thread', e
                else:
                    print 'posting thread %s' % submission.title

                    submission.add_comment(comment)

                    update_queue.enqueue((submission, post))
                    print 'adding thread to update queue {0}'.format(submission.title)
            else:
                print 'Thread {0} already exists'.format(title)

        elif not update_queue.empty():
            post = update_queue.dequeue()

            try:
                post[0].edit(construct_thread(post[1],
                                              submission_id=post[0].id))
            except APIException as e:
                update_queue.enqueue(post)
                print 'Could not update thread', e
            except URLError as e:
                update_queue.enqueue(post)
                print 'Could not update thread', e
            else:
                print 'updating thread {0}'.format(post[0].title)

                time_left = MATCH_LENGTH - post[1].time_after_kick_off()

                if time_left > 0:
                    update_queue.enqueue(post)
                    print 'adding thread {0} to update queue {1} minutes left'.format(post[0].title,
                                                                                      time_left)

        if post_queue.empty() and update_queue.empty():
            print '\n Finished!'
            break

        print '\n'
        sleep(30)


if __name__ == '__main__':
    main()
