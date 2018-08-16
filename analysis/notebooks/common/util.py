#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Useful utility functions for the data analysis Jupyter Notebook."""

import json
import glob
import re


def get_profiles(profiles_dirname, block_size, rwmixread):
    """Return all profiles matching the block size and rwmixread.

    Args:
        block_size (str): The block size.
        rwmixread (int): The percentage of read in R/W mix.

    """
    profile_name_pattern = \
        '/wdpc_bs{:s}_read{:d}_round[0-9]*.json'.format(block_size, rwmixread)
    profiles = sorted(
        glob.glob('../data/' + profiles_dirname + profile_name_pattern))

    if not profiles:
        raise RuntimeError(
            'Cannot find any profiles with pattern %r' % profile_name_pattern)

    rounds = list(
        map(lambda s: int(re.search(r'round(\d+)', s).group(1)), profiles))

    return rounds, profiles


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
