#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

import matplotlib.pyplot as plt
import matplotlib

from IPython.display import display, Markdown, HTML
from matplotlib.ticker import MultipleLocator

import util

BLOCK_SIZES = ['8KB', '4KB', '512B']
RWMIXREADS = [100, 65, 0]


def __get_avg_lat(profiles_dirname, block_size, rwmixread):
    """Get all average latency in profiles matching the block size and rwmixread.

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

        read_ios = util.get_num_in(profile, ['read', 'total_ios'])
        write_ios = util.get_num_in(profile, ['write', 'total_ios'])

        read_lat_mean = util.get_num_in(profile, ['read', 'lat_ns', 'mean'])
        write_lat_mean = util.get_num_in(profile, ['write', 'lat_ns', 'mean'])

        val = (read_lat_mean * read_ios +
               write_lat_mean * write_ios) / (read_ios + write_ios)
        values.append(val)

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
            rounds, values = __get_avg_lat(profiles_dirname, bs, rwmixread)
            bars.append(ax.errorbar(rounds, values, fmt='-o'))

            max_round = max(rounds[-1], max_round)

        ax.set_xticks(range(1, max_round + 1))

        ax.yaxis.set_minor_locator(MultipleLocator(2500))

        ax.grid(which='major', alpha=0.5)
        ax.grid(which='minor', alpha=0.2)

        ax.set_ylabel('Time (ns)')
        ax.set_xlabel('Round')

        plt.legend(
            bars,
            ['BS=' + bs for bs in BLOCK_SIZES],
            loc=8,
            bbox_to_anchor=(0.5, 1),
            frameon=False,
            ncol=3)
        plt.suptitle(
            'Steady State Convergence - R/W Mix=' +
            __get_rwmix_read2write(rwmixread),
            y=1.1)
        plt.show()


def plot_ss_measurement_window(profiles_dirname):
    display(Markdown('---'))
    _, ax = __create_subplots()

    # according to the SSS PTS v2.0.1, the dependent variable for the
    # Steady State Measurement Window plot is Ave 4KiB Random Write Latency.
    bs = BLOCK_SIZES[1]
    rwmixread = RWMIXREADS[0]

    rounds, values = __get_avg_lat(
        profiles_dirname, bs, rwmixread)

    bars, rounds_in_window, values_in_window, avg_value, poly = \
        util.plot_measurement_window(ax, rounds, values)

    ax.set_ylabel('Time (ns)')
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
        ['Ave Latency', 'Average', '110% * Average', '90% * Average', 'Slope'],
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

    avg_lat_trs = ''
    for bs in BLOCK_SIZES:
        avg_lat_tds = '<td><b>{bs}</b></td>'.format(bs=bs)
        for rwmixread in RWMIXREADS:
            _, values = __get_avg_lat(profiles_dirname, bs, rwmixread)
            avg_value = np.mean(util.get_values_in_window(values))
            avg_lat_tds += '<td>{avg_value:.3f}</td>'.format(
                avg_value=avg_value)

        avg_lat_trs += '<tr>' + avg_lat_tds + '</tr>'

    tabular_data = '''\
    <table>
      <caption><b>Avg Latency (ns) - ALL RW Mix & BS - Tabular Data</b></caption>
      <tr>
        <td rowspan="2"><b>Block Size</b></td>
        <td colspan="{num_rwmixreads}"><b>Read / Write Mix %</b></td>
      </tr>
      <tr>
        {rwmixread_tds}
      </tr>
      {avg_lat_trs}
    </table>\
    '''.format(
        num_rwmixreads=len(RWMIXREADS),
        rwmixread_tds=rwmixread_tds,
        avg_lat_trs=avg_lat_trs)

    display(Markdown('---'))
    display(HTML(tabular_data))
