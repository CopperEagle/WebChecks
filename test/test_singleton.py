 
import unittest

from webchecks.utils.singleton import singleton

# correctness should be quite clear...
class SingletonTest(unittest.TestCase):

    def test_singleton(self):

        @singleton
        class A:
            def __init__(self, a1, a2, a3):
                self.a1 = a1
                self.a2 = a2
                self.a3 = a3

            def set(self, a):
                self.a1 = a

        o1 = A(1, 2, 3)
        o2 = A()
        self._test_equ(o1, o2, "init")
        o2.a3 = 100
        o1.a1 = 10
        self._test_equ(o1, o2, "modified attributes")
        o1.set(50)
        self._test_equ(o1, o2, "method")


    
    def _test_equ(self, o1, o2, when):
        self.assertEqual(o1.a1, o2.a1, f"Singleton attribute error at {when}.")
        self.assertEqual(o1.a2, o2.a2, f"Singleton attribute error at {when}.")
        self.assertEqual(o1.a3, o2.a3, f"Singleton attribute error at {when}.")
   
