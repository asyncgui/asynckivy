__all__ = (
    'dt', 'delta_time',
    'et', 'elapsed_time',
    'dt_et', 'delta_time_elapsed_time',
    'progress',
    'dt_et_progress', 'delta_time_elapsed_time_progress',
)

import warnings
from . import _anim_with_xxx


warnings.warn("The 'vanim' module is deprecated. Use 'asynckivy.anim_with_xxx' instead.")


delta_time = dt = _anim_with_xxx.anim_with_dt
elapsed_time = et = _anim_with_xxx.anim_with_et
progress = _anim_with_xxx.anim_with_ratio
delta_time_elapsed_time = dt_et = _anim_with_xxx.anim_with_dt_et
delta_time_elapsed_time_progress = dt_et_progress = _anim_with_xxx.anim_with_dt_et_ratio
