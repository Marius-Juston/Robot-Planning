from timeit import timeit

import numpy as np


def pow(n, glob):
    print("Pow")
    # Pow
    # 49.673028200000005
    # 52.3007959
    # 57.53733650000001

    # BEST
    time = timeit("(a ** 2 for _ in range(n2))", number=n, globals=glob)
    print(time)

    time = timeit("(a * a for _ in range(n2))", number=n, globals=glob)
    print(time)

    time = timeit("(np.pow(a,2) for _ in range(n2))", number=n, globals=glob)
    print(time)


def addition(n, glob):
    # Addition
    # 52.083087199999994
    # 51.90162409999999

    print("Addition")
    time = timeit("(a + a for _ in range(n2))", number=n, globals=glob)
    print(time)

    # BEST
    time = timeit("(np.add(a,a) for _ in range(n2))", number=n, globals=glob)
    print(time)


def scalar_addition(n, glob):
    # Scalar Addition
    # 51.947033499999975
    # 51.84519300000005

    print("Scalar Addition")
    time = timeit("(10 + a for _ in range(n2))", number=n, globals=glob)
    print(time)

    time = timeit("(np.add(10,a) for _ in range(n2))", number=n, globals=glob)
    print(time)


def scalar_multiplication(n, glob):
    # Scalar Multiplication
    # 68.37454680000002
    # 80.71316100000001

    print("Scalar Multiplication")
    # BEST
    time = timeit("(10 * a for _ in range(n2))", number=n, globals=glob)
    print(time)

    time = timeit("(np.multiply(a,10) for _ in range(n2))", number=n, globals=glob)
    print(time)


def factor(n, glob):
    # Factor
    # 58.5694563
    # 56.279166
    # 57.05256050000001
    # 57.06471730000001

    print("Factor")
    time = timeit("((np.add(10 , a)) * a for _ in range(n2))", number=n, globals=glob)
    print(time)

    # BEST
    time = timeit("(np.add(10 * a , a ** 2) for _ in range(n2))", number=n, globals=glob)
    print(time)

    time = timeit("((10 +  a) * a for _ in range(n2))", number=n, globals=glob)
    print(time)

    time = timeit("(10 * a + a ** 2 for _ in range(n2))", number=n, globals=glob)
    print(time)


if __name__ == '__main__':
    a = np.full(10000000, 10)

    n = 100000000
    glob = {'a': a, "n2": 100000000}

    # pow(n, glob)
    # addition(n, glob)
    # scalar_addition(n, glob)
    # scalar_multiplication(n, glob)
    factor(n, glob)
