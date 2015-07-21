import unittest
from os.path import abspath, dirname, realpath, join
import numpy as np
from random import seed
from ...Methods.network import readNetwork
from ...Components.ArrStream import ArrStream
from ...Components.SamplePath2 import SamplePath2
from ...Components.SvcDist import SvcDist
import pdb

# A four-node network 
#     2 ------ 3*
#     |        |
#     |        |
#     |        |
#    *0 ------ 1
# 
#     - Slightly uneven arrival probabilities (starred: 0.3, unstarred: 0.2)
#     - 4 bases, 2 ambs, no hospitals
#     - Travel time = 3 min.
#     - Response time threshold = 4 min.
#     - Service times = 20 min. (deterministic)
#
#   Fix a sample path (e.g., a random seed), and see if things work as intended.

class TestDPHonhon(unittest.TestCase):
    def setUp(self):
        T         = 100
        p         = 0.07
        sd        = 11111
        svc       = 20
        graphFile = "graph.txt"

        base = dirname(realpath(__file__))
        path = join(base, graphFile)
        svca = readNetwork(path)
        astr = ArrStream(svca, T)
        astr.updateP(p)

        dist = SvcDist(vals=[svc], probs=[1])

        seed(sd)
        self.omega = SamplePath2(svca, astr, dist)

        #  Call | Time | Location
        # -----------------------
        #   1   |  1   !   1
        #   2   |  41  |   2
        #   3   |  48  |   2
        #   4   |  70  |   3
        #   5   |  73  |   2
        #   6   |  86  |   0
        #   7   |  87  |   0
        #   8   |  96  |   0
        #   9   |  100 |   1

    def testQ(self):
        Q = self.omega.getQ()

        # Test 1 : Base 2 at time 93 
        # Two possibiliites:
        #  -Distpach to call at time 70 from one node away, no redeploy
        #  -Dispatch to call at time 73 from node location, no redeploy
        self.assertEqual(set(Q[93][2]), set([(70, 3), (73, 2)]))

        # Test 2 : Base 1 at time 60
        self.assertEqual(Q[60][1], [])

        # Test 3 : Base 1 at time 74
        self.assertEqual(Q[74][1], [(48, 2)])

        # Test 4 : Base 0 at time 99
        # Two possibilities: 
        #  -Dispatch to call at time 70 from one node away, redeploy to opposite corner
        #  -Dispatch to call at time 73 from one node away, redeploy one node away
        self.assertEqual(set(Q[99][0]), set([(70, 2), (70, 1), (73, 0), (73, 3)]))

    def testQ2(self):
        Q2 = self.omega.getQ2()

        # Test 1: Base 1 at time 69
        # Call at time 41 (node 2)
        #  -Dispatch from one node away (arrival at 44, arrival at node 1 at 70)
        #
        # Call at time 48 (node 2)
        #  -Dispatch from call location (svc completion at 68, redeploy by 71)
        #       (One node away would have meant svc completion at time 71)
        self.assertEqual(set(Q2[69][1]), set([(41, 0), (41, 3), (48, 2)]))

        # Test 2: Base 1 at time 72
        # Call at time 48 (node 2)
        #  -Dispatch from call location (svc completion at 68, redeploy by 74)
        #  -Dispatch from one node away (svc completion at 71, redeploy by 77)
        self.assertEqual(set(Q2[72][1]), set([(48, 0), (48, 3), (48, 2)]))

        # Test 3: Base 1 at time 75
        self.assertEqual(set(Q2[75][1]), set([(48, 0), (48, 3)]))

        # Test 4: Base 1 at time 71
        self.assertEqual(set(Q2[71][1]), set(Q2[72][1]))

        # Test 4: Base 3 at time 17
        self.assertEqual(Q2[17][3], [])

        # Test 5: Base 3 at time 23
        self.assertEqual(Q2[23][3], [(1, 1)])

        # Test 6: Base 0 at time 99
        self.assertEqual(Q2[99][0], [])

        # Test 7: Base 1 at time 99
        self.assertEqual(set(Q2[99][1]), set([(73, 0), (73, 3)]))

    def testTau(self):
        tau = self.omega.getTau()

        # Test 1: Time 48 call (node 2), Base 2 response, Base 2 redeploy
        #    Done by time 68, response to call at time 70 
        # Number of time periods until call arrives or end of horizon reached is
        #    a min(Geometric(0.07*0.8), 32) random variable.
        #    Expectation = (1 - 0.944^32)/0.056 time periods for call to arrive
        self.assertAlmostEqual(tau[48][2][2], 2 - (1 - 0.944**32)/0.056)

        # Test 2: Time 1 call (node 1), Base 1 response, Base 2 redeploy
        #    Done by time 27, call arrives at time 41
        self.assertAlmostEqual(tau[1][1][2], 14 - (1 - 0.944**73)/0.056)

        # Test 3: Time 1 call (node 1), Base 1 response, Base 1 redeploy
        #    Done by time 21, call arrives at time 70 
        self.assertAlmostEqual(tau[1][1][1], 49 - (1 - 0.944**79)/0.056)

        # Test 4: Time 73 call (node 2), Base 2 response, Base 3 redeploy
        #    Done by time 96, end of horizon (T = 100) reached
        self.assertAlmostEqual(tau[73][2][3], 4 - (1 - 0.951**4)/0.049)
    
if __name__ == '__main__':
    unittest.main() 
