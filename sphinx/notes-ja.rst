==========
Notes |ja|
==========

-------------------------
AsyncKivyにおける入出力
-------------------------

``asynckivy`` はtrioやasyncioのような入出力機能を持たないのでGUIを固まらせずにそれをしたければ別のスレッドで行うのが良いと思います。
今のところ関数を別のスレッドで実行する方法には次の二つの方法があります。

.. code-block::

    from concurrent.futures import ThreadPoolExecutor
    import asynckivy as ak

    executor = ThreadPoolExecutor()

    async def async_func():
        # 方法その一
        # 新しくthreadを作ってそこで渡された関数を実行し、その完了を待つ
        r = await ak.run_in_thread(外部のスレッドで実行させたい関数)
        print("return value:", r)

        # 方法そのニ
        # ThreadPoolExecutor内で渡された関数を実行し、その完了を待つ
        r = await ak.run_in_executor(executor, 外部のスレッドで実行させたい関数)
        print("return value:", r)

スレッド内で起きた例外(ExceptionではないBaseExceptionは除く)は呼び出し元に運ばれるので、
以下のように通常の同期コードを書く感覚で例外を捌けます。

.. code-block::

    import requests
    import asynckivy as ak

    async def async_func(label):
        try:
            response = await ak.run_in_thread(lambda: requests.get('htt...', timeout=10))
        except requests.Timeout:
            label.text = "制限時間内に応答無し"
        else:
            label.text = "応答有り: " + response.text

----------------------------------
Asyncジェネレータが抱える問題
----------------------------------

``asyncio`` や ``trio`` がasyncジェネレータに対して `付け焼き刃的な処置 <https://peps.python.org/pep-0525/#finalization>`__
を行うせいなのか、これらのライブライリを使っているとasynckivy用のasyncジェネレータの後始末が遅れる事があります。なので使い終わったら明示的に閉じて下さい。
以下がasyncジェネレータを返す者達です。

- :func:`~asynckivy.rest_of_touch_events`
- :func:`~asynckivy.interpolate`
- :func:`~asynckivy.interpolate_seq`
- ``~anim_with_xxx``

また代替案として、これらの関数の内部ロジックをコピペしてasyncジェネレータを使わないようにする手もあります。
例えば ``anim_with_et`` が何故か思い通りに動かなかったとします。

.. code-block::

    async for et in anim_with_et(...):
        ...

ここで ``anim_with_et`` の実装を覗いて上のコードをそれに置き換えてしまえばasyncジェネレータに依らないコードになります。

.. code-block::

    async with sleep_freq(...) as sleep:
        et = 0.
        while True:
            dt = await sleep()
            et += dt
            ...

ほとんどの人がこれを愚かな策だと思うでしょうが、それでも時折やってみる価値はあります。
asyncジェネレータという物がそれだけ不安定だからです。
