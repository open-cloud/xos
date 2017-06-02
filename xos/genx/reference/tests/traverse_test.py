from dependency_walker import DependencyWalker
import unittest

class DependencyWalkerTest(unittest.TestCase):
    def test_unbounded(self):
        deps = '{"10": [["4", "ignore", "ignore"], ["3", "ignore", "ignore"]], "1": [["2", "ignore", "ignore"]], "3": [["5", "ignore", "ignore"]], "2": [["1", "ignore", "ignore"]], "5": [["3", "ignore", "ignore"]], "4": [], "7": [], "6": [["2", "ignore", "ignore"], ["6", "ignore", "ignore"], ["9", "ignore", "ignore"], ["5", "ignore", "ignore"]], "9": [["3", "ignore", "ignore"]], "8": []}'
        dw = DependencyWalker(deps, '10')
        walk = sorted(dw)
        self.assertEqual(walk, ['3','4','5'])

    def test_bounded_depth(self):
        deps = '{"10": [["4", "ignore", "ignore"], ["3", "ignore", "ignore"]], "1": [["2", "ignore", "ignore"]], "3": [["5", "ignore", "ignore"]], "2": [["1", "ignore", "ignore"]], "5": [["3", "ignore", "ignore"]], "4": [], "7": [], "6": [["2", "ignore", "ignore"], ["6", "ignore", "ignore"], ["9", "ignore", "ignore"], ["5", "ignore", "ignore"]], "9": [["3", "ignore", "ignore"]], "8": []}'
        dw = DependencyWalker(deps, '10', depth=0)
        walk = sorted(dw)
        self.assertEqual(walk, ['3','4'])
   
if __name__ == '__main__':
    unittest.main()


