from blessed import Terminal
from time import sleep, time
from functools import partial
from collections import defaultdict
from math import factorial
import random


def is_valid(old_block, new_block):
    return all((xy in old_block or grid[xy] == '.') and  # noqa
               xy.imag < height and 0 <= xy.real < width
               for xy in new_block)


def repaint(old_block, new_block):
    for xy in old_block:
        grid[xy] = '.'

    for xy in new_block:
        grid[xy] = '#'


def draw_next_block(block, character='#'):
    for xy in block:
        y = int(term.height//2 + xy.imag)
        x = int((term.width + width)//2 + xy.real + 2)
        echo(term.move_yx(y, x) + character)


def move(block, direction):
    global block_traveling

    moved_block = [xy + direction for xy in block]
    if is_valid(block, moved_block):
        repaint(block, moved_block)
        block = moved_block

    elif direction == 1j:
        if block[0].real != int(block[0].real):
            grid[block[0]] = '.'
        block_traveling = False

    return block


def rotate(block, paint=True):
    center = block[0]
    rotated_block = [center + (xy-center)*1j for xy in block]
    if is_valid(block, rotated_block):
        if paint:
            repaint(block, rotated_block)
        block = rotated_block

    return block


def create_block():
    block = random.choice(blocks)
    for i in range(random.randint(0, 4)):
        block = rotate(block, paint=False)
    return block


def message(s):
    echo(term.move(term.height//2) + term.center(term.reverse(s)))


term = Terminal()
grid = defaultdict(lambda: '.')
echo = partial(print, flush=True)
width = 10
height = 20
score = 0
speed = 0.5

O_block = [4.5-1.5j, 4-1j, 4-2j, 5-1j, 5-2j]
I_block = [5-3j, 5-2j, 5-1j, 5-4j]
T_block = [4-2j, 3-2j, 4-1j, 5-2j]
L_block = [4-1j, 4-2j, 4-3j, 5-3j]
L2_block = [4-1j, 4-2j, 4-3j, 3-3j]
S_block = [5-1j, 4-1j, 5-2j, 6-2j]
Z_block = [5-2j, 4-2j, 5-1j, 6-1j]
blocks = [O_block, I_block, T_block, L_block, L2_block, S_block, Z_block]
block_traveling = False

if __name__ == "__main__":
    with term.cbreak(), term.hidden_cursor(), term.fullscreen():
        message('press any key to play tetris')
        term.inkey()
        message("press 'asd' or 'hjl' to move, 'r' to rotate and 'q' to quit")
        term.inkey()
        message(term.clear)
        next_block = create_block()
        start = time()
        step = start + speed
        while True:
            if not block_traveling:
                score += 1
                if score % 10 == 0:
                    speed -= 0.05

                block = next_block
                next_block = create_block()

                block_traveling = True

                x = int((term.width + width)//2)
                y = int(term.height//2)
                echo(term.move_yx(y-6, x+1) + 'next block:')
                draw_next_block(block, character=' ')
                draw_next_block(next_block)
                echo(term.move_yx(y+2, x+1) + f'score: {score}')

            echo(term.move_y((term.height - height)//2))
            for y in range(height):
                echo(term.move_x((term.width - width)//2) +  # noqa
                     ''.join(grid[x+y*1j] for x in range(width)))

            direction = 0
            character = term.inkey(timeout=step-time())
            if character:
                if character in 'ha':
                    direction = -1
                elif character in 'js':
                    direction = 1j
                elif character in 'ld':
                    direction = 1
                elif character == 'r':
                    block = rotate(block)
                elif character == 'q':
                    break

            block = move(block, direction)
            if time() > step:
                block = move(block, 1j)
                step = time() + speed

            if not block_traveling:
                y = height-1
                completed = []
                while y > 0:
                    if all(grid[x+y*1j] == '#' for x in range(width)):
                        completed.append(y)
                        for z in range(y, -1, -1):
                            for x in range(width):
                                grid[x+z*1j] = grid[x+(z-1)*1j]
                    else:
                        y -= 1
                for y in completed:
                    score += (height - y) * 100

                score += (factorial(len(completed)) - 1) * 500

                if any(xy.imag == 0 for xy in block):
                    message('game over')
                    sleep(2)
                    break

    print(f'score: {score}')
