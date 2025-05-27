
class Closure:
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env.copy()  # Захватываем копию окружения

    def eval_expr(self, args):
        local_env = self.env.copy()  # Создаём новое окружение на основе захваченного
        for name, val in zip(self.params, args):
            local_env[name] = val
        return evaluate(self.body, local_env)


def evaluate(expr, env=None):
    if env is None:
        env = {}

    if isinstance(expr, int):
        return expr

    if isinstance(expr, str):
        if expr in env:
            return env[expr]
        raise NameError(f"Unbound variable: {expr}")

    head, *rest = expr

    if head == 'let':
        var, val_expr, body = rest
        val = evaluate(val_expr, env)
        new_env = env.copy()  # Создаём новое окружение для тела let
        new_env[var] = val
        return evaluate(body, new_env)

    if head == 'fun':
        params, body = rest
        return Closure(params, body, env)

    if head == 'call':
        fun_expr, arg_exprs = rest
        fun_val = evaluate(fun_expr, env)
        if not isinstance(fun_val, Closure):
            raise TypeError("Trying to call a non-function")
        args = [evaluate(arg, env) for arg in arg_exprs]
        return fun_val.eval_expr(args)

    if head == '+':
        a, b = rest
        return evaluate(a, env) + evaluate(b, env)

    if head == '*':
        a, b = rest
        return evaluate(a, env) * evaluate(b, env)

    raise SyntaxError(f"Unknown expression head: {head}")


if __name__ == '__main__':
    program = [
        'let', 'square',
        ['fun', ['x'], ['*', 'x', 'x']],
        ['call', 'square', [5]]
    ]
    result = evaluate(program)
    print(result)  # 25