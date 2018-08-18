#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import numpy as np

import matplotlib.pyplot as plt
import matplotlib

from IPython.display import display, Markdown, HTML
from mpl_toolkits.mplot3d import Axes3D

import util


BLOCK_SIZES = ['1024KB', '128KB', '64KB', '32KB', '16KB', '8KB', '4KB', '512B']
RWMIXREADS = [100, 95, 65, 50, 35, 5, 0]

# I/O patterns for ploting IOPS SS measurement window:
#   - Ave RND 4KiB Write
#   - Ave RND 64K R/W% 65:35
#   - Ave RND 1024K Read
MEASUREMENT_WINDOW_VARS_INXES = [(6, 6), (2, 2), (0, 0)]


def __get_avg_iops(profiles_dirname, block_size, rwmixread):
    """Get all average IOPS in profiles matching the block size and rwmixread.

    Args:
        profiles_dirname (str): The name of the profile folder.
        block_size (str): The block size.
        rwmixread (int): The percentage of read in read/write mix I/O.

    """
    rounds = []
    values = []

    round_profile_pairs = util.get_profiles(
        profiles_dirname, block_size, rwmixread)
    for rpp in round_profile_pairs:
        rounds.append(rpp[0])
        profile = rpp[1]

        runtime = util.get_num_in(profile, ['read', 'runtime'])
        if runtime == 0:
            runtime = util.get_num_in(profile, ['write', 'runtime'])
        runtime_in_seconds = runtime / 1000

        total_iops = util.get_num_in(profile, ['read', 'total_ios']) + \
            util.get_num_in(profile, ['write', 'total_ios'])

        values.append(total_iops / runtime_in_seconds)

    return rounds, values


def __create_subplots():
    fig, ax = plt.subplots()

    # Change the size of figure
    # See https://stackoverflow.com/a/4306340
    fig.set_dpi(util.FIG_DPI)

    return fig, ax


def __get_rwmix_read2write(rwmixread):
    return str(rwmixread) + '/' + str(100 - rwmixread)


def plot_ss_convergence(profiles_dirname):
    for rwmixread in RWMIXREADS:
        display(Markdown('---'))
        _, ax = __create_subplots()

        max_round = 1
        bars = []
        for bs in BLOCK_SIZES:
            rounds, values = __get_avg_iops(profiles_dirname, bs, rwmixread)
            bars.append(ax.errorbar(rounds, values, fmt='-o'))

            max_round = max(rounds[-1], max_round)

        ax.set_xticks(range(1, max_round + 1))
        ax.grid(which='major', alpha=0.5)
        ax.set_ylabel('IOPS')
        ax.set_xlabel('Round')

        plt.legend(
            bars,
            ['BS=' + bs for bs in BLOCK_SIZES],
            loc=8,
            bbox_to_anchor=(0.5, 1),
            frameon=False,
            ncol=4)
        plt.suptitle(
            'Steady State Convergence - R/W Mix=' +
            __get_rwmix_read2write(rwmixread),
            y=1.1)
        plt.show()


def plot_ss_measurement_window(profiles_dirname):
    for vars_idxes in MEASUREMENT_WINDOW_VARS_INXES:
        display(Markdown('---'))
        _, ax = __create_subplots()

        bs = BLOCK_SIZES[vars_idxes[0]]
        rwmixread = RWMIXREADS[vars_idxes[1]]

        rounds, values = __get_avg_iops(
            profiles_dirname, bs, rwmixread)

        bars, rounds_in_window, values_in_window, avg_value, poly = \
            util.plot_measurement_window(ax, rounds, values)

        ax.set_ylabel('IOPS')
        ax.set_xlabel('Round')

        verification_report = '''\
        <table>
          <caption><b>Block Size = {bs}, R/W Mix % = {rwmixread}:{rwmixwrite}</b></caption>
          <tr>
            <td><b>Measurement Window</b></td>
            <td>{start} - {end}</td>
          </tr>
          <tr>
            <td><b>Ave. value in Measurement Window</b></td>
            <td>{avg:.3f}</td>
          </tr>
          <tr>
            <td><b>Calculated allowed range in Measurement Window (+-10% of Ave.)</b></td>
            <td>{excursion_up_val:.3f} (Max) / {excursion_down_val:.3f} (Min)</td>
          </tr>
          <tr>
            <td><b>Measured range in Measurement Window</b></td>
            <td>{max_val:.3f} (Max) / {min_val:.3f} (Min)  (<b>pass</b>)</td>
          </tr>
          <tr>
            <td><b>Slope of best linear fit in Measurement Window (must be &lt;= 10%)</b></td>
            <td>{max_excursion_percentage:.3f}% (<b>pass</b>)</td>
          </tr>
          <tr>
            <td><b>Least Squares Linear Fit Formula</b></td>
            <td>{formula}</td>
          </tr>
        </table><br/>\
        '''.format(
            bs=bs,
            rwmixread=rwmixread,
            rwmixwrite=100 - rwmixread,
            start=rounds_in_window[0],
            end=rounds_in_window[-1],
            avg=avg_value,
            excursion_up_val=avg_value * util.EXCURSION_UP,
            excursion_down_val=avg_value * util.EXCURSION_DOWN,
            max_val=max(values_in_window),
            min_val=min(values_in_window),
            max_excursion_percentage=100 * max(abs(1 - poly(rounds_in_window[0]) / avg_value),
                                               abs(1 - poly(rounds_in_window[-1]) / avg_value)),
            formula=poly)
        display(HTML(verification_report))

        plt.legend(
            bars,
            ['IOPS', 'Average', '110% * Average', '90% * Average', 'Slope'],
            loc=8,
            bbox_to_anchor=(0.5, 1),
            frameon=False,
            ncol=3,
            prop={'size': 9})
        plt.title('Steady State Measurement Window - RND/' + bs + ' RW' +
                  str(rwmixread),
                  y=1.2)
        plt.show()


def plot_measurement_window_tabular(profiles_dirname):
    rwmixread_tds = ''
    for rwmixread in RWMIXREADS:
        rwmixread_tds += '<td><b>{rwmixread}/{rwmixwrite}</b></td>'.format(
            rwmixread=rwmixread,
            rwmixwrite=(100 - rwmixread))

    avg_iops_trs = ''
    for bs in BLOCK_SIZES:
        avg_iops_tds = '<td><b>{bs}</b></td>'.format(bs=bs)
        for rwmixread in RWMIXREADS:
            _, values = __get_avg_iops(profiles_dirname, bs, rwmixread)
            avg_value = np.mean(util.get_values_in_window(values))
            avg_iops_tds += '<td>{avg_value:.3f}</td>'.format(
                avg_value=avg_value)

        avg_iops_trs += '<tr>' + avg_iops_tds + '</tr>'

    tabular_data = '''\
    <table>
      <caption><b>IOPS - ALL RW Mix & BS - Tabular Data</b></caption>
      <tr>
        <td rowspan="2"><b>Block Size</b></td>
        <td colspan="{num_rwmixreads}"><b>Read / Write Mix %</b></td>
      </tr>
      <tr>
        {rwmixread_tds}
      </tr>
      {avg_iops_trs}
    </table>\
    '''.format(
        num_rwmixreads=len(RWMIXREADS),
        rwmixread_tds=rwmixread_tds,
        avg_iops_trs=avg_iops_trs)

    display(Markdown('---'))
    display(HTML(tabular_data))


def __reverse_block_sizes():
    rev_block_sizes = [int(re.sub('[^0-9]', '', bs)) for bs in BLOCK_SIZES]
    # change the last one from 512B to 0.5KB
    rev_block_sizes[-1] = 0.5

    rev_block_sizes.reverse()
    return rev_block_sizes


def plot_measurement_window_2d(profiles_dirname):
    display(Markdown('---'))
    _, ax = __create_subplots()

    xticks = __reverse_block_sizes()

    bars = []
    for rwmixread in RWMIXREADS:
        avg_values = []
        for bs in BLOCK_SIZES:
            _, values = __get_avg_iops(profiles_dirname, bs, rwmixread)
            avg_values.append(np.mean(util.get_values_in_window(values)))

        avg_values.reverse()
        bars.append(ax.errorbar(xticks, avg_values, fmt='-o'))

    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xticks(xticks)
    ax.set_xlim(xmin=xticks[0])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

    ax.set_ylim(ymin=1, ymax=10**5)

    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    ax.set_ylabel('IOPS')
    ax.set_xlabel('Block Size (KB)')

    plt.legend(
        bars,
        [__get_rwmix_read2write(rwmixread) for rwmixread in RWMIXREADS],
        loc=8,
        bbox_to_anchor=(0.5, 1),
        frameon=False,
        ncol=4)
    plt.title('IOPS - ALL RW Mix & BS - 2D Plot', y=1.2)
    plt.show()


def plot_measurement_window_3d(profiles_dirname):
    display(Markdown('---'))

    fig = plt.figure()
    fig.set_dpi(util.FIG_DPI)
    ax = fig.add_subplot(111, projection='3d')

    bin_width = 0.5
    font_size = 8

    x_inits = [x + bin_width / 2 for x in range(len(BLOCK_SIZES))]

    for idx, rwmixread in enumerate(reversed(RWMIXREADS)):
        y_inits = [idx + bin_width / 2] * len(x_inits)
        z_inits = np.zeros_like(x_inits)

        top = []
        for bs in reversed(BLOCK_SIZES):
            _, values = __get_avg_iops(profiles_dirname, bs, rwmixread)
            avg_value = np.mean(util.get_values_in_window(values))
            top.append(avg_value)

        bar3d = ax.bar3d(
            x_inits, y_inits, z_inits,
            bin_width, bin_width, top,
            shade=True,
            label=__get_rwmix_read2write(rwmixread))

        # temporary fix for Poly3DCollection' object has no attribute '_facecolors2d
        # https://github.com/matplotlib/matplotlib/issues/4067#issuecomment-357794003
        bar3d._facecolors2d = bar3d._facecolors3d
        bar3d._edgecolors2d = bar3d._edgecolors3d

    ax.set_xticks(np.arange(bin_width, len(BLOCK_SIZES), step=1))
    ax.set_xticklabels(__reverse_block_sizes(), fontsize=font_size)

    ax.set_xlabel('Block Size (KB)')

    ax.set_yticks(np.arange(bin_width, len(RWMIXREADS), step=1))
    ax.set_yticklabels(
        [__get_rwmix_read2write(rwmixread) for rwmixread in
         reversed(RWMIXREADS)],
        fontsize=font_size)

    ax.set_ylabel('R/W Mix %')

    ax.tick_params(axis='z', labelsize=font_size)
    ax.set_zlabel('IOPS', rotation=90)

    ax.legend(
        loc=8,
        bbox_to_anchor=(0.5, 0.9),
        frameon=False,
        ncol=4)

    plt.title('IOPS - ALL RW Mix & BS - 3D Columns', y=1.2)

#     ax.view_init(azim=150)

    plt.tight_layout()
    plt.show()
