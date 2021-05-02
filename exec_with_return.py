import ast
import copy

def exec_with_return(code, _globals, _locals):
    code_ast = ast.parse(code)

    init_ast = copy.deepcopy(code_ast)
    init_ast.body = code_ast.body[:-1]

    last_ast = copy.deepcopy(code_ast)
    last_ast.body = code_ast.body[-1:]

    exec(compile(init_ast, "<ast>", "exec"), _globals, _locals)

    if not last_ast.body:
        return None

    if type(last_ast.body[0]) == ast.Expr:
        expr = ast.Expression(last_ast.body[0].value, lineno=0, col_offset=0)
        return eval(compile(expr, "<ast>", "eval"), _globals, _locals)

    else:
        exec(compile(last_ast, "<ast>", "exec"), _globals, _locals)
