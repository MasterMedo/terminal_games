from collections import defaultdict
from functools import partial

from blessed import Terminal

import time


fps = 30
step = 1/fps
fov = 10

term = Terminal()
echo = partial(print, flush=True)


def jump():
    ...


def move():
    ...


a_x_max = ...
a_y_max = ...
v_x_max = ...
v_y_max = ...
v_xy = 0
a_xy = 0

level = defaultdict(lambda: ' ')
with open(__file__[:-2] + 'txt') as f:
    for j, line in enumerate(f):
        for i, c in enumerate(line[:-1]):
            if c == 'M':
                xy = i + j*1j

            elif c != ' ':
                level[i + j*1j] = c

start = time.time()

with term.cbreak(), term.hidden_cursor(), term.fullscreen():
    while True:
        frame_time = time.time()

        echo(term.home)
        for j in range(int(xy.imag) - fov, int(xy.imag) + fov):
            for i in range(int(xy.real) - fov, int(xy.real) + fov):
                echo(level[i + j*1j], end='')
            echo()

        cmd = term.inkey(timeout=step + frame_time - time.time())
        if cmd == 'l':
            xy += 1

        while time.time() < step + frame_time:
            pass
