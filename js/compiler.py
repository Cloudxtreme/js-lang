from js.bytecode import CompilerContext


def compile_ast(ast):
    return CompilerContext().compile_ast(ast)
