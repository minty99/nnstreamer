#!/usr/bin/env python

##
# SPDX-License-Identifier: LGPL-2.1-only
#
# Copyright (C) 2018 Samsung Electronics
#
# @file generateGoldenTestResult.py
# @brief Generate golden test results for test cases
# @author MyungJoo Ham <myungjoo.ham@samsung.com>

from __future__ import print_function

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from test_utils import convert_to_bytes
import gen24bBMP as bmp

# Allow to create specific cases only if proper argument is given
target = -1  # -1 == ALL
if len(sys.argv) >= 2:  # There's some arguments
    target = int(sys.argv[1])

if target == -1 or target == 1:
    bmp.write('testcase01.rgb.golden', bmp.gen_RGB()[0])
    bmp.write('testcase01.bgrx.golden', bmp.gen_BGRx()[0])
    bmp.write('testcase01.gray8.golden', bmp.gen_GRAY8()[0])
if target == -1 or target == 2:
    bmp.write('testcase02_RGB_640x480.golden', bmp.gen_BMP_random('RGB', 640, 480, 'testcase02')[0])
    bmp.write('testcase02_BGRx_640x480.golden', bmp.gen_BMP_random('BGRx', 640, 480, 'testcase02')[0])
    bmp.write('testcase02_GRAY8_640x480.golden', bmp.gen_BMP_random('GRAY8', 640, 480, 'testcase02')[0])
    bmp.write('testcase02_RGB_642x480.golden', bmp.gen_BMP_random('RGB', 642, 480, 'testcase02')[0])
    bmp.write('testcase02_BGRx_642x480.golden', bmp.gen_BMP_random('BGRx', 642, 480, 'testcase02')[0])
    bmp.write('testcase02_GRAY8_642x480.golden', bmp.gen_BMP_random('GRAY8', 642, 480, 'testcase02')[0])
if target == -1 or target == 8:
    bmp.gen_BMP_stream('testsequence', 'testcase08.golden', 1)
if target == -1 or target == 9:
    buf = bmp.gen_BMP_random('RGB', 100, 100, 'testcase02')[0]
    bmp.write('testcase01_RGB_100x100.golden', buf)
    bmp.write('testcase02_RGB_100x100.golden', buf + buf)
    bmp.write('testcase03_RGB_100x100.golden', buf + buf + buf)
    bmp.write('testcase04_RGB_100x100.golden', buf + buf + buf + buf)
    bmp.gen_BMP_stream('testsequence01', 'testcase01.golden', 1)
    bmp.gen_BMP_stream('testsequence02', 'testcase02.golden', 2)
    s = bmp.gen_BMP_stream('testsequence03', 'testcase03.golden', 3)
    bmp.gen_BMP_stream('testsequence04', 'testcase04.golden', 4)
    for i in range(0, 4):
        sink_0 = i * 3
        with open('testsynch00_' + str(i) + '.golden', 'wb') as file:
            file.write(s[sink_0])
            file.write(s[i])

    for i in range(0, 10):
        sink_1 = i // 3
        with open('testsynch03_' + str(i) + '.golden', 'wb') as file:
            file.write(s[i])
            file.write(s[sink_1])

    id0 = [0, 1, 1, 2, 3, 3, 4, 5, 5, 6]
    for i in range(0, 10):
        sink_1 = id0[i]
        with open('testsynch04_' + str(i) + '.golden', 'wb') as file:
            file.write(s[i])
            file.write(s[sink_1])

    id0 = [0, 2, 3, 5, 6, 8, 9]
    for i in range(0, 7):
        sink_0 = id0[i]
        with open('testsynch01_' + str(i) + '.golden', 'wb') as file:
            file.write(s[sink_0])
            file.write(s[i])

    for i in range(0, 4):
        sink_0 = i * 3
        sink_1 = i * 2
        with open('testsynch02_' + str(i) + '.golden', 'wb') as file:
            file.write(s[sink_0])
            file.write(s[sink_1])
            file.write(s[i])

    id0 = [0, 1, 1, 2, 3, 3, 4, 5, 5, 6]
    for i in range(0, 10):
        sink_0 = id0[i]
        sink_1 = i // 3
        with open('testsynch05_' + str(i) + '.golden', 'wb') as file:
            file.write(s[i])
            file.write(s[sink_0])
            file.write(s[sink_1])

    id0 = [0, 4, 7, 9]
    for i in range(0, 4):
        sink_0 = id0[i]
        with open('testsynch07_' + str(i) + '.golden', 'wb') as file:
            file.write(s[i])
            file.write(s[sink_0])

    for i in range(0, 4):
        sink_0 = i * 3
        with open('testsynch08_' + str(i) + '.golden', 'wb') as file:
            file.write(s[i])
            file.write(s[sink_0])

    for i in range(0, 4):
        sink_0 = i * 2
        sink_1 = i * 3
        with open('testsynch17_' + str(i) + '.golden', 'wb') as file:
            file.write(s[i])
            file.write(s[sink_0])
            file.write(s[sink_1])

    for i in range(0, 4):
        sink_0 = i * 2
        sink_1 = i * 3
        with open('testsynch18_' + str(i) + '.golden', 'wb') as file:
            file.write(s[i])
            file.write(s[sink_0])
            file.write(s[sink_1])
            file.write(s[sink_0])

    id0_0 = [0, 0, 1, 1, 2]
    id0_1 = [0, 0, 2, 2, 4]
    id1_0 = [0, 2, 3, 5, 6]
    id1_1 = [0, 1, 2, 3, 4]
    for i in range(0, 5):
        sink0_0 = id0_0[i]
        sink0_1 = id0_1[i]
        sink1_0 = id1_0[i]
        sink1_1 = id1_1[i]
        with open('testsynch19_' + str(i) + '.golden', 'wb') as file:
            file.write(s[sink0_0])
            file.write(s[sink0_1])
            file.write(s[sink1_0])
            file.write(s[sink1_1])

if target == -1 or target == 10:
    buf = bmp.gen_BMP_random('RGB', 100, 100, 'testcase')[0]
    bmp.write('testcase.golden', buf)
    bmp.gen_BMP_stream('testsequence', 'testcase_stream.golden', 1)
if target == -1 or target == 11:
    buf = bmp.gen_BMP_random('RGB', 100, 100, 'testcase')[0]
    bmp.write('testcase_0_0.golden', buf)

    s = b''
    for y in range(0, 100):
        for x in range(0, 100):
            s += convert_to_bytes(buf[y * 100 + x])
    bmp.write('testcase_1_0.golden', s)

    s = b''
    for i in range(1, 3):
        for y in range(0, 100):
            for x in range(0, 100):
                s += convert_to_bytes(buf[y * 100 + x + i * 100 * 100])
    bmp.write('testcase_1_1.golden', s)

    for i in range(0, 3):
        s = b''
        for y in range(0, 100):
            for x in range(0, 100):
                s += convert_to_bytes(buf[y * 100 + x + i * 100 * 100])
        bmp.write('testcase_2_' + str(i) + '.golden', s)

    string = bmp.gen_BMP_stream('testsequence', 'testcase_stream.golden', 1)

    s = b''
    for i in range(0, 10):
        for y in range(0, 16):
            for x in range(0, 16):
                s += convert_to_bytes(string[i][y * 16 + x])
    bmp.write('testcase_stream_1_0.golden', s)

    s = b''
    for i in range(0, 10):
        for j in range(1, 3):
            for y in range(0, 16):
                for x in range(0, 16):
                    s += convert_to_bytes(string[i][j * 16 * 16 + y * 16 + x])
    bmp.write('testcase_stream_1_1.golden', s)

    for j in range(0, 3):
        s = b''
        for i in range(0, 10):
            for y in range(0, 16):
                for x in range(0, 16):
                    s += convert_to_bytes(string[i][j * 16 * 16 + y * 16 + x])
        bmp.write('testcase_stream_2_' + str(j) + '.golden', s)

if target == -1 or target == 12:
    string = bmp.gen_BMP_stream('testsequence', 'testsequence.golden', 1)
    for i in range(1, 11):
        with open('testsequence_' + str(i) + '.golden', 'wb') as file:
            file.write(string[i - 1])
