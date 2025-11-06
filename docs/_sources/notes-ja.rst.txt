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
を行うせいなのか、これらのライブライリを使っているとasyncジェネレータの後始末が遅れる事があります。なので使い終わったら明示的に閉じて下さい。
以下がasyncジェネレータを返す者達です。

- :func:`~asynckivy.rest_of_touch_events`
- :func:`~asynckivy.interpolate`
- :func:`~asynckivy.interpolate_seq`
- ``anim_with_xxx``

.. code-block::

    from contextlib import aclosing

    async with aclosing(interpolate(...)) as agen:
        async for v in agen:
            ...

加えてより問題なのはasyncジェネレータを使用する側で例外が起きた場合にその例外がジェネレータに運ばれないという事です。
(一応これ自体は通常のジェネレータにも当てはまりますがそちらではあまり問題にならないと思います。)

.. code-block::

    async for v in agen:
        # ここで例外が起きてもagenには運ばれない

これが意味するのはasyncジェネレータを使用する側が中断された場合にその中断を表す例外がジェネレータに伝わらないという事です。

.. code-block::

    async for v in agen:
        await something  # ここで中断されるとagenは実装次第でそれに正しく対応できない。

長くなるので深入りはしませんがこの事が ``asyncgui`` の中断機構を壊し得ます。
なので上記のAPIが返したasyncジェネレータの消費中はいかなるasync処理も行わないで下さい。

.. code-block::

    async for __ in rest_of_touch_events(...):
        await awaitable  # 駄目
        async with async_context_manager:  # 駄目
            ...
        async for __ in async_iterator:  # 駄目
            ...

もしどうしてもそのような事をしたければ代わりに :class:`~asynckivy.rest_of_touch_events_cm` や :class:`~asynckivy.sleep_freq` を使う事を検討して下さい。
これらによってコードは少し長くなりますが、見返りとしてasyncジェネレータ特有の問題全てから解放されます。

.. code-block::
    
    async with rest_of_touch_events_cm(..., free_to_await=True) as on_touch_move:
        ...

    async with sleep_freq(..., free_to_await=True) as sleep:
        ...
