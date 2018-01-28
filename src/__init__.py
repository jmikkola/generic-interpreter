from interpreter import *


def main():
    ctx = Context({
        'double': LambdaExpression(['n'], BinaryExpression('*', VarExpression('n'), ValueExpression(2))),
        'fib': LambdaExpression(
            ['n'],
            IfExpression(
                BinaryExpression('<', VarExpression('n'), ValueExpression(2)),
                VarExpression('n'),
                BinaryExpression(
                    '+',
                    FunctionApplication(VarExpression('fib'), [BinaryExpression('-', VarExpression('n'), ValueExpression(1))]),
                    FunctionApplication(VarExpression('fib'), [BinaryExpression('-', VarExpression('n'), ValueExpression(2))]),
                ),
            ),
        ),
        'print': BuiltinFunction(print),
    })

    expr = FunctionApplication(
        VarExpression('print'),
        [FunctionApplication(VarExpression('fib'), [ValueExpression(20)])],
    )
    expr.compute(ctx)


if __name__ == '__main__':
    main()
