# AsyncKivy

(This module was originally created as [GitHub Gist code](https://gist.github.com/gottadiveintopython/5f4a775849f9277081c396de65dc57c1), and moved to here.)

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

    # create a new thread, and run a function on it, then
    # wait for the completion of that thread
    r = await ak.thread(some_heavy_task)
    print(f"result of 'some_heavy_task()': {r}")

    # wait for the completion of subprocess
    import subprocess
    p = subprocess.Popen(...)
    returncode = await ak.process(p)

    # wait until EITEHR the button is pressed OR 5sec passes
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
