from functools import partial
from string import ascii_lowercase
from blessed import Terminal

term = Terminal()
echo = partial(print, flush=True)

color_black = term.white_on_black
color_white = term.white_on_blue

pieces = {
    'B': '♝♗',
    'K': '♚♔',
    'N': '♞♘',
    'P': '♟♙',
    'Q': '♛♕',
    'R': '♜♖',
}

board = [
    '♜♞♝♛♚♝♞♜',
    '♟♟♟♟♟♟♟♟',
    '        ',
    '        ',
    '        ',
    '        ',
    '♙♙♙♙♙♙♙♙',
    '♖♘♗♕♔♗♘♖',
]

if __name__ == '__main__':
    with term.cbreak(), term.hidden_cursor():
        echo(' ' + ''.join(ascii_lowercase[i] for i in range(8)))
        for i, line in enumerate(board):
            row = []
            for j, c in enumerate(line):
                color = color_black if (j+i) % 2 == 0 else color_white
                row.append(color + c)
            row.append(term.normal)
            print(f"{i+1}{''.join(row)}")
        while True:
            pass
