import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure


class NthOrderSCurve:
    pass


class TrapezoidalCurve:
    def find_constants(self, v_initial, v_final, acceleration_max):
        delta_v = v_final - v_initial
        accel_sign = np.sign(delta_v)

        a = accel_sign * acceleration_max
        t_a = delta_v / a
        d = (v_final ** 2 - v_initial ** 2) / (2 * a)

        def motion(s_initial, t):
            s = s_initial + v_initial * t + a * t ** 2 / 2
            v = v_initial + a * t
            return s, v, a

        return t_a, d, a, motion

    def find_flat(self, s_initial, s_final, d_a, d_b, v_max):
        delta = (s_final - s_initial) - d_a - d_b
        t_c = delta / v_max

        def motion(s_initial, t):
            s = s_initial + v_max * t
            return s, v_max, 0

        return t_c, delta, 0, motion

    def __init__(self, s_initial, s_final, v_initial, v_final, v_max, acceleration_max) -> None:
        super().__init__()

        self.s_initial = s_initial

        self.times = []
        self.motion = []

        t_a, d_a, a_up, m_a = self.find_constants(v_initial, v_max, acceleration_max)
        t_b, d_b, a_down, m_b = self.find_constants(v_max, v_final, acceleration_max)

        delta_s = s_final - s_initial

        if d_a + d_b == delta_s:
            self.times = [t_a, t_b]
            self.motion = [m_a, m_b]

        if abs(d_a + d_b) > abs(delta_s):
            self.times = []
        else:
            t_c, d_c, a_flat, m_c = self.find_flat(s_initial, s_final, d_a, d_b, v_max)
            self.times = [t_a, t_c, t_b]
            self.motion = [m_a, m_c, m_b]

    def draw_motion(self, precision=50):
        time = np.linspace(0, np.sum(self.times), precision)

        index = 0

        fig: Figure = plt.figure()
        position, velocity, acceleration = fig.subplots(3, 1, sharex=True)

        s_initial = self.s_initial

        p_s = []
        v_s = []
        a_s = []

        t_i = 0

        stop = False

        for t in time:
            while (t - t_i) >= self.times[index]:
                t_i += self.times[index]
                index += 1

                if index >= len(self.times):
                    stop = True
                    break

                s_initial = p_s[-1]

            if stop:
                break

            p, v, a = self.motion[index](s_initial, t - t_i)
            p_s.append(p)
            v_s.append(v)
            a_s.append(a)

        t = time[:len(p_s)]
        position.plot(t, p_s)
        velocity.plot(t, v_s)
        acceleration.plot(t, a_s)

        position.grid()
        position.minorticks_on()
        velocity.grid()
        velocity.minorticks_on()
        acceleration.grid()
        acceleration.minorticks_on()

        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    t = TrapezoidalCurve(5, -10, -1, -3, -1.5, 5)
    t.draw_motion(500)
