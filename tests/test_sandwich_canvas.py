import pytest


@pytest.fixture()
def canvas():
    from kivy.graphics import Canvas, Color
    c = Canvas()
    c.before.add(Color())
    c.add(Color())
    c.after.add(Color())
    return c


def list_children(canvas):
    return [inst.__class__.__name__ for inst in canvas.children]


def test_how_a_before_group_and_an_after_group_work():
    '''
    This just confirms how Kivy works, and does not test any asynckivy code.
    '''
    from kivy.graphics import Canvas, Color
    c = Canvas()
    c.add(Color())
    assert list_children(c) == ['Color', ]
    c.before
    assert list_children(c) == ['CanvasBase', 'Color', ]
    c.after
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]


def test_initial_state_of_the_canvas_fixture(canvas):
    c = canvas
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]
    assert list_children(c.before) == ['Color', ]
    assert list_children(c.after) == ['Color', ]


def test_inner(canvas):
    from kivy.graphics import PushMatrix, PopMatrix
    from asynckivy import sandwich_canvas
    c = canvas
    with sandwich_canvas(c, top_bun=PushMatrix(), bottom_bun=PopMatrix(), insertion_layer="inner"):
        assert list_children(c) == ['CanvasBase', 'PushMatrix', 'Color', 'PopMatrix', 'CanvasBase']
        assert list_children(c.before) == ['Color', ]
        assert list_children(c.after) == ['Color', ]
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]
    assert list_children(c.before) == ['Color', ]
    assert list_children(c.after) == ['Color', ]


def test_outer(canvas):
    from kivy.graphics import PushMatrix, PopMatrix
    from asynckivy import sandwich_canvas
    c = canvas
    with sandwich_canvas(c, top_bun=PushMatrix(), bottom_bun=PopMatrix(), insertion_layer="outer"):
        assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase']
        assert list_children(c.before) == ['PushMatrix', 'Color', ]
        assert list_children(c.after) == ['Color', 'PopMatrix', ]
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]
    assert list_children(c.before) == ['Color', ]
    assert list_children(c.after) == ['Color', ]


def test_inner_outer(canvas):
    from kivy.graphics import PushMatrix, PopMatrix
    from asynckivy import sandwich_canvas
    c = canvas
    with sandwich_canvas(c, top_bun=PushMatrix(), bottom_bun=PopMatrix(), insertion_layer="inner_outer"):
        assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase']
        assert list_children(c.before) == ['Color', 'PushMatrix', ]
        assert list_children(c.after) == ['PopMatrix', 'Color', ]
    assert list_children(c) == ['CanvasBase', 'Color', 'CanvasBase', ]
    assert list_children(c.before) == ['Color', ]
    assert list_children(c.after) == ['Color', ]


def test_inner_no_before_nor_after():
    from kivy.graphics import PushMatrix, PopMatrix, Canvas, Color
    from asynckivy import sandwich_canvas
    c = Canvas()
    c.add(Color())
    with sandwich_canvas(c, top_bun=PushMatrix(), bottom_bun=PopMatrix(), insertion_layer="inner"):
        assert list_children(c) == ['PushMatrix', 'Color', 'PopMatrix', ]
        assert not c.has_before
        assert not c.has_after
    assert list_children(c) == ['Color', ]
    assert not c.has_before
    assert not c.has_after
