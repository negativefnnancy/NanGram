import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='nangram',
    version='0.0.1',
    author='Negative Nancy',
    author_email='negativefnnancy@gmail.com',
    description='Small little context-free expression generator and parser using user provided EBNF-like source.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/negativefnnancy/NanGram',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
