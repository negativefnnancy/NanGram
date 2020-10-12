from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from itertools import product, count, repeat
import string
import random
from .node import Node
from .util import *

# TODO: verbosity in parsing methods?

@dataclass
class Element(ABC):
    """Represents a grammatical element."""

    # TODO: figure out how to not have to duplicate all the default value fields in the element subclasses

    def _generate(self, grammar: Grammar, depth: int = 0, verbose: bool = False):
        """Generate all possible strings this element can match."""

        if verbose:
            print(f'Generation depth = {depth}.')

        if depth < grammar.max_recursions:
            if verbose and self.generation_override:
                print(f'Generation override = {self.generation_override!r}.')
            return [self.generation_override] if self.generation_override else self.generate(grammar, depth, verbose)

        if verbose:
            print(f'Generation depth too high; stopping generation here.')

        return iter(())

    @abstractmethod
    def generate(self, grammar: Grammar, verbose: bool = False):
        """Subclass generation method."""

        ...

    @abstractmethod
    def parse(self, grammar: Grammar, rule: str, string: str, position: int = 0, verbose: bool = False):
        """Generate all possible parse trees."""

        ...

@dataclass
class Terminal(Element):
    """Represents a terminal string element."""

    # literal string to use as the terminal element
    string: str
    generation_override: str = None
    label: str = None

    def generate(self, grammar: Grammar, depth: int = 0, verbose: bool = False):
        """Generate the terminal."""

        if verbose:
            print(f'Generating terminal {self.string!r}.')

        yield self.string

    def parse(self, grammar: Grammar, rule: str, string: str, position: int = 0, verbose: bool = False):
        """Parse the terminal."""

        region = slice(position, position + len(self.string))
        if string[region] == self.string:
            yield Node(grammar, rule, string, region, label=self.label)

    def __str__(self):
        label = f'{self.label}:' if self.label else ''
        return f'{label}"{self.string}"'

@dataclass
class Substitution(Element):
    """Represents a stand-in for another grammar rule."""

    # the name of the rule in the grammar
    name: str
    generation_override: str = None
    label: str = None

    def generate(self, grammar: Grammar, depth: int = 0, verbose: bool = False):
        """Generate the non-terminal."""

        if verbose:
            print(f'Generating substitution rule {self.name!r}.')

        return grammar.rules[self.name]._generate(grammar, depth, verbose)

    def parse(self, grammar: Grammar, rule: str, string: str, position: int = 0, verbose: bool = False):
        """Parse the non-terminal."""

        return label_node(grammar.rules[self.name].parse(grammar, self.name, string, position, verbose), self.label)

    def __str__(self):
        label = f'{self.label}:' if self.label else ''
        return f'{label}{self.name}'

@dataclass
class Sequence(Element):
    """Represents a sequence of elements."""

    # the sequence
    elements: list
    generation_override: str = None
    label: str = None

    def generate(self, grammar: Grammar, depth: int = 0, verbose: bool = False):
        """Generate all possible sequences."""

        if verbose:
            print(f'Generating sequence.')

        return generate_product(grammar, lambda: (element._generate(grammar, depth + 1, verbose) for element in self.elements), verbose)

    def parse(self, grammar: Grammar, rule: str, string: str, position: int = 0, verbose: bool = False):
        """Parse the sequence."""

        return label_node(parse_sequence(self.elements, grammar, rule, string, position, verbose), self.label)

    def __str__(self):
        return ' '.join(map(str, self.elements))

@dataclass
class Choice(Element):
    """Represents a choice among elements."""

    # the possible choices
    elements: list
    generation_override: str = None
    label: str = None

    def generate(self, grammar: Grammar, depth: int = 0, verbose: bool = False):
        """Generate all possible choices."""

        if verbose:
            print(f'Generating choice.')

        for element in self.elements:
            for string in element._generate(grammar, depth + 1, verbose):
                yield string

    def parse(self, grammar: Grammar, rule: str, string: str, position: int = 0, verbose: bool = False):
        """Parse the choice."""

        return label_node(parse_choice(self.elements, grammar, rule, string, position, verbose), self.label)

    def __str__(self):
        return ' | '.join(map(str, self.elements))

@dataclass
class Option(Element):
    """Represents an optional element."""

    # the optional element
    element: Element
    generation_override: str = None
    label: str = None

    def generate(self, grammar: Grammar, depth: int = 0, verbose: bool = False):
        """Generate the optional element."""

        if verbose:
            print(f'Generating option.')

        yield ""
        for string in self.element._generate(grammar, depth + 1, verbose):
            yield string

    def parse(self, grammar: Grammar, rule: str, string: str, position: int = 0, verbose: bool = False):
        """Parse the optional element."""

        yield Node(grammar, rule, string, slice(position, position), label=self.label)
        for node in label_node(self.element.parse(grammar, rule, string, position, verbose), self.label):
            yield node
                
    def __str__(self):
        return f'[ {self.element} ]'

@dataclass
class Repetition(Element):
    """Represents an n-times repeated element."""

    # the element to be repeated
    element: Element
    generation_override: str = None
    label: str = None

    def generate(self, grammar: Grammar, depth: int = 0, verbose: bool = False):
        """Generate the repeated element."""

        if verbose:
            print(f'Generating repetition.')

        yield ""
        for n in range(1, grammar.max_repetitions):
            for prod in generate_product(grammar, lambda: (self.element._generate(grammar, depth + 1, verbose) for _ in range(n)), verbose):
                yield prod

    def parse(self, grammar: Grammar, rule: str, string: str, position: int = 0, verbose: bool = False):
        """Parse the repeated element."""

        yield Node(grammar, rule, string, slice(position, position), label=self.label)
        for n in count(1):
            elements = list(repeat(self.element, n))
            nodes = parse_sequence(elements, grammar, rule, string, position, verbose)
            m = 0
            for node in nodes:
                m += 1
                if self.label:
                    yield Node(grammar, rule, string, node.region, [node], label=self.label)
                else:
                    yield node
            if m == 0:
                break

    def __str__(self):
        return f'{{ {self.element} }}'

@dataclass
class StringLiteralCharacter(Element):
    """Specialized element that accepts literal string characters.

    This includes all unicode characters, excludes the unescaped string delimiter ("), escape character (\), and includes all escaped characters.
    """

    generation_override: str = None
    label: str = None

    delimiter: str = '"'
    escape_character: str = '\\'

    def escape(self, string: str) -> str:
        """Escape every character in a given string."""

        return ''.join([self.escape_character + c for c in string])

    def generate(self, grammar: Grammar, depth: int = 0, verbose: bool = False):
        """Generate the character."""

        characters = list(string.printable)
        characters[characters.index(self.escape_character)] = self.escape(self.escape_character)
        characters[characters.index(self.delimiter)] = self.escape(self.delimiter)
        # TODO: maybe add some common escape sequences?
        return random.choice(characters)

    def parse(self, grammar: Grammar, rule: str, string: str, position: int = 0, verbose: bool = False):
        """Parse the character."""

        character = string[position]
        region = None
        if character == self.escape_character:
            region = slice(position + 1, position + 2)
        elif character != self.delimiter:
            region = slice(position, position + 1)
        if region:
            yield Node(grammar, rule, string, region, label=self.label)

    # NOTE: there is no __str__ because this is a special element that is only used internally (for now lol)
