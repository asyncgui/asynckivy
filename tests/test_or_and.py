import pytest

class Test_and_:
    def test_cancel_root(self):
        import asynckivy as ak
        TS = ak.TaskState

        tasks = [ak.Task(ak.sleep_forever()) for __ in range(3)]
        root = ak.start(ak.and_from_iterable(tasks))
        for task in tasks:
            assert task.state == TS.STARTED
        root.close()
        for task in tasks:
            assert task.state == TS.CANCELLED


class Test_or_:
    def test_normal(self):
        import asynckivy as ak
        TS = ak.TaskState

        e = ak.Event()
        tasks = [
            ak.Task(v) for v in
            (*(ak.sleep_forever() for __ in range(3)), e.wait())
        ]
        ak.start(ak.or_from_iterable(tasks))
        for task in tasks:
            assert task.state == TS.STARTED
        e.set()
        for task in tasks[:-1]:
            assert task.state == TS.CANCELLED
        tasks[-1].state == TS.DONE

    def test_cancel(self):
        import asynckivy as ak
        TS = ak.TaskState

        tasks = [ak.Task(ak.sleep_forever()) for __ in range(3)]
        ak.start(ak.or_from_iterable(tasks))
        for task in tasks:
            assert task.state == TS.STARTED
        tasks[1].close()
        for task in tasks:
            assert task.state == TS.CANCELLED

    def test_cancel_root(self):
        import asynckivy as ak
        TS = ak.TaskState

        tasks = [ak.Task(ak.sleep_forever()) for __ in range(3)]
        root = ak.start(ak.or_from_iterable(tasks))
        for task in tasks:
            assert task.state == TS.STARTED
        root.close()
        for task in tasks:
            assert task.state == TS.CANCELLED
