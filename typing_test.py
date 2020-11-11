#!/usr/bin/env python3
import os
import sys
import signal
import random
import platform

from time import time, strftime, gmtime
from datetime import datetime
from argparse import ArgumentParser, RawTextHelpFormatter
from functools import partial

from blessed import Terminal


def main(words, duration, rows, shuffle, help):
    """Takes chars from user input forming a word every time a whitespace is
    pressed and compares typed words with test `words`. Updates the screen
    calling `draw` every time a key is pressed or every 0.1 seconds, whichever
    comes first.

    The test ends when `duration` time has passed or all words have been typed.
    Upon exiting test results are printed.
    """
    global redraw

    def on_resize(*_):
        global redraw
        redraw = True

    redraw = True
    if platform.system() == 'Windows':
        sys.__stdin__ = open('con:', 'r')  # force stdin from user NOT TESTED
    else:
        signal.signal(signal.SIGWINCH, on_resize)
        sys.__stdin__ = open('/dev/tty', 'r')  # force stdin from user

    if not words:
        if sys.stdin.isatty():  # no test words provided
            sys.exit(help(file=sys.__stdout__))

        words = sys.stdin.read().split()
        sys.argv.extend(words)

    if shuffle:
        random.shuffle(words)

    term = Terminal()

    color_normal = term.normal
    color_correct = term.color_rgb(0, 230, 0)
    color_wrong = term.color_rgb(230, 0, 0)

    timestamp = '00:00:00'
    correct_chars = total_chars = wpm = 0
    duration_ = start = 0
    word_i = 0
    text = ''
    colors = [color_normal]*len(words)

    with term.raw(), \
            term.cbreak(), \
            term.fullscreen(), \
            term.hidden_cursor():
        while word_i < len(words) and (not start or time() - start < duration):
            word = words[word_i]

            if redraw:
                redraw = False

                color = color_correct if word == text else \
                    color_normal if word.startswith(text) else \
                    color_wrong

                colors[word_i] = color + term.reverse
                draw(term, rows, words, colors, word_i, text, wpm, timestamp)

            char = term.inkey(timeout=0.1, esc_delay=0)
            if not char:
                continue

            if not start:
                start = time()

            if char == '\x03' or char == '\x1b':  # ctrl-c or esc
                break

            elif char == '\x08' or char == '\x7f':  # ctrl-h or backspace
                text = text[:-1]

            elif char == '\x12':  # ctrl-r
                os.execv(sys.executable, ['python'] + sys.argv)

            elif char == '\x15' or char == '\x17':  # ctrl-u or ctrl-w
                text = ''

            elif char.isspace() and text:
                if text == word:
                    correct_chars += len(word) + (word_i + 1 < len(words))
                    colors[word_i] = color_correct
                else:
                    correct_chars += (word_i + 1 < len(words))
                    colors[word_i] = color_wrong

                total_chars += len(word) + (word_i + 1 < len(words))
                duration_ = time() - start
                wpm = min(int(correct_chars*12/duration_), 999)
                timestamp = strftime('%H:%M:%S', gmtime(duration_))

                text = ''
                word_i += 1

            elif not char.isspace():
                text += char
                if word_i + 1 >= len(words) and words[-1] == text:
                    term.ungetch(' ')

            redraw = True

    accuracy = 100 * correct_chars // total_chars if total_chars else 0
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'accuracy: {accuracy}%', flush=True, file=term.stream)
    print(f'speed:    {wpm}wpm', flush=True, file=term.stream)
    print(f'duration: {duration_:.2f}s', file=term.stream)


def draw(term, rows, words, colors, word_i, text, wpm, timestamp):
    """Text wraps the `words` list to the terminal width, and prints `rows`
    lines of wrapped words colored with `colors` starting with the line
    containing the current word that is being typed.
    """
    def join(words, length):
        eol = term.clear_eol if length + len(words) - 1 < term.width else ''
        return ' '.join(line_words) + eol

    echo = partial(print, end='', flush=True, file=term.stream)
    allowed_height = min(term.height, rows)

    len_line = 0
    line_words = []
    line_height = None
    for i, (word, color) in enumerate(zip(words, colors)):
        if len_line + len(word) + len(line_words) > term.width:
            if line_height is not None:
                echo(term.move_yx(line_height, 0) + join(line_words, len_line))
                line_height += 1
                if line_height >= allowed_height:
                    break

            len_line = 0
            line_words = []

        if i == word_i:
            line_height = 0

        len_line += len(word)
        line_words.append(color + word + term.normal)

    else:
        echo(term.move_yx(line_height, 0) + join(line_words, len_line))
        line_height += 1

    if allowed_height > 1:
        n = term.width - 21
        echo(term.move_yx(line_height, 0) + f'>>>{text[:n]: <{n}}')
        echo(term.move_yx(line_height, n + 3) + f"{wpm:3d} wpm | {timestamp}")

    for i in range(1, allowed_height - line_height + 1):
        echo(term.move_yx(line_height + i, 0) + term.clear_eol)


def parse_args():
    """Parses `sys.argv` and returns `dict` suitable for `main`."""

    parser = ArgumentParser(description=f"""example:
  {os.path.basename(sys.argv[0])} -d 3.5 The typing seems really strong today.
  echo 'I love typing' | {os.path.basename(sys.argv[0])}
  {os.path.basename(sys.argv[0])} < test.txt
""", epilog="""shortcuts:
  ^c / ctrl+c           end the test and get results now
  ^h / ctrl+h           backspace
  ^r / ctrl+r           restart the same test
  ^w / ctrl+w           delete a word
  ^u / ctrl+u           delete a word
""", formatter_class=RawTextHelpFormatter)

    parser.add_argument('-d', '--duration', type=float, default=float('inf'),
                        help='duration in seconds')
    parser.add_argument('-r', '--rows', type=int, default=2,
                        help='number of test rows to show')
    parser.add_argument('-s', '--shuffle', action='store_true',
                        help='shuffle words')
    parser.add_argument('words', nargs='*',
                        help='provide words via args in lieu of stdin')

    return dict(parser.parse_args()._get_kwargs(), help=parser.print_help)


if __name__ == '__main__':
    main(**parse_args())
