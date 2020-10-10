from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Node:
    """Parse tree node."""

    # the grammar this was parsed with
    grammar: Grammar

    # the grammatical rule in the grammar that generated this node
    rule: str

    # the original string this was parsed from
    string: str

    # the region of the string parsed
    region: slice

    # a list of child nodes, if any
    children: list = field(default_factory=list)

    # label for this node for easy accessing in a list of children
    label: str = None

    def get(self, label, exclude=[]):
        """Yield all nearest branches with a given label.

        Will not traverse nodes with labels in the exclude list.
        """

        for child in self.children:
            if child.label == label:
                yield child
            elif child.label not in exclude:
                for match in child.get(label):
                    yield match

    @property
    def parsed_string(self) -> str:
        """Return the piece of string that was parsed by this node as a whole."""

        return self.string[self.region]

    @property
    def is_empty(self) -> bool:
        """Return whether this node matches the empty string."""

        return self.parsed_string == ''

    @property
    def is_space(self) -> bool:
        """Return whether this node matches white space."""

        return self.parsed_string.isspace()

    @property
    def is_complete(self) -> bool:
        """Whether this node matches the whole string."""

        return self.string == self.parsed_string

    @property
    def filtered_children(self) -> list:
        """Return a list of children that are not empty or whitespace."""

        return list(filter(lambda child: not child.is_empty and not child.is_space, self.children))

    def __str__(self):
        label = f'({self.label!r}) ' if self.label else ''
        string = f'{self.rule} {label}= {self.parsed_string!r}'
        children = self.filtered_children
        for i, child_string in enumerate(map(str, children)):
            arrow, line = ('└ ', '  ') if i == len(children) - 1 else ('├ ', '│ ')
            body = f'\n{line}'.join(child_string.split('\n'))
            string += f'\n{arrow}{body}'
        return string
