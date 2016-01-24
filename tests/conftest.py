from pytest import fixture


from js.interpreter import Interpreter


@fixture
def interpreter(request):
    return Interpreter(testing=True)
