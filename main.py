import collections
import dataclasses
import functools
import itertools

import networkx as nx
import matplotlib.pyplot as plt

SKIP_CHAR = '_'
SKIP_VAL = ''
DEFAULT_LAYOUT = 'QWERTY'


def map_char(ch):
    if ch == SKIP_CHAR:
        return SKIP_VAL
    return ch


def load_layout(layout=DEFAULT_LAYOUT):
    with open(f'./layouts/{layout.upper()}.txt') as f:
        rows = map(lambda row: tuple(map(map_char, row)), map(tuple, f.read().split('\n')))
        return tuple(itertools.zip_longest(*rows, fillvalue=SKIP_VAL))


def create_graph(layout=None):
    if layout is None:
        layout = load_layout()

    rows = tuple(layout)
    graph = nx.Graph()
    height = len(rows[0])
    row_edges = collections.defaultdict(lambda: [SKIP_VAL] * height)

    for column, chars in enumerate(rows):
        column_edge = SKIP_VAL

        for row, char in enumerate(chars):
            if char == SKIP_VAL:
                continue

            graph.add_node(char)

            if column_edge != SKIP_VAL:
                graph.add_edge(char, column_edge)

            column_edge = char

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
    layout_id: str = DEFAULT_LAYOUT

    @functools.cached_property
    def keys(self):
        return tuple(map(
            self.key,
            filter(SKIP_VAL.__ne__, itertools.chain.from_iterable(self.layout))
        ))

    @functools.cached_property
    def layout(self):
        return load_layout(self.layout_id)

    @functools.cached_property
    def graph(self):
        return create_graph(self.layout)

    def key(self, char):
        return Key(char, tuple(self.graph.adj[char]))

    def __iter__(self):
        yield from self.keys


def draw_keyboard():
    g = create_graph()
    nx.draw(g)
    plt.show()


if __name__ == '__main__':
    keyboard = Keyboard()

    print('Keyboard', keyboard.layout)
    for key in keyboard:
        print('→'.center(3), str(key))

    draw_keyboard()
