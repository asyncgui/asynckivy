# AsyncKivy

[Youtube](https://youtu.be/rI-gjCsE1YQ)  
[日本語doc](README_jp.md)  

### Installation

```
# stable version
pip install asynckivy
```

```
# development version
pip install git+https://github.com/gottadiveintopython/asynckivy.git@master#egg=asynckivy
```

### Usage

```python
import asynckivy as ak
from asynckivy.process_and_thread import \
    thread as ak_thread, process as ak_process

async def some_task(button):
    # wait for 1sec
    await ak.sleep(1)
    
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
    r = await ak_thread(some_heavy_task)
    print(f"result of 'some_heavy_task()': {r}")

    # wait for the completion of subprocess
    import subprocess
    p = subprocess.Popen(...)
    returncode = await ak_process(p)

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

#### animation

```python
import asynckivy as ak

async def some_task(widget):
    # wait for the completion of an animation
    await ak.animate(widget, width=200, t='in_out_quad', d=.5)

    # interpolate between the values 0 and 200
    async for v in ak.interpolate(0, 200, s=.2, d=2, t='linear'):
        print(v)
```

#### touch handling

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
            # Don't await anything during this iteration.
            x, y = self.to_local(*touch.pos)
            min_x = min(x, ox)
            min_y = min(y, oy)
            max_x = max(x, ox)
            max_y = max(y, oy)
            line.rectangle = [min_x, min_y, max_x - min_x, max_y - min_y]
        # If you want to do something when 'on_touch_up' is fired, do it here.
        do_something_on_touch_up()
```

#### synchronization primitive

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

### planned api break in version 1.0.0

- remove `animation()`, the older name of `animate()`
- remove `all_touch_moves()`, the older name of `rest_of_touch_moves()`

### Test Environment

- CPython 3.7.1 + Kivy 1.11.1
