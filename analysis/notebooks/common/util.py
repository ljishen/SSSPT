#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Useful utility functions for the data analysis Jupyter Notebook."""

import json
import glob
import operator
import re


FIG_DPI = 120


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
