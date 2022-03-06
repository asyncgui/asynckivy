# AsyncKivy

[Youtube](https://www.youtube.com/playlist?list=PLNdhqAjzeEGjTpmvNck4Uykps8s9LmRTJ)

`asynckivy`はKivy用のlibraryで、
よくあるasync libraryと同じでcallback関数だらけの醜いcodeを読みやすくしてくれます。
例えば

1. `A`を出力
1. 一秒待機
1. `B`を出力
1. buttonが押されるまで待機
1. `C`を出力

といった事を普通にやろうとするとcodeは

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

のように読みにくい物となりますが、`asynckivy`を用いることで

```python
import asynckivy as ak

async def what_you_want_to_do(button):
    print('A')
    await ak.sleep(1)
    print('B')
    await ak.event(button, 'on_press')
    print('C')
```

と分かりやすく書けます。

## Install方法

このmoduleのminor versionが変わった時は何らかの重要な互換性の無い変更が加えられた可能性が高いので、使う際はminor versionまでを固定してください。

```text
poetry add asynckivy@~0.5
pip install "asynckivy>=0.5,<0.6"
```

## 使い方

```python
import asynckivy as ak

async def some_task(button):
    # 1秒待つ
    dt = await ak.sleep(1)
    print(f'{dt}秒経ちました')

    # buttonが押されるまで待つ
    await ak.event(button, 'on_press')

    # 'button.x'の値が変わるまで待つ
    __, x = await ak.event(button, 'x')
    print(f'button.x の現在の値は {x} です')

    # 'button.x'の値が100を超えるまで待つ
    if button.x <= 100:
        __, x = await ak.event(button, 'x', filter=lambda __, x: x>100)
        print(f'button.x の現在の値は {x} です')

    # buttonが押される か 5秒経つまで待つ
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

    # buttonが押され なおかつ (5秒経つ か 'other_async_func'が完了する) まで待つ
    tasks = await ak.and_(
        ak.event(button, 'on_press'),
        ak.or_(
            ak.sleep(5),
            other_async_func(),
        ),
    )
    child_tasks = tasks[1].result
    print("5秒経ちました" if child_tasks[0].done else "other_async_funcが完了しました")

ak.start(some_task(some_button))
```

### animation関連

```python
import asynckivy as ak


async def some_task(button):
    # animationを開始してその完了を待つ。
    # keyword引数は全て `kivy.animation.Animation` と同じ。
    await ak.animate(button, width=200, t='in_out_quad', d=.5)

    # d秒かけて0から200までを線形補間する。中間値の計算はs秒毎に行う。
    # keyword引数は全て `kivy.animation.Animation` と同じ。
    async for v in ak.interpolate(0, 200, s=.2, d=2, t='linear'):
        print(v)
        # await ak.sleep(1)  # この繰り返し中にawaitは使ってはいけない

    # d/2秒かけてwidgetを徐々に透明にしてからwith blobk内を実行し、それから
    # d/2秒かけて元の透明度に戻す。透明度の更新はs秒毎に行う。
    async with ak.fade_transition(widget, d=1, s=.1):
        pass
```

### touch処理

`asynckivy.rest_of_touch_moves()`を用いる事で簡単に`on_touch_xxx`系のeventを捌く事ができる。

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
            # 注意点としてこの繰り返し中は絶対にawaitを使わないこと。
            x, y = self.to_local(*touch.pos)
            min_x, max_x = (x, ox) if x < ox else (ox, x)
            min_y, max_y = (y, oy) if y < oy else (oy, y)
            line.rectangle = (min_x, min_y, max_x - min_x, max_y - min_y, )
        else:
            # 'on_touch_up'時にこのcode blockが実行される
            print("'on_touch_up' was fired")
```

### thread

`asynckivy`はTrioやasyncioのような入出力機能を持たないので、GUIを固まらせずにそれをしたければ別のthreadで行うしかない。今のところ次の二つの方法がある。

```python
from concurrent.futures import ThreadPoolExecuter
import asynckivy as ak

executer = ThreadPoolExecuter()

async def some_task():
    # 方法その一
    # 新しくthreadを作ってそこで渡された関数を実行し、その完了を待つ
    r = await ak.run_in_thread(thread_blocking_operation)
    print("return value:", r)

    # 方法そのニ
    # ThreadPoolExecuterで渡された関数を実行し、その完了を待つ
    r = await ak.run_in_executer(thread_blocking_operation, executer)
    print("return value:", r)
```

thread内で起きた例外(BaseExceptionは除く)は呼び出し元に運ばれるので、
以下のように通常の同期codeを書く感覚で例外を捌ける。

```python
import requests
import asynckivy as ak

async def some_task():
    try:
        r = await ak.run_in_thread(lambda: requests.get('htt...', timeout=10))
    except requests.Timeout:
        print("制限時間内に応答せず")
    else:
        print('通信成功')
```

### Task間の連絡および同期

[trio.Event](https://trio.readthedocs.io/en/stable/reference-core.html#trio.Event)相当の物。

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

Trioやasyncioの物とは違って``Event.set()``が呼ばれた時それを待っているtaskは即座に再開される。
なので上の例で``e.set()``は``A2``と``B2``が出力された後に処理が戻る。

[asyncio.Queue](https://docs.python.org/3/library/asyncio-queue.html)相当の物.

```python
from kivy.app import App
import asynckivy as ak
from asynckivy.queue import Queue

async def producer(q, items):
    for i in items:
        await q.put(i)
    q.close()

async def consumer(q):
    assert ''.join([item async for item in q]) == 'ABCD'  # Queueはasync-iterable

async def consumer2(q):
    '''上の ``consumer()`` と同等のコード'''
    items = []
    try:
        while True:
            items.append(await q.get())
    except ak.EndOfResource:
        assert ''.join(items) == 'ABCD'


q = Queue()
ak.start(producer(q, 'ABCD'))
ak.start(consumer(q))
App().run()  # QueueはClockに依存しているのでevent-loopを回してあげないと動作しない。
```

### 中断への対処

``asynckivy.start()``が返した``Task``の``.cancel()``を呼ぶ事で処理を中断できる。

```python
task = asynckivy.start(async_func())
...
task.cancel()
```

その際`async_func()`の中で`GeneratorExit`例外が起きるので以下のように書けば中断に備えたコードになる。

```python
async def async_func():
    try:
        ...
    except GeneratorExit:
        # .cancel() による明示的な中断が行われた時にだけ行いたい処理をここに書くと良い。
        ...
        raise  # GeneratorExit例外を揉み消してはならない!!
    finally:
        # ここで何か後始末をすると良い
```

また中断は常に速やかに完遂させないといけないので、except-GeneratorExit節とfinally節の中で`await`する事は許されない。

```python
async def async_func():
    try:
        await something  # <-- 良い
    except Exception:
        await something  # <-- 良い
    except GeneratorExit:
        await something  # <-- 駄目
        raise
    finally:
        await something  # <-- 駄目
```

逆にいうと中断されないのであればfinally節で`await`しても良い。

```python
async def async_func():
    try:
        await something  # <-- 良い
    except Exception:
        await something  # <-- 良い
    finally:
        await something  # <-- 良い (中断されない前提)
```

上の決まりを守っている限りは好きなだけ中断できる。
ただもし明示的な``.cancel()``呼び出しがcode内に多く現れるようなら、
それはcodeが正しい構造を採っていない兆しなので修正すべきである。
多くの場合``Task.cancel()``は`asynckivy.and_()`や`asynckivy.or_()`を用いる事で無くせるのでそうされたし。

### その他

```python
import asynckivy as ak

# 次のframeでawaitable/Taskが始まるように予約
ak.start_soon(awaitable_or_task)
```

### Structured Concurrency

(この章はまだ未完成。)

`asynckivy.and_()`と`asynckivy.or_()`は[structured concurrency][sc]の考え方に従っています。

<!--
関連性の無いファイルがたくさん(例えば数千個)あったとして、それらを全て一つのフォルダに入れて管理する人は少ないと思います。
多くの人はそれらを自分なりの基準(日付、ファイルの種類、属するプロジェクト)で別にフォルダを作って小分けしていくでしょう。
同じ事が並行処理にもいえます。
`asyncio.create_task()`や`asynckivy.start()`や`threading.Thread.start()`等で立ち上げたtaskはフォルダに属していないファイルも同然であり
-->

```python
import asynckivy as ak

async def 根():
    await ak.or_(子1(), 子2())

async def 子1():
    ...

async def 子2():
    await ak.and_(孫1(), 孫2())

async def 孫1():
    ...

async def 孫2():
    ...
```

```mermaid
flowchart TB
根 --> 子1 & 子2(子2)
子2 --> 孫1 & 孫2
```

## Test環境

- CPython 3.7 + Kivy 2.0.0
- CPython 3.8 + Kivy 2.0.0
- CPython 3.9 + Kivy 2.0.0

[sc]:https://qiita.com/gotta_dive_into_python/items/6feb3224a5fa572f1e19
