from interpreter import Context, BuiltinFunction
from parser import parse


def main():
    text = '''
    (lambda (n) (* n 2))
    (lambda (n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2)))))
    (print (fib 20))
    '''
    exprs = parse(text)

    ctx = Context({
        'double': exprs[0],
        'fib': exprs[1],
        'print': BuiltinFunction(print),
    })

    expr = exprs[2]
    expr.compute(ctx)


if __name__ == '__main__':
    main()
