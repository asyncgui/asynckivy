from functools import partial


def immediate_call(f):
    return f()


def ver_list(p_value: list):
    value = p_value[0] + 1
    p_value[0] = value


def ver_closure():
    value = 0

    def inner():
        nonlocal value
        _value = value + 1
        value = _value
    return inner


class ver_attr:
    __slots__ = ('value', )

    def __init__(self):
        self.value = 0

    def __call__(self):
        value = self.value + 1
        self.value = value


@immediate_call
def unittest_ver_list():
    obj = partial(ver_list, [0])
    assert obj.args[0][0] == 0
    obj()
    assert obj.args[0][0] == 1
    obj()
    assert obj.args[0][0] == 2


@immediate_call
def unittest_ver_closure():
    obj = ver_closure()
    assert obj.__closure__[0].cell_contents == 0
    obj()
    assert obj.__closure__[0].cell_contents == 1
    obj()
    assert obj.__closure__[0].cell_contents == 2


@immediate_call
def unittest_ver_attr():
    obj = ver_attr()
    assert obj.value == 0
    obj()
    assert obj.value == 1
    obj()
    assert obj.value == 2


from timeit import timeit

t_list = timeit(partial(ver_list, [0]))
t_closure = timeit(ver_closure())
t_attr = timeit(ver_attr())
t_attr2 = timeit(partial(ver_attr.__call__, ver_attr()))
print(f"{t_list = }")
print(f"{t_closure = }")
print(f"{t_attr = }")
print(f"{t_attr2 = }")
