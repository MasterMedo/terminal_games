from blessed import Terminal
from functools import partial

term = Terminal()
echo = partial(print, flush=True)

winning_positions = ('123', '456', '789', '147', '258', '789', '159', '357')
moves = '123456789'
grid = {}
i = 1

with term.cbreak(), term.hidden_cursor():
    while True:
        for move in moves:
            hint = term.gray20 + move + term.normal
            echo(grid.get(move, hint), end='\n' if move in '36' else '')

        if any(len(set(grid.get(c, c) for c in s)) == 1
               for s in winning_positions):
            echo(f"\n{'o' if i % 2 else 'x'} won!")
            break

        if i >= 10:
            echo("\nIt's a draw!")
            break

        echo(term.move_up(3))

        move = term.inkey()
        if move in moves and move not in grid:
            grid[move] = 'x' if i % 2 else 'o'
            i += 1
