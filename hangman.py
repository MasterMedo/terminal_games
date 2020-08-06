from blessed import Terminal
from requests import get
from requests.exceptions import ConnectionError
from functools import partial
from itertools import chain
from random import shuffle


term = Terminal()
echo = partial(print, flush=True)

man = r"""----|
|  lll
| (O.O)
| -|.|-
|  / \
-"""

body_parts = [[9, 10, 11],
              [15, 19], [16], [17], [18],
              [23], [24, 25, 26], [27],
              [32], [34]]

shuffle(body_parts)

tries, letters = 10, set()
word = 'hangman'

try:
    response = get('https://random-word.ryanrk.com/api/en/word/random')
    word = response.json()[0].lower()
except ConnectionError:
    print('You need an internet connection to play this game!\n')


with term.cbreak(), term.hidden_cursor():
    while True:
        echo(f'Tries left: {tries} ')
        for i, x in enumerate(man):
            echo(x if i not in chain(*body_parts) else ' ', end='')

        echo('\n' + ' '.join(c if c in letters else '_' for c in word))

        if tries == 0:
            echo('You lost!')
            break

        if set(word) == letters:
            echo('Congratulations! You won!')
            break

        echo(term.move_up(9))

        c = term.inkey()
        if len(c) == 1 and c in word and c not in letters:
            letters.add(c)
        else:
            tries -= 1
            body_parts = body_parts[:-1]

echo(f'The word was `{word}`!')
