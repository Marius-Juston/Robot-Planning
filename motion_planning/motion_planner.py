from abc import ABC, abstractmethod
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure


class MotionProfile(ABC):
    @abstractmethod
    def get_data(self) -> Dict[str, np.ndarray]:
        pass

    @abstractmethod
    def get_data_point(self, t) -> Dict[str, np.ndarray]:
        pass


class NthOrderSCurve:
    pass


class SCurve(MotionProfile):
    def get_data(self) -> Dict[str, np.ndarray]:
        pass

    def get_data_point(self, t) -> Dict[str, np.ndarray]:
        pass


class TrapezoidalCurve(MotionProfile):
    times = {}

    DOUBLE_TOLERANCE = 0.000000001

    def define_pos(self, ti, position, velocity, acceleration):

        def pos(t):
            return self.position(position, velocity, acceleration, t - ti)

        def vel(t):
            return self.velocity(velocity, acceleration, t - ti)

        return pos, vel

    def define_piece_wise(self):
        t_i = self.period
        p = self.s_final

        i = 0
        for m in self.motion[::-1]:
            time = m['time']

            self.conditions.append((t_i - time, t_i))
            t_i -= time
            p -= m['distance']
            v = m['velocity']
            a = m['acceleration']

            pos, vel = self.define_pos(t_i, p, v, a)

            self.p_result.append(pos)
            self.v_result.append(vel)
            self.a_result.append(a)

            i += 1

    def value(self, x) -> Dict[str, np.ndarray]:
        condition = self.get_condition(x)

        return {"time": x,
                "position": np.piecewise(x, condition, self.p_result),
                "velocity": np.piecewise(x, condition, self.v_result),
                "acceleration": np.piecewise(x, condition, self.a_result)
                }

        # a = {"time": x,
        #         "position": np.piecewise(x, condition, self.p_result),
        #         "velocity": np.piecewise(x, condition, self.v_result),
        #         "acceleration": np.piecewise(x, condition, self.a_result)
        #         }
        # return np.fromiter(a.items(), dtype=np.ndarray, count=len(a))

    def find_accelerating_constants(self, v_initial: float, v_final: float) \
            -> Dict[str, float]:
        delta_v = v_final - v_initial

        if delta_v == 0:
            return {"time": 0, "distance": 0, "velocity": v_initial, "acceleration": 0}

        accel_sign = np.sign(delta_v)
        a = accel_sign * self.acceleration_max
        t = delta_v / a
        d = (v_final ** 2 - v_initial ** 2) / (2 * a)

        return {"time": t, "distance": d, "velocity": v_initial, "acceleration": a}

    def find_flat_constants(self, d_a, d_b) -> Dict[str, float]:
        delta_d = self.delta_s - d_a - d_b
        t = delta_d / self.v_max

        return {"time": t, "distance": delta_d, "velocity": self.v_max, "acceleration": 0}

    def get_too_close_final_velocity(self, v_sign=1, inside=1):
        return v_sign * np.sqrt(
            abs(inside * 2 * self.acceleration_max * self.delta_s + self.v_final ** 2 + self.v_initial ** 2)) / np.sqrt(
            2)

    def __init__(self, s_initial, s_final, v_initial, v_final, v_max, acceleration_max) -> None:
        """
        :parameter s_initial: the initial position of the system
        :parameter s_final: the final position of the system
        :parameter v_initial: the initial velocity of the system
        :parameter v_final: the final velocity of the system
        :parameter v_max: the maximum velocity that the system will experience both negative or
                                    positive. This is the cruise velocity. This value should always be positive

        :parameter acceleration_max: the maximum acceleration that the system will experience both negative or
                                    positive. This value should always be positive
        """
        super().__init__()

        self.s_initial = s_initial
        self.s_final = s_final
        self.v_initial, self.v_final = np.clip((v_initial, v_final), -v_max, v_max)
        self.acceleration_max = acceleration_max
        self.delta_s = s_final - s_initial
        self.v_max = v_max * np.sign(self.delta_s)

        accel = self.find_accelerating_constants(v_initial, self.v_max)
        deccel = self.find_accelerating_constants(self.v_max, v_final)

        distance_accelerating = accel['distance']
        distance_decelerating = deccel['distance']

        if self.delta_s == distance_accelerating + distance_decelerating:
            self.motion = [accel, deccel]
        elif abs(distance_decelerating + distance_accelerating) > abs(self.delta_s):
            accel = {'distance': np.nan}
            deccel = {'distance': np.nan}

            i = 0
            j = 0

            v_sign = [1, -1]
            inside = [1, -1]

            while np.isnan(accel['distance']) or \
                    np.isnan(deccel['distance']) or \
                    abs(accel['distance'] + deccel['distance'] - self.delta_s) > TrapezoidalCurve.DOUBLE_TOLERANCE:
                v_middle = self.get_too_close_final_velocity(v_sign[i], inside[j])
                accel = self.find_accelerating_constants(self.v_initial, v_middle)
                deccel = self.find_accelerating_constants(v_middle, self.v_final)

                # print(v_middle, accel['distance'] + deccel['distance'], i, j)

                i += 1
                j += i // 2
                i %= 2

            self.motion = [accel, deccel]
        else:
            flat = self.find_flat_constants(distance_accelerating, distance_decelerating)
            self.motion = [accel, flat, deccel]

        for i in range(len(self.motion) - 1, -1, -1):
            if self.motion[i]['time'] <= 0:
                self.motion.remove(self.motion[i])

        self.period = sum(m['time'] for m in self.motion)

        self.conditions = []
        self.p_result = []
        self.v_result = []
        self.a_result = []

        self.define_piece_wise()

    @staticmethod
    def position(s, v, a, t):
        return s + v * t + t ** 2 / 2 * a

    @staticmethod
    def velocity(v, a, t):
        return v + a * t

    EMPTY = np.empty(1)

    def get_data_point(self, t) -> Dict[str, np.ndarray]:
        if self.period == 0:
            return {'time': TrapezoidalCurve.EMPTY, 'position': TrapezoidalCurve.EMPTY,
                    'velocity': TrapezoidalCurve.EMPTY, 'acceleration': TrapezoidalCurve.EMPTY}

        return self.value(t)

    def get_data(self, precision=1000) -> Dict[str, np.ndarray]:
        if self.period == 0:
            return {'time': TrapezoidalCurve.EMPTY, 'position': TrapezoidalCurve.EMPTY,
                    'velocity': TrapezoidalCurve.EMPTY, 'acceleration': TrapezoidalCurve.EMPTY}

        if precision not in TrapezoidalCurve.times:
            times = np.linspace(0, self.period, precision)
            TrapezoidalCurve.times[precision] = times
        else:
            times = TrapezoidalCurve.times[precision]

        return self.value(times)

    def get_condition(self, x):
        return list(
            np.logical_and(np.greater_equal(x, min_x), np.less_equal(x, max_x)) for (min_x, max_x) in self.conditions)


def merge(d1, d2):
    return {'time': np.concatenate((d1['time'], d2['time'] + d1['time'][-1])),
            'position': np.concatenate((d1['position'], d2['position'])),
            'velocity': np.concatenate((d1['velocity'], d2['velocity'])),
            'acceleration': np.concatenate((d1['acceleration'], d2['acceleration']))}


if __name__ == '__main__':
    mid = 0.2
    t = TrapezoidalCurve(0, mid, 0, 0, 3, 1)
    d = t.get_data()
    t = TrapezoidalCurve(mid, 0, 0, 0, 2, 1)
    t1 = t.get_data()
    d = np.concatenate((d, t1 + np.array([d[-1, 0], 0, 0, 0])))
    t = TrapezoidalCurve(0, 1, 0, -2, 2, 1)
    t1 = t.get_data()
    d = np.concatenate((d, t1 + np.array([d[-1, 0], 0, 0, 0])))

    fig: Figure = plt.gcf()
    p, v, a = fig.subplots(3, 1)
    p: Axes
    v: Axes
    a: Axes

    p.set_title("Position")
    p.grid(True)
    p.grid(True, 'minor', linewidth=.25)
    p.minorticks_on()

    v.set_title("Velocity")
    v.grid(True)
    v.grid(True, 'minor', linewidth=.25)
    v.minorticks_on()

    a.set_title("Acceleration")
    a.grid(True)
    a.grid(True, 'minor', linewidth=.25)
    a.minorticks_on()

    t = d['time']
    p_y = d['position']
    v_y = d['velocity']
    a_y = d['acceleration']

    p.plot(t, p_y)
    v.plot(t, v_y)
    a.plot(t, a_y)

    plt.tight_layout()
    plt.show()
