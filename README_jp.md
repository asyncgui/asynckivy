# AsyncKivy

[Youtube](https://youtu.be/rI-gjCsE1YQ)

### Install方法

```
# stable version
pip install asynckivy
```

```
# development version
pip install git+https://github.com/gottadiveintopython/asynckivy.git@master#egg=asynckivy
```

### 使い方

```python
import asynckivy as ak
from asynckivy.process_and_thread import \
    thread as ak_thread, process as ak_process

async def some_task(button):
    # 1秒待つ
    await ak.sleep(1)
    
    # buttonが押されるまで待つ
    await ak.event(button, 'on_press')

    # 'button.x'の値が変わるまで待つ
    __, x = await ak.event(button, 'x')
    print(f'button.x の現在の値は {x} です')

    # 'button.x'の値が100を超えるまで待つ
    if button.x <= 100:
        __, x = await ak.event(button, 'x', filter=lambda __, x: x>100)
        print(f'button.x の現在の値は {x} です')

    # 新しくthreadを作ってそこで渡された関数を実行し、その完了を待つ
    r = await ak_thread(some_heavy_task)
    print(f"'some_heavy_task()'の戻り値: {r}")

    # subprocessの完了を待つ
    import subprocess
    p = subprocess.Popen(...)
    returncode = await ak_process(p)

    # buttonが押されるか5秒経つまで待つ
    tasks = await ak.or_(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )
    print("buttonが押されました" if tasks[0].done else "5秒経ちました")

    # buttonが押され なおかつ 5秒経つまで待つ
    tasks = await ak.and_(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )

ak.start(some_task(some_button))
```

#### animation関連

```python
import asynckivy as ak


async def some_task(button):
    # animationの完了を待つ
    await ak.animate(button, width=200, t='in_out_quad', d=.5)

    # 2秒かけて0から200までを線形補間する。中間値の計算は0.2秒毎に行う。
    async for v in ak.interpolate(0, 200, s=.2, d=2, t='linear'):
        print(v)
```

#### touch処理

`asynckivy.rest_of_touch_moves()`を用いる事で簡単に`on_touch_xxx`系のeventを捌く事ができます。

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
            # 'on_touch_move'の度にこのloopが繰り返される。
            # 注意点としてこのloop内では絶対にawaitを使わないこと。
            x, y = self.to_local(*touch.pos)
            min_x = min(x, ox)
            min_y = min(y, oy)
            max_x = max(x, ox)
            max_y = max(y, oy)
            line.rectangle = [min_x, min_y, max_x - min_x, max_y - min_y]
        # 'on_touch_up'時に行いたい処理はここに書く
        do_something_on_touch_up()
```

#### 同期

Trioの[Event](https://trio.readthedocs.io/en/stable/reference-core.html#trio.Event)相当の物があります。

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

### version2.0.0で予定の互換性の無いapi変更

- `animate()`の古い名前である`animation()`を削除
- `rest_of_touch_moves()`の古い名前である`all_touch_moves()`を削除

### Test環境

- CPython 3.7.1 + Kivy 1.11.1
