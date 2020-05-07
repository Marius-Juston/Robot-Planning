import unittest

from motion_planning.motion_planner import TrapezoidalCurve


class TrapezoidTest(unittest.TestCase):

    def test_velocity_calculation(self):
        v = TrapezoidalCurve.velocity(0, 0, 0)
        self.assertEqual(0, v)

        v = TrapezoidalCurve.velocity(0, 1, 1)
        self.assertEqual(1, v)

        v = TrapezoidalCurve.velocity(-1, 0, 2)
        self.assertEqual(-1, v)

        v = TrapezoidalCurve.velocity(-1000, 1000, 1000)
        self.assertEqual(1000 * 1000 - 1000, v)

    def test_position_calculation(self):
        v = TrapezoidalCurve.position(0, 0, 0, 0)
        self.assertEqual(0, v)

        v = TrapezoidalCurve.position(-1, 0, 0, 0)
        self.assertEqual(-1, v)

        v = TrapezoidalCurve.position(1, 0, 0, 0)
        self.assertEqual(1, v)

        v = TrapezoidalCurve.position(1, 1, 0, 1)
        self.assertEqual(2, v)

        v = TrapezoidalCurve.position(-1, 1, 2, 1)
        self.assertEqual(1, v)


if __name__ == '__main__':
    TrapezoidTest().run()
