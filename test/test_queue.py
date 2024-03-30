import unittest
from webchecks.utils.url import *
from webchecks.utils.timedqueue import *


class QueueTest(unittest.TestCase):
    """Test for the timedqueue. Should add more tests."""
    def testrun(self):
        q = TimedQueue()
        time = 0
        q.enqueue("a", 1, 1, time)
        q.enqueue("b", 2, 1, time)
        q.enqueue("b", 3, 3, time)
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        time = 2
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIsNone(q.dequeue(time))
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        time = 3
        self.assertIsNone(q.dequeue(time))
        time = 5
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        self.assertEqual(q.dequeue(time), 3)
        self.assertTrue(q.isempty(), f"Queue empty at time {time}.")
        self.assertIsNone(q.dequeue(time))
        self.assertIsNone(q.dequeue(time))
        time = 1000
        self.assertIsNone(q.dequeue(time))

    def testrun2(self):
        q = TimedQueue()
        time = 0
        q.enqueue("a", 1, 1, time)
        q.enqueue("b", 2, 1, time)
        q.enqueue("c", 2, 1, time)
        q.enqueue("d", 2, 1, time)
        q.enqueue("e", 2, 1, time)
        q.enqueue("a", 3, 3, time)
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        time = 2
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        self.assertIn(q.dequeue(time), (1, 2))
        self.assertIsNone(q.dequeue(time))
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        q.enqueue("b", 3, 1, time)
        q.enqueue("a", 4, 995, time)
        time = 3
        self.assertEqual(q.dequeue(time), 3)
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        self.assertIsNone(q.dequeue(time))
        time = 5
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        self.assertEqual(q.dequeue(time), 3) # one late
        self.assertIsNone(q.dequeue(time))
        self.assertIsNone(q.dequeue(time))
        time = 1000
        self.assertFalse(q.isempty(), f"Queue not empty at time {time}.")
        self.assertEqual(q.dequeue(time), 4)
        self.assertTrue(q.isempty(), f"Queue empty at time {time}.")
        self.assertIsNone(q.dequeue(time))
        self.assertTrue(q.isempty(), f"Queue empty at time {time}.")
