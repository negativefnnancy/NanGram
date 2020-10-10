"""Expression parser and generator using defined grammars."""

from __future__ import annotations
from dataclasses import dataclass, field
import string
from .node import Node
from .element import *

@dataclass
class Grammar:
    """A set of production rules describing a context-free grammar."""

    # the set of production rules
    rules: dict

    # maximum product length, repetitions, and recursions for generation
    max_products:    int = 8
    max_repetitions: int = 4
    max_recursions:  int = 8

    def generate(self, rule_name: str = 'main', verbose: bool = False):
        """Generate all possible expressions matching a rule in the grammar."""

        if verbose:
            print(f'Generating with starting rule {rule_name!r}:')

        return self.rules[rule_name]._generate(self, verbose=verbose)

    def parse(self, string: str, rule_name: str = 'main', verbose: bool = False):
        """Generate all possible parse trees matching a string according to a rule in the grammar."""

        # TODO: figure out a system for reporting likely syntax errors?

        if verbose:
            print(f'Parsing with starting rule {rule_name!r}:')

        return self.rules[rule_name].parse(self, rule_name, string, verbose=verbose)

    def parse_complete(self, string: str, rule_name: str = 'main', verbose: bool = False):
        """Parse a string but filter out any incomplete parse trees."""

        return filter(lambda tree: tree.is_complete, self.parse(string, rule_name, verbose))

    @classmethod
    def parse_bnf(cls, source: str):
        """Return a grammar described by a given BNF source string."""

        # TODO: maybe extract this grammar out so that it doesnt have to be rebuild everytime?

        # create the BNF grammar itself
        bnf = Grammar({
            # TODO: do a proper string contents
            'string_contents':     Repetition(Choice([Terminal(char) for char in string.ascii_letters + string.digits + '\\ '])),
            'optional_whitespace': Repetition(Choice([Terminal(char) for char in string.whitespace]), generation_override=' '),

            # identifier names can contain alphanumeric characters and underscores but must not start with a number
            'identifier': Sequence([Choice([Terminal(char) for char in string.ascii_letters + '_']), Repetition(Choice([Terminal(char) for char in string.ascii_letters + string.digits + '_']))]),

            # the production rules
            'rule': Sequence([Substitution('identifier', label='name'), Substitution('optional_whitespace'),
                              Option(Sequence([Terminal('"'), Substitution('string_contents', label='override'), Terminal('"'), Substitution('optional_whitespace')])),
                              Terminal('='), Substitution('optional_whitespace'),
                              Substitution('expression', label='expression'), Substitution('optional_whitespace'),
                              Terminal('.')]),

            # right hand expression
            'string':     Sequence([Terminal('"'), Substitution('string_contents', label='contents'), Terminal('"')]),
            'repetition': Sequence([Terminal('{'), Substitution('optional_whitespace'), Substitution('expression', label='expression'), Substitution('optional_whitespace'), Terminal('}')]),
            'option':     Sequence([Terminal('['), Substitution('optional_whitespace'), Substitution('expression', label='expression'), Substitution('optional_whitespace'), Terminal(']')]),
            'item':       Sequence([Option(Sequence([Substitution('identifier', label='label'), Substitution('optional_whitespace'), Terminal(':'), Substitution('optional_whitespace')])), Choice([Substitution('string'), Substitution('identifier'), Substitution('option'), Substitution('repetition')], label='contents')]),
            'sequence':   Sequence([Substitution('item', label='item'), Repetition(Sequence([Choice([Terminal(char) for char in string.whitespace], generation_override=' '), Substitution('item', label='item')]))]),
            'expression': Sequence([Substitution('sequence', label='choice'), Repetition(Sequence([Substitution('optional_whitespace'), Terminal('|'), Substitution('optional_whitespace'), Substitution('sequence', label='choice')]))]),

            # bnf script is sequence of production rules
            'main': Sequence([Substitution('rule', label='rule'), Repetition(Sequence([Substitution('optional_whitespace', generation_override='\n'), Substitution('rule', label='rule')]))]),
        })

        def parse_item(item: Node) -> Element:
            # there may or may not be a label
            labels = list(item.get('label', exclude=['contents']))
            label = labels[0].parsed_string if len(labels) == 1 else None
            # there must be exactly one contents node
            contents = next(item.get('contents'))
            node = contents.children[0]
            if node.rule == 'string':
                # TODO: actually parse the string, for escape chars and such
                return Terminal(next(node.get('contents')).parsed_string, label=label)
            elif node.rule == 'identifier':
                return Substitution(node.parsed_string, label=label)
            elif node.rule == 'option':
                return Option(parse_expression(next(node.get('expression'))), label=label)
            elif node.rule == 'repetition':
                return Repetition(parse_expression(next(node.get('expression'))), label=label)

        def parse_choice(sequence: Node) -> Sequence:
            children = list(map(parse_item, sequence.get('item')))
            return Sequence(children) if len(children) > 1 else children[0]

        def parse_expression(expression: Node) -> Element:
            children = list(map(parse_choice, expression.get('choice')))
            return Choice(children) if len(children) > 1 else children[0]

        def parse_rule(rule: Node) -> (name, Element):
            overrides = list(rule.get('override'))
            override = overrides[0].parsed_string if len(overrides) == 1 else None
            # there shoulddddd only be one, so just get the first
            name = next(rule.get('name')).parsed_string
            expression = next(rule.get('expression'))
            element = parse_expression(expression)
            element.generation_override = override
            return name, element

        def parse_rules(tree: Node) -> dict:
            return {name:element for name, element in list(map(parse_rule, tree.get('rule')))}

        # parse the source with the BNF grammar
        parsed = bnf.parse_complete(source.strip())
        rule_sets = map(parse_rules, parsed)
        grammars = map(cls, rule_sets)

        # just return the first valid grammar i supposed lol
        return next(grammars)

    @classmethod
    def load_bnf(cls, path: str):
        """Return a grammar described by an BNF file given the path to the file."""

        with open(path) as f:
            return cls.parse_bnf(f.read())

    def __str__(self):
        return '\n'.join(f'{rule_name} = {self.rules[rule_name]} .' for rule_name in self.rules)
