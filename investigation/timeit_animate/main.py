'''
Comparision between new ver and old ver of `asynckivy._animation._update()`
'''

from functools import partial
from timeit import timeit
import new_ver
import old_ver


class AnimationTarget:
    def __init__(self):
        self.size = [0., 0., ]
        self.pos_hint = {'center_x': 0., }
        self.font_size = 0.


print("-- font_size --")
new_update = partial(new_ver.create_update(AnimationTarget(), font_size=100., duration=10000.), 0.01)
old_update = partial(old_ver.create_update(AnimationTarget(), font_size=100., duration=10000.), 0.01)
t_new = timeit(new_update)
t_old = timeit(old_update)
print("new ver:", t_new)
print("old ver:", t_old)


print("-- size --")
new_update = partial(new_ver.create_update(AnimationTarget(), size=[100., 100., ], duration=10000.), 0.01)
old_update = partial(old_ver.create_update(AnimationTarget(), size=[100., 100., ], duration=10000.), 0.01)
t_new = timeit(new_update)
t_old = timeit(old_update)
print("new ver:", t_new)
print("old ver:", t_old)


print("-- pos_hint --")
new_update = partial(new_ver.create_update(AnimationTarget(), pos_hint={'center_x': 100., }, duration=10000.), 0.01)
old_update = partial(old_ver.create_update(AnimationTarget(), pos_hint={'center_x': 100., }, duration=10000.), 0.01)
t_new = timeit(new_update)
t_old = timeit(old_update)
print("new ver:", t_new)
print("old ver:", t_old)
