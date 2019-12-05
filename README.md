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

async def some_task():
    # wait for 1sec
    await ak.sleep(1)
    
    # wait until the button is pressed
    await ak.event(button, 'on_press')

    # wait until button.x becomes greater than 100
    args, __ = await ak.event(button, 'x', filter=lambda __, x: x>100)
    print(f'button.x is now {args[1]}')

    # wait for the completion of another thread
    r = await ak.thread(some_heavy_task, 5)
    print(f'result of the heavy task: {r}')
ak.start(some_task())
```
