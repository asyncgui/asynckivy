from functools import partial
from timeit import timeit
from types import SimpleNamespace as Destination
from contextlib import ExitStack

from kivy.event import EventDispatcher
from kivy.properties import NumericProperty
import asynckivy as ak


class Source(EventDispatcher):
    value = NumericProperty(0)


def increase_value_n_times(range, src, n):
    for __ in range(n):
        src.value += 1


def benchmark_sync_attrs(n_dests, n_source_changes):
    src = Source()
    dests = [Destination() for _ in range(n_dests)]

    with ak.sync_attrs((src, "value"), *[(d, "value") for d in dests]):
        src.value += 1  # warm cache
        return timeit(partial(increase_value_n_times, range, src, n_source_changes))


def benchmark_sync_attr_with_ExitStack(n_dests, n_source_changes):
    src = Source()
    dests = [Destination() for _ in range(n_dests)]

    with ExitStack() as stack:
        ec = stack.enter_context
        for d in dests:
            ec(ak.sync_attr((src, "value"), (d, "value")))
        src.value += 1  # warm cache
        return timeit(partial(increase_value_n_times, range, src, n_source_changes))


def benchmark_sync_attr_without_ExitStack(n_dests, n_source_changes):
    src = Source()
    dests = [Destination() for _ in range(n_dests)]

    match len(dests):
        case 1:
            with ak.sync_attr((src, "value"), (dests[0], "value")):
                src.value += 1  # warm cache
                return timeit(partial(increase_value_n_times, range, src, n_source_changes))
        case 2:
            with (
                ak.sync_attr((src, "value"), (dests[0], "value")),
                ak.sync_attr((src, "value"), (dests[1], "value")),
            ):
                src.value += 1  # warm cache
                return timeit(partial(increase_value_n_times, range, src, n_source_changes))
        case 3:
            with (
                ak.sync_attr((src, "value"), (dests[0], "value")),
                ak.sync_attr((src, "value"), (dests[1], "value")),
                ak.sync_attr((src, "value"), (dests[2], "value")),
            ):
                src.value += 1  # warm cache
                return timeit(partial(increase_value_n_times, range, src, n_source_changes))
        case 4:
            with (
                ak.sync_attr((src, "value"), (dests[0], "value")),
                ak.sync_attr((src, "value"), (dests[1], "value")),
                ak.sync_attr((src, "value"), (dests[2], "value")),
                ak.sync_attr((src, "value"), (dests[3], "value")),
            ):
                src.value += 1  # warm cache
                return timeit(partial(increase_value_n_times, range, src, n_source_changes))
        case _:
            raise ValueError("Unsupported number of destinations")


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
