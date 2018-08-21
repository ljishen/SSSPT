#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

from IPython.display import display, Markdown, HTML

import util


def __get_avg_bws(profiles_dirname, block_size, mode):
    """Get all average bandwidths in profiles matching the block size and mode.

    Args:
        profiles_dirname (str): The name of the profile folder.
        block_size (str): The block size.
        mode (str): Must be either 'read' or 'write'.

    """
    if mode == 'read':
        rwmixread = 100
    elif mode == 'write':
        rwmixread = 0
    else:
        raise RuntimeError("mode must be either 'read' or 'write'")

    rounds = []
    values = []

    round_profile_pairs = util.get_profiles(
        profiles_dirname, block_size, rwmixread)
    for rpp in round_profile_pairs:
        rounds.append(rpp[0])
        profile = rpp[1]
        bw_mb = util.get_num_in(profile, [mode, 'bw']) / 1024
        values.append(bw_mb)

    return rounds, values


def __create_subplots():
    fig, axes = plt.subplots(1, len(MODES), sharey='row')

    # Change the size of figure
    # See https://stackoverflow.com/a/4306340
    fig.set_dpi(util.FIG_DPI)

    return fig, axes


MODES = ['read', 'write']
BLOCK_SIZES = ['4KB', '8KB', '16KB', '32KB', '128KB', '1024KB']


def plot_ss_convergence(profiles_dirname):
    _, axes = __create_subplots()

    cur_max = 0
    for idx, mode in enumerate(MODES):
        ax = axes[idx]

        bars = []
        for bs in BLOCK_SIZES:
            rounds, values = __get_avg_bws(profiles_dirname, bs, mode)
            bars.append(ax.errorbar(rounds, values, fmt='-o'))

            cur_max = max(max(values), cur_max)

        ymax = cur_max + 100
        ax.set_yticks(np.arange(0, ymax, 25), minor=True)
        ax.set_ylim(ymin=0, ymax=ymax)
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
        ax.set_ylabel(mode.capitalize() + ' - Throughput (MB/s)')
        ax.set_xlabel('Round')

    plt.figlegend(
        bars,
        ['BS=' + bs for bs in BLOCK_SIZES],
        loc=8,
        bbox_to_anchor=(0.5, 0.9),
        frameon=False,
        ncol=2)
    plt.suptitle('Steady State Convergence - SEQ R/W', y=1.05)
    plt.show()


def plot_ss_measurement_window(profiles_dirname):
    for mode in MODES:
        display(Markdown('---'))

        for idx, bs in enumerate(BLOCK_SIZES):
            ax_idx = idx % 2
            if ax_idx == 0:
                _, axes = __create_subplots()

            ax = axes[ax_idx]

            rounds, values = __get_avg_bws(profiles_dirname, bs, mode)

            bars, rounds_in_window, values_in_window, avg_value, poly = \
                util.plot_measurement_window(ax, rounds, values)

            ax.set_ylabel('BS=' + bs + ' - Throughput (MB/s)')
            ax.set_xlabel('Round')

            verification_report = '''\
            <table>
              <caption><b>Block Size: {bs}</b></caption>
              <tr>
                <td><b>Measurement Window</b></td>
                <td>{start} - {end}</td>
              </tr>
              <tr>
                <td><b>Ave. value in Measurement Window</b></td>
                <td>{avg:.3f} MB/s</td>
              </tr>
              <tr>
                <td><b>Calculated allowed range in Measurement Window (+-10% of Ave.)</b></td>
                <td>{excursion_up_val:.3f} MB/s (Max) / {excursion_down_val:.3f} MB/s (Min)</td>
              </tr>
              <tr>
                <td><b>Measured range in Measurement Window</b></td>
                <td>{max_val:.3f} MB/s (Max) / {min_val:.3f} MB/s (Min)  (<b>pass</b>)</td>
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

            if ax_idx == 1:
                plt.figlegend(
                    bars,
                    ['Throughputs',
                     'Average',
                     '110% * Average',
                     '90% * Average',
                     'Slope'],
                    loc=8,
                    bbox_to_anchor=(0.5, 0.9),
                    frameon=False,
                    ncol=3,
                    prop={'size': 9})
                plt.suptitle(
                    'Steady State Measurement Window - SEQ ' +
                    mode.capitalize(),
                    y=1.1)
                plt.show()


def plot_tp_measurement(profiles_dirname):
    display(Markdown('---'))

    for idx, bs in enumerate(BLOCK_SIZES):
        ax_idx = idx % 2
        if ax_idx == 0:
            _, axes = __create_subplots()

        ax = axes[ax_idx]

        for mode in MODES:
            _, values = __get_avg_bws(profiles_dirname, bs, mode)
            values_in_window = util.get_values_in_window(values)
            avg_value = np.mean(values_in_window)

            ax.bar(mode, avg_value)
            ax.text(
                mode,
                avg_value * 1.01,
                '{:.3f}'.format(avg_value),
                fontsize=7,
                ha='center',
                va='bottom')

        ax.set_ylabel('BS=' + bs + ' - Throughput (MB/s)')

        if ax_idx == 1:
            plt.suptitle('Average Throughput - SEQ R/W')
