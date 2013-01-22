from queue import Queue
from match import Match
from datetime import datetime
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
        self.assertEquals(self.q.latest(), None)
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
        row = (2,
               u'2013-01-20 16:00:00',
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
        test_date = datetime.strptime(u'2013-01-20 16:00:00', '%Y-%m-%d %H:%M:%S')
        self.assertIsInstance(self.m.kick_off, datetime)
        self.assertEquals(self.m.kick_off, test_date)

    def test_played(self):
        self.assertFalse(self.m.played)

if __name__ == '__main__':
    unittest.main()
