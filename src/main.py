class ReturnException(Exception):
    def __init__(self, ret_value):
        self.ret_value = ret_value

class Expression:
    def compute(self, ctx):
        pass

class ValueExpression(Expression):
    def __init__(self, value):
        self.value = value

    def compute(self, ctx):
        return self.value

class VarExpression(Expression):
    def __init__(self, name):
        self.name = name

    def compute(self, ctx):
        return ctx.get_var(self.name)

class BinaryExpression(Expression):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def compute(self, ctx):
        lval = self.left.compute(ctx)
        rval = self.right.compute(ctx)
        if self.op == '+':
            return lval + rval
        elif self.op == '-':
            return lval - rval
        elif self.op == '*':
            return lval * rval
        elif self.op == '/':
            return lval / rval
        elif self.op == '==':
            return lval == rval
        elif self.op == '>':
            return lval > rval
        elif self.op == '<':
            return lval < rval
        elif self.op == '&&':
            return lval and rval
        elif self.op == '||':
            return lval or rval
        else:
            raise Exception('unknown op: ' + repr(self.op))

class IfExpression(Expression):
    def __init__(self, test, ifcase, elsecase):
        self.test = test
        self.ifcase = ifcase
        self.elsecase = elsecase

    def compute(self, ctx):
        if self.test.compute(ctx):
            return self.ifcase.compute(ctx)
        else:
            return self.elsecase.compute(ctx)


class SetExpression(Expression):
    def __init__(self, var, value):
        self.var = var
        self.value = value

    def compute(self, ctx):
        ctx.set_var(self.var, ctx.compute(self.value))

class LambdaExpression(Expression):
    def __init__(self, arg_names, body):
        self.arg_names = arg_names
        self.body = body

    def compute(self, ctx):
        return self

    def function_call(self, ctx, arg_values):
        ctx.push_scope()

        for (name, value) in zip(self.arg_names, arg_values):
            ctx.set_var(name, value)

        try:
            ret_value = self.body.compute(ctx)
        except ReturnException as e:
            ret_value = e.ret_value
        ctx.pop_scope()
        return ret_value


class BuiltinFunction(Expression):
    def __init__(self, fn):
        self.fn = fn

    def compute(self, ctx):
        return self

    def function_call(self, ctx, arg_values):
        return self.fn(*arg_values)


class FunctionApplication(Expression):
    def __init__(self, fn_expr, arg_exprs):
        self.fn_expr = fn_expr
        self.arg_exprs = arg_exprs

    def compute(self, ctx):
        fn = self.fn_expr.compute(ctx)  # usually a variable lookup
        arg_values = [
            arg_expr.compute(ctx) for arg_expr in self.arg_exprs
        ]
        return fn.function_call(ctx, arg_values)

class BlockExpression(Expression):
    def __init__(self, statements):
        self.statements = statements

    def compute(self, ctx):
        result = None

        for stmt in self.statements:
            result = stmt.compute(ctx)

        return result


class Context:
    def __init__(self, global_scope):
        self.scopes = [{}]
        self.global_scope = global_scope

    def get_var(self, name):
        if name in self.scopes[-1]:
            return self.scopes[-1][name]
        else:
            return self.global_scope[name]

    def set_var(self, name, value):
        self.scopes[-1][name] = value

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()


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
