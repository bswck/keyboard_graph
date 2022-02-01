import collections
import dataclasses
import functools
import itertools

import networkx as nx
import matplotlib.pyplot as plt

SKIP_VAL = ''
LOOK_BEHIND = 0
DEFAULT_LAYOUT_ID = 'QWERTY'


def map_char(ch, skip):
    if ch == skip:
        return SKIP_VAL
    return ch


def reduce_chained_chars(chars, chain_char):
    mapped = []

    for char in chars:
        mapped.append(char.rstrip(chain_char))
        ratio = char.count(chain_char)
        if ratio:
            mapped.extend([LOOK_BEHIND] * ratio)

    return mapped


def load_keyboard_layout(layout=DEFAULT_LAYOUT_ID):
    with open(f'./layouts/{layout.upper()}.txt', encoding='utf-8') as f:
        skip_decl, sep_decl, chain_decl, _, *layout = f.read().split('\n')

        _, skip_char = skip_decl.split('=')
        _, sep_char = sep_decl.split('=')
        _, chain_char = chain_decl.split('=')

        rows = map(
            lambda row: tuple(map(lambda key: map_char(key, skip_char), row)),
            filter(
                None,
                map(lambda row: reduce_chained_chars(row.split(sep_char), chain_char), layout)
            )
        )

        return tuple(itertools.zip_longest(*rows, fillvalue=SKIP_VAL))


def create_keyboard_graph(layout=None):
    if layout is None:
        layout = load_keyboard_layout()

    rows = tuple(layout)
    graph = nx.Graph()
    height = len(rows[0])
    row_edges = collections.defaultdict(lambda: [SKIP_VAL] * height)

    for column, chars in enumerate(rows):
        column_edge = SKIP_VAL

        for row, char in enumerate(chars):
            looked_behind = False

            if char == LOOK_BEHIND:
                looked_behind = True
                char = row_edges[column - 1][row]

            if char == SKIP_VAL:
                continue

            graph.add_node(char)

            if column_edge != SKIP_VAL:
                graph.add_edge(char, column_edge)

            column_edge = char

            if not looked_behind:
                in_column_behind = row_edges[column - 1][row]
                if in_column_behind != SKIP_VAL:
                    graph.add_edge(char, in_column_behind)

        row_edges[column] = chars

    return graph


@dataclasses.dataclass(frozen=True)
class Key:
    key: str
    neighbours: tuple[str]


@dataclasses.dataclass
class Keyboard:
    layout_id: str = DEFAULT_LAYOUT_ID

    @functools.cached_property
    def keys(self):
        return tuple(map(
            self.key,
            filter(SKIP_VAL.__ne__, itertools.chain.from_iterable(self.layout))
        ))

    @functools.cached_property
    def layout(self):
        return load_keyboard_layout(self.layout_id)

    @functools.cached_property
    def graph(self):
        return create_keyboard_graph(self.layout)

    def key(self, char):
        return Key(char, tuple(self.graph.adj[char]))

    def __iter__(self):
        yield from self.keys


def draw_keyboard(layout_id=DEFAULT_LAYOUT_ID):
    layout = load_keyboard_layout(layout_id)
    graph = create_keyboard_graph(layout)
    nx.draw_kamada_kawai(
        graph,
        with_labels=True,
        node_color='lightgrey',
        node_shape='s',
    )
    plt.show()


if __name__ == '__main__':
    keyboard = Keyboard()
    draw_keyboard()
