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


class Context:
    def __init__(self):
        self.scopes = [{}]

    def get_var(self, name):
        return self.scopes[-1][name]

    def set_var(self, name, value):
        self.scopes[-1][name] = value

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()


def main():
    ctx = Context()
    ctx.set_var('double', LambdaExpression(['n'], BinaryExpression('*', VarExpression('n'), ValueExpression(2))))
    expr = FunctionApplication(VarExpression('double'), [ValueExpression(100)])
    result = expr.compute(ctx)
    print(result)

if __name__ == '__main__':
    main()
