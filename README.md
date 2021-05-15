# AsyncKivy

[Youtube](https://www.youtube.com/playlist?list=PLNdhqAjzeEGjTpmvNck4Uykps8s9LmRTJ)  
[日本語doc](README_jp.md)  

`asynckivy` is an async library that saves you from ugly callback-based code,
just like other async libraries do.
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
```

It's barely readable and not easy to understand.
If you use `asynckivy`, the code above will become like this:

```python
import asynckivy as ak

async def what_you_want_to_do(button):
    print('A')
    await ak.sleep(1)
    print('B')
    await ak.event(button, 'on_press')
    print('C')
```

## Installation

```
# stable version
pip install asynckivy
```

## Pin the minor version

If you use this module, it's recommended to pin the minor version, because if
it changed, it usually means some breaking changes occurred.

## Usage

```python
import asynckivy as ak

async def some_task(button):
    # wait for 1sec
    dt = await ak.sleep(1)
    print(f'{dt} seconds have passed')
    
    # wait until a button is pressed
    await ak.event(button, 'on_press')

    # wait until 'button.x' changes
    __, x = await ak.event(button, 'x')
    print(f'button.x is now {x}')

    # wait until 'button.x' becomes greater than 100
    if button.x <= 100:
        __, x = await ak.event(button, 'x', filter=lambda __, x: x>100)
        print(f'button.x is now {x}')

    # wait until EITHER a button is pressed OR 5sec passes
    tasks = await ak.or_(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )
    print("The button was pressed" if tasks[0].done else "5sec passed")

    # wait until BOTH a button is pressed AND 5sec passes"
    tasks = await ak.and_(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )

ak.start(some_task(some_button))
```

### animation

```python
import asynckivy as ak

async def some_task(widget):
    # start an animation and wait for the completion.
    # the keyword-arguments are the same as kivy.animation.Animation's.
    await ak.animate(widget, width=200, t='in_out_quad', d=.5)

    # interpolate between the values 0 and 200.
    # the keyword-arguments are the same as kivy.animation.Animation's.
    async for v in ak.interpolate(0, 200, s=.2, d=2, t='linear'):
        print(v)
        # await ak.sleep(1)  # Do not await anything during the iteration

    # change the text of Label with fade-transition
    label = Label(...)
    async with ak.fade_transition(label):
        label.text = 'new text'
```

### touch handling

You can easily handle `on_touch_xxx` events via `asynckivy.rest_of_touch_moves()`.

```python
import asynckivy as ak

class Painter(RelativeLayout):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.opos):
            ak.start(self.draw_rect(touch))
            return True
    
    async def draw_rect(self, touch):
        from kivy.graphics import Line, Color, Rectangle
        from kivy.utils import get_random_color
        with self.canvas:
            Color(*get_random_color())
            line = Line(width=2)
        ox, oy = self.to_local(*touch.opos)
        async for __ in ak.rest_of_touch_moves(self, touch):
            # This part is iterated everytime 'on_touch_move' is fired.
            x, y = self.to_local(*touch.pos)
            min_x = min(x, ox)
            min_y = min(y, oy)
            max_x = max(x, ox)
            max_y = max(y, oy)
            line.rectangle = [min_x, min_y, max_x - min_x, max_y - min_y]
            # await ak.sleep(1)  # Do not await anything during the iteration

        # If you want to do something when 'on_touch_up' is fired, do it here.
        do_something_on_touch_up()
```

### threading

`asynckivy` currently does not have any I/O primitives like Trio and asyncio do,
thus threads are the only way to perform them without blocking the main-thread:

```python
from concurrent.futures import ThreadPoolExecuter
import asynckivy as ak

executer = ThreadPoolExecuter()

async def some_task():
    # create a new thread, run a function inside it, then
    # wait for the completion of that thread
    r = await ak.run_in_thread(thread_blocking_operation)
    print("return value:", r)

    # run a function inside a ThreadPoolExecuter, and wait for the completion
    r = await ak.run_in_executer(thread_blocking_operation, executer)
    print("return value:", r)
```

Exceptions(not BaseExceptions) are propagated to the caller,
so you can handle them like you do in synchronous code:

```python
import requests
from requests.exceptions import Timeout
import asynckivy as ak

async def some_task():
    try:
        r = await ak.run_in_thread(lambda: requests.get('htt...', timeout=10))
    except Timeout:
        print("TIMEOUT!")
    else:
        print('GOT A RESPONSE')
```

### synchronization primitive

There is a Trio's [Event](https://trio.readthedocs.io/en/stable/reference-core.html#trio.Event) equivalent.

```python
import asynckivy as ak

async def task_A(e):
    print('A1')
    await e.wait()
    print('A2')
async def task_B(e):
    print('B1')
    await e.wait()
    print('B2')

e = ak.Event()
ak.start(task_A(e))
# A1
ak.start(task_B(e))
# B1
e.set()
# A2
# B2
```

### misc

```python
import asynckivy as ak

# schedule a coroutine/Task to start after the next frame
ak.start_soon(coro_or_task)
```

## Structured Concurrency

Both `asynckivy.and_()` and `asynckivy.or_()` follow the concept of "structured concurrency".
What does that mean?
They promise two things:

* The tasks passed into them never outlive them.
* Exceptions occured in the tasks are propagated to the parent task.

Read [this post][njs_sc] if you want to know more about "structured concurrency".

## Test Environment

- CPython 3.7 + Kivy 2.0.0
- CPython 3.8 + Kivy 2.0.0
- CPython 3.9 + Kivy 2.0.0

## Why this does exist

Kivy supports two legit async libraries, [asyncio][asyncio] and [Trio][trio], from version 2.0.0 so developing another one seems [reinventing the wheel][reinventing]. Actually, I started developing this one just for learning how async/await works so it *was* initially `reinventing the wheel`.

But after playing with Trio and Kivy for a while, I noticed that Trio is not suitable for the situation where fast reactions are required e.g. touch events. The same is true of asyncio. You can confirm it by running `examples/misc/why_xxx_is_not_suitable_for_handling_touch_events.py`, and masshing a mouse button. You'll see sometimes `up` is not paired with `down`. You'll see the coordinates aren't relative to the `RelativeLayout` even though the `target` belongs to it.

The cause of those problems is that `trio.Event.set()` and `asyncio.Event.set()` don't *immediately* resume the tasks that are waiting for the `Event` to be set. They just schedule the tasks to resume.
Same thing can be said to `nursery.start_soon()` and `asyncio.create_task()`.

Trio and asyncio are async **I/O** libraries after all. They probably don't need the functionality that immediately resumes/starts tasks, which I think necessary for Kivy's touch handling.
Their core design may not be suitable for GUI in the first place.
That's why I'm still developing this `asynckivy` library to this day.

[asyncio]:https://docs.python.org/3/library/asyncio.html
[trio]:https://trio.readthedocs.io/en/stable/
[reinventing]:https://en.wikipedia.org/wiki/Reinventing_the_wheel
[njs_sc]:https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/
