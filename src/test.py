import unittest

from .interpreter import *

class InterpreterTest(unittest.TestCase):
    def test_builtins(self):
        foo_called = [False]

        def foo(x):
            foo_called[0] = True
            return 2 * x

        ctx = Context({
            'foo': BuiltinFunction(foo),
        })
        expr = FunctionApplication(VarExpression('foo'), [ValueExpression(100)])
        result = expr.compute(ctx)
        self.assertEqual(200, result)
        self.assertEqual(True, foo_called[0])

    def test_recursive_functions(self):
        ctx = Context({
            'factorial': LambdaExpression(
                ['n'],
                IfExpression(
                    BinaryExpression('<', VarExpression('n'), ValueExpression(2)),
                    ValueExpression(1),
                    BinaryExpression(
                        '*',
                        VarExpression('n'),
                        FunctionApplication(
                            VarExpression('factorial'),
                            [BinaryExpression('-', VarExpression('n'), ValueExpression(1))],
                        ),
                    ),
                ),
            ),
        })
        expr = FunctionApplication(VarExpression('factorial'), [ValueExpression(5)])
        self.assertEqual(120, expr.compute(ctx))

if __name__ == '__main__':
    unittest.main()
