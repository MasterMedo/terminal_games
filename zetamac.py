import random

from time import time
from functools import partial
from operator import add, mul, truediv as div, sub

from blessed import Terminal


def generate(operator, operation, acap=99, bcap=99):
    while True:
        a = random.randint(1, acap)
        b = random.randint(1, bcap)
        result = operation(a, b)
        if result % 1 == 0 and result > 0:
            return f'{a} {operator} {b} = ', str(int(result))


operations = [
        partial(generate, '+', add),
        partial(generate, '-', sub, 189),
        partial(generate, '*', mul, 12),
        partial(generate, '/', div, 999),
]

term = Terminal()
with term.cbreak():
    start = time()
    duration = 120
    score = 0
    while time() - start < duration:
        question, result = random.choice(operations)()
        text = ''
        print(question, end='', flush=True)
        while time() - start < duration and text != result:
            c = term.inkey(timeout=0.1)
            if c == '\x08' or c == '\x7f':
                print('\b \b', end='', flush=True)
                text = text[:-1]

            elif c in '1234567890':
                print(c, end='', flush=True)
                text += c

        print(flush=True)

        score += 1

print(f'score: {score}')
with open(__file__[:-2] + 'txt', 'a') as f:
    print(score, file=f)
