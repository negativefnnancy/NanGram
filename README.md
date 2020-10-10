# NanGram

Negative Nancy's expression generator & parser! XD

Write grammars, generate random expressions, parse expressions.

## Installation

```bash
pip install nangram
```

## Usage

First write yourself a nice little grammar like this!:

`grammar.bnf`:
```
determiner = "the " | "a " .
noun = "cat " | "dog " | "chair " .
verb = "runs " | "snacks " | "plays " .
adverb = "quickly " | "ferociously " | "sneakily " .

noun_phrase = determiner noun .
verb_phrase = verb adverb .
sentence = noun_phrase verb_phrase .

main = sentence .
```

Then import `nangram` and load the grammar source:

```python
import nangram

grammar = nangram.Grammar.load_bnf('grammar.bnf')
```

Then generate some expressions!:

```python
for expression in grammar.generate():
    print(expression)
```

And you get...

```
the cat plays ferociously
the dog plays ferociously
the chair snacks quickly
a cat snacks quickly
a dog runs quickly
a dog snacks ferociously
a dog plays quickly
a chair plays ferociously
```

Then try parsing something:

```python
for parse_tree in grammar.parse('a cat snacks sneakily '):
    print(parse_tree)
```

And you get...

```
sentence = 'a cat snacks sneakily '
├ noun_phrase = 'a cat '
│ ├ determiner = 'a '
│ └ noun = 'cat '
└ verb_phrase = 'snacks sneakily '
  ├ verb = 'snacks '
  └ adverb = 'sneakily '
```

(The parser will yield as many parse trees as are valid, so if you have an ambiguous grammar, for example, you can parse all variations. If the expression is not in the language, you won't get any parse trees.)

See `examples/english.bnf` and `examples/english.py` for another example.
