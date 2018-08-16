#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Useful utility functions for the data analysis Jupyter Notebook."""

import json
import glob
import operator
import re

import numpy as np


FIG_DPI = 120

_MEASUREMENT_WINDOW_SIZE = 5
_EXCURSION_THRESHOLD = 0.1
EXCURSION_UP = 1 + _EXCURSION_THRESHOLD
EXCURSION_DOWN = 1 - _EXCURSION_THRESHOLD


def get_values_in_window(values):
    """Return all the values with in the measurement window."""
    return values[-1 * _MEASUREMENT_WINDOW_SIZE:]


def plot_measurement_window(axes, rounds, values):
    """Plot the measurement window using the rounds and values."""
    rounds_in_window = get_values_in_window(rounds)
    values_in_window = get_values_in_window(values)

    bars = []

    # plot the line of raw values
    bars.append(axes.errorbar(rounds, values, fmt='-D'))

    # plot average lines
    avg_value = np.mean(values_in_window)
    times_to_shape = {1: '-s', EXCURSION_UP: '-^', EXCURSION_DOWN: '-v'}

    for time, shape in times_to_shape.items():
        bars.append(
            axes.errorbar(
                [rounds_in_window[0], rounds_in_window[-1]],
                [avg_value * time] * 2,
                fmt=shape)
        )

    # plot slope line
    coefficients = np.polyfit(rounds_in_window, values_in_window, 1)
    poly = np.poly1d(coefficients)
    bars.append(
        axes.errorbar(
            rounds_in_window,
            poly(rounds_in_window),
            fmt='-.')
    )

    axes.grid(which='major', alpha=0.5)

    return bars, rounds_in_window, values_in_window, avg_value, poly


def get_profiles(profiles_dirname, block_size, rwmixread):
    """Return all profiles matching the block size and rwmixread.

    Args:
        block_size (str): The block size.
        rwmixread (int): The percentage of read in R/W mix.

    """
    profile_name_pattern = \
        '/wdpc_bs{:s}_read{:d}_round[0-9]*.json'.format(block_size, rwmixread)
    profiles = glob.glob('../data/' + profiles_dirname + profile_name_pattern)

    if not profiles:
        raise RuntimeError(
            'Cannot find any profiles with pattern %r' % profile_name_pattern)

    round_profile_pairs = []
    for profile in profiles:
        round_profile_pairs.append(
            (int(re.search(r'round(\d+)', profile).group(1)),
             profile))

    return sorted(round_profile_pairs, key=operator.itemgetter(0))


def __get_job_obj(profile):
    """Return the 'job' object in the profile."""
    with open(profile, 'rt') as json_fobj:
        data = json.load(json_fobj)

    return data['jobs'][0]


def get_num_in(profile, key_path):
    """Return the value pointed by the key path in the JSON profile."""
    job = __get_job_obj(profile)

    obj = job
    for key in key_path:
        obj = obj[key]

    return obj
