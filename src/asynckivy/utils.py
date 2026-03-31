__all__ = ("render_widget_to_texture", )

from kivy.graphics.texture import Texture
from kivy.graphics import Fbo, Translate


def render_widget_to_texture(widget) -> Texture:
    '''
    .. versionadded:: 0.10.0
    '''
    fbo = Fbo(size=widget.size)
    fbo.children.extend(
        (Translate(-widget.x, -widget.y, 0.), widget.canvas, )
    )
    fbo.draw()
    fbo.children.clear()
    return fbo.texture
