
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
    ctx.set_var('x', 123)
    expr = BinaryExpression('+', VarExpression('x'), ValueExpression(456))
    result = expr.compute(ctx)
    print(result)

if __name__ == '__main__':
    main()
