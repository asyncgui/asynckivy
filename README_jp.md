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

what_you_want_to_do(...)
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

ak.start(what_you_want_to_do(...))
```

と分かりやすく書けます。

## Install方法

このmoduleのminor versionが変わった時は何らかの重要な互換性の無い変更が加えられた可能性が高いので、使う際はminor versionまでを固定してください。

```text
poetry add asynckivy@~0.6
pip install "asynckivy>=0.6,<0.7"
```

## 使い方

```python
import asynckivy as ak

async def async_func(button):
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
    tasks = await ak.wait_any(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )
    print("buttonが押されました" if tasks[0].finished else "5秒経ちました")

    # buttonが押され なおかつ 5秒経つまで待つ
    tasks = await ak.wait_all(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )

    # buttonが押され なおかつ [5秒経つ か 'other_async_func'が完了する] まで待つ
    tasks = await ak.wait_all(
        ak.event(button, 'on_press'),
        ak.wait_any(
            ak.sleep(5),
            other_async_func(),
        ),
    )
    child_tasks = tasks[1].result
    print("5秒経ちました" if child_tasks[0].finished else "other_async_funcが完了しました")

ak.start(async_func(a_button))
```

### animation関連

```python
from types import SimpleNamespace
import asynckivy as ak


async def async_func(widget1, widget2):
    obj = SimpleNamespace(attr1=10, attr2=[20, 30, ], attr3={'key': 40, })

    # 任意のオブジェクトの属性をアニメーションしてその完了を待つ。
    await ak.animate(obj, attr1=200, attr2=[200, 100], attr3={'key': 400})

    # duration秒かけて二つの数値を補間する。中間値の計算はstep秒毎に行う。
    async for v in ak.interpolate(0, 200, duration=2, step=0.1):
        print(v)
        # await something  # この繰り返し中にawaitは使ってはいけない

    # duration/2秒かけてwidget達を徐々に透明にしてからwith block内を実行し、それから
    # duration/2秒かけて元の透明度に戻す。透明度の更新はstep秒毎に行う。
    async with ak.fade_transition(widget1, widget2, duration=3, step=0.1):
        widget1.text = 'new text'
        widget2.y = 200
```

### touch処理

`asynckivy.rest_of_touch_events()`を用いる事で簡単に`on_touch_xxx`系のeventを捌く事ができる。

```python
import asynckivy as ak

class TouchReceiver(Widget):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.opos):
            ak.start(self.handle_touch(touch))
            return True

    async def handle_touch(self, touch):
        print('on_touch_up')
        async for __ in ak.rest_of_touch_events(self, touch):
            # この繰り返し中はawaitを使ってはいけない。
            print('on_touch_move')
        print('on_touch_up')
```

Kivyがasyncio/trioモードで動いていると`rest_of_touch_events()`がうまく動かない可能性があります。
そんな時は`watch_touch()`を使って下さい。

```python
import asynckivy as ak

class TouchReceiver(Widget):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.opos):
            ak.start(self.handle_touch(touch))
            return True
        return super().on_touch_down(touch)

    async def handle_touch(self, touch):
        print('on_touch_up')
        async with ak.watch_watch(self, touch) as in_progress:
            # このwithブロック内で 'in_progress()' の戻り値以外の物をawaitしてはならない。
            while await in_progress():
                print('on_touch_move')
        print('on_touch_up')
```

### thread

`asynckivy`はTrioやasyncioのような入出力機能を持たないので、GUIを固まらせずにそれをしたければ別のthreadで行うしかない。今のところ次の二つの方法がある。

```python
from concurrent.futures import ThreadPoolExecutor
import asynckivy as ak

executor = ThreadPoolExecutor()


def thread_blocking_operation():
    '''この関数は main-thread の外から呼ばれるので ここでKivyのGUIに触れてはならない。'''


async def async_func():
    # 方法その一
    # 新しくthreadを作ってそこで渡された関数を実行し、その完了を待つ
    r = await ak.run_in_thread(thread_blocking_operation)
    print("return value:", r)

    # 方法そのニ
    # ThreadPoolExecutorで渡された関数を実行し、その完了を待つ
    r = await ak.run_in_executor(executor, thread_blocking_operation)
    print("return value:", r)
```

thread内で起きた例外(ExceptionではないBaseExceptionは除く)は呼び出し元に運ばれるので、
以下のように通常の同期codeを書く感覚で例外を捌ける。

```python
import requests
import asynckivy as ak

async def async_func(label):
    try:
        response = await ak.run_in_thread(lambda: requests.get('htt...', timeout=10))
    except requests.Timeout:
        label.text = "制限時間内に応答無し"
    else:
        label.text = "応答有り: " + response.text
```

## 留意点

### awaitできない場所

既に上で述べたことですが再び言います。
`rest_of_touch_events()`や`interpolate()`による繰り返し中は`await`してはいけません。

```python
import asynckivy as ak

async def async_fn():
    async for v in ak.interpolate(...):
        await something  # 駄目

    async for __ in ak.rest_of_touch_events(...):
        await something  # 駄目
```

### Kivyがasyncio/trioモードで動いている時はasynckivyはうまく機能しないかもしれません

`asyncio`や`trio`がasync generatorに対して[付け焼き刃的な処置](https://peps.python.org/pep-0525/#finalization)を行うせいなのか、asynckivy用のasync generatorがうまく機能しない事があります。
なので`asyncio`または`trio`を使っている場合は以下の者達を使わなのがお薦めです。

- `rest_of_touch_events()` (代わりに `watch_touch` を用いる)
- `anim_with_xxx` (代わりに `repeat_sleeping` を用いる)
- `interpolate` (現状は代替策無し)
- `fade_transition()` (現状は代替策無し)

これにどう対処すればいいのかは現状分かっていません。
もしかすると[PEP533](https://peps.python.org/pep-0533/)が解決してくれるかもしれません。

## Test環境

- CPython 3.8 + Kivy 2.2.1
- CPython 3.9 + Kivy 2.2.1
- CPython 3.10 + Kivy 2.2.1
- CPython 3.11 + Kivy 2.2.1
