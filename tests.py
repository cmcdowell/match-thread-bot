from queue import Queue
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

if __name__ == '__main__':
    unittest.main()
