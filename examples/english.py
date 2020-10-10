from nangram import Grammar, random_sample

if __name__ == '__main__':

    print('Loading grammar...')
    grammar = Grammar.load_bnf('english.bnf')

    # print some random expressions in the grammar
    # also reparse them for validity
    print('Generating sentences...')
    rule = 'main'
    verbose = False
    sample_size = 5
    for expression in random_sample(lambda: grammar.generate(rule, verbose=verbose), sample_size):
        print(expression)
        for tree in grammar.parse_complete(expression, rule, verbose=verbose):
            print(tree)
        print()
