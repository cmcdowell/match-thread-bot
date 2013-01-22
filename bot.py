#!user/bin/env python

from lib import Match, Queue
from urllib2 import URLError

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
    for submission in subreddit.get_new(limit=25):
        if re.search(r'^Match Thread.*%s.*%s.*' % (home, away), submission.title):
            return True
    return False


def query_fixtures():
    """
    Returns a list of fixtures for the next 24 hours. Each fixture is a list
    containing [id in db, datetime of kick off as a string format YYYY-MM-DD
    hh:mm:ss, home team as string, away team as string, venue as string, league
    as string, played as integer 1 being True 0 being False, home team url,
    away team url]
    """

    con = sqlite3.connect('fixtures.db')
    cursor = con.cursor()
    # This query wont be in the finished version, this is just for testing. The
    # query in the finished version will retrive all of the fixtures for the
    # next 24 hours.

    with con:
        cursor.execute("""
                       select * from fixtures_tbl where id < 3
                       order by kick_off desc;
                       """)

        rows = cursor.fetchall()
        fixture_queue = Queue(len(rows))

        for row in rows:
            fixture_queue.enqueue(Match(row))

        return fixture_queue


def construct_thread(match, submission_id='#'):

    from settings import template, stats_string

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
    text = template % (datetime.strftime(kick_off,
                                         '%H:%M GMT'),
                       datetime.strftime(kick_off + timedelta(hours=1),
                                         '%H:%M CET'),
                       datetime.strftime(kick_off + timedelta(hours=-5),
                                         '%H:%M EST'),
                       match.venue,
                       stats.referee,
                       stats.attendance,
                       submission_id,
                       match.home_team,
                       stats.home_squad,
                       match.away_team,
                       stats.away_squad,
                       stats.score,
                       stats_string,
                       events_string)
    return text


def main():

    post_queue = query_fixtures()
    update_queue = Queue(len(post_queue))

    r = praw.Reddit(user_agent='Match Thread Submiter for /r/soccer, by /u/Match-Thread-Bot')
    r.login()  # Login details in praw.ini file

    while True:

        print '{0} minutes until next kick off.'.format(int(post_queue.latest().time_until_kick_off()))
        print 'Length of post queue:\t{0}'.format(len(post_queue))
        print 'Length of update queue:\t{0}'.format(len(update_queue))

        if not post_queue.empty() and post_queue.latest().time_until_kick_off() < (5 * 60):
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

                time_left = 130 - post.time_past_kick_off()

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
