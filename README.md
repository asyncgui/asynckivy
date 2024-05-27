# AsyncKivy

[Youtube](https://www.youtube.com/playlist?list=PLNdhqAjzeEGjTpmvNck4Uykps8s9LmRTJ)  
[日本語doc](README_jp.md)  

`asynckivy` is an async library that saves you from ugly callback-style code,
like most of async libraries do.
Let's say you want to do:

1. `print('A')`
1. wait for 1sec
1. `print('B')`
1. wait for a button to be pressed
1. `print('C')`

in that order.
Your code would look like this:

```python
from kivy.clock import Clock

def what_you_want_to_do(button):
    print('A')

    def one_sec_later(__):
        print('B')
        button.bind(on_press=on_button_press)
    Clock.schedule_once(one_sec_later, 1)

    def on_button_press(button):
        button.unbind(on_press=on_button_press)
        print('C')

what_you_want_to_do(...)
```

It's not easy to understand.
If you use `asynckivy`, the code above will become:

```python
import asynckivy as ak

async def what_you_want_to_do(button):
    print('A')
    await ak.sleep(1)
    print('B')
    await ak.event(button, 'on_press')
    print('C')

ak.start(what_you_want_to_do(...))
```

## Installation

Pin the minor version.

```text
poetry add asynckivy@~0.6
pip install "asynckivy>=0.6,<0.7"
```

## Usage

```python
import asynckivy as ak

async def some_task(button):
    # waits for 2 seconds to elapse
    dt = await ak.sleep(2)
    print(f'{dt} seconds have elapsed')

    # waits for a button to be pressed
    await ak.event(button, 'on_press')

    # waits for the value of 'button.x' to change
    __, x = await ak.event(button, 'x')
    print(f'button.x is now {x}')

    # waits for the value of 'button.x' to become greater than 100
    if button.x <= 100:
        __, x = await ak.event(button, 'x', filter=lambda __, x: x>100)
        print(f'button.x is now {x}')

    # waits for either 5 seconds to elapse or a button to be pressed.
    # i.e. waits at most 5 seconds for a button to be pressed
    tasks = await ak.wait_any(
        ak.sleep(5),
        ak.event(button, 'on_press'),
    )
    print("Timeout" if tasks[0].finished else "The button was pressed")

    # same as the above
    async with ak.move_on_after(5) as bg_task:
        await ak.event(button, 'on_press')
    print("Timeout" if bg_task.finished else "The button was pressed")

    # waits for both 5 seconds to elapse and a button to be pressed.
    tasks = await ak.wait_all(
        ak.sleep(5),
        ak.event(button, 'on_press'),
    )

    # nest as you want.
    # waits for a button to be pressed, and either 5 seconds to elapse or 'other_async_func' to complete.
    tasks = await ak.wait_all(
        ak.event(button, 'on_press'),
        ak.wait_any(
            ak.sleep(5),
            other_async_func(),
        ),
    )
    child_tasks = tasks[1].result
    print("5 seconds elapsed" if child_tasks[0].finished else "other_async_func has completed")

ak.start(some_task(some_button))
```

For more details, read the [documentation](https://asyncgui.github.io/asynckivy/).

## Tested on

- CPython 3.8 + Kivy 2.3.0
- CPython 3.9 + Kivy 2.3.0
- CPython 3.10 + Kivy 2.3.0
- CPython 3.11 + Kivy 2.3.0
- CPython 3.12 + Kivy 2.3.0 (3.12.0 is not supported due to [this issue](https://github.com/python/cpython/issues/111058))

## Why this even exists

Kivy supports two legitimate async libraries, [asyncio][asyncio] and [Trio][trio], starting from version 2.0.0, so developing another one seems like [reinventing the wheel][reinventing].
Actually, I started this one just to learn how the async/await syntax works, so it initially was "reinventing the wheel".

But after playing with Trio and Kivy for a while, I noticed that Trio is not suitable for the situation where fast reactions are required e.g. touch events.
The same is true of asyncio.
You can confirm that by running `investigation/why_xxx_is_not_suitable_for_handling_touch_events.py`, and mashing a mouse button as quickly as possible.
You'll see sometimes `up` is not paired with `down`.
You'll see the coordinates aren't relative to the `RelativeLayout` even though the `target` belongs to it.

The cause of those problems is that `trio.Event.set()` and `asyncio.Event.set()` don't *immediately* resume the tasks waiting for the `Event` to be set.
They just schedule the tasks to resume.
Same thing can be said to `nursery.start_soon()` and `asyncio.create_task()`.

Trio and asyncio are async **I/O** libraries after all.
They probably don't have to immediately resumes/starts tasks, which I think necessary for touch handling in Kivy.
(If you fail to handle touches promptly, their state might undergo changes, leaving no time to wait for tasks to resume/start).
Their core design might not be suitable for GUI in the first place.
That's why I'm still developing this `asynckivy` library to this day.

[asyncio]:https://docs.python.org/3/library/asyncio.html
[trio]:https://trio.readthedocs.io/en/stable/
[reinventing]:https://en.wikipedia.org/wiki/Reinventing_the_wheel
