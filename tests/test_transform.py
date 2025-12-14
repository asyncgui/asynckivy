import pytest


@pytest.fixture()
def widget():
    from kivy.uix.widget import Widget
    from kivy.graphics import Color
    w = Widget()
    c = w.canvas
    c.add(Color())
    c.before.add(Color())
    c.after.add(Color())
    return w


def list_children(canvas):
    return [inst.__class__.__name__ for inst in canvas.children]


def test_outer(widget):
    from asynckivy import transform
    c = widget.canvas
    with transform(widget, working_layer="outer"):
        assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase']
        assert list_children(c.before) == ['InstructionGroup', 'Color', ]
        assert list_children(c.before.children[0]) == ['PushMatrix', 'InstructionGroup', ]
        assert list_children(c.after) == ['Color', 'PopMatrix', ]
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]
    assert list_children(c.before) == ['Color', ]
    assert list_children(c.after) == ['Color', ]


def test_inner_outer(widget):
    from asynckivy import transform
    c = widget.canvas
    with transform(widget, working_layer="inner_outer"):
        assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase']
        assert list_children(c.before) == ['Color', 'InstructionGroup', ]
        assert list_children(c.before.children[1]) == ['PushMatrix', 'InstructionGroup', ]
        assert list_children(c.after) == ['PopMatrix', 'Color', ]
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]
    assert list_children(c.before) == ['Color', ]
    assert list_children(c.after) == ['Color', ]


def test_inner(widget):
    from asynckivy import transform
    c = widget.canvas
    with transform(widget, working_layer="inner"):
        assert list_children(c) == ['CanvasBase', 'InstructionGroup', 'Color', 'PopMatrix', 'CanvasBase']
        assert list_children(c.before) == ['Color', ]
        assert list_children(c.children[1]) == ['PushMatrix', 'InstructionGroup', ]
        assert list_children(c.after) == ['Color', ]
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]
    assert list_children(c.before) == ['Color', ]
    assert list_children(c.after) == ['Color', ]
