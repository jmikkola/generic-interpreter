import json
import operator


def read_ast(tree):
    if isinstance(tree, str):
        if tree == '#t':
            return ValueExpression(True)
        elif tree == '#f':
            return ValueExpression(False)
        elif tree == '#nil':
            return ValueExpression(None)
        elif tree.startswith('"') and tree.endswith('"'):
            # hacky way to read strings
            val = json.loads(tree)
            return ValueExpression(val)
        else:
            return VarExpression(tree)
    elif isinstance(tree, int) or isinstance(tree, float):
        return ValueExpression(tree)
    else:
        if not tree:
            return []
        kind = tree[0]
        if kind == 'lambda':
            assert(len(tree) == 3)
            return LambdaExpression(tree[1], read_ast(tree[2]))
        elif kind == 'block':
            return BlockExpression([read_ast(child) for child in tree[1:]])
        elif kind == 'set':
            assert(len(tree) == 3)
            return SetExpression(tree[1], read_ast(tree[2]))
        elif kind == 'if':
            assert(len(tree) == 4)
            return IfExpression(
                read_ast(tree[1]), read_ast(tree[2]), read_ast(tree[3]),
            )
        elif kind == 'while':
            assert(len(tree) == 3)
            return WhileExpression(read_ast(tree[1]), read_ast(tree[2]))
        elif kind == 'return':
            assert(len(tree) <= 2)
            if len(tree) == 1:
                expr = ValueExpression(None)
            else:
                expr = read_ast(tree[1])
            return ReturnExpression(expr)
        elif kind == 'new':
            assert(len(tree) > 1)
            assert(len(tree) % 2 == 0)
            fields = [
                (name, read_ast(expr))
                for name, expr in zip(tree[2::2], tree[3::2])
            ]
            return StructureExpression(tree[1], fields)
        elif kind == 'and':
            assert(len(tree) == 3)
            # Treat 'and' as a macro
            return IfExpression(
                read_ast(tree[1]),
                read_ast(tree[2]),
                ValueExpression(False),
            )
        elif kind == 'or':
            assert(len(tree) == 3)
            # Treat 'or' as a macro
            return IfExpression(
                read_ast(tree[1]),
                ValueExpression(True),
                read_ast(tree[2]),
            )
        elif kind == '.':
            assert(len(tree) == 3)
            return StructureAccessExpression(read_ast(tree[1]), tree[2])
        else:
            return FunctionApplication(
                read_ast(kind),
                [read_ast(child) for child in tree[1:]]
            )


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

    def __str__(self):
        if self.value is None:
            return '#nil'
        elif self.value is True:
            return '#t'
        elif self.value is False:
            return '#f'
        elif isinstance(self.value, str):
            return json.dumps(self.value)
        else:
            return str(self.value)


class VarExpression(Expression):
    def __init__(self, name):
        assert(isinstance(name, str))
        self.name = name

    def compute(self, ctx):
        return ctx.get_var(self.name)

    def __str__(self):
        return self.name


class StructureVal:
    def __init__(self, struct_name, fields):
        self.struct_name = struct_name
        self.fields = fields

    def get_field(self, name):
        return self.fields.get(name)


class StructureExpression(Expression):
    def __init__(self, struct_name, fields):
        self.struct_name = struct_name
        self.fields = fields

    def compute(self, ctx):
        field_values = {
            name: expr.compute(ctx)
            for name, expr in self.fields
        }
        return StructureVal(self.struct_name, field_values)

    def __str__(self):
        fields_str = ''
        if self.fields:
            field_strs = [
                '{} {}'.format(name, expr)
                for name, expr in self.fields
            ]
            fields_str = ' ' + ' '.join(field_strs)
        return '(new {}{})'.format(self.struct_name, fields_str)


class StructureAccessExpression(Expression):
    def __init__(self, expr, field_name):
        self.expr = expr
        self.field_name = field_name

    def compute(self, ctx):
        structure_val = self.expr.compute(ctx)
        return structure_val.get_field(self.field_name)

    def __str__(self):
        return '(. {} {})'.format(self.expr, self.field_name)


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

    def __str__(self):
        return '(if {} {} {})'.format(self.test, self.ifcase, self.elsecase)


class WhileExpression(Expression):
    def __init__(self, test, body):
        self.test = test
        self.body = body

    def compute(self, ctx):
        result = None
        while self.test.compute(ctx):
            result = self.body.compute(ctx)
        return result

    def __str__(self):
        return '(while {} {})'.format(self.test, self.body)


class SetExpression(Expression):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def compute(self, ctx):
        value = self.expr.compute(ctx)
        ctx.set_var(self.var, value)
        return value

    def __str__(self):
        return '(set {} {})'.format(self.var, self.expr)


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

    def __str__(self):
        return '(lambda ({}) {})'.format(' '.join(self.arg_names), self.body)


class BuiltinFunction(Expression):
    def __init__(self, fn, name):
        self.fn = fn
        self.name = name

    def compute(self, ctx):
        return self

    def function_call(self, ctx, arg_values):
        return self.fn(*arg_values)

    def __str__(self):
        return self.name


class GenericFunction(Expression):
    def __init__(self, class_name, function_name):
        self.class_name = class_name
        self.function_name = function_name

    def compute(self, ctx):
        return self

    def function_call(self, ctx, arg_values):
        fn = ctx.lookup_generic(
            self.class_name, self.function_name, arg_values,
        )
        return fn.function_call(ctx, arg_values)

    def __str__(self):
        return self.function_name


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

    def __str__(self):
        if self.arg_exprs:
            arg_str = ' '.join(str(a) for a in self.arg_exprs)
            return '({} {})'.format(self.fn_expr, arg_str)
        else:
            return '({})'.format(self.fn_expr)


class ReturnExpression(Expression):
    def __init__(self, expr):
        self.expr = expr

    def compute(self, ctx):
        value = self.expr.compute(ctx)
        raise ReturnException(value)

    def __str__(self):
        return '(return {})'.format(self.expr)


class BlockExpression(Expression):
    def __init__(self, statements):
        self.statements = statements

    def compute(self, ctx):
        result = None

        for stmt in self.statements:
            result = stmt.compute(ctx)

        return result

    def __str__(self):
        inner = ' '.join(str(s) for s in self.statements)
        return '(block {})'.format(inner)


class Context:
    def __init__(self, global_scope):
        self.scopes = [{}]
        self.global_scope = self._default_globals()
        self.global_scope.update(global_scope)
        self.generic_classes = {}
        self.generic_functions_to_class = {}

    def _default_globals(self):
        return {
            '+': BuiltinFunction(operator.add, '+'),
            '-': BuiltinFunction(operator.sub, '-'),
            '*': BuiltinFunction(operator.mul, '*'),
            '/': BuiltinFunction(operator.truediv, '/'),
            '==': BuiltinFunction(operator.eq, '=='),
            '<': BuiltinFunction(operator.lt, '<'),
            '>': BuiltinFunction(operator.gt, '>'),
        }

    def get_var(self, name):
        if name in self.scopes[-1]:
            return self.scopes[-1][name]
        elif name in self.global_scope:
            return self.global_scope[name]
        elif name in self.generic_functions_to_class:
            return GenericFunction(self.generic_functions_to_class[name], name)
        else:
            raise Exception(name + ' is undefined')

    def set_var(self, name, value):
        self.scopes[-1][name] = value

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def add_class(self, class_name, func_names):
        self.generic_classes[class_name] = GenericClass(class_name, func_names)
        for name in func_names:
            self.generic_functions_to_class[name] = class_name

    def add_instance(self, class_name, function_matchers):
        gen_class = self.generic_classes[class_name]
        gen_class.add_instance(function_matchers)

    def lookup_generic(self, class_name, function_name, arg_values):
        gen_class = self.generic_classes[class_name]
        return gen_class.lookup_concrete(function_name, arg_values)


class GenericClass:
    def __init__(self, class_name, func_names):
        self.class_name = class_name
        self.func_names = func_names
        self.functions = {name: [] for name in func_names}

    def add_instance(self, function_matchers):
        assert(set(function_matchers.keys()) == set(self.func_names))
        for name, matcher in function_matchers.items():
            self.functions[name].append(matcher)

    def lookup_concrete(self, function_name, arg_values):
        for matcher in self.functions[function_name]:
            if matcher.matches(arg_values):
                return matcher.function
        raise Exception(
            'generic instance of {} not found for {}'.
            format(function_name, arg_values),
        )


class FunctionMatcher:
    def __init__(self, function, arg_matchers):
        assert(len(arg_matchers) > 0)
        self.function = function
        self.arg_matchers = arg_matchers

    def matches(self, arg_values):
        for key, arg_matcher in self.arg_matchers.items():
            if not arg_matcher.matches(arg_values[key]):
                return False
        return True


class TypeMatcher:
    def __init__(self, t):
        self.t = t

    def matches(self, value):
        return isinstance(value, StructureVal) and value.struct_name == self.t
