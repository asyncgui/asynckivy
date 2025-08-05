import pytest


@pytest.fixture()
def widget():
    from kivy.uix.widget import Widget
    from kivy.graphics import Color
    w = Widget()
    w.canvas.add(Color())
    return w


def list_children(canvas):
    return [inst.__class__.__name__ for inst in canvas.children]


def test_just_confirm_how_a_before_group_and_an_after_group_work(widget):
    c = widget.canvas
    assert list_children(c) == ['Color', ]
    c.before
    assert list_children(c) == ['CanvasBase', 'Color', ]
    c.after
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]


@pytest.mark.parametrize('has_before', (True, False, ))
@pytest.mark.parametrize('has_after', (True, False, ))
def test_use_outer_canvas(widget, has_before, has_after):
    from asynckivy import transform
    c = widget.canvas
    if has_before: c.before
    if has_after: c.after
    with transform(widget, use_outer_canvas=True):
        assert c.has_before
        assert c.has_after
        assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase']
        assert list_children(c.before) == ['PushMatrix', 'InstructionGroup', ]
        assert list_children(c.after) == ['PopMatrix', ]
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]
    assert list_children(c.before) == []
    assert list_children(c.after) == []


@pytest.mark.parametrize('has_before', (True, False, ))
@pytest.mark.parametrize('has_after', (True, False, ))
def test_use_inner_canvas(widget, has_before, has_after):
    from asynckivy import transform
    c = widget.canvas
    if has_before: c.before
    if has_after: c.after
    with transform(widget, use_outer_canvas=False):
        expect = ['PushMatrix', 'InstructionGroup', 'Color', 'PopMatrix', ]
        if has_before:
            assert list_children(c.before) == []
            expect.insert(0, 'CanvasBase')
        if has_after:
            assert list_children(c.after) == []
            expect.append('CanvasBase')
        assert list_children(c) == expect
    assert c.has_before is has_before
    assert c.has_after is has_after
