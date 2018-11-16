#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

data_in_nextline = False

throughputs = []

rkB_s_idx = -1
wkB_s_idx = -1

with open(sys.argv[1], 'r') as fp:
    for line in fp:
        if data_in_nextline:
            if line.strip():
                nums = line.split()
                throughputs.append(
                    float(nums[rkB_s_idx]) + float(nums[wkB_s_idx]))
            elif throughputs:
                throughputs.append(0)

            data_in_nextline = False
            continue

        if 'Device' in line:
            data_in_nextline = True

            if rkB_s_idx < 0 or wkB_s_idx < 0:
                headers = line.split()
                rkB_s_idx = headers.index('rkB/s')
                wkB_s_idx = headers.index('wkB/s')

with open('throughputs.iostat.csv', 'w') as fp:
    for idx, num in enumerate(throughputs):
        fp.write(str(idx * 3) + "," + str(num) + ",\n")
