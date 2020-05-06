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

    def get_too_close_final_velocity(self, solution=1):
        return solution * np.sqrt(
            solution * 2 * self.acceleration_max * self.delta_s + self.v_final ** 2 + self.v_initial ** 2) / np.sqrt(
            2)

    def clip(self, min_x, max_x, x):
        return min(max_x, max(min_x, x))

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
        self.v_initial = self.clip(-v_max, v_max, v_initial)
        self.v_final = self.clip(-v_max, v_max, v_final)
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
            v_f = self.get_too_close_final_velocity()
            print(v_f)

            accel = self.find_accelerating_constants(self.v_initial, v_f)
            deccel = self.find_accelerating_constants(v_f, self.v_final)

            if accel['distance'] + accel['distance'] != self.delta_s:
                v_f = self.get_too_close_final_velocity(-1)
                accel = self.find_accelerating_constants(self.v_initial, v_f)
                deccel = self.find_accelerating_constants(v_f, self.v_final)

            self.motion = [accel, deccel]
        else:
            flat = self.find_flat_constants(distance_accelerating, distance_decelerating)
            self.motion = [accel, flat, deccel]

        for i in range(len(self.motion) - 1, -1, -1):
            if self.motion[i]['time'] <= 0:
                self.motion.remove(self.motion[i])

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
    mid = -.25
    t = TrapezoidalCurve(0, mid, 1, 3, 3, 1)
    d = t.get_data()
    # t = TrapezoidalCurve(mid, 5, 0, 0, 2, 1)
    # t1 = t.get_data()
    # d = np.concatenate((d, t1 + np.array([d[-1, 0], 0, 0, 0])))

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
