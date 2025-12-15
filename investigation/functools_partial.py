'''
FutureWarning: functools.partial will be a method descriptor in future Python versions; wrap it in
staticmethod() if you want to preserve the old behavior

partialを噛ました関数は自動でstaticmethodになっていたと思うが、どうやら将来はそうじゃなくなる？
なので以下の `printB` のように明示的にstaticmethodで包む事にするが、念のために余分な関数呼び出しが
発生しないか確認。
'''

from functools import partial

class MyClass:
    printA = partial(print, 'A', 'B')
    printB = staticmethod(printA)

    def __init__(self):
        assert partial(self.printA, 'C').func is print
        assert partial(self.printB, 'C').func is print

MyClass()
