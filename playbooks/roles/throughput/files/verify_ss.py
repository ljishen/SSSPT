#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to verify if the input values satisfy the criteria of steady state.

Definition of Steady State:
(https://www.snia.org/sites/default/files/technical_work/PTS/SSS_PTS_2.0.1.pdf)

Steady State: A device is said to be in Steady State when, for the dependent
variable (y) being tracked:
    a) Range(y) is less than 20% of Ave(y): Max(y)-Min(y) within the
       Measurement Window is no more than 20% of the Ave(y) within the
       Measurement Window; and
    b) Slope(y) is less than 10%: Max(y)-Min(y), where Max(y) and Min(y) are
       the maximum and minimum values on the best linear curve fit of the
       y-values within the Measurement Window, is within 10% of Ave(y) value
       within the Measurement Window.

Note that the length of measurement window is 4 according to the specific
performance test in the PTS (e.g. Throughput Test on page 37).

"""

import sys
import ast

import numpy as np

WINDOWN_LEN = 4


def main():
    """Perform verification.

    Exit status:
        1: Do not satisfy the criteria of steady state.
        0: Satisfy the criteria of steady state.

    """
    throughputs = ast.literal_eval(sys.argv[1])

    if len(throughputs) < WINDOWN_LEN:
        print('Minimum number of input values is', WINDOWN_LEN)
        exit(1)

    avg_val = np.mean(throughputs)
    if max(throughputs) - min(throughputs) > avg_val * 0.2:
        exit(1)

    coefficients = np.polyfit(range(WINDOWN_LEN), throughputs, 1)
    poly = np.poly1d(coefficients)
    if abs(poly(0) - poly(4)) > avg_val * 0.1:
        exit(1)

    exit(0)


if __name__ == "__main__":
    main()
