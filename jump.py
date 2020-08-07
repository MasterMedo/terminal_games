from functools import partial
from math import sin, pi

from blessed import Terminal

import time

term = Terminal()


def jump(t, f, lower_boundary, upper_boundary):
    if t >= lower_boundary and t < upper_boundary:
        return f(t)


fps = 240
step = 1/fps
jump_function = sin
lower_boundary = 0
upper_boundary = pi
jump_amplitude = term.height
jump_duration = upper_boundary - lower_boundary

echo = partial(print, flush=True, end='')
jump = partial(jump,
               f=jump_function,
               lower_boundary=lower_boundary,
               upper_boundary=upper_boundary)

jumping = False
jump_time = None
y = 0
y_ = term.height

with term.cbreak(), term.hidden_cursor(), term.fullscreen():
    echo(term.move_y(term.height//2) + term.center('Press any key to jump!'))
    while True:
        frame_start = time.time()

        if jumping:
            y = jump(time.time() - jump_time)
            if y is None:  # jump duration exceeded!
                jumping = False
                y = 0
            else:
                y = min(1, max(0, y))

        if (tmp := term.height - round(y * jump_amplitude)) != y_:
            echo(term.move_yx(y_, 0) + ' '*term.width)
            y_ = tmp
            echo(term.move_yx(y_, 0) + '#'*term.width)

        key_pressed = term.inkey(timeout=frame_start - time.time() + step)
        if not jumping and key_pressed:
            jump_time = time.time()
            jumping = True

        while time.time() < frame_start + step:
            pass
