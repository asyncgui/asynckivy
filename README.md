# AsyncKivy

[Youtube](https://youtu.be/rI-gjCsE1YQ)

### Note

[The PR for async support](https://github.com/kivy/kivy/pull/6368) was already merged to master branch, and it would be available on version `2.0.0`. So there is no point of using this module unless you are using Kivy version `1.x.x`.

### Installation

```
pip install git+https://github.com/gottadiveintopython/asynckivy#egg=asynckivy
```

### Usage

```python
import asynckivy as ak

async def some_task(button):
    # wait for 1sec
    await ak.sleep(1)
    
    # wait until the button is pressed
    await ak.event(button, 'on_press')

    # wait until 'button.x' changes
    __, x = await ak.event(button, 'x')
    print(f'button.x is now {x}')

    # wait until 'button.x' becomes greater than 100
    if button.x <= 100:
        __, x = await ak.event(button, 'x', filter=lambda __, x: x>100)
        print(f'button.x is now {x}')

    # create a new thread, run a function on it, then
    # wait for the completion of the thread
    r = await ak.thread(some_heavy_task)
    print(f"result of 'some_heavy_task()': {r}")

    # wait for the completion of a subprocess
    import subprocess
    p = subprocess.Popen(...)
    returncode = await ak.process(p)

    # wait until EITHER the button is pressed OR 5sec passes
    tasks = await ak.or_(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )
    print("The button was pressed" if tasks[0].done else "5sec passed")

    # wait until BOTH the button is pressed AND 5sec passes"
    tasks = await ak.and_(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )

    # wait for the completion of animation
    await ak.animation(button, width=200, t='in_out_quad', d=.5)
ak.start(some_task(some_button))
```

You can easily handle `on_touch_xxx` events via `asynckivy.all_touch_moves()`. The following code supports multi touch as well.

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
        async for __ in ak.all_touch_moves(self, touch):
            # Don't await anything during this async-for-loop or you'll
            # get an unexpected result.
            x, y = self.to_local(*touch.pos)
            min_x = min(x, ox)
            min_y = min(y, oy)
            max_x = max(x, ox)
            max_y = max(y, oy)
            line.rectangle = [min_x, min_y, max_x - min_x, max_y - min_y]
        # If you want to do something when 'on_touch_up' is fired, do it here.
        do_something_on_touch_up()
```

### Test Environment

- CPython 3.7.1 + Kivy 1.11.1
- CPython 3.7.1 + Kivy 2.0.0rc1,git-b1c643c,20200106
