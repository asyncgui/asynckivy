# AsyncKivy

[Youtube](https://www.youtube.com/playlist?list=PLNdhqAjzeEGjTpmvNck4Uykps8s9LmRTJ)  
[日本語doc](README_jp.md)  

`asynckivy` is an async library that saves you from ugly callback-based code,
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
```

It's barely readable and not easy to understand.
If you use `asynckivy`, the code above will become:

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

If you use this module, it's recommended to pin the minor version, because if
it changed, it means some *important* breaking changes occurred.

```text
poetry add asynckivy@~0.5
pip install "asynckivy>=0.5,<0.6"
```

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

    # wait until EITHER a button is pressed OR 5sec passes.
    # i.e. wait at most 5 seconds for a button to be pressed
    tasks = await ak.or_(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )
    print("The button was pressed" if tasks[0].done else "Timeout")

    # wait until a button is pressed AND 5sec passes.
    tasks = await ak.and_(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )

    # nest as you want.
    # wait for a button to be pressed AND (5sec OR 'other_async_func' to complete)
    tasks = await ak.and_(
        ak.event(button, 'on_press'),
        ak.or_(
            ak.sleep(5),
            other_async_func(),
        ),
    )
    child_tasks = tasks[1].result
    print("5sec passed" if child_tasks[0].done else "other_async_func has completed")

ak.start(some_task(some_button))
```

### animation

```python
import asynckivy as ak

async def some_task(widget):
    # start an animation and wait for the completion.
    # keyword-arguments are the same as kivy.animation.Animation's.
    await ak.animate(widget, width=200, t='in_out_quad', d=.5)

    # interpolate between the values 0 and 200 in an async-manner.
    # keyword-arguments are the same as kivy.animation.Animation's.
    async for v in ak.interpolate(0, 200, s=.2, d=2, t='linear'):
        print(v)
        # await ak.sleep(1)  # Do not await anything during this iteration

    # change the text of Label with fade-transition
    label = Label(...)
    async with ak.fade_transition(label):
        label.text = 'new text'

    # If you want more low-level control over animations, use the vanim module.
    # Read the module doc for details.
    from asynckivy import vanim
    async for dt in vanim.delta_time():
        ...
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
            min_x, max_x = (x, ox) if x < ox else (ox, x)
            min_y, max_y = (y, oy) if y < oy else (oy, y)
            line.rectangle = (min_x, min_y, max_x - min_x, max_y - min_y, )
            # await ak.sleep(1)  # Do not await anything during this iteration
        else:
            print("'on_touch_up' was fired")
```

### threading

`asynckivy` does not have any I/O primitives like Trio and asyncio do,
thus threads are the only way to perform them without blocking the main-thread:

```python
from concurrent.futures import ThreadPoolExecuter
import asynckivy as ak

executer = ThreadPoolExecuter()


def thread_blocking_operation():
    '''This function is called from outside the main-thread, so you are not allowed to touch gui components here.'''


async def some_task():
    # create a new thread, run a function inside it, then
    # wait for the completion of that thread
    r = await ak.run_in_thread(thread_blocking_operation)
    print("return value:", r)

    # run a function inside a ThreadPoolExecuter, and wait for the completion
    # (ProcessPoolExecuter is not supported)
    r = await ak.run_in_executer(thread_blocking_operation, executer)
    print("return value:", r)
```

Exceptions(not BaseExceptions) are propagated to the caller
so you can catch them like you do in synchronous code:

```python
import requests
import asynckivy as ak

async def some_task(label):
    try:
        response = await ak.run_in_thread(lambda: requests.get('htt...', timeout=10))
    except requests.Timeout:
        label.text = "TIMEOUT!"
    else:
        label.text = "RECEIVED: " + response.text
```

### synchronizing and communicating between tasks

There is a [trio.Event](https://trio.readthedocs.io/en/stable/reference-core.html#trio.Event) equivalent.

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

Unlike Trio's and asyncio's, when you call ``Event.set()``,
the tasks waiting for it to happen will *immediately* be resumed.
As a result, ``e.set()`` will return *after* ``A2`` and ``B2`` are printed.

And there is an [asyncio.Queue](https://docs.python.org/3/library/asyncio-queue.html) equivalent.

```python
from kivy.app import App
import asynckivy as ak
from asynckivy.queue import Queue

async def producer(q, items):
    for i in items:
        await q.put(i)
    q.close()

async def consumer(q):
    assert ''.join([item async for item in q]) == 'ABCD'  # Queue is async-iterable

async def consumer2(q):
    '''The ``consumer()`` above can be written in more primitive way like this'''
    items = []
    try:
        while True:
            items.append(await q.get())
    except ak.EndOfResource:
        assert ''.join(items) == 'ABCD'


q = Queue()
ak.start(producer(q, 'ABCD'))
ak.start(consumer(q))
App().run()  # Queue relies on Clock so you need to run the event-loop
```

### dealing with cancellations

``asynckivy.start()`` returns a ``Task``,
which can be used to cancel the execution.

```python
task = asynckivy.start(async_func())
...
task.cancel()
```

When `.cancel()` is called, `GeneratorExit` will occur inside the task,
which means you can prepare for cancellations as follows:

```python
async def async_func():
    try:
        ...
    except GeneratorExit:
        print('cancelled')
        raise  # You must re-raise !!
    finally:
        print('cleanup resources here')
```

You are not allowed to `await` inside `except-GeneratorExit-clause` and `finally-clause` if you want the task to be cancellable
because cancellations always must be done immediately.

```python
async def async_func():
    try:
        await something  # <-- ALLOWED
    except Exception:
        await something  # <-- ALLOWED
    except GeneratorExit:
        await something  # <-- NOT ALLOWED
        raise
    finally:
        await something  # <-- NOT ALLOWED
```

You are allowed to `await` inside `finally-clause` if the task will never get cancelled.

```python
async def async_func():  # Assuming this never gets cancelled
    try:
        await something  # <-- ALLOWED
    except Exception:
        await something  # <-- ALLOWED
    finally:
        await something  # <-- ALLOWED
```

As long as you follow the above rules, you can cancel tasks as you wish.
But note that if there are lots of explicit calls to `Task.cancel()` in your code,
**it's a sign of your code being not well-structured**.
You can usually avoid it by using `asynckivy.and_()` and `asynckivy.or_()`.  

### misc

```python
import asynckivy as ak

# schedule an awaitable/Task to start after the next frame
ak.start_soon(awaitable_or_task)
```

## Notes

### Places you cannot await

I already mentioned about this but I'll say again.
**You cannot await while iterating `rest_of_touch_moves()` or `interpolate()`.**

```python
import asynckivy as ak

async def async_fn():
    async for v in ak.interpolate(...):
        await something  # <-- NOT ALLOWED

    async for __ in ak.rest_of_touch_moves(...):
        await something  # <-- NOT ALLOWED
```

### asynckivy cannot be used with asyncio or trio

`asyncio` and `trio` do some hacky stuff, `sys.set_asyncgen_hooks()` and `sys.get_asyncgen_hooks`,
which likely hinders asynckivy-flavored async generators.
You can see its details [here](https://peps.python.org/pep-0525/#finalization).
I don't know how to make it work.
Maybe if [PEP355](https://peps.python.org/pep-0533/) is accepted,
it might work.

### Structured Concurrency

(This section is incomplete, and will be filled some day.)

`asynckivy.and_()` and `asynckivy.or_()` follow the concept of [structured concurrency][njs_sc].

```python
import asynckivy as ak

async def root():
    await ak.or_(child1(), child2())

async def child1():
    ...

async def child2():
    await ak.and_(ground_child1(), ground_child2())

async def ground_child1():
    ...

async def ground_child2():
    ...
```

```mermaid
flowchart TB
root --> C1(child 1) & C2(child 2)
C2 --> GC1(ground child 1) & GC2(ground child 2)
```


## Tested on

- CPython 3.7 + Kivy 2.1.0
- CPython 3.8 + Kivy 2.1.0
- CPython 3.9 + Kivy 2.1.0
- CPython 3.10 + Kivy 2.1.0

## Why this even exists

Kivy supports two legit async libraries, [asyncio][asyncio] and [Trio][trio], from version 2.0.0 so developing another one seems [reinventing the wheel][reinventing].
Actually, I started this one just for learning how async/await works so it *was* initially "reinventing the wheel".

But after playing with Trio and Kivy for a while, I noticed that Trio is not suitable for the situation where fast reactions are required e.g. touch events.
The same is true of asyncio.
You can confirm it by running `investigation/why_xxx_is_not_suitable_for_handling_touch_events.py`, and masshing a mouse button.
You'll see sometimes `up` is not paired with `down`.
You'll see the coordinates aren't relative to the `RelativeLayout` even though the `target` belongs to it.

The cause of those problems is that `trio.Event.set()` and `asyncio.Event.set()` don't *immediately* resume the tasks waiting for the `Event` to be set. They just schedule the tasks to resume.
Same thing can be said to `nursery.start_soon()` and `asyncio.create_task()`.

Trio and asyncio are async **I/O** libraries after all. They probably don't have to immediately resumes/starts tasks, which I think necessary for Kivy's touch handling.
(If a touch is not handled immediately, its coordinate's origin may change, its `pos` might be updated and the previous value will be lost.)
Their core design might not be suitable for GUI in the first place.
That's why I'm still developing this `asynckivy` library to this day.

[asyncio]:https://docs.python.org/3/library/asyncio.html
[trio]:https://trio.readthedocs.io/en/stable/
[reinventing]:https://en.wikipedia.org/wiki/Reinventing_the_wheel
[njs_sc]:https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/
