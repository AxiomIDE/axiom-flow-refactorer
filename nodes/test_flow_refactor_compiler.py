from nodes.flow_refactor_compiler import flow_refactor_compiler


def test_flow_refactor_compiler_imports():
    assert callable(flow_refactor_compiler)
