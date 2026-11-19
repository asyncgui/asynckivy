'''
Unlike `benchmark_sync_attrs.py`, this one includes the cost of creating, entering, and leaving context managers.
'''

from functools import partial
from timeit import timeit
from types import SimpleNamespace as Destination
from contextlib import ExitStack

from kivy.event import EventDispatcher
from kivy.properties import NumericProperty
import asynckivy as ak
from asynckivy._etc import sync_attr


class Source(EventDispatcher):
    value = NumericProperty(0)


def _benchmark_sync_attrs(src, dests, n_source_changes):
    with ak.sync_attrs((src, "value"), *[(d, "value") for d in dests]):
        for __ in range(n_source_changes):
            src.value += 1
def benchmark_sync_attrs(n_dests, n_source_changes):
    return timeit(partial(
        _benchmark_sync_attrs, 
        Source(),
        [Destination() for _ in range(n_dests)],
        n_source_changes,
    ))


def _benchmark_sync_attr_with_ExitStack(src, dests, n_source_changes):
    with ExitStack() as stack:
        ec = stack.enter_context
        sync_attr = ak.sync_attr
        for d in dests:
            ec(sync_attr((src, "value"), (d, "value")))
        for __ in range(n_source_changes):
            src.value += 1
def benchmark_sync_attr_with_ExitStack(n_dests, n_source_changes):
    return timeit(partial(
        _benchmark_sync_attr_with_ExitStack, 
        Source(),
        [Destination() for _ in range(n_dests)],
        n_source_changes,
    ))


def _benchmark_sync_attr_1(src, dests, n_source_changes):
    with sync_attr((src, "value"), (dests[0], "value")):
        for __ in range(n_source_changes):
            src.value += 1
def _benchmark_sync_attr_2(src, dests, n_source_changes):
    with (
        sync_attr((src, "value"), (dests[0], "value")),
        sync_attr((src, "value"), (dests[1], "value")),
    ):
        for __ in range(n_source_changes):
            src.value += 1
def _benchmark_sync_attr_3(src, dests, n_source_changes):
    with (
        sync_attr((src, "value"), (dests[0], "value")),
        sync_attr((src, "value"), (dests[1], "value")),
        sync_attr((src, "value"), (dests[2], "value")),
    ):
        for __ in range(n_source_changes):
            src.value += 1
def _benchmark_sync_attr_4(src, dests, n_source_changes):
    with (
        sync_attr((src, "value"), (dests[0], "value")),
        sync_attr((src, "value"), (dests[1], "value")),
        sync_attr((src, "value"), (dests[2], "value")),
        sync_attr((src, "value"), (dests[3], "value")),
    ):
        for __ in range(n_source_changes):
            src.value += 1
def benchmark_sync_attr_without_ExitStack(n_dests, n_source_changes):
    return timeit(partial(
        _benchmark_sync_attr_1 if n_dests == 1 else
        _benchmark_sync_attr_2 if n_dests == 2 else
        _benchmark_sync_attr_3 if n_dests == 3 else
        _benchmark_sync_attr_4 if n_dests == 4 else
        None,
        Source(),
        [Destination() for _ in range(n_dests)],
        n_source_changes,
    ))


N_SYNC_SOURCE_CHANGES_LIST = (0, 1, 2, 8)
N_SYNC_DESTS_LIST = (1, 2, 3, 4)


def benchmark_and_stdout():
    for n_source_changes in N_SYNC_SOURCE_CHANGES_LIST:
        for n_dests in N_SYNC_DESTS_LIST:
            sync_attrs_time = benchmark_sync_attrs(n_dests, n_source_changes)
            sync_attr_time = benchmark_sync_attr_without_ExitStack(n_dests, n_source_changes)
            sync_attr_with_ExitStack_time = benchmark_sync_attr_with_ExitStack(n_dests, n_source_changes)
            print("-----------------------------")
            print(f"Number of sync destinations: {n_dests}")
            print(f"Number of sync source changes: {n_source_changes}")
            print(f"sync_attrs time:            {sync_attrs_time}")
            print(f"sync_attr time:             {sync_attr_time}")
            print(f"sync_attr time (ExitStack): {sync_attr_with_ExitStack_time}")


def benchmark_and_plot():
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter

    fig = plt.figure()
    axs = fig.subplots(len(N_SYNC_SOURCE_CHANGES_LIST), 1, gridspec_kw={'hspace': 0.5})

    for ax, n_source_changes in zip(axs, N_SYNC_SOURCE_CHANGES_LIST):
        ax.plot(
            N_SYNC_DESTS_LIST,
            [benchmark_sync_attrs(n_dests, n_source_changes) for n_dests in N_SYNC_DESTS_LIST],
            color="#44AA00",
            label="sync_attrs",
        )
        ax.plot(
            N_SYNC_DESTS_LIST,
            [benchmark_sync_attr_without_ExitStack(n_dests, n_source_changes) for n_dests in N_SYNC_DESTS_LIST],
            color="#FF3300",
            label="sync_attr",
        )
        ax.plot(
            N_SYNC_DESTS_LIST,
            [benchmark_sync_attr_with_ExitStack(n_dests, n_source_changes) for n_dests in N_SYNC_DESTS_LIST],
            color="#2266FF",
            label="sync_attr (ExitStack)"
        )
        ax.set_title(f"Number of sync source changes: {n_source_changes}")
        ax.set_xlabel("Number of sync destinations")
        ax.set_ylabel("Time")
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.legend()
    plt.show()


def main():
    try:
        import matplotlib
    except ImportError:
        print("Matplotlib is not installed. Fallback to stdout.")
        benchmark_and_stdout()
    else:
        benchmark_and_plot()


if __name__ == "__main__":
    main()
