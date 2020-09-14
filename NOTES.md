# TODO

## High Priority

- **[bug fix]**`rest_of_touch_moves()`の実装がasync generatorがgcされる時機に依存しているのでしないように修正する。(unit testsのxfailで印付けられた物がそれ)

## Low Priority

- complete `asynckivy.Task`
- implement `asyncio.as_completed()` equivalent
- implement `trio.Semaphore` equivalent
