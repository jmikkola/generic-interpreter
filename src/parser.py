import re

from interpreter import read_ast


token_re = re.compile(
    r'([(]|[)]|;;[^\n]*\n|"(?:[^"\\]|\\.)*"|[^\s()]+|\s+|\n)',
)
float_re = re.compile(r'^[+-]?\d+(\.\d+)?([eE][+-]?\d+)?$')


def parse(text):
    tokens = tokenize(text)
    lists = parse_tokens(tokens)
    return [read_ast(lst) for lst in lists]


def tokenize(text):
    return [
        t for t in token_re.findall(text)
        if not t.isspace() and not t.startswith(';;')
    ]


def parse_tokens(tokens):
    expressions = []
    while tokens:
        expr, tokens = parse_expr(tokens)
        expressions.append(expr)
    return expressions


def parse_expr(tokens):
    if tokens[0] == '(':
        return parse_list(tokens)
    elif tokens[0].isdigit():
        return int(tokens[0]), tokens[1:]
    elif float_re.match(tokens[0]):
        return float(tokens[0]), tokens[1:]
    else:
        return tokens[0], tokens[1:]


def parse_list(tokens):
    tokens = tokens[1:]
    expressions = []
    while tokens[0] != ')':
        expr, tokens = parse_expr(tokens)
        expressions.append(expr)
    tokens = tokens[1:]
    return expressions, tokens
