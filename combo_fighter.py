from collections import namedtuple

import time
import functools

from blessed import Terminal

import pandas as pd

Combo = namedtuple('Combo', 'name damage children')
term = Terminal()
echo = functools.partial(print, flush=True)

fps = 120
step = 1/fps
combo_timeout = 1


def create_combo_tree(combo_table):
    """
    Creates and returns a `trie` tree structure that holds `Combo` nodes.
    A button press represents an edge in the tree; `Combo.children` is a `dict`
    whose `key: value` pairs are `button: Combo`.
    """
    combo_root = Combo(name='', damage=0, children=dict())
    for combo in combo_table.itertuples():
        combo_node = combo_root
        for i, button in enumerate(combo.button_combination):
            if button not in combo_node.children:
                if i == len(combo.button_combination) - 1:
                    name = combo.name
                elif button in combo_root.children:
                    name = combo_root.children[button].name
                else:
                    name = ''

                combo_node.children[button] = Combo(name=name,
                                                    damage=combo.damage,
                                                    children=dict())
            combo_node = combo_node.children[button]

    return combo_root


combo_table = pd.read_csv(__file__[:-2] + 'csv')
combo_root = create_combo_tree(combo_table)
health = 100
health_regeneration_per_second = 10
combo_start_time = 0
combo_node = combo_root

with term.cbreak(), term.fullscreen(), term.hidden_cursor():
    echo(term.home)
    echo(term.center(term.reverse('--- controls ---')))
    for line in repr(combo_table[:6]).splitlines():
        echo(term.center(line))
    echo(term.move_down(1))
    echo(term.center(term.reverse('--- press any button to play ---')))
    term.inkey()
    echo(term.clear)
    while True:
        frame_start_time = time.time()

        health_bar = f"health: {'#'*int((term.width - 8)*health/100)}"
        echo(term.home + health_bar + term.clear_eol)
        if health <= 0:
            echo(term.center('K.O.'))
            time.sleep(1)
            break

        health = min(100, health + health_regeneration_per_second / fps)

        button = term.inkey(timeout=frame_start_time - time.time() + step)
        if button:
            if time.time() - combo_start_time >= combo_timeout:
                combo_counter = 1
                combo_node = combo_root
            else:
                combo_counter += 1

            if button not in combo_node.children:
                if button in combo_root.children:
                    if combo_root.children[button].name in combo_node.name:
                        combo_counter = 1
                combo_node = combo_root

            combo_start_time = time.time()
            if button in combo_node.children:
                combo_node = combo_node.children[button]
                damage_multiplier = min(combo_counter + 100, 300) * 0.01
                health -= combo_node.damage * damage_multiplier
                echo(term.move_yx(term.height//2, 0))
                echo(term.center(combo_node.name))
                echo(term.move_down(1) + term.center(combo_counter))

        while time.time() < frame_start_time + step:
            pass
