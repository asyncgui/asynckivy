# 0.10.0

- ~~Remove `anim_with_xxx`~~
- ~~適切な名前のファイルへコードを移す。~~
- ~~Add `transition.fade_multiple` ~~
- ~~Add `block_touch_events`~~
- ~~Update `imitating_screenmanager.py`~~
- ~~Remove `__all__`s from private modules.~~

# 0.11.0

- Remove `fade_transition`

# Undetermind

- Re-implement `n_frames` without relying on closures
  - Relying on  `kivy.clock.Clock.frames` instead.
- `run_in_thread` が作るスレッドの名前を指定できるようにする。
- Remove `anim_with_ratio`
- `modal` サブモジュールでは `out_duration` と `in_duration` を個別に指定するのに対し `transition` サブモジュールでは両者を足した `duration` を指定する。
  この仕様のばらつきを統一する。
