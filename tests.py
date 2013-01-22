from lib import Match, Queue
from datetime import datetime, timedelta
import unittest


class TestQueue(unittest.TestCase):

    def setUp(self):
        self.q = Queue(1)

    def test_print(self):
        self.assertEquals(self.q.__str__(), '[0]')

    def test_len(self):
        self.assertEquals(len(self.q), 0)
        self.q.enqueue('test')
        self.assertEquals(len(self.q), 1)

    def test_dequeue_empty_queue(self):
        self.assertIsNone(self.q.dequeue())

    def test_enqueue_full_queue(self):
        self.q.enqueue('test')
        self.assertFalse(self.q.enqueue('test'))

    def test_latest(self):
        self.assertEquals(self.q.latest(), 0)
        self.q.enqueue('test')
        self.assertEquals(self.q.latest(), 'test')

    def test_empty(self):
        self.assertTrue(self.q.empty())

    def test_enqueue(self):
        self.assertTrue(self.q.enqueue(0))

    def test_full(self):
        self.q.enqueue(0)
        self.assertTrue(self.q.full())

    def test_dequeue(self):
        self.q.enqueue('test')
        self.assertEquals(self.q.dequeue(), 'test')


class TestMatch(unittest.TestCase):

    def setUp(self):

        self.dt = datetime.now() - timedelta(hours=-1)
        self.test_kick_off = datetime(self.dt.year, self.dt.month, self.dt.day,
                                      self.dt.hour, self.dt.minute, self.dt.second)
        self.test_kick_off_string = datetime.strftime(self.test_kick_off,
                                                      '%Y-%m-%d %H:%M:%S')
        row = (2,
               self.test_kick_off_string,
               u'Tottenham Hotspur',
               u'Manchester United',
               u'White Hart Lane, London',
               u'premier-league',
               0)
        self.m = Match(row)

    def test_home_team(self):
        self.assertIsInstance(self.m.home_team, unicode)
        self.assertEquals(self.m.home_team, u'Tottenham Hotspur')

    def test_away_team(self):
        self.assertIsInstance(self.m.away_team, unicode)
        self.assertEquals(self.m.away_team, u'Manchester United')

    def test_venue(self):
        self.assertIsInstance(self.m.venue, unicode)
        self.assertEquals(self.m.venue, u'White Hart Lane, London')

    def test_datetime(self):
        self.assertIsInstance(self.m.kick_off, datetime)
        self.assertEquals(self.m.kick_off, self.test_kick_off)

    def test_played(self):
        self.assertFalse(self.m.played)

    def test_time_until_kick_off(self):
        self.assertAlmostEquals(self.m.time_until_kick_off(), 60, 0)

    def test_time_after_kick_off(self):

        dt = datetime.now() - timedelta(hours=1)
        test_kick_off = datetime(dt.year, dt.month, dt.day,
                                 dt.hour, dt.minute, dt.second)
        test_kick_off_string = datetime.strftime(test_kick_off,
                                                 '%Y-%m-%d %H:%M:%S')
        row = (2,
               test_kick_off_string,
               u'Tottenham Hotspur',
               u'Manchester United',
               u'White Hart Lane, London',
               u'premier-league',
               0)
        m = Match(row)

        self.assertAlmostEquals(m.time_after_kick_off(), 60, 0)

if __name__ == '__main__':
    unittest.main()
