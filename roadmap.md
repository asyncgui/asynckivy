# Undetermind

- Re-implement `n_frames` without relying on closures
  - Relying on  `kivy.clock.Clock.frames` instead.
- `run_in_thread` が作るスレッドの名前を指定できるようにする。
- Remove `anim_with_ratio`
- `modal` サブモジュールでは `out_duration` と `in_duration` を個別に指定するのに対し `transition` サブモジュールでは両者を足した `duration` を指定する。
  この仕様のばらつきを統一する。


# 0.12.0

- `sync_attr` `sync_attrs` `smooth_attr` を通常のコンテキストマネージャのように `__enter__()` の実行によって効力を発揮するように変更する。
- Remove `sleep_free`
