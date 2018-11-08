#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

data_in_nextline = False

throughputs = []

with open(sys.argv[1], 'r') as fp:
    for line in fp:
        if data_in_nextline:
            if line.strip():
                nums = line.split()
                throughputs.append(float(nums[5]) + float(nums[6]))

            data_in_nextline = False
            continue

        if 'Device:' in line:
            data_in_nextline = True

with open('throughputs.iostat.csv', 'w') as fp:
    for idx, num in enumerate(throughputs):
        fp.write(str(idx * 3) + "," + str(num) + ",\n")
