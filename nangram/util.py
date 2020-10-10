from __future__ import annotations
from itertools import product
from functools import reduce
import random
import operator
from .node import Node

def get_length(sequence) -> int:
    """Return the length of any sequence, which may be a generator.

    Beware of infinite sequences.
    """

    n = 0
    for _ in sequence:
        n += 1
    return n

def random_sample(sequence_func, n: int, length: int = None):
    """Specialized function to sample n items from a sequence, which may be a generator.

    sequence_func is a function to return the sequence.
    """

    # the predeturmined indices of the items to collect
    length = length or get_length(sequence_func())
    indices = random.sample(range(length), min(n, length))

    for i, item in enumerate(sequence_func()):
        if i in indices:
            yield item

def make_padding(indent: int) -> str:
    """Make a left-side whitespace padding for a given indention level."""

    return '   ' * indent

def parse_sequence(elements: list, grammar: Grammar, rule: str, string, position: int = 0, verbose: bool = False):
    """Parse a sequence."""

    def sequential_choices(elements: list, position: int) -> list:
        if elements:
            head, tail = elements[0], elements[1:]
            head_choices = head.parse(grammar, rule, string, position, verbose)
            for head_choice in head_choices:
                tail_choices = sequential_choices(tail, head_choice.region.stop)
                for tail_choice in tail_choices:
                    yield [head_choice] + tail_choice
        else:
            yield [Node(grammar, rule, string, slice(position, position))]

    for children in sequential_choices(elements, position):
        region = slice(children[0].region.start, children[-1].region.stop)
        yield Node(grammar, rule, string, region, children)

def generate_product(grammar: Grammar, generators_func, verbose: bool = False):
    """Generate the combinations of some generators.

    generators_func is a function to return a list of generators.
    """

    if verbose:
        length = get_length(generators_func())
        print("Generating product of {length} sequences.")
    lengths = list(map(get_length, generators_func()))
    length = reduce(operator.mul, lengths, 1)
    for prod in random_sample(lambda: product(*generators_func()), grammar.max_products, length):
        yield ''.join(prod)

    # TODO: get way more performance out of this lol

    #for i, prod in enumerate(product(*generators_func())):
    #    if i < grammar.max_products:
    #        if verbose:
    #            print(f'Joining sequence of length {len(prod)}.')
    #        yield ''.join(prod)
    #        if verbose:
    #            print(f'Finished joining sequence.')
    #    else:
    #        if verbose:
    #            print(f'Generation sequence too long; stopping generation here.')
    #        break
