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

マイナーバージョンが変わった時は何らかの重要な互換性の無い変更が加えられた事を意味するので使う際はマイナーバージョンまでを固定してください。

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

    # buttonが押される か 5秒経つまで待つ (その１)
    tasks = await ak.wait_any(
        ak.event(button, 'on_press'),
        ak.sleep(5),
    )
    print("buttonが押されました" if tasks[0].finished else "5秒経ちました")

    # buttonが押される か 5秒経つまで待つ (その２)
    async with ak.move_on_after(5) as bg_task:
        await ak.event(button, 'on_press')
    print("5秒経ちました" if bg_task.finished else "buttonが押されました")

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
