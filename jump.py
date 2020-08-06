from functools import partial
from math import sin, pi

from blessed import Terminal

import time

term = Terminal()
echo = partial(print, flush=True, end='')


fps = 240
step = 1/fps


def f(t):
    """ Jump function

    x - time since jump was performed

    Returns jump height if jump duration is not exceeded else `None`.
    The returned value is externally trimmed to [0, 1].
    """
    if t >= 0 and t < pi:
        return sin(t)


jump_amplitude = term.height
z = y = 0
y_ = jump_amplitude
jump_time = None
jumping = False

with term.cbreak(), term.hidden_cursor(), term.fullscreen():
    while True:
        frame_start = time.time()

        if jumping:
            y = f(time.time() - jump_time)
            if y is None:
                jumping = False
                y = 0
            else:
                y = min(1, max(0, y))

        if (tmp := term.height - round(y*(jump_amplitude))) != y_:
            echo(term.move_yx(y_, 0) + ' '*term.width)
            y_ = tmp
            echo(term.move_yx(y_, 0) + '#'*term.width)

        jump = term.inkey(timeout=frame_start - time.time() + step)
        if not jumping and jump:
            jump_time = time.time()
            jumping = True

        while time.time() < frame_start + step:
            pass
