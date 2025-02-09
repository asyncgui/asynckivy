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
を行うせいなのか、asynckivy用のasyncジェネレータがうまく機能しない事があります。
なので ``asyncio`` 或いは ``trio`` を使っている場合は以下のAPI達を使わなのがお薦めです。

* `rest_of_touch_events()`
* `anim_with_xxx`
* `interpolate`
* `interpolate_seq`
* `fade_transition()`

これにどう対処すればいいのかは現状分かっていません。
もしかすると :pep:`533` が解決してくれるかも。

-----------------------------
async操作が禁じられている場所
-----------------------------

``asynckivy`` のAPIでasyncイテレータを返す物のほとんどはその繰り返し中にasync操作を行うことを認めていません。
以下が該当する者たちです。

* :func:`asynckivy.rest_of_touch_events`
* :func:`asynckivy.interpolate`
* :func:`asynckivy.interpolate_seq`
* ``asynckivy.anim_with_xxx``
* :any:`asynckivy.event_freq`

.. code-block::

    async for __ in rest_of_touch_events(...):
        await awaitable  # 駄目
        async with async_context_manager:  # 駄目
            ...
        async for __ in async_iterator:  # 駄目
            ...
