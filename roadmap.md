# 0.9.0

- Removes `MotionEventAlreadyEndedError`, and leaves the users to handle the `touch.time_end != -1` situation on their own.

# Eventually

- 適切な名前のファイルへコードを移す。例: `suppress_event` を `_event.py` へ。

# Undetermind

- `n_frames` をclosureを用いない実装にする。
  - `kivy.clock.Clock.frames`
- `run_in_thread` が作るスレッドの名前を指定できるようにする。

