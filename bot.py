#!/usr/bin/env python

from lib import Match, Queue
from lib.templates import template, comment
from settings import MATCH_LENGTH, PRE_KICK_OFF, SUBREDDIT

from datetime import datetime, timedelta
from praw.errors import APIException
from time import sleep
from urllib2 import URLError
import argparse
import logging
import pickle
import re
import sys

import praw  # Python Reddit Api Wrapper


def thread_exists(home, away, r):
    """
    Takes home team, away team and Reddit object as argument.
    Returns True if a thread for the match featuring the home team
    and away team exists, returns false if one does not exist.
    """

    log = logging.getLogger('ex')

    home = max(home.split(), key=len)
    away = max(away.split(), key=len)
    sleep(1)  # Sleep to ensure reddit API ratelimit not exceded.
    try:
        subreddit = r.get_subreddit(SUBREDDIT)

        for submission in subreddit.get_new(limit=25):
            if re.search(u'^Match Thread.*{0}.*{1}.*'.format(home, away),
                         submission.title):
                return True
        return False

    except Exception:
        log.exception('could not search new queue')
        return True  # if new queue can not be searched, assume thread exists.


def construct_match_queue(verbose):
    """
    Returns a Queue of Match objects constructed from piped in sql
    query.
    """

    rows = [line.decode('utf-8').split(u'|') for line in sys.stdin]

    fixture_queue = Queue(len(rows))

    for row in rows:
        if verbose:
            print u'{0} v {1}, {2}'.format(row[2], row[3], row[1])

        fixture_queue.enqueue(Match(row))

    # Prompt for fixtures in verbose mode
    if verbose:
        sys.stdin = open('/dev/tty')
        while True:
            msg = raw_input('[Y/N] >')
            if 'n' in msg or 'N' in msg:
                sys.exit()
            elif 'y' in msg or 'Y' in msg:
                break

    return fixture_queue


def construct_thread(match, submission_id='#'):
    """
    Takes a match object and returns a markdown string for posting
    in a reddit thread. Takes submission id of a thread as an optional
    keyword argument for redditstream.
    """

    from lib.templates import stats_string

    kick_off = match.kick_off

    stats = match.scrape_stats()
    events = match.scrape_events()

    # Adds home tam and away team names to the top of the stats table
    stats_string = stats_string.format(match.home_team, match.away_team)
    events_string = ''

    for i in range(len(events.minute)):
        events_string += u'{0} {1} {2}  \n'.format(events.minute[i].strip(),
                                                   events.event_type[i].strip(),
                                                   events.event[i].strip())

    for i in range(len(stats.stat)):
        stats_string += u'{0}|{1}|{2}  \n'.format(stats.home[i].strip(),
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

    return template.safe_substitute(context)


def load_from_save(file='queues.pickle'):
    """
    Loads objects from pickle file, by default this
    file is queues.pickle

    Takes optional argument, file, as string containing path to
    pickle file.
    """

    with open(file, 'rb') as f:
        previous_state = pickle.load(f)

    return previous_state


def save_to_file(file='queues.pickle', **kwargs):
    """
    Saves kwargs to pickle file, by default this file is queues.pickle

    Takes optional argument, file, as string containing path to pickle
    file.
    """

    with open(file, 'wb') as f:
        pickle.dump(kwargs, f)


def main():

    logging.basicConfig(filename='errors.log', level=logging.ERROR)
    log = logging.getLogger('ex')

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='increase output verbosity',
                        action='store_true')
    parser.add_argument('-l', '--load', help='load from last canceled run',
                        action='store_true')
    args = parser.parse_args()

    if args.load:
        previous_state = load_from_save()

        post_queue = previous_state['post_queue']
        update_queue = previous_state['update_queue']
    else:
        post_queue = construct_match_queue(args.verbose)
        update_queue = Queue(len(post_queue))

    r = praw.Reddit(user_agent='Match Thread Submiter for /r/soccer, by /u/Match-Thread-Bot')
    r.login()  # Login details in praw.ini file

    while True:

        try:
            if not post_queue.empty():
                time_until_kick_off = post_queue.latest().time_until_kick_off()
            else:
                time_until_kick_off = 0

            print '{0} minutes until next kick off.'.format(int(time_until_kick_off))
            print 'Length of post queue:\t{0}'.format(len(post_queue))
            print 'Length of update queue:\t{0}'.format(len(update_queue))

            if not post_queue.empty():
                time_until_kick_off = post_queue.latest().time_until_kick_off()
            else:
                time_until_kick_off = 0

            if not post_queue.empty() and time_until_kick_off < (PRE_KICK_OFF):
                post = post_queue.dequeue()
                title = u'Match Thread: {0} v {1}'.format(post.home_team,
                                                          post.away_team)
                if not thread_exists(post.home_team, post.away_team, r):

                    content = construct_thread(post)
                    try:
                        submission = r.submit(SUBREDDIT, title, content)
                        submission.add_comment(comment)
                    except (APIException, URLError, IOError):
                        log.exception('Could not submit thread.')
                    else:
                        print 'posting thread %s' % submission.title

                        update_queue.enqueue((submission.id, post))
                        print u'adding thread to update queue {0}'.format(submission.title)
                else:
                    print u'Thread {0} already exists'.format(title)

            elif not update_queue.empty():
                post = update_queue.dequeue()

                try:
                    submission = r.get_submission(submission_id=post[0])
                    submission.edit(construct_thread(post[1],
                                                     submission_id=post[0]))
                except (APIException, URLError, IOError):
                    update_queue.enqueue(post)
                    log.exception('Could not update thread')
                else:
                    print u'updating thread {0}'.format(submission.title)

                    time_left = MATCH_LENGTH - post[1].time_after_kick_off()

                    if time_left > 0:
                        update_queue.enqueue(post)
                        print u'adding thread {0} to update queue {1} minutes left'.format(submission.title,
                                                                                           int(time_left))

            if post_queue.empty() and update_queue.empty():
                print '\nFinished!'
                break

            print '\n'
            sleep(30)

        except KeyboardInterrupt:
            save_to_file(post_queue=post_queue, update_queue=update_queue)
            raise


if __name__ == '__main__':
    main()
