# AsyncKivy

[Youtube](https://www.youtube.com/playlist?list=PLNdhqAjzeEGjTpmvNck4Uykps8s9LmRTJ)  
[日本語doc](README_jp.md)  

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

    # create a new thread, run a function on it, then
    # wait for the completion of that thread
    r = await ak.run_in_thread(some_heavy_task)
    print(f"result of 'some_heavy_task()': {r}")

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
    # start an animation and wait for its completion
    await ak.animate(widget, width=200, t='in_out_quad', d=.5)

    # Interpolate between the values 0 and 200.
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

### Misc

```python
import asynckivy as ak

# schedule a coroutine/Task to start after the next frame
ak.start_soon(coro_or_task)

# schedule a coroutine/Task to close before the next frame
ak.close_soon(coro_or_task)
```

## Test Environment

- CPython 3.7 + Kivy 2.0.0
- CPython 3.8 + Kivy 2.0.0
- CPython 3.9 + Kivy 2.0.0

## Why this does exist

Kivy supports two legit async libraries, [asyncio][asyncio] and [Trio][trio], from version 2.0.0 so developing another one seems [reinventing the wheel][reinventing]. Actually, I started developing this library just for learning how async/await works so it *was* initially `reinventing the wheel`.

But after playing with Trio and Kivy for a while, I noticed that Trio is not suitable for the situation where fast reactions are required e.g. touch events. The same is true of asyncio. You can see why by running `examples/misc/why_xxx_is_not_suitable_for_handling_touch_events.py`, and masshing a mouse button. You'll see sometimes the printed `up` and `down` aren't paired. You'll see the printed coordinates aren't relative to the `RelativeLayout` even though the `target` belongs to it.

The cause of those problems is that calling `trio.Event.set()` / `asyncio.Event.set()` doesn't *immediately* resume the tasks that are waiting for the `Event` to be set. It just schedules the tasks to resume.
Same thing can be said to `nursery.start_soon()` and `asyncio.create_task()`. Yes, Trio has `nursery.start()`, which immediately starts a task, but it's an async-function so it cannot be called from synchronous code, which means it's no use here.

Trio and asyncio are async **I/O** libraries after all. They probably don't need the functionality that immediately resumes/starts tasks, which is necessary for Kivy's touch handling.
Thier core design may not be suitable for GUI in the first place.
That's why I'm still developing this `asynckivy` library to this day.

[asyncio]:https://docs.python.org/3/library/asyncio.html
[trio]:https://trio.readthedocs.io/en/stable/
[reinventing]:https://en.wikipedia.org/wiki/Reinventing_the_wheel
