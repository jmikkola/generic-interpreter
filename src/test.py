import unittest

from interpreter import (
    BuiltinFunction,
    Context,
    FunctionApplication,
    FunctionMatcher,
    TypeMatcher,
    ValueExpression,
    VarExpression,
)
from parser import parse


class InterpreterTest(unittest.TestCase):
    def test_builtins(self):
        foo_called = [False]

        def foo(x):
            foo_called[0] = True
            return 2 * x

        ctx = Context({
            'foo': BuiltinFunction(foo, 'foo'),
        })
        expr = FunctionApplication(
            VarExpression('foo'), [ValueExpression(100)],
        )
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

    def test_generics(self):
        text = '''
        (lambda (person) (return (+ "Hello, " (. person name))))
        (lambda (dog) "Woof!")
        (greet (new Person name "Joe"))
        (greet (new Dog))
        '''
        exprs = parse(text)

        ctx = Context({})
        ctx.add_class('Greeter', ['greet'])
        ctx.add_instance('Greeter', {
            'greet': FunctionMatcher(exprs[0], {
                0: TypeMatcher(t='Person'),
            }),
        })
        ctx.add_instance('Greeter', {
            'greet': FunctionMatcher(exprs[1], {
                0: TypeMatcher(t='Dog'),
            }),
        })

        self.assertEqual('Hello, Joe', exprs[2].compute(ctx))
        self.assertEqual('Woof!', exprs[3].compute(ctx))

    def test_short_circuit(self):
        text = '''
        (and #t (log "good" #t))  ;; expected: True
        (and #t (log "good" #f))  ;; expected: False
        (and #f (log "error" #t)) ;; expected: False
        (or #f (log "good" #t))   ;; expected: True
        (or #f (log "good" #f))   ;; expected: False
        (or #t (log "error" #t))  ;; expected: True
        '''
        exprs = parse(text)

        logs = []

        def log_and_return(message, value):
            logs.append(message)
            return value

        ctx = Context({
            'log': BuiltinFunction(log_and_return, 'log'),
        })

        expectations = [True, False, False, True, False, True]
        for (expected, expr) in zip(expectations, exprs):
            self.assertEqual(expected, expr.compute(ctx))
        self.assertEqual(logs, ["good"] * 4)

    def test_while(self):
        text = '''
        (block
            (set x 30)
            (set n 1)
            (while (> x 1)
                (block
                    (set n (* n x))
                    (set x (- x 1))))
            n)
        '''
        exprs = parse(text)

        ctx = Context({})
        self.assertEqual(
            265252859812191058636308480000000,
            exprs[0].compute(ctx),
        )

    def test_self_parses(self):
        ''' ensure that the __str__ method returns a parsable result '''
        text = '''
        (block
            (set x 10)
            (set n 1)
            (while (> x 1)
                (block
                    (set n (* n x))
                    (set x (- x 1))))
            n)
        ((lambda (n) (+ n 1)) 234)
        (foo 123 123.45 #t #f #nil "a string")
        (and (or #t #f) #t)
        (if 1 2 3)
        (. (new MyStruct foo 123 bar (+ 10 3)) bar)
        '''
        exprs = parse(text)

        ctx = Context({
            'foo': BuiltinFunction(lambda *a: list(a), 'foo'),
        })

        foo_values = [123, 123.45, True, False, None, 'a string']
        expected_values = [3628800, 235, foo_values, True, 2, 13]
        for (expected, expr) in zip(expected_values, exprs):
            text1 = str(expr)
            expr2 = parse(text1)
            text2 = str(expr2[0])
            self.assertEqual(text1, text2)
            self.assertEqual(expected, expr2[0].compute(ctx))


if __name__ == '__main__':
    unittest.main()
