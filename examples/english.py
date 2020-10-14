from nangram import Grammar, random_sample, random_choice

if __name__ == '__main__':

    print('Loading grammar...')
    grammar = Grammar.load_bnf('english.bnf')

    # print some random expressions in the grammar
    # also reparse them for validity
    rule = 'main'
    verbose = False
    sample_size = 5

    print('Generating a single sentence...\n')
    expression = random_choice(lambda: grammar.generate(rule, verbose=verbose))
    print(expression)
    print()

    print(f'Generating {sample_size} sentences...\n')
    for expression in random_sample(lambda: grammar.generate(rule, verbose=verbose), sample_size):
        print(expression)
        for tree in grammar.parse_complete(expression, rule, verbose=verbose):
            print(tree)
        print()
