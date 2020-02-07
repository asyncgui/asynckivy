# AsyncKivy

[Youtube](https://youtu.be/rI-gjCsE1YQ)

[asyncの為の公式のPR](https://github.com/kivy/kivy/pull/6368)は既にmaster branchに取り込まれていているのでそれ以前のversionを使わない限りはこのmoduleの存在意義は低いです。

### Install方法

```
pip install git+https://github.com/gottadiveintopython/asynckivy#egg=asynckivy
```

### 使い方

```python
import asynckivy as ak

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
    r = await ak.thread(some_heavy_task)
    print(f"'some_heavy_task()'の戻り値: {r}")

    # subprocessの完了を待つ
    import subprocess
    p = subprocess.Popen(...)
    returncode = await ak.process(p)

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

    # animationの完了を待つ
    await ak.animation(button, width=200, t='in_out_quad', d=.5)
ak.start(some_task(some_button))
```

`asynckivy.all_touch_moves()`を用いる事で簡単に`on_touch_xxx`系のeventを捌く事ができる。

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
            # 'on_touch_move'時に行いたい処理はここに書く。
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

### Test環境

- CPython 3.7.1 + Kivy 1.11.1
- CPython 3.7.1 + Kivy 2.0.0rc1,git-b1c643c,20200106
