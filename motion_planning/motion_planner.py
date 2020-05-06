from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure


class MotionProfile(ABC):
    @abstractmethod
    def get_data(self) -> Tuple[Tuple[float, float, float, float]]:
        pass


class NthOrderSCurve:
    pass


class TrapezoidalCurve(MotionProfile):
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

    def __init__(self, s_initial, s_final, v_initial, v_final, v_max, acceleration_max) -> None:
        super().__init__()

        self.s_initial = s_initial
        self.s_final = s_final
        self.v_initial = v_initial
        self.v_final = v_final
        self.v_max = v_max
        self.acceleration_max = acceleration_max
        self.delta_s = s_final - s_initial

        accel = self.find_accelerating_constants(v_initial, v_max)
        deccel = self.find_accelerating_constants(v_max, v_final)

        distance_accelerating = accel['distance']
        distance_decelerating = deccel['distance']

        if self.delta_s == distance_accelerating + distance_decelerating:
            self.motion = (accel, deccel)
        elif abs(distance_decelerating + distance_accelerating) > abs(self.delta_s):

            self.motion = (accel, deccel)
        else:
            flat = self.find_flat_constants(distance_accelerating, distance_decelerating)
            self.motion = (accel, flat, deccel)

        self.period = sum(m['time'] for m in self.motion)

    def position(self, s, v, a, t):
        return s + v * t + t ** 2 / 2 * a

    def velocity(self, v, a, t):
        return v + a * t

    def get_data_point(self, t) -> Optional[Tuple[float, float, float, float]]:
        if t > self.period:
            return None

        i = 0
        t_i = self.motion[i]['time']
        s = self.s_initial

        while t > t_i:
            s += self.motion[i]['distance']
            i += 1
            t_i += self.motion[i]['time']

        t_i -= self.motion[i]['time']
        t2 = t - t_i

        v = self.motion[i]['velocity']
        a = self.motion[i]['acceleration']

        p = self.position(s, v, a, t2)
        v = self.velocity(v, a, t2)

        return t, p, v, a

    def get_data(self, precision=1000) -> np.ndarray:
        return np.array([self.get_data_point(t) for t in np.linspace(0, self.period, precision)])


if __name__ == '__main__':
    t = TrapezoidalCurve(0, 10, 0, 0, 2, 1)

    d = t.get_data()

    fig: Figure = plt.gcf()
    p, v, a = fig.subplots(3, 1)

    p.grid(True)
    p.grid(True, 'minor', linewidth=.25)
    p.minorticks_on()

    v.grid(True)
    v.grid(True, 'minor', linewidth=.25)
    v.minorticks_on()

    a.grid(True)
    a.grid(True, 'minor', linewidth=.25)
    a.minorticks_on()

    t = d[:, 0]
    p_y = d[:, 1]
    v_y = d[:, 2]
    a_y = d[:, 3]

    p.plot(t, p_y)
    v.plot(t, v_y)
    a.plot(t, a_y)

    plt.tight_layout()
    plt.show()
