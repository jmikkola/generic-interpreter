import unittest

from .interpreter import *
from .parser import parse

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
        text = '''
        (lambda (n) (if (< n 2) 1 (* n (factorial (- n 1)))))
        (factorial 5)
        '''
        exprs = parse(text)
        ctx = Context({'factorial': exprs[0]})
        self.assertEqual(120, exprs[1].compute(ctx))

    def test_structures(self):
        text = '''
        (. (new MyStruct foo 123 bar (+ 10 3)) bar)
        '''
        exprs = parse(text)
        ctx = Context({})
        self.assertEqual(13, exprs[0].compute(ctx))


if __name__ == '__main__':
    unittest.main()
