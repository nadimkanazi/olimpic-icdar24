import unittest
from .LinearizerTestCase import LinearizerTestCase
from ..Linearizer import Linearizer


class BasicsTest(LinearizerTestCase):
    def test_one_empty_measure(self):
        self.process_sample("basics/one_empty_measure")
    
    # def test_sum_wrong(self):
    #     self.assertEqual(42, 43)
